#!/usr/bin/env python3
import argparse
import concurrent.futures
import html
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path("_site")
ALLOWLIST_PATH = Path("tools/known_external_url_issues.txt")
BASELINE_PATH = Path("tools/external_urls_baseline.txt")
INTERNAL_HOSTS = {"decentralizedthoughts.github.io"}
TEXT_SUFFIXES = {".html", ".xml", ".css"}
URL_RE = re.compile(r"""https?://[^\s"'<>]+""")
CSS_URL_RE = re.compile(r"""url\(\s*['"]?(https?://[^)'"]+)['"]?\s*\)""")
TIMEOUT_SECONDS = 8
MAX_WORKERS = 32
RETRIES = 1


def load_allowlist():
    allowed = set()
    if not ALLOWLIST_PATH.exists():
        return allowed
    for line in ALLOWLIST_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            allowed.add(line)
    return allowed


ALLOWLIST = load_allowlist()


def normalize_url(raw):
    return html.unescape(raw.strip().rstrip(").,"))


class ExternalAssetParser(HTMLParser):
    ASSET_TAG_ATTRS = {
        "script": {"src"},
        "img": {"src", "srcset"},
        "iframe": {"src"},
        "audio": {"src"},
        "video": {"src", "poster"},
        "source": {"src", "srcset"},
        "embed": {"src"},
        "object": {"data"},
    }

    def __init__(self, include_anchor_hrefs=False):
        super().__init__()
        self.include_anchor_hrefs = include_anchor_hrefs
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        attr_map = dict(attrs)
        if tag == "link":
            href = attr_map.get("href")
            rel = {part.strip().lower() for part in attr_map.get("rel", "").split()}
            if href and ({"stylesheet", "preload", "icon"} & rel):
                self._add_url(href)
            return
        if tag == "a" and self.include_anchor_hrefs:
            self._add_url(attr_map.get("href"))
            return
        for attr in self.ASSET_TAG_ATTRS.get(tag, set()):
            self._add_attr_value(attr_map.get(attr))

    def _add_attr_value(self, value):
        if not value:
            return
        if "," in value and " " in value:
            for candidate in value.split(","):
                url = candidate.strip().split()[0]
                self._add_url(url)
            return
        self._add_url(value)

    def _add_url(self, raw):
        if not raw:
            return
        raw = normalize_url(raw)
        parsed = urlparse(raw)
        if parsed.scheme not in {"http", "https"}:
            return
        if parsed.netloc in INTERNAL_HOSTS:
            return
        if raw in ALLOWLIST:
            return
        self.urls.add(raw)


def iter_urls(include_anchor_hrefs=False):
    urls = set()
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        data = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix == ".css":
            for raw in CSS_URL_RE.findall(data):
                raw = normalize_url(raw)
                parsed = urlparse(raw)
                if parsed.netloc not in INTERNAL_HOSTS and raw not in ALLOWLIST:
                    urls.add(raw)
            continue
        parser = ExternalAssetParser(include_anchor_hrefs=include_anchor_hrefs)
        parser.feed(data)
        urls.update(parser.urls)
        if include_anchor_hrefs:
            for raw in URL_RE.findall(data):
                raw = normalize_url(raw)
                parsed = urlparse(raw)
                if parsed.netloc in INTERNAL_HOSTS or raw in ALLOWLIST:
                    continue
                urls.add(raw)
    return sorted(urls)


def load_baseline(path):
    if not path.exists():
        return set()
    urls = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.add(line)
    return urls


def write_baseline(path, urls):
    path.write_text("".join(f"{url}\n" for url in urls), encoding="utf-8")


def fetch(url):
    headers = {"User-Agent": "decentralizedthoughts-link-checker/1.0"}
    last_error = None
    for attempt in range(RETRIES + 1):
        for method in ("HEAD", "GET"):
            request = urllib.request.Request(url, headers=headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                    status = getattr(response, "status", 200)
                    if 200 <= status < 400:
                        return None
                    last_error = f"HTTP {status}"
            except urllib.error.HTTPError as exc:
                if method == "HEAD" and exc.code in (400, 403, 405, 429, 503):
                    last_error = f"{method} HTTP {exc.code}"
                    continue
                if 200 <= exc.code < 400:
                    return None
                last_error = f"{method} HTTP {exc.code}"
            except Exception as exc:
                last_error = f"{method} {exc}"
        if attempt < RETRIES:
            time.sleep(1.5 * (attempt + 1))
    return last_error or "unknown error"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--include-anchor-hrefs",
        action="store_true",
        help="also check outbound <a href> links; slower and more brittle than asset checks",
    )
    parser.add_argument(
        "--baseline",
        default=str(BASELINE_PATH),
        help="path to the tracked external URL baseline",
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="verify all discovered URLs instead of only newly introduced ones",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="write the current discovered URL set to the baseline file and exit",
    )
    args = parser.parse_args()

    if not ROOT.exists():
        print("ERROR: build the site first", file=sys.stderr)
        return 2

    urls = iter_urls(include_anchor_hrefs=args.include_anchor_hrefs)
    if not urls:
        print("OK: no external URLs found")
        return 0

    baseline_path = Path(args.baseline)
    if args.write_baseline:
        write_baseline(baseline_path, urls)
        print(f"OK: wrote {len(urls)} external URLs to {baseline_path}")
        return 0

    baseline_urls = load_baseline(baseline_path)
    urls_to_check = urls if args.check_all else sorted(set(urls) - baseline_urls)
    if not urls_to_check:
        scope = "external URLs" if args.include_anchor_hrefs else "page-critical external assets"
        print(f"OK: no new {scope} compared with {baseline_path}")
        return 0

    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(fetch, url): url for url in urls_to_check}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            error = future.result()
            if error:
                failures.append((url, error))

    if failures:
        for url, error in sorted(failures):
            print(f"ERROR: external URL failed: {url} ({error})", file=sys.stderr)
        print(f"FAIL: {len(failures)} new external URLs failed", file=sys.stderr)
        return 1

    mode = "external URLs" if args.include_anchor_hrefs else "page-critical external assets"
    if args.check_all:
        print(f"OK: {len(urls_to_check)} {mode} reachable")
    else:
        print(f"OK: {len(urls_to_check)} new {mode} reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
