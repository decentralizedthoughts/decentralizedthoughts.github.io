#!/usr/bin/env python3
import os, re, sys
from pathlib import Path

ROOT=Path("_site")
OUT=Path("tests/snapshots")

def url_to_file(url: str) -> Path:
    if url.endswith("feed.xml"):
        return ROOT/"feed.xml"
    u=url.strip("/")
    if u=="":
        return ROOT/"index.html"
    return ROOT/u/"index.html"

def url_to_snapshot_path(url: str) -> Path:
    u=url.strip("/")
    if url.endswith("feed.xml"):
        return OUT/"feed.xml"
    if u=="":
        return OUT/"index.html"
    return OUT/u/"index.html"

def normalize_html(s: str) -> str:
    s = s.replace("\r\n", "\n")

    # normalize legacy baseurl prefix used in some environments
    s = s.replace("https://decentralizedthoughts.github.io/pages/decentralizedthoughts/", "https://decentralizedthoughts.github.io/")
    s = s.replace("/pages/decentralizedthoughts/", "/")
    s = s.replace(
        "https%3A%2F%2Fdecentralizedthoughts.github.io%2Fpages%2Fdecentralizedthoughts%2F",
        "https%3A%2F%2Fdecentralizedthoughts.github.io%2F",
    )
    s = s.replace("&apos;", "'")
    s = re.sub(r"(?m)^[ \t]+$", "", s)

    # strip multiple whitespace
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n+", "\n", s)
    # remove build noise patterns if any appear
    s = re.sub(r"<!--.*?-->", "", s)
    return s.strip() + "\n"

def main():
    urls = [l.strip() for l in sys.stdin.read().splitlines() if l.strip() and not l.strip().startswith("#")]
    if not urls:
        print("No URLs provided on stdin", file=sys.stderr)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    missing=[]
    for url in urls:
        src=url_to_file(url)
        if not src.exists():
            missing.append((url, str(src)))
            continue
        dst=url_to_snapshot_path(url)
        dst.parent.mkdir(parents=True, exist_ok=True)
        data=src.read_text(encoding="utf-8", errors="ignore")
        dst.write_text(normalize_html(data), encoding="utf-8")
    if missing:
        for url, path in missing[:20]:
            print(f"Missing built file for {url}: {path}", file=sys.stderr)
        return 1
    return 0

if __name__=="__main__":
    raise SystemExit(main())
