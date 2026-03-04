#!/usr/bin/env python3
import subprocess
import sys


def main():
    command = "python3 tools/list_urls.py | python3 tools/snapshot_html.py"
    result = subprocess.run(["bash", "-lc", command], capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return result.returncode

    changed = subprocess.run(
        ["git", "status", "--porcelain=v1", "tests/snapshots"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if changed:
        print(
            "Snapshot changes detected. Run: python3 tools/list_urls.py | python3 tools/snapshot_html.py and commit the updates.",
            file=sys.stderr,
        )
        print(changed, file=sys.stderr)
        return 1

    print("OK: snapshots unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
