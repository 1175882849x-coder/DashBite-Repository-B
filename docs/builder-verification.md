# Builder verification — 2026-10-01

The initial record below is historical. The student subsequently found two runtime issues
and reported manual results; see the follow-up section and README for current status.

This records Builder automated checks, not the student's manual smoke test.
No code was committed or pushed. Finalized `docs/plan.md` was read fully and left unchanged.
Existing Makefile/README working edits were retained. Classroom checkout was read only;
its HEAD remains `3f51661f08e7b4c98137e94b09e7711f3c3f7e0b`, its origin remains the classroom
URL, and only its prior Makefile/README edits appear in status.

## Initial Builder results (before student smoke fixes)

| Check | Status / observed result |
|---|---|
| Initial `python -m pytest` | **Failed:** 31 passed, 2 GBK decoding failures in inherited source-inspection tests; Python 3.14.7 |
| Baseline `python -X utf8 -m pytest -q` | **Passed:** 33 passed in 1.61s |
| First expanded local collection | **Failed:** host Python lacked Streamlit, required by the new dashboard-loader integration test |
| Host pip installation | **Failed:** repeated network connection resets on package index requests, including explicit PyPI retry |
| Local dependency recovery | **Passed:** downloaded Windows wheels through Docker networking, including Windows-only tzdata/colorama, installed offline into ignored Repository B `.venv` |
| Full local suite | **Passed:** 39 passed in 27.36s, Python 3.14.7, UTF-8 mode |
| Resolved Compose | **Passed:** JSON parsed; test service has no mounts, dependencies, ports or runtime environment; distinct tag/test target; five runtime targets; project-scoped volume |
| Runtime/test image builds | **Passed:** both targets built; Docker network package downloads succeeded |
| Image contents | **Passed:** runtime lacks `/app/tests` and pytest config; test image contains config and fixture CSV |
| Fresh full container suites | **Passed:** 39 passed in 3.67s, 3.55s and 3.53s in separate containers |
| Actual test container mounts | **Passed:** Docker inspect returned `[]` |
| Deliberate failure in disposable `/tmp/failing` copy | **Passed:** `1 failed`, Compose run exit 1; production checkout/image unchanged; copy removed with container |
| Live positive health | **Passed:** dashboard healthy at first inspection, within 15 seconds of start; health log exit 0; Streamlit 1.64.0 |
| Disposable negative Docker health | **Passed:** no HTTP server; unhealthy, health-log exit 1 with connection-refused diagnostics |
| Controlled HTTP probe tests | **Passed:** 200 succeeds; 204/503, refused connection and request timeout fail |
| Live first output snapshot | **Passed:** within 15 seconds; 136 features, 122 predictions, 8 batches; raw CSV, quality, markers, checkpoint, metrics and state present; validator passed |
| Training independence | **Passed:** train stopped; checkpoint `20261001_220911`; predictions grew from 318 to 908, recent rows referenced same checkpoint |
| Data isolation | **Passed:** all writers stopped; inventory/content hashes of 213 volume files identical before/after test runs; host data content inventory unchanged |
| Persistence | **Passed:** down/create without `-v`; same named volume and all 213 hashes retained before writers restarted |
| Resumed output | **Passed:** after restart, validation passed with 1,896 features/predictions in the loader snapshot; pipeline continued advancing |
| Logs | **Inspected:** no traceback in captured smoke logs; pandas timestamp-format warnings observed for deliberately corrupted input |
| Make shortcuts | **Passed/inspected:** all new commands dry-run successfully; actual `make container-status` executed successfully |
| Final actual Make execution | **Passed:** `make test`: 39 passed in 6.19s; `make container-test`: rebuilt final image, 39 passed in 3.08s |
| Git whitespace | **Passed:** `git diff --check` |
| Browser rendering and screenshots | **Not run:** student must inspect both views and capture real evidence |
| Student manual smoke / independent Tester | **Not run:** still required |

Initial verification mistakes were corrected: `tests -q` attempted to execute `-q` and
failed; corrected `tests python -m pytest -q` passed. The initial injected-test command had
a quoting SyntaxError; it was corrected and rerun to prove an actual pytest assertion failure,
not merely a failing interpreter invocation. Neither mistaken attempt counts as acceptance evidence.

