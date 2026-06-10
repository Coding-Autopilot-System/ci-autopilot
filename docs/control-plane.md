# Control Plane

## Overview
CI Autopilot uses GitHub Issues as a control plane. Failures are captured as issues, then queued for remediation by the runner.

## Intake pipeline
1) Workflow run fails
2) `autopilot-failure-intake.yml` creates a queued issue
3) The runner inventories queued issues for operator visibility

## Issue labels
- `queued` - waiting to be processed
- `autofix` - eligible for automated remediation
- `in-progress` - being processed by the runner
- `done` - resolved or superseded

## Guardrails
- No direct merges; all fixes go through PRs
- CI must pass before any automated change is accepted
- Human approval required for risky changes

## Current worker contract
The worker is read-only. It does not claim issues, execute issue content, dispatch Codex, write branches, or open pull requests. Those capabilities require a separately reviewed trust policy and guarded dispatcher.
