# Repository B Plan: DashBite Containerization Improvements

## 1. Goal

Complete Assignment Option 1 by extending the working classroom DashBite application with verifiable container-readiness improvements.

DashBite simulates food-delivery orders, preprocesses records, trains a late-delivery prediction model, produces predictions, and displays results in a Streamlit dashboard.

The project will preserve this workflow while improving service observability, containerized testing, and documentation.

## 2. Baseline and Repository Setup

Use the working local project as the implementation baseline:

`C:\Users\11758\OneDrive\Desktop\ids_706\TestingAndContainerizationDemo`

Before implementation:

- Inspect the current code and run the existing test suite.
- Preserve the uncommitted Makefile and README changes.
- Establish a separate student-owned Repository B.
- Record the classroom source repository and baseline commit.
- Retain applicable attribution and license notices.
- Do not modify or push to the classroom repository.
- Exclude local virtual environments, secrets, caches, and generated runtime data from the new repository.

Existing functionality includes a Dockerfile, Docker Compose with five services, persistent shared storage, and unit, regression, and integration tests. These are inherited features, not new student contributions.

If `docs/plan.md` already exists, append this project section without deleting earlier planning history.

## 3. Proposed Improvements

### A. Dashboard Health Check

Add a health check to the dashboard service.

- Verify the appropriate Streamlit health endpoint for the installed version.
- Use a probe available inside the image, preferably Python's standard library.
- Configure a startup allowance, timeout, interval, and retry count.
- Document how to inspect health status.
- Explain that dashboard health does not prove the entire pipeline is producing correct results.

### B. Isolated Containerized Testing

Provide a documented command for running the complete test suite inside a container.

- Include tests, fixtures, and pytest configuration in a dedicated test build target.
- Keep application services on the runtime build target.
- Add a test service under an opt-in Compose profile.
- Do not mount the application's persistent data volume into the test service.
- Use temporary test directories.
- Preserve pytest's exit status so failures remain visible.

### C. Consistent Commands and Documentation

Following the classroom workflow, add Makefile targets for:

- Building images.
- Starting the application.
- Inspecting service status and logs.
- Running containerized tests.
- Inspecting pipeline output.
- Stopping services while preserving data.

Document the equivalent Docker Compose commands for environments without Make.

Replace outdated README statements such as “No containers.” Explain which features were inherited and which improvements were added.

## 4. Architecture and Boundaries

Preserve the existing five-service architecture:

Simulator → raw data → preprocessing → features → training/model checkpoints → inference/predictions → dashboard.

Training and inference remain independent processes. Inference must be able to use an existing checkpoint while training is stopped.

Keep the existing shared named volume for application data. Test execution must remain isolated from it.

Run one instance of each service. Kubernetes, cloud deployment, model redesign, and concurrent scaling are outside this project's scope.

Preserve the local dashboard's existing functionality rather than replacing it with a different classroom version.

## 5. Important Files

- `Dockerfile`: runtime and test build targets.
- `.dockerignore`: exclude unnecessary files while allowing required test inputs.
- `compose.yaml`: dashboard health check and isolated test service.
- `Makefile`: convenient build, run, test, inspect, and stop commands.
- `tests/`: meaningful verification for new behavior.
- `README.md`: setup, usage, evidence, limitations, and reflection.
- `docs/plan.md`: agreed implementation and verification plan.
- `docs/transcripts/`: complete role conversations.
- `docs/images/`: screenshots of actual execution.

## 6. Automated Verification

The Builder should:

1. Record the baseline test result.
2. Preserve existing unit, regression, and integration tests.
3. Add focused checks for health-probe behavior and test-service isolation where practical.
4. Validate the resolved Compose configuration.
5. Run the full suite locally and in the test container.
6. Confirm failed containerized tests produce a nonzero exit status.
7. Verify test execution does not create or modify application runtime artifacts.

Tests should check behavior, not merely search configuration files for expected strings.

## 7. Manual Smoke Test

The student must perform this after Builder completion and before the Tester conversation.

The Builder must provide exact, runnable Makefile and Compose commands for the final implementation.

### What to demonstrate

1. Build and start all five application services.
2. Confirm the dashboard becomes healthy.
3. Open the dashboard and verify its main views load.
4. Inspect real pipeline artifacts:
   - Raw order batches.
   - Preprocessed feature files.
   - Model checkpoints and metrics.
   - Prediction files with populated rows.
   - Data-quality logs.
5. After a checkpoint exists, stop training and verify inference produces predictions for new orders using that checkpoint.
6. Stop and recreate the application containers without deleting the named volume. Confirm previously recorded artifacts remain.
7. Run containerized tests separately and verify application data is unaffected.
8. Stop the application cleanly.

Save screenshots and record actual observations in the README. Do not describe planned checks as completed checks.

## 8. Risks and Design Decisions

