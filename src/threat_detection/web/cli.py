"""Console entry for `threat-serve`."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from threat_detection.web.app import serve


def _parse_source(raw: str) -> str | int:
    text = raw.strip()
    return int(text) if text.isdigit() else text


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(description="Host live threat-detection website")
    p.add_argument("--weights", type=Path, required=True, help="Trained YOLO .pt")
    p.add_argument("--source", default="0", help="Webcam index / file / RTSP")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=7860)
    p.add_argument("--conf", type=float, default=0.5)
    p.add_argument("--device", default="cpu")
    p.add_argument("--imgsz", type=int, default=640)
    args = p.parse_args()
    if not args.weights.exists():
        print(f"Weights not found: {args.weights}", file=sys.stderr)
        sys.exit(1)
    serve(
        weights=args.weights,
        host=args.host,
        port=args.port,
        source=_parse_source(args.source),
        conf=args.conf,
        device=args.device,
        imgsz=args.imgsz,
    )


if __name__ == "__main__":
    main()
