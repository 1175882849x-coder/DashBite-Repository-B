# DashBite — Simple Stage-by-Stage ML Pipeline

Teaching demo of a modular data + ML application. **DashBite** predicts whether a food-delivery order will be **late**.

The inherited Dockerfile and Compose configuration run five container services. Stages are separate Python modules that share folders under `data/`. Training and inference are **independent processes** coupled only by timestamped checkpoints in `data/models/`. Inference always uses the **newest** checkpoint.

## Stages

| Stage | Module | What it does |
|-------|--------|----------------|
| 0 | `pipeline.config`, `pipeline.paths` | Shared config + data folders |
| 1 | `pipeline.simulator` | Writes timed CSV batches to `data/raw/` (“new orders arrived”) |
| 2 | `pipeline.preprocess` | Drops bad rows, adds `hour` / `is_peak` → `data/features/` |
| 3 | `pipeline.train` | Retrains when ≥ `TRAIN_EVERY_N_EVENTS` new labeled rows; writes checkpoints |
| 4 | `pipeline.infer` | Scores unscored rows with newest checkpoint → `data/predictions/` |
| 5–6 | `pipeline.dashboard` | Streamlit: **Model Pulse** + **Ops Control** |

## Setup

```bash
make install
```

Or manually:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Makefile shortcuts

```bash
make help          # list targets
make test          # full pytest gate
make run           # start all stages in background + dashboard
make stop          # stop background pipeline
make clean-data    # wipe runtime CSVs/checkpoints under data/
```

Foreground single stages: `make simulator`, `make preprocess`, `make train`, `make infer`, `make dashboard`.

## Testing gate (required after every stage)

After each stage you implement or change, run the **full** suite:

```bash
pytest
```

That runs **unit**, **regression**, and **integration** tests together so new work cannot break older stages.

```bash
pytest -m unit
pytest -m regression
pytest -m integration
```

Layout:

```
tests/
  unit/
  regression/
  integration/
  fixtures/
```

## Run the pipeline (separate terminals)

Use a small retrain threshold for demos:

```bash
export TRAIN_EVERY_N_EVENTS=50
export BATCH_SIZE=20
```

Terminal 1 — intake:

```bash
python -m pipeline.simulator
```

Terminal 2 — preprocess:

```bash
python -m pipeline.preprocess
```

Terminal 3 — train (write path only):

```bash
python -m pipeline.train
```

Terminal 4 — infer (read path only; picks newest checkpoint):

```bash
python -m pipeline.infer
```

Terminal 5 — dashboards:

```bash
streamlit run pipeline/dashboard/app.py
```

## Config (environment)

| Variable | Default | Meaning |
|----------|---------|---------|
| `TRAIN_EVERY_N_EVENTS` | `2000` | Retrain after this many **new** labeled rows |
| `BATCH_SIZE` | `50` | Orders per simulator tick |
| `POLL_INTERVAL_SECONDS` | `2.0` | Sleep between polls/ticks |
| `RANDOM_SEED` | `42` | Training seed |
| `CORRUPT_BATCH_RATE` | `0.25` | Fraction of batches that include NaNs / bad types |

Preprocess logs per-batch **throughput** and **field-level failures** to `data/quality/batch_quality.csv`. Model Pulse shows these live.

## Design notes for class

- Intake uses **batch CSV files** under the hood; logs say “new orders arrived”.
- Train **only writes** `data/models/checkpoint_*.joblib`.
- Infer **only reads** that folder and never imports train.
- Dashboards read `data/features/` and `data/predictions/` — test the metric helpers with `pytest`, not the browser UI.


## Repository B: IDS706 Option 1

Source: https://github.com/ammylin/TestingAndContainerizationDemo.git, baseline
`3f51661f08e7b4c98137e94b09e7711f3c3f7e0b` (Added Docker).
Repository B retains source history. Its current origin is
https://github.com/1175882849x-coder/DashBite-Repository-B.git.
Builder has not committed or pushed these changes; remote configuration was inspected locally.
No license file was found; no license is invented here. Classroom source was not modified.

**Inherited:** simulator, preprocessing/quality logging, independent training and inference,
Model Pulse and Ops Control UI, shared data volume, five-service Compose architecture,
Dockerfile and 33 unit/regression/integration tests. The Windows Makefile adjustments
and README activation instructions were already uncommitted at Builder entry; they
remain preserved, and authorship must be confirmed before claiming them as contributions.

**New:** runtime/test Docker targets and distinct `dashbite-b:runtime` / `dashbite-b:test`
tags; dashboard-only Python health probe; independently defined opt-in test service;
container Make targets; artifact inspection/hash/validation commands; five probe tests
and one deterministic raw-to-dashboard integration test; automated rendering checks for both
views and a disposable runtime regression script; verification and smoke instructions.
Manual testing identified two additional fixes already present at follow-up review:
explicit IPv4-only Compose networking and `PYTHONPATH=/app` in the Docker base stage.
The existing UI and pipeline model were preserved.

### Container commands (PowerShell or Git Bash)

