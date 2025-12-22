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
