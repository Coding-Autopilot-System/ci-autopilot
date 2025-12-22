# Control Plane

## Overview
CI Autopilot uses GitHub Issues as a control plane. Failures are captured as issues, then queued for remediation by the runner.

## Intake pipeline
1) Workflow run fails
2) `autopilot-failure-intake.yml` creates a queued issue
3) The runner processes queued issues and posts status updates

## Issue labels
- `queued` - waiting to be processed
- `autofix` - eligible for automated remediation
- `in-progress` - being processed by the runner
- `done` - resolved or superseded

## Guardrails
- No direct merges; all fixes go through PRs
- CI must pass before any automated change is accepted
- Human approval required for risky changes