Run from Repository B with Docker Desktop's Linux engine available. Make is optional.

| Make shortcut | Equivalent command |
|---|---|
| `make container-build` | `docker compose -p dashbite-b build simulator preprocess train infer dashboard` |
| `make container-up` | `docker compose -p dashbite-b up -d simulator preprocess train infer dashboard` |
| `make container-status` | `docker compose -p dashbite-b ps -a` |
| `make container-logs` | `docker compose -p dashbite-b logs --tail=100 simulator preprocess train infer dashboard` |
| `make container-inspect` | `docker compose -p dashbite-b exec -T dashboard python -m pipeline.inspect_data` |
| `make container-test` | The two test build/run commands below |
| `make container-down` | `docker compose -p dashbite-b down` |

```powershell
docker compose -p dashbite-b-tests --profile test config
docker compose -p dashbite-b-tests --profile test build tests
docker compose -p dashbite-b-tests --profile test run --rm --no-deps tests
```

Expected current test result after Tester regressions: `44 passed`, exit status 0. In PowerShell inspect `$LASTEXITCODE`
immediately; in Git Bash use `echo $?`. A failing pytest returns nonzero; the Make target
also fails. Compose service command overrides must include the program, e.g.
`tests python -m pytest -q`, rather than just `tests -q`.
Tests/fixtures/config are copied only into the test target. The test service has no volumes,
ports, dependencies, runtime environment anchor or shared runtime image tag. Separate
project names plus the actual absence of mounts establish isolation. The profile by itself
is insufficient. Each `run --rm --no-deps` uses a fresh disposable container and pytest
`tmp_path` workspaces. Never use `up` to run the test profile/whole stack.

Dashboard: http://127.0.0.1:8501. Inspect health:

```powershell
docker inspect dashbite-b-dashboard-1 --format '{{json .State.Health}}'
```

The installed Streamlit 1.64.0 endpoint `/_stcore/health` returned HTTP 200 in Builder
verification. The Python standard-library probe requires exactly 200; connection errors,
other statuses and request timeouts return exit 1. Request timeout 3s; Compose interval
10s, timeout 5s, startup allowance 30s, retries 3. Endpoint responsiveness does not establish
page rendering, fresh/correct data, upstream health or model quality. Docker health status
alone does not restart containers. Reference: https://docs.streamlit.io/deploy/tutorials/docker.

The volume is project-scoped (`dashbite-b_dashbite-data` for normal application commands).
`down` preserves it. Do not add `-v` to ordinary shutdown. If port 8501 is occupied,
do not stop unrelated services: use a temporary Compose override publishing another loopback
port and apply that same override to every runtime command. The base Compose file remains
on host port **8501**. The student used **8502** through ignored `work/port.yaml`; the smoke
guide now includes that override explicitly. Both map to Streamlit port 8501 inside the container.

### Verification and remaining work

See [Builder evidence](docs/builder-verification.md) and the
[exact student manual smoke procedure](docs/manual-smoke.md).
The student reported performing the manual smoke test with guidance in a separate chat.
The observations below are **student-reported**, not checks personally performed by Builder:

| Student observation | Recorded result |
|---|---|
| Browser views on host port 8502 | Both Model Pulse and Ops Control rendered metrics and data |
| Training stopped | Predictions increased from **12,672 to 13,102** using checkpoint `20261001_223646` |
| Training container shutdown | Exit code **137** observed; graceful shutdown is **not established**; requires Tester review |
| Container tests after the two fixes | **39 passed**, exit 0 (before the two new rendering regressions) |
| Test isolation | All writers stopped; application-volume snapshots before/after containerized tests identical |
| Container recreation | Volume not deleted; application resumed and data counts increased |
| Persistence snapshot comparison across recreation | **Student-confirmed passed (2026-10-01):** comparison produced no output; snapshots before and after container recreation were identical |
| Starting data | Volume reused; it contained earlier Builder verification data |

Student screenshots: [Model Pulse](docs/images/manual-model-pulse.png) and
[Ops Control](docs/images/manual-ops-control.png). Builder confirmed both files exist.
No additional manual checks are inferred from this report, including host-data hashes,
exact metric reconciliation, actual test-container mounts, or graceful shutdown.

Builder follow-up verification is recorded separately in
[Builder evidence](docs/builder-verification.md). Independent Tester review and final
submission remain pending. The training exit 137 must be carried into that review.
The persistence result is explicitly student-confirmed, not a new Builder verification.

Transcript headers are now supplied: Zhuotong Xie, NetID `zx180`, Option 1, Codex,
Repository B URL https://github.com/1175882849x-coder/DashBite-Repository-B.
Save the complete role conversations as `docs/transcripts/zx180_architect.txt`,
`zx180_builder.txt`, and `zx180_tester.txt`, using the provided headers and `[STUDENT]` /
`[AGENT]` speaker labels. Upload those same files separately to Canvas. Both Architect and Builder files now exist.
Tester found mixed-case labels in the Builder file and a message-count mismatch with the
historical export inventory. Completeness is unverified; compare with the original visible
conversations and use exactly `[STUDENT]` / `[AGENT]`. See `docs/tester-verification.md`.

