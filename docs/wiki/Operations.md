# Operations

## CI gate (`.github/workflows/ci.yml`)

CI runs on `ubuntu-latest` for every push/PR to `main`:

```bash
python -m py_compile agent/poll_once.py
python -c "import agent.poll_once"
python -m unittest discover -v
```

There is no `--cov-fail-under` or branch-coverage percentage gate configured in `ci.yml` as of
this writing — the CI gate is syntax check, import check, and unit-test pass/fail, not a
coverage threshold.

## Local run

```pwsh
# Prerequisites: Python 3.12 and authenticated GitHub CLI
$env:GH_TOKEN = gh auth token
python -m agent.poll_once
```

## Runner service control

```pwsh
cd C:\actions-runner
$serviceName = Get-Content .\.service
Get-Service -Name $serviceName
Start-Service -Name $serviceName
Stop-Service -Name $serviceName
Restart-Service -Name $serviceName
```

## Runner health

- `Runner Health Monitor` runs every 15 minutes on GitHub-hosted runners; if the self-hosted
  runner is offline it opens or updates an issue labeled `runner-offline`, and sends an email
  alert if `SMTP_*`/`EMAIL_*` secrets are configured.
- If the health monitor cannot list runners with the default `GITHUB_TOKEN`, add a repo secret
  `RUNNER_PAT` with `repo` and `workflow` scopes (plus `read:org` for org repos).

## Other CI workflows

| Workflow | Purpose |
|---|---|
| `autopilot-failure-intake.yml` | Intake on `workflow_run` failure |
| `autopilot-create-issue.yml` | Issue creation via `actions/github-script` |
| `fixer.yml` | Runs the read-only queue-inventory agent on the self-hosted runner |
| `runner-smoke-test.yml` | On-demand runner smoke test |
| `runner-health.yml` | Scheduled + on-demand runner health check |
| `codeql.yml` | CodeQL static analysis |
| `pr-lint.yml` | PR metadata/title linting |
| `stale.yml` | Stale issue/PR sweep |
| `pages.yml` | Publishes docs to GitHub Pages |

## Runbook path

1. [docs/control-plane.md](../control-plane.md) — issue-queue contract with `autopilot-core`.
2. [docs/runner-setup.md](../runner-setup.md) — provision the worker host.
3. [docs/operations.md](../operations.md) and [docs/troubleshooting.md](../troubleshooting.md) —
   day-2 support.

<!-- docs-verified: 4590462b38e0a835385c3a7c4a4b35d761bed5dc 2026-07-08 -->
