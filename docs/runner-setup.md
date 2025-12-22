# Runner setup (Windows)

## Prerequisites
- Admin PowerShell
- GitHub CLI `gh`
- Access to both repos:
  - `OgeonX-Ai/enterprise-ai-gateway`
  - `Coding-Autopilot-System/ci-autopilot`

## Authenticate
```pwsh
cd C:\actions-runner
gh auth login -s repo,workflow,read:org,admin:org
gh auth status
```

## Remove from old repo
```pwsh
$removeToken = gh api -X POST repos/OgeonX-Ai/enterprise-ai-gateway/actions/runners/remove-token -q .token
.\config.cmd remove --token $removeToken
```

## Register to target repo
```pwsh
$regToken = gh api -X POST repos/Coding-Autopilot-System/ci-autopilot/actions/runners/registration-token -q .token
.\config.cmd --unattended --url https://github.com/Coding-Autopilot-System/ci-autopilot --token $regToken --name MyLocalPC --runasservice --replace
```

## Start service
```pwsh
$serviceName = Get-Content .\.service
Start-Service -Name $serviceName
Get-Service -Name $serviceName
```

## Validate runner online
```pwsh
gh api repos/Coding-Autopilot-System/ci-autopilot/actions/runners -q '.runners[] | {name, status, online}'
```

## Notes
- Registration and removal tokens are short-lived. Always fetch fresh tokens.
- Use `-X POST` with `gh api` for runner token endpoints.
