#!/usr/bin/env python3
"""Render fixed fixtures with the real layouts, without reading published posts."""
import argparse
import difflib
import subprocess
import sys
import tempfile
from pathlib import Path

from snapshot_html import normalize_html_like

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "tests/snapshots"
CASES = {
    "plain-page.html": "plain-page/index.html",
    "plain-post.html": "2020-01-01-background/index.html",
    "reading-links.html": "2020-01-02-reading-links/index.html",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true", help="refresh layout fixture baselines")
    args = parser.parse_args()
    failed = False
    with tempfile.TemporaryDirectory(prefix="dt-layout-output-") as output:
        result = subprocess.run(
            ["ruby", str(ROOT / "tools/build_snapshot_fixtures.rb"), output], cwd=ROOT
        )
        if result.returncode:
            return result.returncode
        for name, built_path in CASES.items():
            actual = normalize_html_like((Path(output) / built_path).read_text(encoding="utf-8"))
            baseline = SNAPSHOTS / name
            if args.update:
                baseline.parent.mkdir(parents=True, exist_ok=True)
                baseline.write_text(actual, encoding="utf-8")
                continue
            expected = baseline.read_text(encoding="utf-8") if baseline.exists() else ""
            if actual != expected:
                failed = True
                sys.stderr.writelines(difflib.unified_diff(
                    expected.splitlines(keepends=True), actual.splitlines(keepends=True),
                    fromfile=str(baseline.relative_to(ROOT)), tofile="rendered/" + name,
                ))
    if failed:
        print("Layout changed. Review the diff, then run: python3 tools/check_snapshots.py --update", file=sys.stderr)
        return 1
    print("Updated 3 layout snapshots" if args.update else "OK: 3 layout snapshots unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
