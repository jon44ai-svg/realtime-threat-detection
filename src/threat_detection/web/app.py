"""Minimal hostable webcam detection site (stdlib HTTP + MJPEG)."""

from __future__ import annotations

import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import cv2

from threat_detection.pipeline.detector import YOLOv8Detector
from threat_detection.pipeline.threat_interpreter import ThreatInterpreter
from threat_detection.pipeline.video_source import VideoSource

logger = logging.getLogger(__name__)

# ponytail: single shared JPEG buffer — fine for one camera / few viewers
_lock = threading.Lock()
_jpeg: bytes | None = None
_status = "starting"
_stop = threading.Event()

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Threat Detection</title>
  <style>
    :root { color-scheme: dark; --bg:#0e1116; --fg:#e8eaed; --muted:#9aa0a6; }
    * { box-sizing: border-box; }
    body { margin:0; font:15px/1.4 ui-sans-serif,system-ui,sans-serif;
           background:var(--bg); color:var(--fg); min-height:100vh; }
    header { padding:1rem 1.25rem; display:flex; gap:1rem; align-items:baseline;
             border-bottom:1px solid #22262e; }
    h1 { margin:0; font-size:1.15rem; letter-spacing:.02em; }
    #status { color:var(--muted); font-variant-numeric:tabular-nums; }
    main { padding:0; }
    img { display:block; width:100%; max-height:calc(100vh - 3.5rem);
          object-fit:contain; background:#000; }
  </style>
</head>
<body>
  <header>
    <h1>Threat Detection</h1>
    <span id="status">connecting…</span>
  </header>
  <main><img src="/stream" alt="live detection"/></main>
  <script>
    async function tick() {
      try {
        const r = await fetch("/status");
        document.getElementById("status").textContent = await r.text();
      } catch (_) {}
    }
    tick(); setInterval(tick, 1000);
  </script>
</body>
</html>
"""


def _capture_loop(
    weights: Path,
    source: str | int,
    conf: float,
    device: str,
    imgsz: int,
) -> None:
    global _jpeg, _status
    detector = YOLOv8Detector(weights, conf_threshold=conf, imgsz=imgsz, device=device)
    detector.load()
    interpreter = ThreatInterpreter()
    video = VideoSource(source)
    video.open()
    fps_ema = 0.0
    try:
        for packet in video.iter_frames():
            if _stop.is_set():
                break
            t0 = time.perf_counter()
            result = detector.predict(packet.frame)
            frame = result.annotated_frame if result.annotated_frame is not None else packet.frame
            title = ""
            if result.detections:
                assessment = interpreter.interpret(result.detections)
                title = assessment.title
                cv2.putText(
                    frame,
                    title,
                    (10, 58),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )
            dt = time.perf_counter() - t0
            inst = 1.0 / dt if dt > 0 else 0.0
            fps_ema = inst if fps_ema == 0 else (0.9 * fps_ema + 0.1 * inst)
            ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if not ok:
                continue
            with _lock:
                _jpeg = buf.tobytes()
                _status = (
                    f"FPS {fps_ema:.1f} · infer {result.inference_ms:.0f}ms · "
                    f"dets {len(result.detections)}"
                    + (f" · {title}" if title else "")
                )
    finally:
        video.close()
        with _lock:
            _status = "camera stopped"


def _make_handler() -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            logger.debug("%s - %s", self.address_string(), fmt % args)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path in ("/", "/index.html"):
                body = _PAGE.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if path == "/status":
                with _lock:
                    text = _status
                body = text.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if path == "/stream":
                self.send_response(200)
                self.send_header("Age", "0")
                self.send_header("Cache-Control", "no-cache, private")
                self.send_header(
                    "Content-Type", "multipart/x-mixed-replace; boundary=frame"
                )
                self.end_headers()
                try:
                    while not _stop.is_set():
                        with _lock:
                            chunk = _jpeg
                        if chunk is None:
                            time.sleep(0.05)
                            continue
                        self.wfile.write(
                            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + chunk + b"\r\n"
                        )
                        time.sleep(0.03)
                except (BrokenPipeError, ConnectionResetError):
                    return
                return
            self.send_error(404)

    return Handler


def serve(
    weights: Path,
    host: str = "0.0.0.0",
    port: int = 7860,
    source: str | int = 0,
    conf: float = 0.5,
    device: str = "cpu",
    imgsz: int = 640,
) -> None:
    _stop.clear()
    worker = threading.Thread(
        target=_capture_loop,
        kwargs={
            "weights": weights,
            "source": source,
            "conf": conf,
            "device": device,
            "imgsz": imgsz,
        },
        daemon=True,
    )
    worker.start()
    httpd = ThreadingHTTPServer((host, port), _make_handler())
    url_host = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    print(f"Threat Detection → http://{url_host}:{port}/  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping…")
    finally:
        _stop.set()
        httpd.server_close()
