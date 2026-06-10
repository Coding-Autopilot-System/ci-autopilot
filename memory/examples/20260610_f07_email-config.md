# Configure notification recipient through secrets

Issue Description:
The runner-health workflow exposed and hard-coded a personal email recipient.

State:
Email alerts always targeted a repository-specific personal address.

Action:
Replaced the address with the `EMAIL_TO` secret and documented the required notification secrets.

Result:
Deployments control their recipient without source changes or personal data in Git.

Diff Patch:
```diff
-          to: personal@example.com
+          to: ${{ env.EMAIL_TO }}
```

Rationale:
Notification endpoints are deployment configuration and may contain personal data.