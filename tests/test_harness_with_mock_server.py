import os
import sys

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from mock_server import start_mock_server
from platform_client import PlatformClient, estimate_tokens, get_path

DATA = "CVE-2024-0001 low\nCVE-2024-0003 critical\n"


@pytest.fixture()
def client(tmp_path):
    server, base_url = start_mock_server()
    path = tmp_path / "cves.txt"
    path.write_text(DATA)
    yield PlatformClient(base_url=base_url, api_key="test-key"), str(path)
    server.shutdown()


def test_upload_then_ask_returns_answer_tokens_and_latency(client):
    c, path = client
    file_id = c.upload(path)
    result = c.ask("Which is highest?", file_id)
    assert "CVE-2024-0003" in result["answer"]
    assert result["tokens_reported"] > 0
    assert result["latency_seconds"] >= 0


def test_bad_api_key_is_rejected(client):
    c, path = client
    bad = PlatformClient(base_url=c.base_url, api_key="wrong")
    with pytest.raises(requests.HTTPError):
        bad.upload(path)


def test_unknown_file_id_returns_error(client):
    c, _ = client
    with pytest.raises(requests.HTTPError):
        c.ask("anything", "does-not-exist")


def test_get_path_reads_nested_values():
    assert get_path({"usage": {"total_tokens": 42}}, "usage.total_tokens") == 42
    assert get_path({"usage": {}}, "usage.total_tokens") is None


def test_token_estimate_is_positive_and_scales():
    assert estimate_tokens("a" * 400) == 100
    assert estimate_tokens("") == 1
