# Test Plan and Coverage

| # | Test area | What it checks | Status |
|---|---|---|---|
| 1 | Data ingestion | File format support and parsing correctness | Done |
| 2 | Retrieval accuracy | Answers match the uploaded content | Done |
| 3 | Hallucination and grounding | Model invents no facts (CVEs, log events) | Done |
| 4 | Scalability and volume | Behaviour on large inputs | Partial (about 50,000 records tested) |
| 5 | Environment comparison | SaaS vs on-prem accuracy, tokens, behaviour | Done |
| 6 | Knowledge graph verification | Uploaded files appear and link correctly | Done |
| 7 | Agent functionality | Basic tasks, file editing, downloads, errors | Done |
| 8 | Code execution boundary | Which languages run, and where | Done |
| 9 | UI functional testing | Uploads, buttons, messages, file management | Done (file deletion pending) |
| 10 | Telemetry validation | Accuracy of timing and token readouts | Done |
| 11 | Defect management | Report, retest after fix | Done |
| 12 | Performance and latency | Response time under normal and peak load | Remaining |
| 13 | Security | Prompt injection, data leakage, access control | Remaining |
| 14 | Privacy and compliance | PII handling, retention | Remaining |
| 15 | Regression suite | Re-run saved scripts after each release | Remaining |
| 16 | Robustness and edge cases | Corrupt, empty, huge, non-English, conflicting files | Remaining |
| 17 | Agent safety and reliability | Multi-step tasks, looping, recovery | Remaining |
| 18 | Metrics and sign-off | Pass/fail thresholds | Remaining |

## Example test cases (template)
| ID | Area | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| TC-01 | Ingestion | Upload a .csv | File accepted and answerable | Failed at first, passed after fix | Closed |
| TC-02 | Ingestion | Upload a .log | Questions answered from the log | Failed at first, passed after fix | Closed |
| TC-03 | Grounding | Ask for highest-severity CVE | Correct ID from file | [fill in] | [fill in] |
| TC-04 | Scale | 50,000-record CVE file | Correct answer, comparable tokens | Correct; on-prem used more tokens, then fixed | Closed |
| TC-05 | UI | Delete an uploaded file | File removed | Not supported | Open |
| TC-06 | Agent | Edit a file and return a download link | Working link | Link failed at first, mostly fixed | Closed |
| TC-07 | Boundary | Run Python in chat UI | [fill in expected] | Did not run in chat UI; ran on agent | Documented |

Add real rows from your notes. Only list results you actually observed.

## Suggested pass/fail thresholds (to agree with the team)
| Metric | Example target |
|---|---|
| Formats ingested correctly | 100% of supported list |
| Unsupported identifiers in answers | 0 on the golden set |
| Grounding rate | at least 95% |
| On-prem vs SaaS token difference | within an agreed margin |
These are proposals, not results.
