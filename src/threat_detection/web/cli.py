"""Console entry for `threat-serve`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from threat_detection.logging_config import setup_logging
from threat_detection.web.app import serve


def _parse_source(raw: str) -> str | int:
    text = raw.strip()
    return int(text) if text.isdigit() else text


def main() -> None:
    p = argparse.ArgumentParser(description="Host live threat-detection website")
    p.add_argument("--weights", type=Path, required=True, help="Trained YOLO .pt")
    p.add_argument("--source", default="0", help="Webcam index / file / RTSP")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=7860)
    p.add_argument("--conf", type=float, default=0.5)
    p.add_argument("--device", default="cpu")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--log-dir", type=Path, default=Path("logs"))
    p.add_argument("--quiet", action="store_true", help="Less verbose (INFO only)")
    args = p.parse_args()
    setup_logging(log_dir=args.log_dir, verbose=not args.quiet)
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
        log_dir=args.log_dir,
    )


if __name__ == "__main__":
    main()
