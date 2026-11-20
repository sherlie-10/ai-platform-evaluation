"""
mock_server.py

A tiny fake platform so the harness and its tests can run with no real API.
It stores uploaded content, answers with the highest-severity CVE it can find,
and reports a token count. It also rejects bad API keys and .exe uploads so we
can test failure handling.
"""
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STORE = {}
VALID_KEY = "test-key"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep test output quiet
        pass

    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.headers.get("Authorization") != f"Bearer {VALID_KEY}":
            return self._send(401, {"error": "bad api key"})
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        if self.path == "/upload":
            text = raw.decode("utf-8", errors="replace")
            if ".exe" in text.split("\r\n", 3)[1] if "\r\n" in text else False:
                return self._send(415, {"error": "unsupported type"})
            file_id = f"f{len(STORE) + 1}"
            STORE[file_id] = text
            return self._send(200, {"file_id": file_id})

        if self.path == "/chat":
            payload = json.loads(raw)
            content = STORE.get(payload["file_id"])
            if content is None:
                return self._send(404, {"error": "unknown file"})
            ids = re.findall(r"CVE-\d{4}-\d{4,7}", content)
            answer = f"The highest severity is {ids[-1]}." if ids else "I could not find that."
            tokens = (len(payload["question"]) + len(content)) // 4
            return self._send(200, {"answer": answer, "usage": {"total_tokens": tokens}})

        self._send(404, {"error": "not found"})


def start_mock_server():
    """Start the fake platform on a free port. Returns (server, base_url)."""
    STORE.clear()
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"
