# CI Autopilot runner health workflow hardened

Issue Description:
Runner health checks failed with HTTP 403, gh issue commands failed outside a git repo, and the runner-offline label was missing.

State:
Runner Health Monitor failed, masking actual runner status and blocking notifications.

Action:
Switched to github.token defaults, tolerated runner API auth failures, added explicit --repo to gh issue commands, and ensured the runner-offline label exists.

Result:
Runner Health Monitor completed successfully even when runner status is unknown.

Rationale:
The workflow now degrades gracefully under limited token scopes and no longer depends on repository checkout.

Diff Patch:
```diff
commit a45838ab557875b3dad7c7fb17c6e24311900b75
Author: Kim Harjamaki <ogeon@msn.com>
Date:   Mon Dec 22 23:12:36 2025 +0200

    Fix CI token handling and runner health

diff --git a/.github/workflows/fixer.yml b/.github/workflows/fixer.yml
index 28e3275..5975ec9 100644
--- a/.github/workflows/fixer.yml
+++ b/.github/workflows/fixer.yml
@@ -19,8 +19,8 @@ jobs:
       run:
         shell: pwsh
     env:
-      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
-      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
+      GH_TOKEN: ${{ github.token }}
+      GITHUB_TOKEN: ${{ github.token }}
     steps:
       - name: Preflight diagnostics
         run: |
diff --git a/.github/workflows/runner-health.yml b/.github/workflows/runner-health.yml
index 2643da2..c84d88d 100644
--- a/.github/workflows/runner-health.yml
+++ b/.github/workflows/runner-health.yml
@@ -14,7 +14,7 @@ jobs:
   check-runner:
     runs-on: ubuntu-latest
     env:
-      GH_TOKEN: ${{ github.token }}
+      GH_TOKEN: ${{ secrets.RUNNER_PAT || github.token }}
       RUNNER_NAME: MyLocalPC
     steps:
       - name: Check runner status
diff --git a/docs/operations.md b/docs/operations.md
index 7ae0d8b..dc55c97 100644
--- a/docs/operations.md
+++ b/docs/operations.md
@@ -30,3 +30,7 @@ Use the steps in `docs/runner-setup.md` to remove and re-register.
 `Runner Health Monitor` runs every 15 minutes on GitHub-hosted runners.
 If the self-hosted runner is offline, it opens or updates an issue labeled `runner-offline`.
 If SMTP secrets are configured, it also sends an email alert.
+
+## Runner status API access
+If the health monitor cannot list runners with the default `GITHUB_TOKEN`, add a repo secret
+named `RUNNER_PAT` with `repo` and `workflow` scopes (plus `read:org` for org repos).

commit 9f1f6b049fc25f927cc2b8a02b9735df2b610523
Author: Kim Harjamaki <ogeon@msn.com>
Date:   Mon Dec 22 23:27:39 2025 +0200

    Handle runner status API auth failures

diff --git a/.github/workflows/runner-health.yml b/.github/workflows/runner-health.yml
index c84d88d..2dd6329 100644
--- a/.github/workflows/runner-health.yml
+++ b/.github/workflows/runner-health.yml
@@ -21,7 +21,10 @@ jobs:
         id: status
         run: |
           set -euo pipefail
-          status="$(gh api repos/${GITHUB_REPOSITORY}/actions/runners --jq ".runners[] | select(.name==\"${RUNNER_NAME}\") | .status")"
+          status=""
+          if ! status="$(gh api repos/${GITHUB_REPOSITORY}/actions/runners --jq ".runners[] | select(.name==\"${RUNNER_NAME}\") | .status")"; then
+            status="unknown"
+          fi
           if [ -z "${status}" ]; then
             status="not_found"
           fi
@@ -47,6 +50,7 @@ jobs:
           - Verify the runner service on the host
           - Restart the service if needed
           - Confirm network reachability to GitHub
+          - If status is "unknown", set RUNNER_PAT with repo/workflow/read:org scopes
           EOF
           )
           if [ -n "${existing}" ]; then

commit 7b21a5f2abbb2750a2ae1b62c64ea7915f1c4ae3
Author: Kim Harjamaki <ogeon@msn.com>
Date:   Mon Dec 22 23:29:32 2025 +0200

    Fix runner health issue commands

diff --git a/.github/workflows/runner-health.yml b/.github/workflows/runner-health.yml
index 2dd6329..a2718fc 100644
--- a/.github/workflows/runner-health.yml
+++ b/.github/workflows/runner-health.yml
@@ -37,7 +37,7 @@ jobs:
           title="Runner offline: ${RUNNER_NAME}"
           marker="Autopilot Runner Health"
           status="${{ steps.status.outputs.runner_status }}"
-          existing="$(gh issue list -s open -l runner-offline -S "${title}" --json number --jq '.[0].number')"
+          existing="$(gh issue list -s open -l runner-offline -S "${title}" --repo "${GITHUB_REPOSITORY}" --json number --jq '.[0].number')"
           body=$(cat <<EOF
           ${marker}
 
@@ -54,9 +54,9 @@ jobs:
           EOF
           )
           if [ -n "${existing}" ]; then
-            gh issue comment "${existing}" -b "${body}"
+            gh issue comment "${existing}" -b "${body}" --repo "${GITHUB_REPOSITORY}"
           else
-            gh issue create -t "${title}" -b "${body}" -l "runner-offline"
+            gh issue create -t "${title}" -b "${body}" -l "runner-offline" --repo "${GITHUB_REPOSITORY}"
           fi
 
       - name: Email notification

commit 99884aec07a95421d78ac95c251ea53a284d43d3
Author: Kim Harjamaki <ogeon@msn.com>
Date:   Mon Dec 22 23:30:34 2025 +0200

    Ensure runner-offline label exists

diff --git a/.github/workflows/runner-health.yml b/.github/workflows/runner-health.yml
index a2718fc..281d8da 100644
--- a/.github/workflows/runner-health.yml
+++ b/.github/workflows/runner-health.yml
@@ -37,6 +37,7 @@ jobs:
           title="Runner offline: ${RUNNER_NAME}"
           marker="Autopilot Runner Health"
           status="${{ steps.status.outputs.runner_status }}"
+          gh label create runner-offline --color "B60205" --description "Runner offline alerts" --force --repo "${GITHUB_REPOSITORY}" || true
           existing="$(gh issue list -s open -l runner-offline -S "${title}" --repo "${GITHUB_REPOSITORY}" --json number --jq '.[0].number')"
           body=$(cat <<EOF
           ${marker}
```
