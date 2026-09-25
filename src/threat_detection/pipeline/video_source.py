"""Video acquisition from webcam, file, or RTSP via OpenCV."""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass
from typing import Iterator

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FramePacket:
    """Single video frame with metadata."""

    frame: np.ndarray
    frame_index: int
    timestamp_s: float


def _resolve_source(source: str | int) -> str | int:
    if isinstance(source, int):
        return source
    text = source.strip()
    if text.isdigit():
        return int(text)
    return text


class VideoSource:
    """Capture frames from webcam index, video file, or RTSP URL."""

    def __init__(self, source: str | int = 0, target_fps: float = 30.0) -> None:
        self.source = _resolve_source(source)
        self.target_fps = target_fps
        self._cap: cv2.VideoCapture | None = None
        self._opened = False

    def open(self) -> None:
        if self._opened:
            return

        src = self.source
        if isinstance(src, int) and sys.platform == "win32":
            cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap.release()
                cap = cv2.VideoCapture(src)
        else:
            cap = cv2.VideoCapture(src)

        if not cap.isOpened():
            raise RuntimeError(
                f"Could not open video source {src!r}. "
                "Check the webcam is connected and not used by another app."
            )

        if isinstance(src, int) and self.target_fps > 0:
            cap.set(cv2.CAP_PROP_FPS, self.target_fps)

        self._cap = cap
        self._opened = True
        logger.info("VideoSource opened (source=%s)", src)

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self._opened = False
        logger.info("VideoSource closed")

    def iter_frames(self) -> Iterator[FramePacket]:
        if not self._opened or self._cap is None:
            raise RuntimeError("Call open() before iter_frames()")

        idx = 0
        t0 = time.perf_counter()
        while True:
            ok, frame = self._cap.read()
            if not ok or frame is None:
                logger.info("VideoSource ended after %d frames", idx)
                break
            yield FramePacket(
                frame=frame,
                frame_index=idx,
                timestamp_s=time.perf_counter() - t0,
            )
            idx += 1

    def __enter__(self) -> VideoSource:
        self.open()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
