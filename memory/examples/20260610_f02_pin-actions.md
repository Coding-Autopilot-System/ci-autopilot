# Pin workflow actions to immutable commits

Issue Description:
GitHub Actions dependencies used mutable major-version tags.

State:
Workflow actions referenced `@v3`, `@v4`, `@v5`, or `@v7` tags.

Action:
Pinned each external action to the commit currently referenced by its major tag and retained the tag in a comment.

Result:
Workflow dependencies cannot change without a reviewed repository diff.

Diff Patch:
```diff
- uses: actions/checkout@v4
+ uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
```

Rationale:
Immutable action references reduce supply-chain risk in privileged automation.