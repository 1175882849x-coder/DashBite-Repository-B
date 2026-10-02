# Student manual smoke test — repeatable procedure and reported observations

The student reported executing the smoke test on port 8502 with a reused volume; see the
README observation table. On 2026-10-01, the student confirmed that the persistence snapshot
comparison produced no output and the snapshots before/after recreation were identical.
Training exited with code 137 (Tester review required). The commands below
are a repeatable procedure, not claims that every listed check was performed. Use PowerShell from Repository B:

```powershell
Set-Location 'C:\Users\11758\OneDrive\Desktop\ids_706\DashBite-Repository-B'
New-Item -ItemType Directory -Force work, docs/images | Out-Null
```

Builder left the stopped `dashbite-b-smoke_dashbite-data` volume with verification artifacts.
For a genuinely fresh student smoke volume, this **optional destructive reset deletes only
that disposable project's data**. Do not run against a classroom or normal runtime project:

```powershell
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml down -v
```

The reported run retained existing artifacts, including earlier Builder data. The default
Compose port remains 8501. The student used this local ignored `work/port.yaml` override
for host port 8502 (already present; preserve it):

```yaml
services:
  dashboard:
    ports: !override
      - "127.0.0.1:8502:8501"
```

Every runtime command below includes both files and uses host port 8502. The internal
Streamlit/health port stays 8501. To use the default port 8501 instead, omit both `-f` options
and browse 8501. Do not apply the port override to the independent test service.

## 1. Build, start and inspect

```powershell
# Make equivalent for this override:
# make "COMPOSE=docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml" container-build container-up
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml config
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml build simulator preprocess train infer dashboard
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml up -d simulator preprocess train infer dashboard
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml ps -a
docker inspect dashbite-b-smoke-dashboard-1 --format '{{json .State.Health}}'
```

Expect five running services and dashboard `healthy` with probe `ExitCode: 0`. Allow up to
2 minutes for startup; poll status, and inspect logs if unhealthy or exited. Start a separate
2-minute output deadline once services are running. Repeat this command until populated:

```powershell
# Make equivalent for this override:
# make "COMPOSE=docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml" container-inspect container-logs
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml exec -T dashboard python -m pipeline.inspect_data --validate
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml logs --tail=100 simulator preprocess train infer dashboard
```

Expect raw `orders_*.csv`, features plus `.done_*` markers, loadable checkpoints,
metrics JSON, train state, populated predictions and `quality/batch_quality.csv`.
Validation prints `PASS: pipeline artifact contracts` and sample/score/throughput metrics;
exit status is 0. It verifies valid probabilities, binary labels, checkpoint references,
quality accounting and prediction IDs belonging to features. It permits pending features
while inference catches up. On failure record the error and logs, not a successful check.
At 50 new labeled rows per checkpoint, corrupted batches can delay the first model.

Wait another 10–20 seconds and repeat inspection. Expect advancing batches, samples and
prediction count, with `rows_in = rows_out + rows_dropped`. Inspect logs for tracebacks,
partial-file errors or stalled stages. Record actual counts/checkpoint IDs and times.

## 2. Inspect the browser personally

Open http://127.0.0.1:8502. Confirm both sidebar views load:

- Model Pulse: sample volume, batch count, rows in/out, drop rate, mean probability,
  field failures, throughput and score distribution.
- Ops Control: late rate, at-risk order value, rows kept and recent prediction rows.

Use the inspection command's matching metrics to reconcile values; ongoing writers may
advance between observations. For exact reconciliation, stop simulator/preprocess/train/infer,
leave dashboard running, then inspect and refresh. Resume with the explicit five-service
`up -d` command. Save actual screenshots under `docs/images/` and observations in README.
Endpoint health alone does not prove these pages render.

## 3. Stop training while inference continues

After a checkpoint exists:

```powershell
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml stop train
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml exec -T dashboard python -c "from pipeline.infer import newest_checkpoint,load_existing_predictions; p=load_existing_predictions(); print(newest_checkpoint().name, len(p)); print(p.tail(5).to_string(index=False))"
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml ps -a
```

Before removing the stopped container, also record its exit details:

```powershell
docker inspect dashbite-b-smoke-train-1 --format '{{json .State}}'
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml logs --tail=100 train
```

The reported run showed exit 137. Do not label it graceful or infer its cause from the exit
code alone; carry state/logs to Tester review. Record the checkpoint name and prediction count. Wait 10–20 seconds and repeat the Python
command and `ps -a`. Expect a larger count and new prediction rows referencing that same
checkpoint ID; train remains exited/stopped while simulator, preprocess and infer run.

```powershell
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml start train
```