The resumed live sample and quality counts can advance between individual reads. The final
live report had quality rows_out 1,916 while the earlier feature/prediction loader snapshot
was 1,896. This is consistent with live writers advancing; exact comparisons require stopping
writers. Hash comparisons above were performed with all writers stopped.

## Initial tested environment

- Host: Windows, Python 3.14.7; container Python 3.12.14.
- Docker Engine/CLI 29.7.2; Docker Desktop 4.88.1; Compose v5.4.0; Linux engine.
- Runtime image ID: `sha256:dc248476d06d77436adbc39452554836f59df397ca77645e57502137c33c90ad`.
- Final test image ID: `sha256:0521fb199b6ed42b2af33d2a3b65e7983f34ba0252dc578b53f854a743ce4000`.
- Test image ID at initial verification: `sha256:22725ff2b4a73abfe1340f5467fcc7f123a85eac7fb7b7b555daf3d8b5a3be25`.
- Base resolved during build: `python:3.12-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f`.
- Main installed versions: pandas 3.0.6, numpy 2.5.3, scikit-learn 1.9.1, joblib 1.6.0,
  Streamlit 1.64.0, pytest 9.1.1. Full lists: `container-dependencies.txt` and `local-dependencies.txt`.
- Dependencies/image are not locked; rebuilding may change resolution. These are observed
  versions, not promised future versions.

## Focused tests and supporting commands

The integration test uses fixed fixture IDs/timestamps and both classes under `tmp_path`,
adds one invalid row, and exercises raw preprocessing, quality accounting, training/state,
loadable checkpoint, prediction ID coverage, no duplicates, finite bounded probabilities,
binary labels, checkpoint references and dashboard loader/metric values. Second calls with
no new input leave all file contents unchanged. The health tests exercise the actual probe
against controlled HTTP servers rather than searching configuration strings.

`python -m pipeline.inspect_data` lists actual files and dashboard helper metrics.
`--validate` checks populated artifact contracts and returns nonzero on assertion failure.
It permits pending feature IDs during live inference and does not certify UI rendering.
`--snapshot` hashes all files, including hidden markers; stop writers before using it as
unchanged-data evidence. Full manual commands are in `manual-smoke.md`.

## Initial handoff state and limitations (historical)

All Builder-created service/test/negative-health/download containers and project networks
were removed. The disposable `dashbite-b-smoke_dashbite-data` volume remains intentionally
preserved. It contains Builder output; the manual guide labels an optional targeted destructive
reset if the student wants a fresh smoke volume. Normal shutdown always preserves data.
The host `.venv` and `work` downloads/evidence are ignored. No classroom data volume was used.

At the initial handoff, the student's smoke, browser observations/screenshots, Tester findings
and complete exported role transcripts were outstanding, and transcript headers had not yet
been supplied. The follow-up below supersedes those status statements.
Brief runtime verification does not exclude file-read races or guarantee long-run reliability.
No dependency locking, base digest pinning, scaling, DATA_ROOT override, UI replacement,
automatic restart, model redesign or cloud deployment was added.


## Follow-up after student manual report — 2026-10-01

### Student-reported evidence (not Builder execution)

The student reported both Model Pulse and Ops Control displaying metrics/data on host port
8502 through `work/port.yaml`, with screenshots in `docs/images/manual-model-pulse.png` and
`manual-ops-control.png`. Training stopped; predictions rose from 12,672 to 13,102 with
checkpoint `20261001_223646`. The training container showed exit 137; graceful shutdown is
not established and the cause requires Tester review. No cause is inferred from the code alone.
The student reported 39 container tests passed/exit 0 after the fixes, identical application-
volume snapshots before/after tests with all writers stopped, and resumed growth after
recreation without deleting the reused volume. That volume included earlier Builder data.

**Persistence snapshots across recreation: student-confirmed passed (2026-10-01).**
The student explicitly confirmed that the comparison produced no output and that the snapshots
before and after container recreation were identical. This is separate from test-isolation
snapshots and the earlier Builder persistence check; Builder did not rerun this comparison.
No additional student checks are inferred from the confirmation.

### Builder review and additional execution

The fixes were already present when this follow-up began; Builder reviewed and preserved them:

