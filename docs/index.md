# CI Autopilot

Welcome to the **CI Autopilot** documentation!

`ci-autopilot` packages the worker/runtime side of the Coding Autopilot System platform. It monitors GitHub Actions workflows, detects failures, and exposes them through an issue queue. 

The current Python worker is deliberately read-only: it inventories queued issues on a self-hosted runner. Autonomous repair dispatch and queue state transitions are part of the future vision for guarded repair pipelines.

## Purpose

CI Autopilot bridges the gap between CI pipeline failures and AI-assisted remediation. By translating GitHub Action `workflow_run` failures into tracked, labeled issues, it provides:
- **Operator Visibility:** A clear queue of failing workflows ready for human or AI inspection.
- **Auditability:** Explicit tracking of failure states and resolution attempts.
- **Security Boundary:** A deliberate separation between issue governance (Control Plane) and remediation execution (Worker).

## Repository Boundary

Within the broader ecosystem:
- [**autopilot-core**](https://github.com/Coding-Autopilot-System/autopilot-core): The control plane for org-level scheduling, rollout, and PR governance.
- **ci-autopilot (this repo)**: The worker/runtime implementation for runner execution and read-only queue polling.
- [**autopilot-demo**](https://github.com/Coding-Autopilot-System/autopilot-demo): The demonstration target used to show the runtime and control plane working together.

## Getting Started

Check out the [Architecture Overview](architecture.md) to understand how the components interact, or head over to the [Setup Guide](runner-setup.md) to get the runner running on your own infrastructure.

### Quick Links
- [Architecture](architecture.md)
- [Runner Setup](runner-setup.md)
- [Operations & Runbook](operations.md)
- [Troubleshooting](troubleshooting.md)
- [Security Posture](security.md)
