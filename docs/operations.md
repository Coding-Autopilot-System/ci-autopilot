# Operations

## Service control
```pwsh
cd C:\actions-runner
$serviceName = Get-Content .\.service
Get-Service -Name $serviceName
Start-Service -Name $serviceName
Stop-Service -Name $serviceName
Restart-Service -Name $serviceName
```

## Upgrade runner binaries
1) Stop the service
2) Unzip the new runner package into the same folder
3) Start the service

## Re-register runner
Use the steps in `docs/runner-setup.md` to remove and re-register.

## Logs
- GitHub Actions logs: Actions tab in the repo
- Host logs: `C:\src\ci-autopilot\logs` (if enabled by the agent)

## Health checks
- `Get-Service -Name $serviceName` should report `Running`
- Runner should show `status: online` in repo runners list

## Notifications
`Runner Health Monitor` runs every 15 minutes on GitHub-hosted runners.
If the self-hosted runner is offline, it opens or updates an issue labeled `runner-offline`.
If `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, and `EMAIL_TO` secrets are configured, it also sends an email alert.

## Runner status API access
If the health monitor cannot list runners with the default `GITHUB_TOKEN`, add a repo secret
named `RUNNER_PAT` with `repo` and `workflow` scopes (plus `read:org` for org repos).
