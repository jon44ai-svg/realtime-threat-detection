"""Decision gate: confidence threshold + cooldown (paper Fig. 1)."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from threat_detection.pipeline.detector import Detection, DetectionResult

logger = logging.getLogger(__name__)


@dataclass
class GateDecision:
    triggered: bool
    reason: str
    selected: list[Detection]


class DecisionGate:
    """Pass detections above confidence; suppress repeats during cooldown."""

    def __init__(self, conf_threshold: float = 0.5, cooldown_s: float = 5.0) -> None:
        self.conf_threshold = conf_threshold
        self.cooldown_s = cooldown_s
        self._last_trigger_t: float | None = None

    def evaluate(self, result: DetectionResult, now: float | None = None) -> GateDecision:
        now = time.monotonic() if now is None else now
        selected = [d for d in result.detections if d.confidence >= self.conf_threshold]

        if not selected:
            return GateDecision(False, "no_detections_above_threshold", [])

        if self._last_trigger_t is not None and (now - self._last_trigger_t) < self.cooldown_s:
            return GateDecision(False, "cooldown_active", selected)

        self._last_trigger_t = now
        logger.info(
            "DecisionGate triggered (%d detections, cooldown=%.1fs)",
            len(selected),
            self.cooldown_s,
        )
        return GateDecision(True, "threat_candidate", selected)

    def reset(self) -> None:
        self._last_trigger_t = None
