# Enforce unit-test discovery in CI

Issue Description:
The unit test command completed without discovering the worker tests.

State:
The test directory was not importable and CI did not execute the suite.

Action:
Made the test package discoverable, wired the suite into CI, and tightened malformed `GITHUB_REPOSITORY` rejection.

Result:
CI executes six worker boundary tests.

Diff Patch:
```diff
+      - name: Unit tests
+        run: python -m unittest discover -v
```

Rationale:
A zero-test success is not valid verification.