# CI Autopilot - Toolchain bootstrap (Windows)
# - Checks tools
# - Installs missing ones via winget (if available)
# - Prints a final status table

$ErrorActionPreference = "Stop"

function Has($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Run($cmd, $args=@()) {
  try { & $cmd @args 2>&1 | Out-String } catch { $_.Exception.Message }
}

Write-Host "=== Checking winget ==="
$hasWinget = Has "winget"
Write-Host ("winget: " + ($(if($hasWinget){"OK"}else{"MISSING"})))

# Tools we want
$want = @(
  @{name="git";    check="git";    winget="Git.Git"},
  @{name="pwsh";   check="pwsh";   winget="Microsoft.PowerShell"},
  @{name="python"; check="python"; winget="Python.Python.3.12"},
  @{name="node";   check="node";   winget="OpenJS.NodeJS.LTS"},
  @{name="npm";    check="npm";    winget="OpenJS.NodeJS.LTS"},
  @{name="gh";     check="gh";     winget="GitHub.cli"},
  @{name="dotnet"; check="dotnet"; winget="Microsoft.DotNet.SDK.10"}
)

# Install missing tools
if ($hasWinget) {
  foreach ($t in $want) {
    if (-not (Has $t.check)) {
      Write-Host "=== Installing $($t.name) via winget: $($t.winget) ==="
      winget install --id $t.winget -e --source winget --accept-source-agreements --accept-package-agreements
    }
  }
} else {
  Write-Host "No winget found. Install tools manually, then rerun this script."
}

Write-Host ""
Write-Host "=== Final status ==="
$rows = foreach ($t in $want) {
  $present = Has $t.check
  $ver = if ($present) { (Run $t.check @("--version")).Trim() } else { "MISSING" }
  [pscustomobject]@{ Tool=$t.name; Present=$present; Version=$ver }
}
$rows | Format-Table -AutoSize

Write-Host ""
Write-Host "Next: authenticate GitHub CLI (gh auth login) and verify access."
