# Pre-Deployment Evaluation of an Enterprise AI Platform and Agent

A test-and-evaluation case study: how I tested an enterprise AI platform (SaaS model, on-prem model, chat UI and AI agent) before deployment, and the small Python tools I used.

## About this repo
This is a **use case and reference implementation**, not a copy of any real project files.
- The evaluation described here was done as part of earlier work. The original scripts, data, messages and platform details belong to that work and are **not** included.
- The platform and vendor are described generically on purpose.
- The code in `scripts/` is **sample code written to illustrate the approach** (uploading files through an API, counting tokens, and checking answers automatically). It was created with AI assistance, runs against a local mock API, and has not been run against any real platform.
- Findings below are recalled from the original evaluation and are approximate. No exact counts or timings are claimed.

## Objective
Find out whether the platform can ingest many file types, including large CVE datasets and log files, and return accurate, grounded answers without inventing facts.

## Scope
| Area | Covered |
|---|---|
| Environments | SaaS and on-prem models |
| Interfaces | Chat UI and the AI agent |
| Data | Fresh files in nearly all formats, log files, and a CVE dataset of about 50,000 records |
| Automation | Python scripts that uploaded files through the platform API, counted tokens, and automatically checked whether answers were correct; also ingestion, retrieval accuracy, file-format and graph-visibility checks |
| Reporting | Findings reported to my manager and the vendor on Slack and Teams, then re-tested after each fix |

Status: pre-deployment, roughly 60% of the full test plan executed (see [test-plan.md](test-plan.md)).

## Method
1. **Fresh data per round.** New files for every format so earlier results could not hide a bug.
2. **Source-of-truth comparison.** Every answer was judged against the uploaded file. If an answer contained a fact (a CVE ID, a score, a log event) not in the file, it counted as a hallucination.
3. **Same input, both environments.** SaaS and on-prem got identical files and questions so differences were real.
4. **Independent measurement.** Timing and token figures were measured by my own scripts outside the platform's dev tools, because those readouts looked wrong. Token counts reported by the API were compared with my own estimate.
5. **API-driven checks.** Scripts uploaded each file through the platform API, confirmed the upload succeeded, asked a question, and checked the answer against the source file automatically instead of by eye.
6. **Report, fix, re-test.** Every defect was logged with steps, expected and actual result, then re-tested after the vendor's fix.

## Metrics I used
| Metric | Meaning |
|---|---|
| Accuracy | Does the answer match the source? |
| Hallucination rate | Unsupported claims divided by total claims checked |
| Grounding rate | Share of facts in an answer that appear in the source |
| Completeness | Did it miss or truncate details? |
| Token usage and latency | Cost and speed, measured independently |
| Consistency | Same result across repeated runs and across SaaS and on-prem |

## Key findings (from the original evaluation, recalled from memory)
| Area | Finding | Outcome |
|---|---|---|
| File formats | Only PDFs were read at first | Nearly all formats worked after fixes |
| Large CVE file (about 50,000 records) | Answers were correct, but on-prem used more tokens than SaaS | Resolved after reporting |
| Code execution | Python ran only on the agent, not in the chat UI. JavaScript, Java, C and C++ did not run | Boundary documented |
| Agent file editing | Download links failed and the agent returned a generic "contact support" style message | Mostly fixed |
| UI | Many functional defects | Many fixed |
| Dev-tool timing and token metrics | Inaccurate | Resolved |
| File deletion | Not supported | Pending |

Full list: [defect-log.md](defect-log.md).

## What is in this repo
| File | Purpose |
|---|---|
| `scripts/platform_client.py` | Small API client: upload a file, ask a question, return the answer, reported token count and measured latency. Endpoint and field names are set by environment variables |
| `scripts/file_format_test.py` | Test harness: for 7 file formats, uploads via the API, asks a question, verifies the answer, compares reported vs estimated tokens, and writes `results.csv` |
| `scripts/hallucination_check.py` | Flags CVE IDs in an answer that are not in the source file |
| `scripts/mock_server.py` | A fake platform API so the harness and tests run without the real system |
| `tests/` | pytest tests for the checker, the client, auth failure and error handling |
| `sample-data/` | Synthetic CVE data plus one good and one bad sample answer |

## Try it
```bash
pip install -r requirements.txt
python scripts/file_format_test.py --dry-run       # runs against the local mock API
python scripts/hallucination_check.py --source sample-data/cves.txt --answer sample-data/answer_bad.txt
pytest
```
To point it at a real platform, set `PLATFORM_BASE_URL` and `PLATFORM_API_KEY` (and the endpoint or field names if they differ from the defaults), then run `python scripts/file_format_test.py --live`. Never commit API keys; `.gitignore` already excludes `.env`.

## Limitations
- The hallucination check only covers identifier-type facts (CVE IDs). It does not catch wrong scores, invented explanations or paraphrased errors, which I checked by hand.
- The harness uses small synthetic files and a mock API. The endpoint and field names are configurable defaults, so they must be matched to the real API documentation before a live run.
- The token estimate is a rough characters-divided-by-four figure used only as a sanity check against the platform's reported count.
- The 50,000-record test was run separately.
- The sample code was written with AI assistance to illustrate the method. It is not the original tooling, and I am still building my own coding depth.

## Not yet done (remaining test plan)
Performance and load, security (prompt injection, data leakage, role-based access), privacy and PII handling, a saved regression suite, edge cases (corrupt, empty, huge or non-English files), agent reliability (multi-step tasks, loops, recovery) and defined pass/fail thresholds.

## Lessons learned
- A chat answer alone does not prove a file was indexed; check it independently.
- Do not trust a tool's own timing and token numbers without a second measurement.
- Test the same data in every environment.
- Small, repeatable scripts are worth more than one-off manual checks.
