#!/usr/bin/env python3
import os
from pathlib import Path

ROOT = Path("_site")
EXCLUDED_PREFIXES = ("tests/", "tools/")
EXCLUDED_FILES = {
    "grep.sh",
    "print-logs.sh",
    "setup-docker.sh",
    "start-server.sh",
    "stop-server.sh",
}


def to_url(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    if rel in EXCLUDED_FILES or rel.startswith(EXCLUDED_PREFIXES):
        return None
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + path.relative_to(ROOT).parent.as_posix().strip("/") + "/"
    if rel.endswith(".html"):
        return "/" + rel
    if rel.endswith(".xml"):
        return "/" + rel
    return None


def main():
    if not ROOT.exists():
        raise SystemExit("Build the site first")

    urls = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        url = to_url(path)
        if url is not None:
            urls.append(url)

    print("\n".join(urls))


if __name__ == "__main__":
    main()
