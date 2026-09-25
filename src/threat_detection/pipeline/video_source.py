"""Video acquisition module (stub).

Paper: surveillance camera / webcam at ~30 FPS.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterator

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FramePacket:
    """Single video frame with metadata."""

    frame: np.ndarray
    frame_index: int
    timestamp_s: float


class VideoSource:
    """Capture frames from webcam, file, or RTSP.

    Stub: does not open devices yet. Callers should use ``iter_frames`` once
    implemented with OpenCV ``VideoCapture``.
    """

    def __init__(self, source: str | int = 0, target_fps: float = 30.0) -> None:
        self.source = source
        self.target_fps = target_fps
        self._opened = False

    def open(self) -> None:
        logger.info("VideoSource.open stub (source=%s)", self.source)
        self._opened = True
        raise NotImplementedError(
            "VideoSource.open is stubbed. Wire cv2.VideoCapture in a later iteration."
        )

    def close(self) -> None:
        self._opened = False
        logger.info("VideoSource closed")

    def iter_frames(self) -> Iterator[FramePacket]:
        if not self._opened:
            raise RuntimeError("Call open() before iter_frames()")
        raise NotImplementedError("VideoSource.iter_frames is stubbed")

    def __enter__(self) -> VideoSource:
        self.open()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
