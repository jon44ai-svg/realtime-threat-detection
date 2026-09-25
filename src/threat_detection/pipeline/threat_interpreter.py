"""Threat interpretation: map detections + VLM output to severity levels."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from threat_detection.pipeline.detector import Detection
from threat_detection.pipeline.vlm_analyzer import VLMReport

logger = logging.getLogger(__name__)


class ThreatLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ThreatAssessment:
    level: ThreatLevel
    title: str
    detail: str
    detections: list[Detection]


class ThreatInterpreter:
    """Heuristic stub — replace with paper threat classification logic later."""

    def interpret(
        self,
        detections: list[Detection],
        vlm_report: VLMReport | None = None,
    ) -> ThreatAssessment:
        class_names = {d.class_name.lower() for d in detections}
        if "gun" in class_names:
            level = ThreatLevel.CRITICAL
        elif "knife" in class_names:
            level = ThreatLevel.HIGH
        elif "blunt_object" in class_names:
            level = ThreatLevel.MEDIUM
        else:
            level = ThreatLevel.LOW

        detail = vlm_report.summary if vlm_report else "VLM report unavailable (stub)."
        title = f"{level.value}: {', '.join(sorted(class_names)) or 'unknown'}"
        logger.info("ThreatInterpreter -> %s", level.value)
        return ThreatAssessment(
            level=level,
            title=title,
            detail=detail,
            detections=list(detections),
        )
