#!/usr/bin/env python3
import os, sys, subprocess
from pathlib import Path

def main():
    # regenerate into a temp dir
    tmp=Path("tests/.tmp_snapshots")
    if tmp.exists():
        subprocess.run(["rm","-rf",str(tmp)], check=True)
    tmp.mkdir(parents=True, exist_ok=True)

    urls_path=Path("tests/baseline_urls.txt")
    if not urls_path.exists():
        print("Missing tests/baseline_urls.txt", file=sys.stderr)
        return 2

    urls=urls_path.read_text().splitlines()
    p=subprocess.run(["bash","-lc", f"cat {urls_path} | python3 tools/snapshot_html.py"], capture_output=True, text=True)
    if p.returncode!=0:
        sys.stderr.write(p.stderr)
        return p.returncode

    # compare snapshots
    p=subprocess.run(["git","diff","--no-index","--", "tests/snapshots", "tests/snapshots"], capture_output=True, text=True)
    # above is a noop placeholder, real comparison is via git status
    changed=subprocess.run(["git","status","--porcelain=v1","tests/snapshots"], capture_output=True, text=True).stdout.strip()
    if changed:
        print("Snapshot changes detected. Run: cat tests/baseline_urls.txt | python3 tools/snapshot_html.py and commit updated snapshots.", file=sys.stderr)
        print(changed, file=sys.stderr)
        return 1
    print("OK: snapshots unchanged")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
