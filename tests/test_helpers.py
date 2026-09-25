"""Unit tests for pure helpers (no GPU / no dataset required)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from threat_detection.data.explore import parse_yolo_boxes, yolo_to_xyxy
from threat_detection.pipeline.decision_gate import DecisionGate
from threat_detection.pipeline.detector import Detection, DetectionResult
from threat_detection.pipeline.temporal_buffer import TemporalBuffer
from threat_detection.pipeline.threat_interpreter import ThreatInterpreter, ThreatLevel
from threat_detection.training.evaluate import PAPER_TABLE_II, compare_to_paper, format_comparison_table


def test_parse_yolo_boxes(tmp_path: Path) -> None:
    label = tmp_path / "a.txt"
    label.write_text("1 0.5 0.5 0.2 0.4\n0 0.1 0.2 0.05 0.1\n", encoding="utf-8")
    boxes = parse_yolo_boxes(label)
    assert len(boxes) == 2
    assert boxes[0][0] == 1
    assert boxes[1][0] == 0


def test_yolo_to_xyxy() -> None:
    x1, y1, x2, y2 = yolo_to_xyxy(0.5, 0.5, 0.2, 0.4, 100, 200)
    assert (x1, y1, x2, y2) == (40, 60, 60, 140)


def test_temporal_buffer_capacity_and_sampling() -> None:
    buf = TemporalBuffer(capacity_s=5.0, sample_fps=3.0)
    assert buf.capacity == 15
    frame = np.zeros((8, 8, 3), dtype=np.uint8)
    assert buf.maybe_add(frame, 0.0, 0) is True
    assert buf.maybe_add(frame, 0.1, 1) is False  # too soon for 3 FPS
    assert buf.maybe_add(frame, 0.34, 2) is True
    assert len(buf) == 2


def test_decision_gate_cooldown() -> None:
    gate = DecisionGate(conf_threshold=0.5, cooldown_s=5.0)
    det = Detection(1, "gun", 0.9, (0, 0, 10, 10))
    result = DetectionResult(detections=[det])
    d1 = gate.evaluate(result, now=0.0)
    d2 = gate.evaluate(result, now=1.0)
    d3 = gate.evaluate(result, now=6.0)
    assert d1.triggered is True
    assert d2.triggered is False
    assert d2.reason == "cooldown_active"
    assert d3.triggered is True


def test_threat_interpreter_levels() -> None:
    interp = ThreatInterpreter()
    gun = [Detection(1, "gun", 0.9, (0, 0, 1, 1))]
    knife = [Detection(2, "knife", 0.8, (0, 0, 1, 1))]
    blunt = [Detection(0, "blunt_object", 0.7, (0, 0, 1, 1))]
    assert interp.interpret(gun).level == ThreatLevel.CRITICAL
    assert interp.interpret(knife).level == ThreatLevel.HIGH
    assert interp.interpret(blunt).level == ThreatLevel.MEDIUM


def test_paper_table_comparison_format() -> None:
    measured = {
        "precision": 0.85,
        "recall": 0.75,
        "map50": 0.81,
        "map50_95": 0.56,
        "gun_map50": 0.90,
        "knife_map50": 0.78,
        "blunt_object_map50": 0.74,
    }
    rows = compare_to_paper(measured, "100")
    assert len(rows) == len(PAPER_TABLE_II["100"])
    table = format_comparison_table(rows)
    assert "map50" in table
    assert "0.819" in table
