import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from hallucination_check import check_answer, extract_cve_ids

SOURCE = "CVE-2024-0001 low. CVE-2024-0002 medium. CVE-2024-0003 critical."


def test_extracts_ids_case_insensitive():
    assert extract_cve_ids("see cve-2024-0001 and CVE-2024-0002") == {"CVE-2024-0001", "CVE-2024-0002"}


def test_grounded_answer_passes():
    result = check_answer(SOURCE, "The worst is CVE-2024-0003.")
    assert result["unsupported"] == []
    assert result["grounding_rate"] == 1.0


def test_invented_id_is_flagged():
    result = check_answer(SOURCE, "CVE-2024-0003 and CVE-2099-9999 are serious.")
    assert result["unsupported"] == ["CVE-2099-9999"]
    assert result["grounding_rate"] == 0.5


def test_answer_with_no_ids_is_not_flagged():
    result = check_answer(SOURCE, "I could not find that.")
    assert result["unsupported"] == []
