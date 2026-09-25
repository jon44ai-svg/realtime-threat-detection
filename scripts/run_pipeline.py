#!/usr/bin/env python
"""Print pipeline stages and attempt stub orchestrator run."""

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


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Surveillance pipeline stub runner")
    parser.add_argument(
        "--weights",
        type=Path,
        default=None,
        help="Optional YOLO weights (unused until live loop is implemented)",
    )
    parser.add_argument(
        "--describe-only",
        action="store_true",
        help="Only print planned stages (do not call run())",
    )
    args = parser.parse_args()

    orch = SurveillanceOrchestrator(PipelineConfig(weights=args.weights))
    print(orch.describe())
    if args.describe_only:
        return

    try:
        orch.run()
    except NotImplementedError as exc:
        print(f"\n[stub] {exc}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
