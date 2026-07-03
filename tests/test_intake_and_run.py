"""Unit tests for the failure-intake / fixer decision logic and the
subprocess wrapper in agent.poll_once.

`main()` is the intake path: it resolves the target repo, pulls the queued
issue backlog from GitHub, and decides which items are actionable failures
(open issues labelled "queued", excluding pull requests). These tests cover
the branch decisions and error propagation. `_run` is the subprocess boundary
every gh CLI call flows through; its failure translation is asserted here.

All subprocess / API boundaries are mocked. No real gh or HTTP calls.
"""

import io
import os
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from agent import poll_once


def _issue(number, title="t", url="u", **extra):
    data = {"number": number, "title": title, "html_url": url}
    data.update(extra)
    return data


class MainIntakeQueryTests(unittest.TestCase):
    """main() must request the correct queued-issue backlog for the target repo."""

    def test_requests_open_queued_issues_for_resolved_repo(self) -> None:
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "acme/worker"}, clear=True):
            with patch("agent.poll_once._gh_api_json", return_value=[]) as api, \
                 patch("sys.stdout", io.StringIO()):
                self.assertEqual(poll_once.main(), 0)
        api.assert_called_once_with(
            "/repos/acme/worker/issues",
            fields={"state": "open", "labels": "queued", "per_page": "50"},
        )

    def test_falls_back_to_default_owner_repo(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("agent.poll_once._gh_api_json", return_value=[]) as api, \
                 patch("sys.stdout", io.StringIO()):
                poll_once.main()
        called_path = api.call_args.args[0]
        self.assertEqual(called_path, "/repos/Coding-Autopilot-System/ci-autopilot/issues")


class MainIntakeFilteringTests(unittest.TestCase):
    """The fixer only acts on real issues; PRs and malformed items are excluded."""

    def _run_main(self, payload):
        out = io.StringIO()
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "acme/worker"}, clear=True):
            with patch("agent.poll_once._gh_api_json", return_value=payload), \
                 patch("sys.stdout", out):
                rc = poll_once.main()
        return rc, out.getvalue()

    def test_excludes_pull_requests_from_queue(self) -> None:
        payload = [
            _issue(1),
            _issue(2, pull_request={"url": "x"}),  # a PR, must be filtered out
            _issue(3),
        ]
        rc, out = self._run_main(payload)
        self.assertEqual(rc, 0)
        self.assertIn("Found 2 queued issues", out)

    def test_ignores_non_dict_entries(self) -> None:
        payload = [_issue(1), "junk", None, 42, _issue(2)]
        rc, out = self._run_main(payload)
        self.assertEqual(rc, 0)
        self.assertIn("Found 2 queued issues", out)

    def test_empty_list_reports_zero(self) -> None:
        rc, out = self._run_main([])
        self.assertEqual(rc, 0)
        self.assertIn("Found 0 queued issues", out)

    def test_none_response_treated_as_empty(self) -> None:
        rc, out = self._run_main(None)
        self.assertEqual(rc, 0)
        self.assertIn("Found 0 queued issues", out)

    def test_only_first_five_issues_are_detailed(self) -> None:
        payload = [_issue(n, title=f"issue-{n}") for n in range(1, 9)]
        rc, out = self._run_main(payload)
        self.assertEqual(rc, 0)
        self.assertIn("Found 8 queued issues", out)
        self.assertIn("issue-5", out)
        self.assertNotIn("issue-6", out)

    def test_issue_detail_lines_include_number_and_url(self) -> None:
        rc, out = self._run_main([_issue(42, title="broken build", url="http://gh/42")])
        self.assertEqual(rc, 0)
        self.assertIn("#42 broken build", out)
        self.assertIn("http://gh/42", out)


class MainErrorHandlingTests(unittest.TestCase):
    """main() must fail closed (return 1) on bad config, API errors, or bad shapes."""

    def test_invalid_repo_env_returns_one(self) -> None:
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "acme/worker/extra"}, clear=True):
            with patch("agent.poll_once._gh_api_json") as api, \
                 patch("sys.stdout", io.StringIO()):
                self.assertEqual(poll_once.main(), 1)
        api.assert_not_called()  # never queries GitHub with a bad target

    def test_api_runtime_error_returns_one(self) -> None:
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "acme/worker"}, clear=True):
            with patch(
                "agent.poll_once._gh_api_json",
                side_effect=RuntimeError("boom"),
            ), patch("sys.stdout", io.StringIO()) as out:
                self.assertEqual(poll_once.main(), 1)
        self.assertIn("boom", out.getvalue())

    def test_unexpected_dict_response_returns_one(self) -> None:
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "acme/worker"}, clear=True):
            with patch(
                "agent.poll_once._gh_api_json",
                return_value={"message": "Not Found"},
            ), patch("sys.stdout", io.StringIO()):
                self.assertEqual(poll_once.main(), 1)


class RepoResolutionTests(unittest.TestCase):
    """Repo-segment validation guards against path injection into API URLs."""

    def test_owner_repo_split_from_env(self) -> None:
        with patch.dict(os.environ, {"GITHUB_OWNER": "o", "GITHUB_REPO": "r"}, clear=True):
            self.assertEqual(poll_once._repo_from_env(), ("o", "r"))

    def test_rejects_slash_in_segment(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Invalid GitHub owner"):
            poll_once._validate_repo_segment("a/b", "owner")

    def test_rejects_empty_segment(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Invalid GitHub repository"):
            poll_once._validate_repo_segment("   ", "repository")

    def test_accepts_dotted_and_dashed_names(self) -> None:
        self.assertEqual(poll_once._validate_repo_segment("my-repo.v2_x", "repository"), "my-repo.v2_x")


class RunSubprocessTests(unittest.TestCase):
    """_run wraps subprocess and translates failures into RuntimeError."""

    def test_returns_stripped_stdout_on_success(self) -> None:
        proc = MagicMock(returncode=0, stdout="  hello  \n", stderr="")
        with patch("agent.poll_once.subprocess.run", return_value=proc):
            self.assertEqual(poll_once._run(["gh", "api", "/x"]), "hello")

    def test_nonzero_exit_raises_with_stderr(self) -> None:
        proc = MagicMock(returncode=1, stdout="", stderr="gh: HTTP 404")
        with patch("agent.poll_once.subprocess.run", return_value=proc):
            with self.assertRaisesRegex(RuntimeError, "Command failed"):
                poll_once._run(["gh", "api", "/missing"])

    def test_missing_binary_raises_command_not_found(self) -> None:
        with patch("agent.poll_once.subprocess.run", side_effect=FileNotFoundError()):
            with self.assertRaisesRegex(RuntimeError, "Command not found: gh"):
                poll_once._run(["gh", "api", "/x"])

    def test_timeout_is_translated(self) -> None:
        with patch(
            "agent.poll_once.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="gh", timeout=20),
        ):
            with self.assertRaisesRegex(RuntimeError, "timed out after 20s"):
                poll_once._run(["gh", "api", "/x"], timeout=20)

    def test_passes_capture_and_text_flags(self) -> None:
        proc = MagicMock(returncode=0, stdout="ok", stderr="")
        with patch("agent.poll_once.subprocess.run", return_value=proc) as run:
            poll_once._run(["gh", "--version"], timeout=5)
        kwargs = run.call_args.kwargs
        self.assertTrue(kwargs["capture_output"])
        self.assertTrue(kwargs["text"])
        self.assertEqual(kwargs["timeout"], 5)


if __name__ == "__main__":
    unittest.main()
