"""
hallucination_check.py

Checks whether an AI answer contains facts that are NOT in the source file.
Focus: CVE identifiers (e.g. CVE-2023-1234).

Idea: if the answer mentions a CVE ID that never appears in the source data,
the model invented it. That is a hallucination for identifier-type facts.

Usage:
    python scripts/hallucination_check.py --source sample-data/cves.txt \
                                          --answer sample-data/answer_bad.txt
"""
import argparse
import re

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)


def extract_cve_ids(text):
    """Return the set of CVE IDs found in a piece of text (uppercase)."""
    return {match.upper() for match in CVE_PATTERN.findall(text)}


def check_answer(source_text, answer_text):
    """Compare CVE IDs in the answer against the source.

    Returns a dict with:
      grounded       - IDs in the answer that exist in the source
      unsupported    - IDs in the answer that do NOT exist in the source
      grounding_rate - grounded / total IDs in the answer (1.0 if none mentioned)
    """
    source_ids = extract_cve_ids(source_text)
    answer_ids = extract_cve_ids(answer_text)

    grounded = sorted(answer_ids & source_ids)
    unsupported = sorted(answer_ids - source_ids)
    total = len(answer_ids)
    rate = 1.0 if total == 0 else len(grounded) / total

    return {
        "grounded": grounded,
        "unsupported": unsupported,
        "grounding_rate": round(rate, 3),
    }


def main():
    parser = argparse.ArgumentParser(description="Check an AI answer for invented CVE IDs.")
    parser.add_argument("--source", required=True, help="path to the source data file")
    parser.add_argument("--answer", required=True, help="path to a file holding the AI answer")
    args = parser.parse_args()

    with open(args.source, encoding="utf-8", errors="replace") as f:
        source_text = f.read()
    with open(args.answer, encoding="utf-8", errors="replace") as f:
        answer_text = f.read()

    result = check_answer(source_text, answer_text)
    print(f"Grounded IDs     : {result['grounded']}")
    print(f"Unsupported IDs  : {result['unsupported']}")
    print(f"Grounding rate   : {result['grounding_rate']}")
    print("RESULT           :", "PASS" if not result["unsupported"] else "FAIL (possible hallucination)")


if __name__ == "__main__":
    main()
