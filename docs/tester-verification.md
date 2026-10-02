# Independent Tester verification — 2026-10-01

Scope: Repository B only; all of docs/plan.md including amendments read. Existing student
changes retained. No classroom checkout edits, commits, pushes, student service stops or
persistent volume deletions. No containers were running at entry. Tester used project
`dashbite-b-tester`, a fresh project-scoped volume and an automatically allocated loopback
port. Test runs used `dashbite-b-tester-tests` without application mounts. Tester containers
and networks were removed; `dashbite-b-tester_dashbite-data` is intentionally preserved.

## Findings and disposition

| Severity | Finding | Disposition |
|---|---|---|
| Medium, fixed | Health probe followed HTTP redirects and accepted a 302 leading to a 200 page, violating the exact-200 endpoint contract | Reject redirects. New controlled HTTP regression first failed (1 failed, 5 passed), then passed after correction. |
| Medium, open limitation | Training does not stop gracefully in the reproduced Docker stop | SIGTERM followed by SIGKILL; exit 137, OOMKilled=false, Error empty. No signal-handling redesign, consistent with amendment 12. Forced termination can interrupt file writes; no graceful-shutdown claim. |
| Medium, student action | Builder transcript format/coverage mismatch | File exists with six labeled messages; three use mixed-case labels. Historical inventory describes 15 visible messages before cutoff. Re-export/compare against original chat; completeness cannot be certified. Neither transcript edited. |
| Low, fixed | README claimed Builder transcript absent despite present file | Current status corrected; historical Builder/export records retained with dated clarification. |
| Low, maintenance | Six Altair interval-type warnings | Score-distribution value_counts(bins=10) produces an IntervalIndex; Altair defaults to nominal categories. Both populated views render without exceptions. No demonstrated page/pipeline failure. Explicit chart interval labels/types are a future maintenance improvement; browser appearance not independently certified. |
| Low, coverage improved | Empty first-start dashboard not covered by Builder rendering tests | Added Model Pulse and Ops Control empty-data cases; waiting messages and zero metrics verified. |

Architecture, targets, opt-in test profile, project-scoped volume, explicit IPv4 true/IPv6
false, and PYTHONPATH=/app match the finalized plan. Base publishing remains loopback 8501;
ignored work/port.yaml resolves to loopback 8502. Neither port configuration was changed.
Health proves endpoint responsiveness only, separately from AppTest rendering and live
pipeline artifact validation. No new model, UI, restart policy or shutdown design was added.

## Exact independent results

| Check | Actual result |
|---|---|
| Baseline local `.venv/Scripts/python -X utf8 -m pytest -q` | 41 passed, 6 warnings, 24.84s; exit 0 |
| Baseline container full suite | 41 passed, 6 warnings, 4.14s; exit 0 |
| Final local full suite | 44 passed, 6 warnings, 7.72s; exit 0 |
| Final fresh container suite 1 | 44 passed, 6 warnings, 4.79s; exit 0 |
| Final fresh container suite 2 | 44 passed, 6 warnings, 4.67s; exit 0 |
| Runtime and test image builds | Passed before and after probe correction; existing dependency layers cached |
| Resolved Compose | Independent test definition: no mounts, ports, depends_on or runtime environment; test target selected. IPv4 enabled, IPv6 disabled; default/override ports 8501/8502 verified |
| Actual retained test-container mounts | `[]` |
| Image contents | Runtime lacks /app/tests and /app/pytest.ini; test image contains both |
| Deliberately failing test in disposable container /tmp | Actual assertion failure, `1 failed`; Compose exit 1 preserved |
| Runtime regression script, before and after change | Three PASS lines each: actual IPv4 address/network; host HTTP 200; real script imports from /tmp; cleared PYTHONPATH reproduces ModuleNotFoundError |
| Live full stack | Five services started on fresh volume; first validator passed: 210 features, 190 predictions, 12 quality batches, 240 input / 210 output / 30 dropped |
| Dashboard health | Healthy with probe exit 0, including recreated final runtime image |
| Train stopped, inference independent | Predictions 244 -> 480; checkpoint remained 20261001_231846; new rows referenced that checkpoint while train exited |
| Isolation snapshots, writers stopped | All 151 file inventory/content hashes identical before/after final container tests; host data comparison also identical |
| Persistence before writers resumed | Down/create without -v, same named volume; all 151 hashes identical |
| Resumed pipeline | Validator passed: 822 features, 802 predictions; 45 batches, 900 input / 822 output / 78 dropped |
| Runtime logs | Initial and final captured logs checked for tracebacks; see final check below |
| Windows PowerShell commands | Build/run/config/inspect/stop/recreate commands executed successfully |
| Git Bash | Actual `docker compose ... config --quiet` and `make PROJECT=dashbite-b-tester container-status` succeeded |
| Make shortcuts | All seven container targets dry-run successfully; destructive inherited local targets not executed |

Final runtime image: sha256:a996560523f88fd90074ebb4e25a83e1d3d09d92bed9dfb54897e6afb78b10ff.
Final test image: sha256:797f504a55d62abf8d22ce3a24461d7462e9fd991a9f9df6a559a6edf125d9e9.
Docker 29.7.2, Compose v5.4.0; local Python 3.14.7 and container Python 3.12.14.
Dependency versions are the existing installed environment recorded in Builder dependency
lists; dependency installation from an empty cache was not repeated. Floating base and >=
requirements still preclude frozen reproducibility.

