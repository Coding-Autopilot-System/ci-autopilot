# Architecture

## Overview
CI Autopilot is a runner-hosted automation layer that coordinates Codex-driven workflows, issue triage, and safe remediation.

## Core components
- Runner host: Windows service running GitHub Actions self-hosted runner
- Workflow layer: GitHub Actions workflows that trigger repair or hygiene pipelines
- Agent runtime: Python agent that executes tasks and reports status
- Control plane: Repository configuration and issue workflow conventions
- Logs and artifacts: Local logs and GitHub Action run outputs

## Data flow (high level)
1) Event triggers a workflow (dispatch, schedule, or issue activity)
2) Workflow schedules a job to the self-hosted runner
3) Runner executes the agent or scripts in a controlled workspace
4) Artifacts and logs are uploaded for audit and review

## Design goals
- Deterministic execution on a dedicated host
- Clear separation between orchestration (GitHub Actions) and execution (agent)
- Safe automation with explicit controls and audit trails
- Straightforward runbooks for operations and recovery

## Observability
- GitHub Actions job logs are the primary source of truth
- Local logs are stored under `logs/` for host-level troubleshooting
