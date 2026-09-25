#!/usr/bin/env python
"""Run live webcam threat detection with a trained YOLO checkpoint."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from threat_detection.pipeline.orchestrator import PipelineConfig, SurveillanceOrchestrator


def _parse_source(raw: str) -> str | int:
    text = raw.strip()
    if text.isdigit():
        return int(text)
    return text


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Live surveillance pipeline (webcam + YOLO)")
    parser.add_argument(
        "--weights",
        type=Path,
        default=None,
        help="Path to trained YOLO .pt checkpoint (required for live run)",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Webcam index (0), video file path, or RTSP URL",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.5,
        help="Detection confidence threshold",
    )
    parser.add_argument(
        "--cooldown",
        type=float,
        default=5.0,
        help="Seconds between threat alerts for the same stream",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Ultralytics device (cpu on this machine; 0 for CUDA)",
    )
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Disable OpenCV preview window (headless)",
    )
    parser.add_argument(
        "--with-vlm",
        action="store_true",
        help="Attempt Gemini VLM stages (still stubbed unless implemented)",
    )
    parser.add_argument(
        "--describe-only",
        action="store_true",
        help="Only print planned stages (do not open the camera)",
    )
    args = parser.parse_args()

    config = PipelineConfig(
        weights=args.weights,
        source=_parse_source(args.source),
        conf_threshold=args.conf,
        cooldown_s=args.cooldown,
        device=args.device,
        imgsz=args.imgsz,
        show=not args.no_show,
        skip_vlm=not args.with_vlm,
    )
    orch = SurveillanceOrchestrator(config)
    print(orch.describe())
    if args.describe_only:
        return

    if args.weights is None:
        print(
            "\nError: --weights is required for a live run.\n"
            "Example:\n"
            "  uv run python scripts/run_pipeline.py "
            "--weights path/to/best.pt --source 0 --device cpu",
            file=sys.stderr,
        )
        sys.exit(2)

    orch.run()


if __name__ == "__main__":
    main()
