# 20260610_ci-autopilot_boundary-readme

Issue Description: README overlapped with neighboring repos and undersold the worker/runtime role.
State: It was not explicit enough that this repo is the runner-side execution path.
Action: Added repo boundary language, enterprise proof points, and a short runbook path in `README.md`.
Result: The repo now reads as the worker/runtime implementation instead of a generic platform overview.
Diff Patch: Updated `README.md` only.
Rationale: Portfolio readers need a fast distinction between governance/control plane and runner-hosted execution.
