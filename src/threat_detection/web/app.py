"""Minimal hostable webcam detection site (stdlib HTTP + MJPEG)."""

from __future__ import annotations

import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import cv2

from threat_detection.logging_config import format_detection_line, search_logs
from threat_detection.pipeline.detector import YOLOv8Detector
from threat_detection.pipeline.threat_interpreter import ThreatInterpreter
from threat_detection.pipeline.video_source import VideoSource

logger = logging.getLogger("threat.detect")

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
    :root { color-scheme: dark; --bg:#0e1116; --fg:#e8eaed; --muted:#9aa0a6; --line:#22262e; }
    * { box-sizing: border-box; }
    body { margin:0; font:15px/1.4 ui-sans-serif,system-ui,sans-serif;
           background:var(--bg); color:var(--fg); min-height:100vh; }
    header { padding:1rem 1.25rem; display:flex; gap:1rem; align-items:baseline; flex-wrap:wrap;
             border-bottom:1px solid var(--line); }
    h1 { margin:0; font-size:1.15rem; letter-spacing:.02em; }
    #status { color:var(--muted); font-variant-numeric:tabular-nums; }
    main img { display:block; width:100%; max-height:55vh; object-fit:contain; background:#000; }
    #logs { border-top:1px solid var(--line); padding:1rem 1.25rem 1.5rem; }
    #logs form { display:flex; gap:.5rem; flex-wrap:wrap; margin-bottom:.75rem; }
    #logs input[type=search] { flex:1; min-width:12rem; padding:.4rem .6rem;
      background:#151a22; color:var(--fg); border:1px solid var(--line); }
    #logs button { padding:.4rem .8rem; background:#1f6feb; color:#fff; border:0; cursor:pointer; }
    #logout { margin:0; max-height:28vh; overflow:auto; white-space:pre-wrap; word-break:break-word;
      font:12px/1.45 ui-monospace,Consolas,monospace; color:var(--muted);
      background:#0a0c10; border:1px solid var(--line); padding:.75rem; }
  </style>
</head>
<body>
  <header>
    <h1>Threat Detection</h1>
    <span id="status">connecting…</span>
  </header>
  <main><img src="/stream" alt="live detection"/></main>
  <section id="logs">
    <form id="logform">
      <input type="search" id="q" name="q" placeholder="Search logs (knife, CRITICAL, gun:0.9…)" />
      <button type="submit">Search</button>
    </form>
    <pre id="logout">Load recent lines via search (empty query = last 100).</pre>
  </section>
  <script>
    async function tick() {
      try {
        const r = await fetch("/status");
        document.getElementById("status").textContent = await r.text();
      } catch (_) {}
    }
    async function runSearch(q) {
      const r = await fetch("/logs?q=" + encodeURIComponent(q || "") + "&n=100");
      document.getElementById("logout").textContent = await r.text() || "(no matches)";
    }
    document.getElementById("logform").addEventListener("submit", (e) => {
      e.preventDefault();
      runSearch(document.getElementById("q").value);
    });
    tick(); setInterval(tick, 1000);
    runSearch("");
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
    logger.info(
        "capture started weights=%s source=%s conf=%.2f device=%s imgsz=%d",
        weights, source, conf, device, imgsz,
    )
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
                logger.info(
                    format_detection_line(
                        frame_index=packet.frame_index,
                        infer_ms=result.inference_ms,
                        fps=fps_ema or 0.0,
                        detections=result.detections,
                        threat_level=assessment.level.value,
                    )
                )
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
            elif packet.frame_index % 30 == 0:
                logger.debug(
                    "frame=%d fps=%.1f infer_ms=%.0f n=0",
                    packet.frame_index,
                    fps_ema,
                    result.inference_ms,
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
        logger.info("capture stopped")
        with _lock:
            _status = "camera stopped"


def _make_handler() -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            logging.getLogger("threat.http").debug("%s - %s", self.address_string(), fmt % args)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)
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
            if path == "/logs":
                q = (qs.get("q") or [""])[0]
                try:
                    n = int((qs.get("n") or ["100"])[0])
                except ValueError:
                    n = 100
                n = max(1, min(n, 2000))
                # empty q → last n lines via matching everything with a broad read
                if q.strip():
                    lines = search_logs(q, limit=n)
                else:
                    from threat_detection.logging_config import log_path

                    p = log_path()
                    if p.exists():
                        all_lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
                        lines = all_lines[-n:]
                    else:
                        lines = []
                body = ("\n".join(lines) + ("\n" if lines else "")).encode()
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
    print(f"Log search → http://{url_host}:{port}/logs?q=knife")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping…")
    finally:
        _stop.set()
        httpd.server_close()
