#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

ROOT = "_site"
INTERNAL_HOSTS = {"decentralizedthoughts.github.io"}
FORBIDDEN_PREFIXES = ("tests/", "tools/")
FORBIDDEN_FILES = {
    "grep.sh",
    "print-logs.sh",
    "setup-docker.sh",
    "start-server.sh",
    "stop-server.sh",
}

ATTR_RE = re.compile(
    r"""(?:href|src|poster)\s*=\s*["']([^"']+)["']""",
    re.IGNORECASE,
)
SRCSET_RE = re.compile(r"""srcset\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
CSS_URL_RE = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", re.IGNORECASE)
XML_LINK_RE = re.compile(r"""<(?:link|guid|loc)>([^<]+)</(?:link|guid|loc)>""", re.IGNORECASE)

PREFIXES = ["/pages/decentralizedthoughts"]


def load_allowlist():
    path = os.path.join("tools", "known_broken_links.txt")
    allowed = set()
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                line = line.strip()
                if line and not line.startswith("#"):
                    allowed.add(line)
    return allowed


ALLOWLIST = load_allowlist()


def looks_like_placeholder(raw: str) -> bool:
    value = raw.strip()
    if value in ("...",):
        return True
    if value.startswith("..."):
        return True
    if " " in value and not value.startswith("http"):
        return True
    if value.lower().startswith("post-on") or value.lower().startswith("post%20on"):
        return True
    if value.lower().startswith("post"):
        return True
    if value.startswith("(") and value.endswith(")") and ("http://" in value or "https://" in value):
        return True
    return False


def normalize_site_path(path: str) -> str:
    path = unquote(path).split("?", 1)[0]
    for prefix in PREFIXES:
        if path == prefix:
            path = "/"
        elif path.startswith(prefix + "/"):
            path = path[len(prefix):]
    return path


def normalize_relative_path(path: str) -> str:
    normalized = str(PurePosixPath(path))
    if normalized == ".":
        return ""
    return normalized.lstrip("/")


def resolve_internal_target(referrer: str, raw: str):
    raw = raw.strip()
    if not raw or raw.startswith("#") or raw.startswith("//"):
        return None
    if raw.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None
    if "{{" in raw or "}}" in raw:
        return None
    if looks_like_placeholder(raw):
        return None

    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in ("http", "https"):
            return None
        if parsed.netloc not in INTERNAL_HOSTS:
            return None
        path = normalize_site_path(parsed.path)
        if path in ALLOWLIST:
            return None
        return normalize_relative_path(path)

    path = normalize_site_path(parsed.path)
    if path in ALLOWLIST:
        return None

    if raw.startswith("/"):
        return normalize_relative_path(path)

    base_dir = PurePosixPath(referrer).parent
    combined = normalize_relative_path(str(base_dir / path))
    if combined.startswith("../"):
        return "__OUTSIDE_ROOT__"
    return combined


def exists_target(rel_path: str) -> bool:
    if not rel_path:
        return True
    file_path = os.path.join(ROOT, rel_path)
    if os.path.isfile(file_path):
        return True
    if os.path.isdir(file_path) and os.path.isfile(os.path.join(file_path, "index.html")):
        return True
    if os.path.isfile(os.path.join(ROOT, rel_path, "index.html")):
        return True
    return False


def iter_site_files():
    for dirpath, _, filenames in os.walk(ROOT):
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT)
            yield rel, full


def check_forbidden_outputs(all_files):
    errors = 0
    for rel in sorted(all_files):
        if rel in FORBIDDEN_FILES:
            print(f"ERROR: unexpected published file: {rel}")
            errors += 1
        if rel.startswith(FORBIDDEN_PREFIXES):
            print(f"ERROR: unexpected published path: {rel}")
            errors += 1
    return errors


def check_text_references(rel, full, patterns):
    errors = 0
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as handle:
            data = handle.read()
    except Exception as exc:
        print(f"ERROR: cannot read {rel}: {exc}")
        return 1

    for pattern in patterns:
        for match in pattern.finditer(data):
            raw = match.group(1).strip()
            if pattern is SRCSET_RE:
                for candidate in raw.split(","):
                    parts = candidate.strip().split()
                    if not parts:
                        continue
                    errors += check_target(rel, parts[0])
            else:
                errors += check_target(rel, raw)
    return errors


def check_target(referrer, raw):
    target = resolve_internal_target(referrer, raw)
    if target is None:
        return 0
    if target == "__OUTSIDE_ROOT__":
        print(f"ERROR: path escapes site root from {referrer}: {raw}")
        return 1
    if not exists_target(target):
        print(f"ERROR: missing target referenced from {referrer}: {raw}")
        return 1
    return 0


def check_redirects():
    path = os.path.join(ROOT, "redirects.json")
    if not os.path.isfile(path):
        return 0

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:
        print(f"ERROR: cannot parse redirects.json: {exc}")
        return 1

    errors = 0
    for source, dest in sorted(data.items()):
        target = resolve_internal_target("redirects.json", dest)
        if target == "__OUTSIDE_ROOT__":
            print(f"ERROR: redirect target escapes site root: {source} -> {dest}")
            errors += 1
        elif target and not exists_target(target):
            print(f"ERROR: redirect target missing: {source} -> {dest}")
            errors += 1
    return errors


def main():
    if not os.path.isdir(ROOT):
        print(f"ERROR: {ROOT} not found. Run jekyll build first.", file=sys.stderr)
        return 2

    all_files = {rel for rel, _ in iter_site_files()}
    errors = check_forbidden_outputs(all_files)

    for rel, full in iter_site_files():
        if rel.endswith((".html", ".xml")):
            errors += check_text_references(rel, full, [ATTR_RE, SRCSET_RE, XML_LINK_RE])
        elif rel.endswith(".css"):
            errors += check_text_references(rel, full, [CSS_URL_RE])

    errors += check_redirects()

    if errors:
        print(f"FAIL: {errors} site validation errors")
        return 1

    print("OK: internal targets/assets exist and output surface is clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
