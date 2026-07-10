# Runner health target variable

Issue Description: Runner Health Monitor created alerts for its GitHub-hosted monitor instead of the intended self-hosted runner.
State: The workflow defined `RUNNER_NAME`, which GitHub Actions reserves for the executing runner and overwrote at runtime.
Action: Renamed the target variable to `MONITORED_RUNNER_NAME` and added a regression test for the workflow contract.
Result: Health checks now query and report the configured self-hosted runner name.
Diff Patch: Updated `.github/workflows/runner-health.yml` and added `tests/test_runner_health_workflow.py`.
Rationale: Workflow environment variables must not collide with GitHub Actions built-ins.
