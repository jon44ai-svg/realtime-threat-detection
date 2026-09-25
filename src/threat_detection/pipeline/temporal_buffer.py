"""Temporal frame buffer (~5s context at ~3 FPS per paper methodology)."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque

import numpy as np


@dataclass
class BufferedFrame:
    frame: np.ndarray
    timestamp_s: float
    frame_index: int


class TemporalBuffer:
    """Circular buffer storing recent frames for VLM behavior analysis."""

    def __init__(self, capacity_s: float = 5.0, sample_fps: float = 3.0) -> None:
        self.capacity_s = capacity_s
        self.sample_fps = sample_fps
        self.max_frames = max(1, int(capacity_s * sample_fps))
        self._frames: Deque[BufferedFrame] = deque(maxlen=self.max_frames)
        self._last_sample_t: float | None = None

    def __len__(self) -> int:
        return len(self._frames)

    @property
    def capacity(self) -> int:
        return self.max_frames

    def clear(self) -> None:
        self._frames.clear()
        self._last_sample_t = None

    def maybe_add(self, frame: np.ndarray, timestamp_s: float, frame_index: int) -> bool:
        """Add a frame if sampling interval since last sample has elapsed."""
        min_dt = 1.0 / self.sample_fps if self.sample_fps > 0 else 0.0
        if self._last_sample_t is not None and (timestamp_s - self._last_sample_t) < min_dt:
            return False
        self._frames.append(
            BufferedFrame(frame=frame.copy(), timestamp_s=timestamp_s, frame_index=frame_index)
        )
        self._last_sample_t = timestamp_s
        return True

    def snapshot(self) -> list[BufferedFrame]:
        return list(self._frames)
