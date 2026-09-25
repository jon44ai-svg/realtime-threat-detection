#!/usr/bin/env python
"""Run notebook-style EDA on the downloaded dataset."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from threat_detection.data.explore import main

if __name__ == "__main__":
    main()
