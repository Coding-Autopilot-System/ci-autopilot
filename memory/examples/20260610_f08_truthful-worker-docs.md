# Align documentation with read-only worker

Issue Description:
Documentation claimed the worker dispatches autonomous repairs, but the implementation only inventories queued issues.

State:
Portfolio and operations claims overstated runtime behavior.

Action:
Documented the current read-only contract and the security gates required before repair dispatch.

Result:
Repository claims now match executable behavior and expose the next architecture milestone.

Diff Patch:
```diff
- dispatches autonomous repairs
+ inventories queued issues for operator visibility
```

Rationale:
Enterprise portfolio evidence must be truthful, especially at privileged automation boundaries.