## 4. Isolation and persistence with writers stopped

Build the independent test image first, then stop runtime writers. Stop any separately
launched local Python pipeline before comparing host `data/`.

```powershell
docker compose -p dashbite-b-tests --profile test build tests
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml stop simulator preprocess train infer
docker volume inspect dashbite-b-smoke_dashbite-data --format '{{.Name}}'
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml exec -T dashboard python -m pipeline.inspect_data --snapshot | Set-Content -Encoding utf8 work/smoke-before.json
Get-ChildItem data -Recurse -File -Force | Get-FileHash -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json | Set-Content -Encoding utf8 work/host-before.json
# Make equivalent: make container-test (includes build)
docker compose -p dashbite-b-tests --profile test run --rm --no-deps tests
$LASTEXITCODE
```

Expect the current suite to report `44 passed` and exit 0. The student reported 39 passed
before the two new rendering regression cases were added. To inspect actual mounts, use a retained one-off container:

```powershell
docker compose -p dashbite-b-tests --profile test run --name dashbite-b-student-test-inspect --no-deps tests python -m pytest -q
docker inspect dashbite-b-student-test-inspect --format '{{json .Mounts}}'
docker rm dashbite-b-student-test-inspect
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml exec -T dashboard python -m pipeline.inspect_data --snapshot | Set-Content -Encoding utf8 work/smoke-after-tests.json
Get-ChildItem data -Recurse -File -Force | Get-FileHash -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json | Set-Content -Encoding utf8 work/host-after.json
Compare-Object (Get-Content work/smoke-before.json) (Get-Content work/smoke-after-tests.json)
Compare-Object (Get-Content work/host-before.json) (Get-Content work/host-after.json)
```

Expect mounts `[]` and no comparison output. Hashes cover all volume files including CSV,
JSON, joblib and hidden markers. Writers must remain stopped throughout the comparison.

Recreate without deleting data, before resuming writers:

```powershell
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml down
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml create simulator preprocess train infer dashboard
docker volume inspect dashbite-b-smoke_dashbite-data --format '{{.Name}}'
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml run --rm --no-deps dashboard python -m pipeline.inspect_data --snapshot | Set-Content -Encoding utf8 work/smoke-after-recreate.json
Compare-Object (Get-Content work/smoke-before.json) (Get-Content work/smoke-after-recreate.json)
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml up -d simulator preprocess train infer dashboard
```

Expect the same volume name, no hash differences, then resumed growth when inspection is
repeated after 10–20 seconds. Save screenshots/evidence. `create` does not start writers;
the temporary dashboard command only reads the runtime volume and prints hashes.

## 5. Shutdown and recording

```powershell
# Make equivalent for this override:
# make "COMPOSE=docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml" container-down
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml down
docker compose -p dashbite-b-tests --profile test down
docker compose -p dashbite-b-smoke -f compose.yaml -f work/port.yaml ps -a
docker volume inspect dashbite-b-smoke_dashbite-data --format '{{.Name}}'
```

Expect no remaining smoke service containers; the volume still exists. Do not add `-v` to
ordinary shutdown. Only use the separately labeled destructive reset at the start if you
choose to discard disposable smoke artifacts. Record your actual pass/fail observations,
commands, screenshots and limitations in README before starting the separate Tester chat.


## Current report boundaries

Student-reported: both views rendered; screenshots exist at `images/manual-model-pulse.png`
and `images/manual-ops-control.png`; predictions rose 12,672 -> 13,102 while training stopped,
using checkpoint `20261001_223646`; test result 39 passed/exit 0 after fixes; stopped-writer
application-volume snapshots before/after tests identical; recreation retained the volume and
was followed by resumed growth. The volume contained previous Builder verification output.
The student explicitly confirmed on 2026-10-01 that the snapshot comparison across recreation
produced no output and the before/after snapshots were identical. This is a student-confirmed
result, not an additional Builder execution.
No host-data comparison, exact browser-to-artifact reconciliation or graceful shutdown is
claimed from those observations. Builder's additional automated checks are recorded separately.

## Tester follow-up (2026-10-01)

Tester reproduced a forced stop: SIGTERM followed by SIGKILL, exit 137, OOMKilled=false.
This diagnoses the isolated reproduction, not the removed original student container.
Shutdown removes containers and preserves the volume; it does not promise graceful worker
termination. Avoid stopping during writes when possible; inspect artifacts after restart.
The strict health probe now rejects redirects. The requested post-fix rebuild/startup, health
and both browser-view recheck has now been reported passed by the student, as recorded below.
The independent verified suite count remains 44; no new student test run is inferred.
Do not reset or delete your existing smoke volume. See tester-verification.md for evidence.

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
