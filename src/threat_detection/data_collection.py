"""Local-first camera data collection site.

The browser owns camera permission; this server only receives JPEG snapshots.
Default binding is localhost. LAN mode is opt-in and token-protected.
"""

from __future__ import annotations

import html
import json
import logging
import secrets
import socket
import ssl
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger("threat.collect")
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_LABELS = {"empty", "gun", "knife", "blunt_object", "other"}

_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Threat dataset collection</title>
<style>
:root{color-scheme:dark}body{font:16px system-ui;max-width:760px;margin:auto;padding:1rem;background:#111;color:#eee}
video{width:100%;max-height:60vh;background:#000}button,select,input{font:1rem;padding:.55rem;margin:.25rem 0}
button{cursor:pointer}.row{display:flex;gap:.5rem;flex-wrap:wrap;align-items:center}.ok{color:#7fda89}.warn{color:#ffb86b}
</style></head><body>
<h1>Threat dataset collection</h1>
<p class="warn">Local collection only. Do not expose this server to the internet.</p>
<video id="video" autoplay muted playsinline></video>
<div class="row">
<label>Camera <select id="facing"><option value="user">Front</option><option value="environment">Back</option></select></label>
<label>Label <select id="label">
<option>empty</option><option>gun</option><option>knife</option>
<option>blunt_object</option><option>other</option></select></label>
</div>
<input id="note" placeholder="optional note" maxlength="200">
<div class="row"><button id="start">Start camera</button><button id="capture">Capture frame</button></div>
<p id="status">Camera is off.</p><p id="count">Captured: 0</p>
<canvas id="canvas" hidden></canvas>
<script>
const token = new URLSearchParams(location.search).get("token") || "";
const video = document.querySelector("#video"), canvas = document.querySelector("#canvas");
const status = document.querySelector("#status"), count = document.querySelector("#count");
let stream, captured = 0;
async function start() {
  if (stream) stream.getTracks().forEach(t => t.stop());
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video:{facingMode:document.querySelector("#facing").value}, audio:false});
    video.srcObject = stream; status.textContent = "Camera ready.";
  } catch (e) { status.textContent = "Camera error: " + e.message; }
}
document.querySelector("#start").onclick = start;
document.querySelector("#facing").onchange = start;
document.querySelector("#capture").onclick = async () => {
  if (!stream) return status.textContent = "Start the camera first.";
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const blob = await new Promise(r => canvas.toBlob(r, "image/jpeg", .92));
  const response = await fetch("/api/capture", {method:"POST", headers:{
    "Content-Type":"image/jpeg", "X-Collection-Token":token,
    "X-Label":document.querySelector("#label").value,
    "X-Note":document.querySelector("#note").value}, body:blob});
  const text = await response.text();
  if (!response.ok) return status.textContent = text;
  captured++; count.textContent = "Captured: " + captured; status.textContent = text;
};
</script></body></html>"""


def _safe_header(value: str, limit: int) -> str:
    return value.replace("\r", " ").replace("\n", " ")[:limit]


def serve_collection(
    output_dir: Path = Path("data/collected"),
    host: str = "127.0.0.1",
    port: int = 8765,
    token: str | None = None,
    certfile: Path | None = None,
    keyfile: Path | None = None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_dir = output_dir / session
    image_dir = session_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    token = token or secrets.token_urlsafe(24)
    lock = Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            logger.info("%s - %s", self.address_string(), fmt % args)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path)
            if path.path not in {"/", "/index.html"}:
                self.send_error(404)
                return
            query_token = (parse_qs(path.query).get("token") or [""])[0]
            if not secrets.compare_digest(query_token, token):
                self.send_error(403, "Open the printed URL containing the collection token")
                return
            body = _PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/api/capture":
                self.send_error(404)
                return
            supplied = self.headers.get("X-Collection-Token", "")
            if not secrets.compare_digest(supplied, token):
                self.send_error(403, "Invalid collection token")
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                size = 0
            if size <= 0 or size > MAX_UPLOAD_BYTES:
                self.send_error(413, "JPEG must be between 1 byte and 5 MB")
                return
            label = self.headers.get("X-Label", "other")
            if label not in ALLOWED_LABELS:
                self.send_error(400, "Invalid label")
                return
            payload = self.rfile.read(size)
            if len(payload) != size or not payload.startswith(b"\xff\xd8"):
                self.send_error(400, "Expected a JPEG image")
                return
            stamp = f"{time.time_ns()}_{secrets.token_hex(4)}"
            image_name = f"{stamp}.jpg"
            tmp = image_dir / f".{image_name}.tmp"
            target = image_dir / image_name
            with lock:
                tmp.write_bytes(payload)
                tmp.replace(target)
                with (session_dir / "metadata.jsonl").open("a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "image": str(target.relative_to(session_dir)),
                        "label": label,
                        "note": _safe_header(self.headers.get("X-Note", ""), 200),
                        "utc": datetime.now(timezone.utc).isoformat(),
                        "bytes": size,
                    }) + "\n")
            logger.info("captured image=%s label=%s bytes=%d", image_name, label, size)
            body = f"Saved {html.escape(image_name)} as {html.escape(label)}".encode()
            self.send_response(201)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    if (certfile is None) != (keyfile is None):
        raise ValueError("--certfile and --keyfile must be supplied together")
    server = HTTPServer((host, port), Handler)
    scheme = "http"
    if certfile is not None and keyfile is not None:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        scheme = "https"
    shown_host = "127.0.0.1" if host == "0.0.0.0" else host
    url = f"{scheme}://{shown_host}:{port}/?token={token}"
    print(f"Collection URL (this PC): {url}")
    if host == "0.0.0.0":
        try:
            lan_ip = socket.gethostbyname(socket.gethostname())
            print(f"Collection URL (trusted LAN phone): {scheme}://{lan_ip}:{port}/?token={token}")
        except OSError:
            pass
    print(f"Saving images and metadata under: {session_dir.resolve()}")
    if host == "0.0.0.0":
        print("WARNING: LAN mode is enabled; do not port-forward this server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping collection server.")
    finally:
        server.server_close()
