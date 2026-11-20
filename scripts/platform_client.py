"""
platform_client.py

A thin client for the platform's HTTP API: upload a file, ask a question about it,
and return the answer, the token count the platform REPORTS, and latency that
THIS script measures.

The real platform's endpoint names and JSON field names are NOT hard-coded here.
Set them with environment variables (or edit the defaults) to match the API docs:

    PLATFORM_BASE_URL   e.g. https://your-instance.example.com/api
    PLATFORM_API_KEY    your key (never commit it; keep it in .env or your shell)
    UPLOAD_PATH         default /upload
    CHAT_PATH           default /chat
    FILE_ID_FIELD       default file_id          (field in the upload response)
    ANSWER_FIELD        default answer           (field in the chat response)
    TOKENS_FIELD        default usage.total_tokens   (dotted path allowed)
"""
import os
import time

import requests


def get_path(data, dotted):
    """Read a value from nested JSON using a dotted path like 'usage.total_tokens'."""
    current = data
    for part in dotted.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def estimate_tokens(text):
    """Rough independent token estimate (about 4 characters per token for English).
    Use it as a sanity check against the platform's reported number, not as exact."""
    return max(1, len(text) // 4)


class PlatformClient:
    def __init__(self, base_url=None, api_key=None, timeout=60):
        self.base_url = (base_url or os.environ.get("PLATFORM_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.environ.get("PLATFORM_API_KEY", "")
        self.timeout = timeout
        self.upload_path = os.environ.get("UPLOAD_PATH", "/upload")
        self.chat_path = os.environ.get("CHAT_PATH", "/chat")
        self.file_id_field = os.environ.get("FILE_ID_FIELD", "file_id")
        self.answer_field = os.environ.get("ANSWER_FIELD", "answer")
        self.tokens_field = os.environ.get("TOKENS_FIELD", "usage.total_tokens")

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def upload(self, path):
        """Upload a file. Returns the file id. Raises if the upload fails."""
        with open(path, "rb") as f:
            response = requests.post(
                self.base_url + self.upload_path,
                headers=self._headers(),
                files={"file": (os.path.basename(path), f)},
                timeout=self.timeout,
            )
        response.raise_for_status()
        file_id = get_path(response.json(), self.file_id_field)
        if not file_id:
            raise ValueError(f"No '{self.file_id_field}' in upload response: {response.text[:200]}")
        return file_id

    def ask(self, question, file_id):
        """Ask a question about an uploaded file.
        Returns dict: answer, tokens_reported, latency_seconds (measured here)."""
        start = time.perf_counter()
        response = requests.post(
            self.base_url + self.chat_path,
            headers=self._headers(),
            json={"question": question, "file_id": file_id},
            timeout=self.timeout,
        )
        latency = round(time.perf_counter() - start, 4)
        response.raise_for_status()
        data = response.json()
        return {
            "answer": str(get_path(data, self.answer_field) or ""),
            "tokens_reported": get_path(data, self.tokens_field),
            "latency_seconds": latency,
        }
