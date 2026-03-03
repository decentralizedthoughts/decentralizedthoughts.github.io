#!/usr/bin/env python3
import os, re, sys
from urllib.parse import urlparse, urldefrag, unquote

ROOT = "_site"

HREF_RE = re.compile(r'''(?:href|src)\s*=\s*["']([^"']+)["']''', re.IGNORECASE)

PREFIXES = [
    "/pages/decentralizedthoughts",
]

def load_allowlist():
    path = os.path.join("tools", "known_broken_links.txt")
    s = set()
    if os.path.isfile(path):
        for line in open(path, "r", encoding="utf-8", errors="ignore"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            s.add(line)
    return s

ALLOWLIST = load_allowlist()

def looks_like_placeholder(raw: str) -> bool:
    r = raw.strip()
    if r in ("...",):
        return True
    if r.startswith("..."):
        return True
    if " " in r:
        return True
    # common accidental patterns
    if r.lower().startswith("post-on") or r.lower().startswith("post%20on"):
        return True
    if r.lower().startswith("post"):
        return True
    # markdown typo: href="(https://example.com)"
    if r.startswith("(") and r.endswith(")") and ("http://" in r or "https://" in r):
        return True
    return False

def norm_path(p: str) -> str:
    p = unquote(p)
    p = p.split("?", 1)[0]

    for pref in PREFIXES:
        if p == pref:
            p = "/"
        elif p.startswith(pref + "/"):
            p = p[len(pref):]

    # Normalize common internal absolute urls
    p = p.lstrip("/")
    return p

def exists_target(p: str) -> bool:
    if not p:
        return True
    fp = os.path.join(ROOT, p)
    if os.path.isfile(fp):
        return True
    if os.path.isdir(fp) and os.path.isfile(os.path.join(fp, "index.html")):
        return True
    if p.endswith("/") and os.path.isfile(os.path.join(ROOT, p, "index.html")):
        return True
    if os.path.isfile(os.path.join(ROOT, p, "index.html")):
        return True
    return False

def main():
    if not os.path.isdir(ROOT):
        print(f"ERROR: {ROOT} not found. Run jekyll build first.", file=sys.stderr)
        return 2

    all_files = set()
    for dirpath, _, filenames in os.walk(ROOT):
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            all_files.add(rel)

    errors = 0
    html_files = [f for f in all_files if f.endswith(".html")]
    for rel in sorted(html_files):
        path = os.path.join(ROOT, rel)
        try:
            data = open(path, "r", encoding="utf-8", errors="ignore").read()
        except Exception as e:
            print(f"ERROR: cannot read {rel}: {e}")
            errors += 1
            continue

        for m in HREF_RE.finditer(data):
            raw = m.group(1).strip()
            if not raw:
                continue

            if looks_like_placeholder(raw):
                continue

            if raw.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
                continue
            if raw.startswith("#"):
                continue
            if raw.startswith("//"):
                continue
            if "{{" in raw or "}}" in raw:
                continue

            raw2, _frag = urldefrag(raw)
            parsed = urlparse(raw2)
            if parsed.scheme or parsed.netloc:
                continue

            # allowlist is checked on the original path (before stripping prefixes)
            if parsed.path in ALLOWLIST:
                continue

            p = norm_path(parsed.path)
            if not exists_target(p):
                print(f"ERROR: missing target referenced from {rel}: {raw}")
                errors += 1

    if errors:
        print(f"FAIL: {errors} missing targets/assets")
        return 1

    print("OK: internal targets/assets exist")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
