#!/usr/bin/env python3
import concurrent.futures
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path("_site")
ALLOWLIST_PATH = Path("tools/known_external_url_issues.txt")
INTERNAL_HOSTS = {"decentralizedthoughts.github.io"}
TEXT_SUFFIXES = {".html", ".xml"}
URL_RE = re.compile(r"""https?://[^\s"'<>]+""")
TIMEOUT_SECONDS = 15
MAX_WORKERS = 16
RETRIES = 2


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


def iter_urls():
    urls = set()
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        data = path.read_text(encoding="utf-8", errors="ignore")
        for raw in URL_RE.findall(data):
            raw = raw.rstrip(").,")
            parsed = urlparse(raw)
            if parsed.netloc in INTERNAL_HOSTS:
                continue
            if raw in ALLOWLIST:
                continue
            urls.add(raw)
    return sorted(urls)


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
    if not ROOT.exists():
        print("ERROR: build the site first", file=sys.stderr)
        return 2

    urls = iter_urls()
    if not urls:
        print("OK: no external URLs found")
        return 0

    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(fetch, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            error = future.result()
            if error:
                failures.append((url, error))

    if failures:
        for url, error in sorted(failures):
            print(f"ERROR: external URL failed: {url} ({error})", file=sys.stderr)
        print(f"FAIL: {len(failures)} external URLs failed", file=sys.stderr)
        return 1

    print(f"OK: {len(urls)} external URLs reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
