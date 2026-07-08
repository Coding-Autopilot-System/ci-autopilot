# Decisions

## 2026-06-10 enterprise audit-fix (`.planning/audits/20260610-ci-autopilot-audit-fix.md`)

A `gsd-audit-fix` pass (severity `all`, max 8 auto-fixes) covering worker/runtime correctness,
security boundaries, CI, tests, packaging, reliability, and documentation. Key outcomes:

| ID | Finding | Result |
|---|---|---|
| F-01 | Persistent self-hosted checkout retained prior-job files | Fixed |
| F-02 | External GitHub Actions used mutable tags | Fixed; pinned to immutable commits |
| F-03 | Worker accepted malformed repo/API inputs, no boundary tests | Fixed; validation + tests added |
| F-08 | Docs claimed autonomous dispatch not present in implementation | Fixed; read-only contract documented |
| F-11 | Guarded autonomous repair dispatcher and queue state machine are absent | Open (manual-only) — this is why the agent is read-only today |
| F-12 | Persistent runner host hardening/isolation not implemented as code | Open (manual-only) — requires a deployment architecture decision |

The full finding list, including items not yet attempted (F-09, F-13, F-15, F-16), is in the
[audit report](../../.planning/audits/20260610-ci-autopilot-audit-fix.md).

## Architecture Decision Records (`docs/adr/`)

[`docs/adr/`](../adr/README.md) is the formal ADR home for this repo. No sequentially-numbered
ADR files have been recorded yet as of this writing — the directory holds only the governance
README. The audit findings above (F-11, F-12 in particular) are the leading candidates for the
first formal ADRs once a guarded-dispatch design is chosen.

<!-- docs-verified: 4590462b38e0a835385c3a7c4a4b35d761bed5dc 2026-07-08 -->
