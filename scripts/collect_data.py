#!/usr/bin/env python
"""Run the local-first browser camera collection website."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from threat_detection.data_collection import serve_collection


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect labeled camera frames locally")
    parser.add_argument("--output", type=Path, default=Path("data/collected"))
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Use 0.0.0.0 only for a trusted LAN phone; never expose publicly",
    )
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--token", default=None, help="Optional access token")
    parser.add_argument("--certfile", type=Path, help="TLS certificate for phone HTTPS")
    parser.add_argument("--keyfile", type=Path, help="TLS private key for phone HTTPS")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    serve_collection(
        output_dir=args.output,
        host=args.host,
        port=args.port,
        token=args.token,
        certfile=args.certfile,
        keyfile=args.keyfile,
    )


if __name__ == "__main__":
    main()
