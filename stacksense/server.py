"""Local web UI + JSON API using only the standard library (works offline)."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .cli import dumps, load_and_recommend

STATIC = Path(__file__).resolve().parent / "static"


class Handler(BaseHTTPRequestHandler):
    server_version = "StackSense/1.0"

    def _send(self, code, body, ctype):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/index.html"):
            self._send(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path.split("?")[0] != "/api/recommend":
            self._send(404, "not found", "text/plain")
            return
        length = int(self.headers.get("Content-Length") or 0)
        text = self.rfile.read(length).decode("utf-8", "replace")
        try:
            out = load_and_recommend(text)
        except Exception as ex:  # keep the server alive on engine bugs
            self._send(500, json.dumps({"error": str(ex)}), "application/json")
            return
        self._send(200, dumps(out), "application/json; charset=utf-8")

    def log_message(self, fmt, *args):
        pass


def serve(host="127.0.0.1", port=8000):
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"StackSense UI on http://{host}:{port}  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
