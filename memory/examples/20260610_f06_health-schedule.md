# Schedule runner health monitoring

Issue Description:
Operations documentation promised 15-minute runner monitoring, but the workflow was dispatch-only.

State:
`runner-health.yml` only supported manual invocation.

Action:
Added a 15-minute cron trigger.

Result:
Runner availability is checked continuously as documented.

Diff Patch:
```diff
+  schedule:
+    - cron: "*/15 * * * *"
```

Rationale:
An offline self-hosted worker needs an independent scheduled detector.