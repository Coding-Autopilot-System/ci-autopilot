from pathlib import Path


def test_runner_health_uses_non_reserved_target_name() -> None:
    workflow = Path(".github/workflows/runner-health.yml").read_text(encoding="utf-8")

    assert "MONITORED_RUNNER_NAME: CAS-Workstation-Kim" in workflow
    assert "${MONITORED_RUNNER_NAME}" in workflow
    assert "RUNNER_NAME: MyLocalPC" not in workflow
    assert 'subject: "Runner offline: ${{ env.MONITORED_RUNNER_NAME }}"' in workflow
    assert "Runner: ${{ env.MONITORED_RUNNER_NAME }}" in workflow
