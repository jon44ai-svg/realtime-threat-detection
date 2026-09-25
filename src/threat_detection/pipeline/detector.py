"""YOLOv8 detection stage for live frames."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    xyxy: tuple[float, float, float, float]


@dataclass
class DetectionResult:
    detections: list[Detection] = field(default_factory=list)
    annotated_frame: np.ndarray | None = None
    inference_ms: float = 0.0


class YOLOv8Detector:
    """Thin wrapper around Ultralytics YOLO for stream inference."""

    def __init__(
        self,
        weights: str | Path,
        conf_threshold: float = 0.5,
        imgsz: int = 640,
        device: str | None = None,
    ) -> None:
        self.weights = Path(weights)
        self.conf_threshold = conf_threshold
        self.imgsz = imgsz
        self.device = device
        self._model: Any = None

    def load(self) -> None:
        from ultralytics import YOLO

        if not self.weights.exists():
            raise FileNotFoundError(f"Weights not found: {self.weights}")
        self._model = YOLO(str(self.weights))
        logger.info("Loaded detector weights from %s", self.weights)

    def predict(self, frame: np.ndarray) -> DetectionResult:
        if self._model is None:
            raise RuntimeError("Call load() before predict()")

        kwargs: dict[str, Any] = {
            "source": frame,
            "conf": self.conf_threshold,
            "imgsz": self.imgsz,
            "verbose": False,
        }
        if self.device is not None:
            kwargs["device"] = self.device

        results = self._model.predict(**kwargs)
        if not results:
            return DetectionResult()

        r0 = results[0]
        names = r0.names if hasattr(r0, "names") else {}
        detections: list[Detection] = []
        if r0.boxes is not None:
            for box in r0.boxes:
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())
                xyxy_t = (
                    float(box.xyxy[0][0]),
                    float(box.xyxy[0][1]),
                    float(box.xyxy[0][2]),
                    float(box.xyxy[0][3]),
                )
                detections.append(
                    Detection(
                        class_id=cls_id,
                        class_name=str(names.get(cls_id, cls_id)),
                        confidence=conf,
                        xyxy=xyxy_t,
                    )
                )

        annotated = r0.plot() if hasattr(r0, "plot") else None
        return DetectionResult(detections=detections, annotated_frame=annotated)