- File-based stages can take time to produce their first outputs. Use bounded waiting and logs for diagnosis.
- Dashboard health is narrower than end-to-end pipeline health.
- Tests must not inherit the application's writable data volume.
- Ordinary shutdown must preserve stored data; destructive cleanup should be a separate, clearly documented action.
- Docker Hub connectivity has previously failed on the home Ethernet connection. Record network-related failures separately from application defects.
- Verify Windows/Git Bash commands instead of assuming Unix shell scripts work unchanged.

## 9. AI Workflow and Submission

- Architect: inspect, propose, discuss tradeoffs, and finalize this plan after student review.
- Builder: implement the agreed plan and explain important decisions.
- Student: perform and document the manual smoke test.
- Tester: independently compare the implementation with the plan, check edge cases, and verify instructions.
- Fix important findings and rerun relevant checks.

The README must explain at least one AI recommendation accepted and one changed or rejected, based on actual decisions.

Preserve complete visible conversations as:

- `<NetID>_architect.txt`
- `<NetID>_builder.txt`
- `<NetID>_tester.txt`

Use the assignment's required headers and speaker labels. Commit them under `docs/transcripts/` and upload the same three files separately to Canvas.

## 10. Completion Criteria

The project is complete when:

- The separate Repository B identifies its classroom source and original improvements.
- The application builds and produces meaningful outputs in containers.
- The dashboard health check works and its limitations are documented.
- Containerized tests pass without affecting persistent application data.
- The student has completed the manual smoke test.
- Tester findings have been addressed.
- The README, finalized plan, screenshots, and three transcripts are present.
## 11. Architect Finalization and Acceptance Details (2026-10-01)

This plan incorporates the student's reviewed scope. No application changes were made during Architect setup.

### Provenance and local Repository B

- Classroom source: https://github.com/ammylin/TestingAndContainerizationDemo.git
- Baseline commit: 3f51661f08e7b4c98137e94b09e7711f3c3f7e0b (Added Docker).
- Separate local Repository B: C:\Users\11758\OneDrive\Desktop\ids_706\DashBite-Repository-B.
- Repository B retains baseline Git history. Its inherited origin has been removed; no student remote has been configured and nothing has been pushed.
- Existing Makefile and README working changes have been copied exactly into Repository B and remain uncommitted. Record these separately from new implementation contributions; confirm authorship before claiming them as original work.
- Do not commit virtual environments, runtime data, secrets, or caches. Retain any applicable source attribution and license notices; inspection did not identify a license file, so do not invent one.
- The classroom checkout must retain the same HEAD, remotes, and Makefile/README diff after this setup.

### Reviewed choices and scope

The student-selected opt-in test profile replaces the Architect's initial recommendation for a separate test-only Compose file. This keeps commands in one configuration, but introduces a risk of inheriting runtime settings. The test service must be defined independently of the x-dashbite anchor: no dashbite-data mount, no host data bind mount, no depends_on, no published ports, and no shared runtime image tag. Resolve and inspect Compose configuration and actual container mounts to verify this boundary.

Application services explicitly select the runtime Dockerfile target. The test service explicitly selects the test target and uses a distinct student test image tag. Use a student-specific runtime image tag as well, avoiding classroom dashbite:demo collisions. Allow tests and fixtures through .dockerignore while keeping them out of runtime images through explicit COPY instructions.

Dependency locking and base-image digest pinning are optional follow-ups, not required implementation scope. The mandatory workflow provides repeatable commands and disposable environments, not fully frozen dependency resolution. Existing >= requirements and the floating Python image tag can change future rebuild results. Record Python, Docker, Compose, installed dependency versions and tested image IDs; describe this limitation rather than claiming bit-for-bit reproducibility. If strict dependency reproducibility is required by the rubric, review and add locking before Builder implementation.

No DATA_ROOT override, Kubernetes deployment, scaling, automatic restart policy, model redesign, or application UI replacement is planned. Existing base arguments support temporary test workspaces. Clarify the README's outdated 'No containers' statement and mark the older Docker guide's unimplemented DATA_ROOT and Kubernetes content as conceptual guidance.

### Health-check contract

Use the installed Streamlit version's /_stcore/health endpoint at http://127.0.0.1:8501. Require HTTP 200 and a zero exit code; connection errors, non-200 responses and request timeout must produce a nonzero exit. Prefer Python urllib.request with a three-second request timeout. Initial Compose settings: interval 10s, timeout 5s, start_period 30s, retries 3. Tune only from observed startup behavior.

Apply the check only to dashboard in Compose, not globally to the shared Dockerfile. Healthy establishes endpoint responsiveness only. It does not establish successful page rendering, correct/fresh data, model quality, pipeline progress, or upstream service health. Docker health status alone does not restart unhealthy containers.

Where practical, exercise the actual probe against a controlled HTTP server for success, non-200 and connection-failure behavior. Verify live Docker health status and failure reporting in a disposable environment. Avoid tests that only search YAML for strings.

### Test commands and isolation evidence

