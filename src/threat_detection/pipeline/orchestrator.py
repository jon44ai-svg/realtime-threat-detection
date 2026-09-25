"""End-to-end pipeline orchestrator for live webcam detection.

Flow (paper Fig. 1):
  VideoSource → YOLOv8Detector → DecisionGate
  → TemporalBuffer → VLMAnalyzer [optional stub] → ThreatInterpreter → AlertService
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from threat_detection.pipeline.alerts import AlertService
from threat_detection.pipeline.decision_gate import DecisionGate
from threat_detection.pipeline.detector import DetectionResult, YOLOv8Detector
from threat_detection.pipeline.temporal_buffer import TemporalBuffer
from threat_detection.pipeline.threat_interpreter import ThreatAssessment, ThreatInterpreter
from threat_detection.pipeline.video_source import VideoSource
from threat_detection.pipeline.vlm_analyzer import VLMAnalyzer, VLMReport

logger = logging.getLogger(__name__)

PIPELINE_STAGES = [
    "VideoSource (webcam/file @ ~30 FPS)",
    "Frame preprocess (Ultralytics imgsz resize)",
    "YOLOv8Detector (gun / knife / blunt_object)",
    "DecisionGate (confidence + cooldown)",
    "TemporalBuffer (~5s @ 3 FPS)",
    "VLMAnalyzer stage-1 screen (Gemini 2.5 Flash Lite) [STUB — skipped by default]",
    "VLMAnalyzer stage-2 report [STUB — skipped by default]",
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
    device: str = "cpu"
    imgsz: int = 640
    show: bool = True
    skip_vlm: bool = True
    window_name: str = "Threat Detection"


class SurveillanceOrchestrator:
    """Live webcam loop: detect → gate → (skip VLM) → interpret → alert → display."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self.video = VideoSource(self.config.source)
        self.detector: YOLOv8Detector | None = None
        if self.config.weights is not None:
            self.detector = YOLOv8Detector(
                weights=self.config.weights,
                conf_threshold=self.config.conf_threshold,
                imgsz=self.config.imgsz,
                device=self.config.device,
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
        self._last_assessment: ThreatAssessment | None = None

    def describe(self) -> str:
        lines = ["Planned surveillance pipeline stages:"]
        for i, stage in enumerate(PIPELINE_STAGES, 1):
            lines.append(f"  {i}. {stage}")
        return "\n".join(lines)

    def run(self) -> None:
        """Open the camera, run YOLO on each frame, show annotated video until 'q'."""
        if self.config.weights is None:
            raise FileNotFoundError(
                "Provide --weights pointing to a trained .pt checkpoint "
                "(e.g. best.pt from Colab)."
            )
        if self.detector is None:
            self.detector = YOLOv8Detector(
                weights=self.config.weights,
                conf_threshold=self.config.conf_threshold,
                imgsz=self.config.imgsz,
                device=self.config.device,
            )

        logger.info("\n%s", self.describe())
        print(self.describe())
        print(
            f"\nLive detection on source={self.config.source!r} "
            f"device={self.config.device} weights={self.config.weights}"
        )
        print("Press q in the preview window to quit.\n")

        self.detector.load()
        fps_ema = 0.0

        try:
            with self.video:
                for packet in self.video.iter_frames():
                    t0 = time.perf_counter()
                    result = self.detector.predict(packet.frame)
                    infer_ms = (time.perf_counter() - t0) * 1000.0
                    result.inference_ms = infer_ms

                    self.buffer.maybe_add(
                        packet.frame, packet.timestamp_s, packet.frame_index
                    )
                    decision = self.gate.evaluate(result)

                    if decision.triggered:
                        vlm_report = self._maybe_vlm()
                        assessment = self.interpreter.interpret(
                            decision.selected, vlm_report
                        )
                        self.alerts.notify(assessment)
                        self._last_assessment = assessment

                    dt = time.perf_counter() - t0
                    inst_fps = 1.0 / dt if dt > 0 else 0.0
                    fps_ema = inst_fps if fps_ema == 0.0 else (0.9 * fps_ema + 0.1 * inst_fps)

                    if self.config.show:
                        display = self._compose_display(result, fps_ema, infer_ms)
                        cv2.imshow(self.config.window_name, display)
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord("q"):
                            logger.info("Quit requested")
                            break
        finally:
            if self.config.show:
                cv2.destroyAllWindows()

    def _maybe_vlm(self) -> VLMReport | None:
        if self.config.skip_vlm:
            return None
        try:
            return self.vlm.analyze(self.buffer.snapshot())
        except NotImplementedError:
            logger.debug("VLM still stubbed; continuing with detection-only assessment")
            return None

    def _compose_display(
        self,
        result: DetectionResult,
        fps: float,
        infer_ms: float,
    ) -> np.ndarray:
        frame = (
            result.annotated_frame
            if result.annotated_frame is not None
            else np.zeros((480, 640, 3), dtype=np.uint8)
        )
        overlay = frame.copy()
        label = f"FPS {fps:.1f}  infer {infer_ms:.0f}ms  dets {len(result.detections)}"
        cv2.putText(
            overlay,
            label,
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        if self._last_assessment is not None:
            threat = self._last_assessment
            color = {
                "CRITICAL": (0, 0, 255),
                "HIGH": (0, 80, 255),
                "MEDIUM": (0, 200, 255),
                "LOW": (200, 200, 0),
            }.get(threat.level.value, (255, 255, 255))
            cv2.putText(
                overlay,
                threat.title,
                (10, 58),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
                cv2.LINE_AA,
            )
        return overlay