For the local suite use `.venv/Scripts/python -X utf8 -m pytest` on Windows (Unix:
`.venv/bin/python -X utf8 -m pytest`). The original local background shortcuts use POSIX
utilities and require Git Bash on Windows; the new container targets also work with
Windows Make/PowerShell. The existing UTF-8 Makefile setting is retained. Direct Windows
Python without UTF-8 mode can fail two inherited source-inspection tests under GBK.

### Reflection and limitations

Accepted AI recommendation: a dashboard-only endpoint health check with explicit limits.
Changed recommendation after student review: one opt-in Compose profile instead of a separate
test-only Compose file. This simplifies commands, but requires an independent test service
and inspection of resolved configuration and actual mounts.

Dependencies retain inherited `>=` constraints and `python:3.12-slim` floats. Commands and
disposable environments are repeatable; future rebuilds are not guaranteed to resolve the
same packages or image. Tested versions/image IDs are recorded in Builder evidence and
`docs/*-dependencies.txt`. Locking and digest pinning remain optional follow-ups.
File writers/readers can race; the brief Builder run is not a concurrency guarantee.
No DATA_ROOT override, restart policy, scaling, Kubernetes, cloud deployment or model redesign
was added. `docs/docker-k8s-guide.md` is inherited conceptual guidance; its DATA_ROOT and
Kubernetes examples are not implemented commands for this submission.


### Troubleshooting the two student-discovered issues

**Healthy container but host browser cannot connect:** the student reported an IPv6-only
Compose network while Streamlit listened on IPv4 (`0.0.0.0`). The default network now sets
`enable_ipv4: true` and `enable_ipv6: false`. Existing networks must be recreated for that
change to apply. Preserve the data volume by using `down` without `-v`, then `up` with the
same project and override files. For the student's port-8502 setup:

```powershell
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml down
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml up -d simulator preprocess train infer dashboard
docker network inspect dashbite-b-smoke_default --format '{{.EnableIPv4}} {{.EnableIPv6}}'
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml port dashboard 8501
```

Expect `true false` and `127.0.0.1:8502`. Internal health probes cannot prove host port access.

**Browser shows `ModuleNotFoundError: No module named 'pipeline'`:** the base image now sets
`PYTHONPATH=/app`, inherited by runtime and test targets. This exposes the package root when
Streamlit executes the script under `pipeline/dashboard/`. Rebuild both images and recreate
the runtime containers after changing Dockerfile; a healthy endpoint alone does not run the
page's imports. The two page-rendering tests exercise the real dashboard with fixed temporary
data and disable only timed auto-refresh. The runtime regression below also executes the real
script from `/tmp`, then clears `PYTHONPATH` to confirm it detects the original import failure.

```powershell
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml build simulator preprocess train infer dashboard
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml up -d --force-recreate simulator preprocess train infer dashboard
docker compose -p dashbite-b-tests --profile test build tests
docker compose -p dashbite-b-tests --profile test run --rm --no-deps tests
python scripts/verify_container_runtime.py
```

The last command uses the host Python standard library and Docker, a uniquely named disposable
project, an automatically allocated loopback port, and its own empty volume. It starts only the
dashboard and checks actual network flags/address, host HTTP 200 and package imports. It removes
only its own temporary project/volume afterward. It does not mount or start the student's data.
Expected: three `PASS` lines and cleanup. Keep any exit-137 diagnosis separate: capture container
state (`ExitCode`, `OOMKilled`, `Error`) and logs before `down` removes containers; the reported
137 alone does not establish its cause or prove a graceful stop.

### Independent Tester review (2026-10-01)

See [Tester findings and exact verification](docs/tester-verification.md). Final suites: 44
passed locally and twice in fresh containers, six Altair warnings each. The probe now rejects
redirects; two added rendering cases cover empty startup data. The isolated stop reproduced
137 with SIGTERM then SIGKILL and OOMKilled=false; this is forced termination, not graceful
shutdown. The original student stop cannot be retrospectively diagnosed from its exit code.
No signal-handling redesign was made. The requested health and browser recheck is now
student-reported passed, as recorded below. Persistent student data and original transcripts
were preserved.

### Student-reported post-fix manual recheck (2026-10-01)

The student reported successfully rebuilding the runtime image, starting all five services
with the existing `work/port.yaml` override, confirming a healthy dashboard mapped to host
port **8502**, and personally opening **Model Pulse** and **Ops Control**; both displayed
normally without errors. These are student-reported manual observations, not new independent
Tester execution. The requested post-fix manual recheck is recorded as student-reported passed.

No new test-suite run, persistence/isolation comparison, shutdown check, exact metric
reconciliation or screenshot capture is claimed from this report. Existing independent
verification results and all other pending checks/limitations remain unchanged. In particular,
graceful shutdown is not established, and Architect/Builder transcript review remains pending.