Builder must provide final runnable equivalents of:

    docker compose -p dashbite-b-tests --profile test config
    docker compose -p dashbite-b-tests --profile test build tests
    docker compose -p dashbite-b-tests --profile test run --rm --no-deps tests

The service is provisionally named tests. Its command is python -m pytest, preserving pytest's exit status. Normal application startup must name the five runtime services explicitly; enabling the test profile must not be part of the normal startup shortcut. Test shortcuts must never invoke up for the whole stack. A profile alone does not guarantee isolation.

Run baseline tests in Repository B before implementation, preserving the classroom checkout. Record results without representing inspection as test execution. Retain the existing full suite and add one meaningful integration test covering raw input -> preprocessing -> training -> inference -> dashboard loaders/metric helpers, entirely under tmp_path. Use fixed fixture IDs/timestamps and both label classes rather than the nondeterministic live simulator.

Assert nonempty valid features and derived columns; quality rows_in = rows_out + rows_dropped; loadable checkpoint and valid training metrics/state; expected prediction ID coverage without duplicates; finite probabilities in [0, 1]; binary labels and correct checkpoint references; expected dashboard helper values; and no duplicate work on a second preprocessing/inference call without new input.

Run the full container suite twice in fresh containers. In a disposable verification copy, introduce a deliberately failing test and confirm a nonzero command exit status. Remove the deliberate failure before final validation. Inspect actual test container mounts and confirm absence of runtime-volume access.

For unchanged-data evidence, stop runtime writers and capture a file inventory plus content hashes of the named runtime volume before and after containerized tests. Include generated CSV, JSON, joblib and marker files. Compare host data separately if present. Running pipeline writers would invalidate an unchanged-hash comparison. Mounts and independent project names provide the primary isolation boundary; hashes provide supporting evidence.

### Runtime verification and student smoke procedure

Use explicit project names: dashbite-b for normal runtime and dashbite-b-smoke for disposable smoke testing. Verify the named data volume remains project-scoped, without an external or fixed global volume name. Do not share the classroom runtime volume. Account for an occupied dashboard port without stopping unrelated services.

Validate resolved Compose configuration, build both targets, inspect image contents, then start all five smoke services on a fresh smoke volume. Use an initial two-minute deadline for raw CSVs, nonempty features, quality records, a loadable checkpoint, metrics JSON and populated predictions. Startup and output deadlines are separate. Diagnose deadline failures with logs and training thresholds; do not accept mere container startup as success.

Check feature/prediction ID correspondence, probability ranges, checkpoint references and quality accounting. Observe a second interval to show advancing batches, throughput and predictions. In the browser, inspect Model Pulse and Ops Control and reconcile displayed metrics with actual artifacts. Review logs for tracebacks, repeated partial-file reads or stalled stages.

After a checkpoint exists, stop only train; record the checkpoint ID, allow new raw/features to arrive, and verify new predictions reference that existing checkpoint while train remains stopped. Restart train afterward if needed.

Stop and recreate smoke containers without deleting the volume. Record named-volume identity and artifact hashes across recreation before allowing writers to resume; verify retained artifacts and resumed progress. Ordinary shutdown uses down without -v. Any volume deletion must be a separately documented action targeting only the explicitly named disposable smoke project.

A supplementary demonstration may stop simulator and show dashboard remains healthy while throughput ceases, making the health limitation concrete. Keep one instance of each service. Direct file writes and concurrent readers can race even at one replica; record any observed issue. Atomic-write redesign requires a separate scope decision if a defect blocks acceptance.

### Evidence and handoff

Builder implements the finalized plan and supplies exact commands. Student performs the manual smoke test before the separate Tester conversation. Tester independently verifies plan compliance, negative cases, data isolation and documentation, and records findings. Resolve important findings and rerun affected verification.

README evidence must distinguish inspected, passed, failed, blocked and not-run checks. Capture actual screenshots under docs/images. Do not fabricate screenshots or completed observations. Network failures, including the student-reported prior Docker Hub connectivity problem, must be recorded separately from application defects.

The accepted recommendation is a dashboard-only endpoint check with explicit limitations. The changed recommendation is using an opt-in profile rather than a standalone test Compose file; explain its convenience and the required independent service definition. Base the final reflection on actual implementation decisions.

The student must export complete visible Architect, Builder and Tester conversations with the actual NetID and assignment-required headers/speaker labels, save them under docs/transcripts, and upload the same files separately to Canvas. NetID and required transcript header format remain to be supplied; do not fabricate them or substitute a summary for a transcript.

Inspection evidence as of Architect finalization: baseline Compose validates; Docker 29.7.2 and Compose v5.4.0 are installed; Docker reports a Linux engine. No image builds, pytest runs, service startups or smoke tests were performed by Architect.

References:
- https://docs.streamlit.io/deploy/tutorials/docker
- https://docs.docker.com/reference/compose-file/services/#healthcheck
- https://docs.docker.com/reference/cli/docker/compose/run/