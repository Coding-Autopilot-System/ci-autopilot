# CI Autopilot Audit-Fix Report

Date: 2026-06-10
Source: gsd-audit-fix (fresh repository audit; no existing UAT phase artifacts)
Arguments: `--severity all --max 8`
Scope: worker/runtime correctness, security boundaries, CI, tests, packaging, reliability, documentation

## Classification

| ID | Finding | Severity | Classification | Result |
|---|---|---|---|---|
| F-01 | Persistent self-hosted checkout retained prior-job files | high | auto-fixable | Fixed; clean checkout moved before log creation |
| F-02 | External GitHub Actions used mutable tags | high | auto-fixable | Fixed; pinned to immutable commits |
| F-03 | Worker accepted malformed repo/API inputs and had no boundary tests | high | auto-fixable | Fixed; validation, error wrapping, response checks, tests |
| F-04 | CI did not execute tests and local tests left generated artifacts | medium | auto-fixable | Fixed; discovery in CI and ignore rules |
| F-05 | Bootstrap installed Python 3.11 while CI/runtime require 3.12 | medium | auto-fixable | Fixed |
| F-06 | Runner health monitor was manual-only despite 15-minute runbook claim | medium | auto-fixable | Fixed; schedule added |
| F-07 | Runner-health email recipient was hard-coded personal data | medium | auto-fixable | Fixed; `EMAIL_TO` secret |
| F-08 | Docs claimed autonomous dispatch not present in implementation | high | auto-fixable | Fixed; read-only contract documented |
| F-09 | Failure-intake shell interpolates `workflow_run` fields directly into Bash | high | auto-fixable | Not attempted; `--max 8` reached |
| F-10 | Two failure-intake workflows overlap with inconsistent deduplication and labels | medium | manual-only | Choose and migrate to one canonical intake contract |
| F-11 | Guarded autonomous repair dispatcher and queue state machine are absent | high | manual-only | Requires trust policy, sandbox, allowlists, PR-only output, authorization |
| F-12 | Persistent runner host hardening and isolation controls are not implemented as code | high | manual-only | Requires deployment architecture and host policy |
| F-13 | Runner identity is hard-coded as `MyLocalPC` | medium | auto-fixable | Not attempted; `--max 8` reached |
| F-14 | Runner-health authentication depends on a manually scoped PAT | medium | manual-only | Prefer GitHub App or centrally governed fine-grained identity |
| F-15 | Scheduled fixer has no concurrency guard | medium | auto-fixable | Not attempted; `--max 8` reached |
| F-16 | Queue inventory is limited to the first API page and displays only five items | low | manual-only | Define inventory/processing pagination contract first |

## Fixed Commits

- F-01: `ae2f052`, `dd4cc15`
- F-02: `b622adf`
- F-03: `364f4a2`
- F-04: `53ae712`, `9385ee0`
- F-05: `8a5c893`
- F-06: `aae07d2`
- F-07: `4da6055`
- F-08: `21b8065`, `b129f3a`

## Verification

- `python -m unittest discover -v`: 6 passed
- `python -m py_compile agent/poll_once.py`: passed
- `python -m compileall -q agent tests`: passed
- `git diff --check`: passed
- Existing PR: https://github.com/Coding-Autopilot-System/ci-autopilot/pull/1965

## Manual Gate

Do not grant worker write permissions or execute issue content until F-11 and F-12 have approved designs and testable controls.