Commands for final suites (from Repository B):

```powershell
.venv/Scripts/python -X utf8 -m pytest -q
docker compose -p dashbite-b-tester --profile test build tests dashboard
docker compose -p dashbite-b-tester-tests --profile test run --rm --no-deps tests
docker compose -p dashbite-b-tester-tests --profile test run --rm --no-deps tests
.venv/Scripts/python -X utf8 scripts/verify_container_runtime.py
```

Supporting scratch evidence remains under ignored work/: tester-first.txt,
tester-resumed.txt, tester-before.json, tester-host-before.json, tester-host-after.json,
tester-train-events.jsonl, tester-runtime.log, tester-final-runtime.log and tester_checks.py.
These are verification records, not role transcripts or student observations.

## Exit 137 diagnosis boundaries

The reproduced training container was Python directly as PID 1. Its loop has no SIGTERM
handler. Docker events recorded signal 15 at 23:18:44.762 UTC, signal 9 at 23:18:47.774 UTC,
then exit 137. Inspect reported OOMKilled=false and Error="". This establishes forced
SIGKILL after the stop request for this reproduction, rather than an OOM explanation.
The original student container had already been removed: the same cause is plausible but
not provable retrospectively. Do not describe either the observed reproduction or the
unverified historical stop as graceful. Shutdown still preserved the tested volume.

## Tests and evidence quality

The new health test uses a real HTTP redirect and target server, not source-string matching.
Existing health tests cover 200, 204, 503, refusal and timeout. New empty-state tests run real
Streamlit widgets with temporary paths; only timed refresh is disabled. Builder's full-chain
test checks fixture IDs, quality accounting, checkpoint loading, prediction bounds and
idempotence under tmp_path. Those provide meaningful behavioral coverage. Some inherited
tests inspect source strings and do not independently prove runtime behavior; live checks
above supplement them. No tests were weakened or removed.

The six warnings are emitted across repeated Model Pulse renders (including the initial
render before switching to Ops Control); they do not mean six separate application defects.
AppTest is not a real-browser screenshot check, and bounded smoke tests do not exclude
partial-write races, all malformed inputs or long-run reliability problems.

## Transcript and manual evidence boundaries

Architect: six supplied header fields, start/end markers and 17 uppercase speaker labels
present. Builder: same header fields and markers present, but [Agent]/[Student] casing and
coverage discrepancy require review. No original conversations were consulted, so neither
file is certified complete. Original text was left untouched. Tester transcript must be
exported after this chat finishes as zx180_tester.txt with the same headers, ROLE: tester,
and exact [STUDENT]/[AGENT] labels. Preserve complete visible messages; upload all three to
Canvas and include them in the repository. This report is not a substitute transcript.

Persistence equality in the plan/README is explicitly student-confirmed on 2026-10-01;
it was not inferred from resumed growth. Independent Tester equality above concerns a
separate 151-file volume and is not a reclassification of student evidence.

## Changed files and required follow-up

- pipeline/healthcheck.py: reject redirects.
- tests/unit/test_healthcheck.py: redirect regression.
- tests/integration/test_dashboard_views.py: two empty-data rendering cases.
- README.md and docs/manual-smoke.md: current test count, shutdown and repeat-check guidance.
- docs/builder-verification.md and docs/transcripts/builder-export-notes.md: dated status clarification only.
- docs/tester-verification.md: this report.

The requested runtime rebuild, five-service startup with work/port.yaml, dashboard health
and both browser-view recheck on 8502 are now student-reported passed; see the dated report
below. This report does not claim a new container-test run; the verified suite count remains 44. No UI/model/data-format
change requires repeating the entire persistence or training-independence demonstration.
Do not claim graceful shutdown. Review transcript completeness/labels, export this Tester
conversation, and finish submission. Git Bash configuration/status were exercised; a clean
Windows dependency install and all inherited POSIX background commands were not retested.

Final checks: negative-health container became unhealthy with repeated probe exit 1 and
connection-refused diagnostics while no server ran; its 60-second sleep later ended.
Final runtime logs contained no Traceback/Error matches. `git diff --check` passed.
No Tester containers remain. Student smoke and classroom volumes remain present.

## Student-reported post-fix manual recheck (2026-10-01)

The student reported successfully rebuilding the runtime image, starting all five services
with the existing `work/port.yaml` override, confirming a healthy dashboard mapped to host
port **8502**, and personally opening **Model Pulse** and **Ops Control**; both displayed
normally without errors. These are student-reported manual observations, not new independent
Tester execution. The requested post-fix manual recheck is recorded as student-reported passed.

No new test-suite run, persistence/isolation comparison, shutdown check, exact metric
reconciliation or screenshot capture is claimed from this report. Existing independent
verification results and all other pending checks/limitations remain unchanged. In particular,
graceful shutdown is not established, and Architect/Builder transcript review remains pending.

This follow-up changed documentation only. No application code, configuration, services or
runtime data were changed, and automated tests were not rerun.

## Tester transcript export status

`docs/transcripts/zx180_tester.txt` now contains exact saved visible messages through the
export update, with the requested headers and labels. The closing reply must be appended
verbatim before the end marker after it appears. See `transcripts/tester-export-notes.md`
for the precise cutoff; this is not yet a complete finished-chat export. No Architect or
Builder transcript content was altered.
