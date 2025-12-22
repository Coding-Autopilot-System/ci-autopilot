# Troubleshooting

## 401 Bad credentials during runner registration
- Ensure `gh auth status` shows the correct account
- Confirm scopes include `repo` and `workflow`
- Use `gh api -X POST` for token endpoints

## 404 Not Found for runner remove token
- Confirm you have access to the repo
- Verify the repo name and owner are correct

## Runner shows offline
- Check service status with `Get-Service`
- Restart the service
- Confirm the machine has outbound access to GitHub

## Service fails to start
- Re-run registration steps
- Check Windows Event Viewer for service errors
