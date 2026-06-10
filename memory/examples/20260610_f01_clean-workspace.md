# Clean persistent runner workspace

Issue Description:
The fixer checkout preserved files from previous self-hosted runner jobs.

State:
The checkout step used `clean: false`.

Action:
Enabled the checkout action's clean workspace behavior.

Result:
Each fixer run removes untracked files and resets tracked files before execution.

Diff Patch:
```diff
-          clean: false
+          clean: true
```

Rationale:
Persistent self-hosted runner workspaces must not carry untrusted or stale files between jobs.