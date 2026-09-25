"""Unit checks for log search / detection line formatting."""

from __future__ import annotations

from pathlib import Path

from threat_detection.logging_config import format_detection_line, search_logs
from threat_detection.pipeline.detector import Detection


def test_format_detection_line() -> None:
    dets = [Detection(2, "knife", 0.81, (10.0, 20.0, 30.0, 40.0))]
    line = format_detection_line(
        frame_index=3, infer_ms=50.0, fps=8.0, detections=dets, threat_level="HIGH"
    )
    assert "knife:0.810@[10,20,30,40]" in line
    assert "threat=HIGH" in line


def test_search_logs(tmp_path: Path, monkeypatch) -> None:
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "threat-detection.log").write_text(
        "alpha knife here\nbeta gun there\nalpha again knife\n",
        encoding="utf-8",
    )
    hits = search_logs("knife", log_dir=log_dir, limit=10)
    assert len(hits) == 2
    assert all("knife" in h for h in hits)
