"""End-to-end pipeline orchestrator (stubs for live loop).

Flow (paper Fig. 1):
  VideoSource → preprocess → YOLOv8Detector → DecisionGate
  → TemporalBuffer → VLMAnalyzer → ThreatInterpreter → AlertService
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from threat_detection.pipeline.alerts import AlertService
from threat_detection.pipeline.decision_gate import DecisionGate
from threat_detection.pipeline.detector import YOLOv8Detector
from threat_detection.pipeline.temporal_buffer import TemporalBuffer
from threat_detection.pipeline.threat_interpreter import ThreatInterpreter
from threat_detection.pipeline.video_source import VideoSource
from threat_detection.pipeline.vlm_analyzer import VLMAnalyzer

logger = logging.getLogger(__name__)

PIPELINE_STAGES = [
    "VideoSource (webcam/file @ ~30 FPS)",
    "Frame preprocess (resize / normalize)",
    "YOLOv8Detector (gun / knife / blunt_object)",
    "DecisionGate (confidence + cooldown)",
    "TemporalBuffer (~5s @ 3 FPS)",
    "VLMAnalyzer stage-1 screen (Gemini 2.5 Flash Lite) [STUB]",
    "VLMAnalyzer stage-2 report [STUB]",
    "ThreatInterpreter (CRITICAL/HIGH/MEDIUM/LOW)",
    "AlertService (log / email / desktop) [email+desktop STUB]",
]


@dataclass
class PipelineConfig:
    weights: Path | None = None
    source: str | int = 0
    conf_threshold: float = 0.5
    cooldown_s: float = 5.0
    buffer_s: float = 5.0
    sample_fps: float = 3.0


class SurveillanceOrchestrator:
    """Wires pipeline stages. Live loop is not fully implemented yet."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self.video = VideoSource(self.config.source)
        self.detector = (
            YOLOv8Detector(
                weights=self.config.weights,
                conf_threshold=self.config.conf_threshold,
            )
            if self.config.weights
            else None
        )
        self.gate = DecisionGate(
            conf_threshold=self.config.conf_threshold,
            cooldown_s=self.config.cooldown_s,
        )
        self.buffer = TemporalBuffer(
            capacity_s=self.config.buffer_s,
            sample_fps=self.config.sample_fps,
        )
        self.vlm = VLMAnalyzer()
        self.interpreter = ThreatInterpreter()
        self.alerts = AlertService()

    def describe(self) -> str:
        lines = ["Planned surveillance pipeline stages:"]
        for i, stage in enumerate(PIPELINE_STAGES, 1):
            lines.append(f"  {i}. {stage}")
        return "\n".join(lines)

    def run(self) -> None:
        """Attempt a live run — raises until video/VLM stages are implemented."""
        logger.info("\n%s", self.describe())
        print(self.describe())
        print(
            "\nLive orchestrator is scaffolded only. "
            "Train a model, then implement VideoSource + VLM before run()."
        )
        raise NotImplementedError(
            "SurveillanceOrchestrator.run is stubbed. "
            "Detection training/eval works via scripts/train.py and scripts/evaluate.py."
        )
