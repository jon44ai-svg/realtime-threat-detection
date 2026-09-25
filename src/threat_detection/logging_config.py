"""Single persistent log stream for the project (stdlib only).

One file, many logger names (`threat.detect`, `threat.alert`, …).
Search with ``search_logs`` or GET /logs?q= on the web UI.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_LOG_DIR = Path("logs")
DEFAULT_LOG_NAME = "threat-detection.log"
_configured = False


def log_path(log_dir: Path | None = None) -> Path:
    return (log_dir or DEFAULT_LOG_DIR) / DEFAULT_LOG_NAME


def setup_logging(
    *,
    log_dir: Path | None = None,
    verbose: bool = True,
    also_console: bool = True,
) -> Path:
    """Idempotent: file + optional console. Returns the log file path."""
    global _configured
    path = log_path(log_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    level = logging.DEBUG if verbose else logging.INFO
    root.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not _configured:
        fh = RotatingFileHandler(
            path, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        )
        fh.setLevel(level)
        fh.setFormatter(fmt)
        root.addHandler(fh)

        if also_console:
            sh = logging.StreamHandler()
            sh.setLevel(level)
            sh.setFormatter(fmt)
            root.addHandler(sh)

        _configured = True
    else:
        root.setLevel(level)
        for h in root.handlers:
            h.setLevel(level)

    logging.getLogger("threat").info("logging to %s (verbose=%s)", path.resolve(), verbose)
    return path


def search_logs(
    query: str,
    *,
    log_dir: Path | None = None,
    limit: int = 200,
    case_sensitive: bool = False,
) -> list[str]:
    """Return matching lines from the persistent log (newest last, capped)."""
    path = log_path(log_dir)
    if not path.exists():
        return []
    needle = query if case_sensitive else query.lower()
    hits: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            hay = line if case_sensitive else line.lower()
            if needle in hay:
                hits.append(line.rstrip("\n"))
    return hits[-limit:]


def format_detection_line(
    *,
    frame_index: int,
    infer_ms: float,
    fps: float,
    detections: list,
    threat_level: str | None = None,
) -> str:
    """One verbose line for a frame with detections."""
    parts = [
        f"frame={frame_index}",
        f"fps={fps:.1f}",
        f"infer_ms={infer_ms:.0f}",
        f"n={len(detections)}",
    ]
    if threat_level:
        parts.append(f"threat={threat_level}")
    for d in detections:
        x1, y1, x2, y2 = d.xyxy
        parts.append(
            f"{d.class_name}:{d.confidence:.3f}"
            f"@[{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}]"
        )
    return " ".join(parts)
