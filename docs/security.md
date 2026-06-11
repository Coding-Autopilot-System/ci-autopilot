# Security

## Access model
- Use least-privilege tokens; only grant org scopes when required
- Restrict runner machine access to trusted administrators
- Store secrets in GitHub Secrets, not on disk

## Token scopes
- Minimum for runner admin operations: `repo`, `workflow`, `read:org`
- `admin:org` may be required depending on org policies

## Auditing
- Prefer GitHub Actions logs as the authoritative audit trail
- Keep local host logs for forensic debugging only

## Rotation
- Remove and re-register runners on a cadence or after incident response

## Worker boundary
The current fixer workflow grants only contents: read and issues: read. The worker treats issue data as untrusted display-only input and does not execute it. Any future repair dispatcher must define command allowlists, sandboxing, queue-state authorization, and PR-only output before receiving write permissions.
