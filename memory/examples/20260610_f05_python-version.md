# Align bootstrap Python version

Issue Description:
The Windows bootstrap installed Python 3.11 while the runtime and CI require Python 3.12.

State:
`Machinesetup.ps1` requested the Python 3.11 winget package.

Action:
Changed the winget package to Python 3.12.

Result:
New runner hosts receive the documented and tested runtime version.

Diff Patch:
```diff
- winget="Python.Python.3.11"
+ winget="Python.Python.3.12"
```

Rationale:
Bootstrap, CI, and runtime requirements must be consistent.