# ci-autopilot

Enterprise-grade CI automation and operational control plane for Codex-driven workflows.

## Quick start (local)
```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m agent.poll_once
```

## Documentation
- `docs/README.md` - Documentation index
- `docs/architecture.md` - System architecture and design goals
- `docs/runner-setup.md` - Runner registration and service setup
- `docs/operations.md` - Day-2 operations runbook
- `docs/security.md` - Security posture and access model
- `docs/troubleshooting.md` - Common issues and remediation
- `docs/site/index.html` - Professional docs landing page

## Workflow triggers
```pwsh
gh workflow list
gh workflow run "CI Autopilot Fixer"
gh api repos/Coding-Autopilot-System/ci-autopilot/dispatches -f event_type=ci-autopilot
```