- `compose.yaml`: default network enables IPv4 and disables IPv6, matching the existing
  Streamlit `0.0.0.0` listener and loopback IPv4 host publishing.
- Dockerfile base-stage environment: `PYTHONPATH=/app`, inherited by runtime/test stages.
  This makes package imports independent of the script directory used by Streamlit.
- `work/port.yaml`: retained unchanged, mapping `127.0.0.1:8502:8501`; base Compose still uses
  host port 8501. Runnable manual commands now include the override consistently.

Actual additional results:

| Builder follow-up check | Result |
|---|---|
| Source/current files | Both fixes and both screenshot files inspected as present; screenshot existence is not a new personal browser smoke test |
| Runtime and test image builds | Passed, exit 0 |
| New automated view tests | Two parametrized Streamlit AppTest cases passed with fixed temporary feature/prediction data; actual app/widgets rendered, timed auto-refresh disabled only in harness |
| Full local suite | **41 passed**, 6 warnings, 7.14s; exit 0 |
| Full container suite | **41 passed**, 6 warnings, 3.95s; exit 0 |
| Actual disposable network | Explicit IPv4 true / IPv6 false and assigned IPv4 address verified |
| Host-published endpoint | HTTP 200 reached from host on a dynamically allocated loopback port |
| Real dashboard script import | Succeeded after changing working directory to `/tmp`, using the runtime image environment |
| Negative import control | Clearing PYTHONPATH reproduced `ModuleNotFoundError: No module named 'pipeline'`, nonzero exit |
| Disposable cleanup | Unique project `dashbite-b-regression-4117bac8` and its own volume removed; student smoke volume not mounted or altered by this check |

Both suites emitted six Altair warnings about inferring a Vega-Lite type from an interval
column, defaulting to nominal. The tests did not raise dashboard rendering exceptions; no
chart redesign was made. Automated rendering is distinct from the student's browser evidence.
The runtime regression starts only a dashboard against its own empty volume, so it does not
claim a new complete pipeline/manual smoke test or a shutdown diagnosis.

Commands executed after rebuilding:

```powershell
.venv/Scripts/python -X utf8 -m pytest -q
docker compose -p dashbite-b-tests --profile test run --rm --no-deps tests
.venv/Scripts/python -X utf8 scripts/verify_container_runtime.py
```

Use `python scripts/verify_container_runtime.py` to repeat the disposable runtime check after
building the runtime image; the script needs only host standard-library Python and Docker.
Current runtime image: `sha256:ef50565d437525319ec27eface0222355cc48acef33580f61bbbea564e9533e8`.
Current test image: `sha256:5900e999c6f8b0adadc582893a8028613a0418c65dcef0f123088e7011935623`.
These supersede initial image IDs above for the follow-up code, without rewriting history.

NetID/header details are now supplied. Saving the Builder transcript was blocked by automatic approval review; the requested
transcript file has not been created. An export-status note records available-message coverage
and what a final manual export must include. The pasted student report remains
a student message, not evidence of Builder execution in the other chat. Independent Tester
review and exit-137 investigation remain outstanding. Student persistence confirmation has
now been received and is recorded above.


Final follow-up documentation checks: both resolved Compose variants parsed successfully;
assertions confirmed host ports 8501/8502 respectively, explicit IPv4-only networking and
continued absence of test mounts/ports/dependencies. The documented Make override commands
were dry-run successfully. Git whitespace checks passed. No Builder-created containers
remain. Persistence snapshot equality was subsequently explicitly confirmed by the student
on 2026-10-01; no new automated checks were run for this documentation-only update.

Transcript limitation: automatic approval review rejected the export command and the narrower
save with "blocked by policy" and no more specific reason. The requested transcript has not
been saved; see `transcripts/builder-export-notes.md`. No earlier visible messages were found
missing in the inspected records, but an inventory is not a completed transcript.

## Tester status clarification (2026-10-01)

The export-failure statements above are historical. `zx180_builder.txt` now exists under
`docs/transcripts/`, with six labeled messages (including mixed-case labels), whereas the
export inventory described 15 visible messages before its cutoff. Original conversations
were not available to Tester; completeness cannot be certified. Compare and export from
the original chat, retaining exact message content and required uppercase speaker labels.
Tester did not alter either original transcript. See `docs/tester-verification.md`.
