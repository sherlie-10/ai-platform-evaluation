"""
file_format_test.py

An API test harness that, for each file format:
  1. creates a fresh synthetic file,
  2. uploads it through the platform API (platform_client.py),
  3. asks a question about it,
  4. VERIFIES the answer: expected value present, and no invented CVE IDs,
  5. records the platform's reported token count next to an independent estimate,
     plus latency measured by this script,
  6. writes everything to results.csv.

Try it with no real platform (starts a local mock API):
    python scripts/file_format_test.py --dry-run

Run against the real platform (set PLATFORM_BASE_URL and PLATFORM_API_KEY first):
    python scripts/file_format_test.py --live
"""
import argparse
import csv
import json
import os
import time

from hallucination_check import check_answer
from mock_server import start_mock_server
from platform_client import PlatformClient, estimate_tokens

OUT_DIR = "generated-files"
QUESTION = "Which CVE ID has the highest severity in this file, and what is its score?"
EXPECTED = "CVE-2024-0003"  # the highest-severity record in our synthetic data

RECORDS = [
    {"id": "CVE-2024-0001", "severity": "LOW", "score": 3.1},
    {"id": "CVE-2024-0002", "severity": "MEDIUM", "score": 5.4},
    {"id": "CVE-2024-0003", "severity": "CRITICAL", "score": 9.8},
]


def make_files():
    """Create the same data in several formats. Returns {format: path}."""
    os.makedirs(OUT_DIR, exist_ok=True)
    paths = {}

    p = os.path.join(OUT_DIR, "cves.txt")
    with open(p, "w") as f:
        for r in RECORDS:
            f.write(f"{r['id']} severity={r['severity']} score={r['score']}\n")
    paths["txt"] = p

    p = os.path.join(OUT_DIR, "cves.csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "severity", "score"])
        w.writeheader()
        w.writerows(RECORDS)
    paths["csv"] = p

    p = os.path.join(OUT_DIR, "cves.json")
    with open(p, "w") as f:
        json.dump(RECORDS, f, indent=2)
    paths["json"] = p

    p = os.path.join(OUT_DIR, "cves.log")
    with open(p, "w") as f:
        for i, r in enumerate(RECORDS):
            f.write(f"2024-05-0{i+1} 10:00:00 INFO scanner found {r['id']} "
                    f"severity={r['severity']} score={r['score']}\n")
    paths["log"] = p

    p = os.path.join(OUT_DIR, "cves.md")
    with open(p, "w") as f:
        f.write("# CVE report\n\n| ID | Severity | Score |\n|---|---|---|\n")
        for r in RECORDS:
            f.write(f"| {r['id']} | {r['severity']} | {r['score']} |\n")
    paths["md"] = p

    p = os.path.join(OUT_DIR, "cves.xml")
    with open(p, "w") as f:
        f.write("<cves>\n")
        for r in RECORDS:
            f.write(f'  <cve id="{r["id"]}" severity="{r["severity"]}" score="{r["score"]}"/>\n')
        f.write("</cves>\n")
    paths["xml"] = p

    p = os.path.join(OUT_DIR, "cves.html")
    with open(p, "w") as f:
        f.write("<table>\n")
        for r in RECORDS:
            f.write(f"<tr><td>{r['id']}</td><td>{r['severity']}</td><td>{r['score']}</td></tr>\n")
        f.write("</table>\n")
    paths["html"] = p

    return paths


def run(client):
    paths = make_files()
    rows = []

    for fmt, path in paths.items():
        with open(path, encoding="utf-8") as f:
            source_text = f.read()

        row = {"format": fmt, "upload": "", "answer_correct": "", "unsupported_ids": "",
               "tokens_reported": "", "tokens_estimated": "", "latency_seconds": "",
               "status": "FAIL", "error": ""}
        try:
            file_id = client.upload(path)
            row["upload"] = "OK"
            result = client.ask(QUESTION, file_id)

            check = check_answer(source_text, result["answer"])
            row["answer_correct"] = "YES" if EXPECTED in result["answer"] else "NO"
            row["unsupported_ids"] = " ".join(check["unsupported"])
            row["tokens_reported"] = result["tokens_reported"]
            row["tokens_estimated"] = estimate_tokens(QUESTION + source_text)
            row["latency_seconds"] = result["latency_seconds"]
            if row["answer_correct"] == "YES" and not check["unsupported"]:
                row["status"] = "PASS"
        except Exception as exc:  # one failure must not stop the whole run
            row["upload"] = row["upload"] or "FAILED"
            row["error"] = str(exc)[:150]
        rows.append(row)

    fields = ["format", "upload", "answer_correct", "unsupported_ids", "tokens_reported",
              "tokens_estimated", "latency_seconds", "status", "error"]
    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    passed = sum(1 for r in rows if r["status"] == "PASS")
    print(f"{passed}/{len(rows)} formats passed. Details in results.csv")
    for r in rows:
        print(f"  {r['format']:5} {r['status']}  tokens(reported/est)={r['tokens_reported']}/{r['tokens_estimated']}  "
              f"{r['latency_seconds']}s  {r['error']}")
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="use a local mock API")
    mode.add_argument("--live", action="store_true", help="use the real platform from env vars")
    args = parser.parse_args()

    if args.dry_run:
        server, base_url = start_mock_server()
        run(PlatformClient(base_url=base_url, api_key="test-key"))
        server.shutdown()
    else:
        run(PlatformClient())
