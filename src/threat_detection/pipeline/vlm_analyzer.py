"""Vision-language behavior analysis (Gemini 2.5 Flash Lite stub).

Paper: two-stage inference — rapid keyframe screen, then detailed report.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from threat_detection.pipeline.temporal_buffer import BufferedFrame

logger = logging.getLogger(__name__)


@dataclass
class VLMScreenResult:
    suspicious: bool
    rationale: str


@dataclass
class VLMReport:
    summary: str
    actions: list[str]
    raw_response: str | None = None


class VLMAnalyzer:
    """Two-stage Gemini-backed analyzer — not wired in this scaffold."""

    def __init__(self, model_name: str = "gemini-2.5-flash-lite", api_key: str | None = None) -> None:
        self.model_name = model_name
        self.api_key = api_key

    def stage1_screen(self, frames: list[BufferedFrame]) -> VLMScreenResult:
        logger.warning("VLMAnalyzer.stage1_screen is stubbed (%d frames)", len(frames))
        raise NotImplementedError(
            "Gemini stage-1 screening not implemented. Set GEMINI_API_KEY and implement later."
        )

    def stage2_report(self, frames: list[BufferedFrame]) -> VLMReport:
        logger.warning("VLMAnalyzer.stage2_report is stubbed (%d frames)", len(frames))
        raise NotImplementedError(
            "Gemini stage-2 reporting not implemented. Set GEMINI_API_KEY and implement later."
        )

    def analyze(self, frames: list[BufferedFrame]) -> VLMReport | None:
        """Run two-stage pipeline; return None if stage-1 filters as non-suspicious."""
        screen = self.stage1_screen(frames)
        if not screen.suspicious:
            return None
        return self.stage2_report(frames)
