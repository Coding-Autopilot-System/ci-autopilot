# Add worker boundary tests and validation

Issue Description:
The worker had no tests and accepted malformed repository or API response data.

State:
CI only compiled and imported the worker.

Action:
Added stdlib unit tests, repository-segment validation, network error handling, JSON error handling, and response-shape checks.

Result:
Worker boundary failures are deterministic and covered by tests.

Diff Patch:
```diff
+def _validate_repo_segment(value: str, name: str) -> str:
+    ...
+class MainTests(unittest.TestCase):
+    ...
```

Rationale:
The worker consumes environment and network inputs at a privileged automation boundary.