#!/usr/bin/env python
"""Search the persistent threat-detection log file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from threat_detection.logging_config import log_path, search_logs


def main() -> None:
    p = argparse.ArgumentParser(description="Search logs/threat-detection.log")
    p.add_argument("query", help="Substring to find (e.g. knife, CRITICAL, gun:)")
    p.add_argument("--log-dir", type=Path, default=Path("logs"))
    p.add_argument("-n", "--limit", type=int, default=200)
    args = p.parse_args()
    path = log_path(args.log_dir)
    if not path.exists():
        print(f"No log file at {path}", file=sys.stderr)
        sys.exit(1)
    hits = search_logs(args.query, log_dir=args.log_dir, limit=args.limit)
    print(f"# {len(hits)} matches in {path}")
    for line in hits:
        print(line)


if __name__ == "__main__":
    main()
