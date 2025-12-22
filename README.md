# ci-autopilot
This repo will store the bundle we built (modes, issue control-plane, hygiene workflows, env configs, wrappers, scripts).

## How to run locally
```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m agent.poll_once
```

## How to trigger workflow
```pwsh
gh workflow list
gh workflow run "CI Autopilot Fixer"
gh api repos/Coding-Autopilot-System/ci-autopilot/dispatches -f event_type=ci-autopilot
```
