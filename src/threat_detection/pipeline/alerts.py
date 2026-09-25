"""Alert generation: email / desktop / log (stubs except logging)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from threat_detection.pipeline.threat_interpreter import ThreatAssessment

logger = logging.getLogger(__name__)


@dataclass
class AlertResult:
    logged: bool
    email_sent: bool
    desktop_notified: bool


class AlertService:
    """Dispatch security alerts. Only logging is active in this scaffold."""

    def __init__(self, enable_email: bool = False, enable_desktop: bool = False) -> None:
        self.enable_email = enable_email
        self.enable_desktop = enable_desktop

    def notify(self, assessment: ThreatAssessment) -> AlertResult:
        logger.warning(
            "ALERT [%s] %s — %s",
            assessment.level.value,
            assessment.title,
            assessment.detail,
        )
        email_sent = False
        desktop = False
        if self.enable_email:
            email_sent = self._send_email(assessment)
        if self.enable_desktop:
            desktop = self._desktop_notify(assessment)
        return AlertResult(logged=True, email_sent=email_sent, desktop_notified=desktop)

    def _send_email(self, assessment: ThreatAssessment) -> bool:
        raise NotImplementedError("Email alerts are stubbed (configure SMTP later).")

    def _desktop_notify(self, assessment: ThreatAssessment) -> bool:
        raise NotImplementedError("Desktop notifications are stubbed.")
