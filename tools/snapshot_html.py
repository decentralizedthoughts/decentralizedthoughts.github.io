#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path("_site")
OUT = Path("tests/snapshots")


def url_to_file(url: str) -> Path:
    if url == "/":
        return ROOT / "index.html"
    stripped = url.strip("/")
    if url.endswith("/"):
        return ROOT / stripped / "index.html"
    return ROOT / stripped


def url_to_snapshot_path(url: str) -> Path:
    if url == "/":
        return OUT / "index.html"
    stripped = url.strip("/")
    if url.endswith("/"):
        return OUT / stripped / "index.html"
    return OUT / stripped


def normalize_html_like(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace(
        "https://decentralizedthoughts.github.io/pages/decentralizedthoughts/",
        "https://decentralizedthoughts.github.io/",
    )
    text = text.replace("/pages/decentralizedthoughts/", "/")
    text = text.replace(
        "https%3A%2F%2Fdecentralizedthoughts.github.io%2Fpages%2Fdecentralizedthoughts%2F",
        "https%3A%2F%2Fdecentralizedthoughts.github.io%2F",
    )
    text = text.replace("&apos;", "'")
    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip() + "\n"


def normalize_json(text: str) -> str:
    data = json.loads(text)
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def normalize_text(path: Path, text: str) -> str:
    if path.suffix == ".json":
        return normalize_json(text)
    if path.suffix in {".html", ".xml"}:
        return normalize_html_like(text)
    return text.replace("\r\n", "\n").strip() + "\n"


def main():
    urls = [line.strip() for line in sys.stdin.read().splitlines() if line.strip() and not line.startswith("#")]
    if not urls:
        print("No URLs provided on stdin", file=sys.stderr)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    missing = []
    for url in urls:
        src = url_to_file(url)
        if not src.exists():
            missing.append((url, str(src)))
            continue
        dst = url_to_snapshot_path(url)
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_text(encoding="utf-8", errors="ignore")
        dst.write_text(normalize_text(src, data), encoding="utf-8")

    if missing:
        for url, path in missing[:20]:
            print(f"Missing built file for {url}: {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
