import io
import json
import os
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from agent import poll_once


class RepoFromEnvTests(unittest.TestCase):
    def test_uses_github_repository(self) -> None:
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "acme/worker"}, clear=True):
            self.assertEqual(poll_once._repo_from_env(), ("acme", "worker"))

    def test_rejects_path_injection(self) -> None:
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "acme/worker/extra"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "Invalid GitHub repository"):
                poll_once._repo_from_env()


class GithubApiTests(unittest.TestCase):
    @patch("agent.poll_once.urllib.request.urlopen")
    def test_http_api_parses_json(self, urlopen: MagicMock) -> None:
        response = MagicMock()
        response.read.return_value = json.dumps([{"number": 1}]).encode()
        urlopen.return_value.__enter__.return_value = response
        with patch.dict(os.environ, {"GITHUB_TOKEN": "token"}, clear=True):
            self.assertEqual(poll_once._gh_api_http("/test"), [{"number": 1}])

    @patch("agent.poll_once.urllib.request.urlopen")
    def test_http_api_wraps_network_errors(self, urlopen: MagicMock) -> None:
        urlopen.side_effect = urllib.error.URLError("offline")
        with patch.dict(os.environ, {"GITHUB_TOKEN": "token"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "request failed: offline"):
                poll_once._gh_api_http("/test")


class MainTests(unittest.TestCase):
    @patch("agent.poll_once._gh_api_json", return_value=[{"number": 4, "title": "Fix", "html_url": "url"}, {"pull_request": {}}])
    def test_main_lists_only_issues(self, api: MagicMock) -> None:
        output = io.StringIO()
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "acme/worker"}, clear=True), patch("sys.stdout", output):
            self.assertEqual(poll_once.main(), 0)
        self.assertIn("Found 1 queued issues", output.getvalue())

    @patch("agent.poll_once._gh_api_json", return_value={"message": "unexpected"})
    def test_main_rejects_unexpected_response(self, api: MagicMock) -> None:
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "acme/worker"}, clear=True):
            self.assertEqual(poll_once.main(), 1)


if __name__ == "__main__":
    unittest.main()