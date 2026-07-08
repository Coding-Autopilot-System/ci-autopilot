# ci-autopilot Wiki

`ci-autopilot` is the **worker/runtime** side of the CAS autonomous CI-repair platform. It
monitors GitHub Actions workflows, detects failures, and exposes them through an issue queue via
a self-hosted-runner-hosted Python agent. The current agent is deliberately read-only: it
inventories queued issues; autonomous repair dispatch and queue state transitions are not
implemented yet.

## Role in the CAS portfolio

| Repo | Role |
|---|---|
| [autopilot-core](https://github.com/Coding-Autopilot-System/autopilot-core) | Control plane for org-level scheduling, rollout, and PR governance |
| **ci-autopilot** (this repo) | Worker/runtime implementation for runner execution and read-only queue polling |
| [autopilot-demo](https://github.com/Coding-Autopilot-System/autopilot-demo) | Demonstration target used to show the runtime and control plane working together |

## Quickstart

```pwsh
# Prerequisites: Python 3.12 and authenticated GitHub CLI
$env:GH_TOKEN = gh auth token
python -m agent.poll_once
```

The worker only reads and lists queued issues. It does not execute issue content, mutate
repositories, or dispatch Codex.

## Where to go next

- [Architecture](Architecture.md) — the self-hosted runner + fixer/poll loop
- [Operations](Operations.md) — verified run/test/CI commands
- [Decisions](Decisions.md) — index of recorded architectural decisions and the 2026-06-10 audit

<!-- docs-verified: 4590462b38e0a835385c3a7c4a4b35d761bed5dc 2026-07-08 -->
