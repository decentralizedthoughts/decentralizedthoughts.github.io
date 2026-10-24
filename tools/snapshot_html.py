"""Stable normalization shared by the isolated layout snapshot tests."""
import json
import re
from pathlib import Path


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


if __name__ == "__main__":
    raise SystemExit("Article snapshots are no longer used. For layout changes, run: python3 tools/check_snapshots.py --update")
