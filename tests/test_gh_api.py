"""Unit tests for gh API request construction in agent.poll_once.

These tests lock down the exact HTTP method, endpoint, query, headers and
gh-CLI command shape so regressions like the "gh api POST bug"
(missing ``-X GET`` on the CLI fallback, which made ``gh api`` default to a
POST for any request carrying ``-f`` fields) are caught before shipping.

All network / subprocess boundaries are mocked. No real gh or HTTP calls.
"""

import json
import os
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from agent import poll_once


class GhCliFallbackCommandTests(unittest.TestCase):
    """The gh-CLI fallback path (no token) must build a safe GET command.

    This is the exact regression surface of the prior fix:
    ``gh api <path> -f k=v`` implicitly POSTs, so ``-X GET`` must be present.
    """

    def _run_fallback(self, path, fields=None):
        """Drive _gh_api_json through the CLI fallback and return the argv used."""
        captured = {}

        def fake_run(cmd, timeout=20):
            captured["cmd"] = cmd
            captured["timeout"] = timeout
            return "[]"

        # No token in env -> forces the gh CLI fallback branch.
        with patch.dict(os.environ, {}, clear=True):
            with patch("agent.poll_once._run", side_effect=fake_run):
                poll_once._gh_api_json(path, fields=fields)
        return captured

    def test_fallback_forces_get_method(self) -> None:
        # Regression guard: without -X GET, gh treats -f fields as a POST body.
        cmd = self._run_fallback("/repos/acme/worker/issues", fields={"state": "open"})["cmd"]
        self.assertIn("-X", cmd)
        method_value = cmd[cmd.index("-X") + 1]
        self.assertEqual(method_value, "GET")

    def test_fallback_never_uses_a_mutating_method(self) -> None:
        cmd = self._run_fallback("/repos/acme/worker/issues", fields={"state": "open"})["cmd"]
        for mutating in ("POST", "PUT", "PATCH", "DELETE"):
            self.assertNotIn(mutating, cmd)

    def test_fallback_command_prefix_and_endpoint(self) -> None:
        cmd = self._run_fallback("/repos/acme/worker/issues")["cmd"]
        self.assertEqual(cmd[0], "gh")
        self.assertEqual(cmd[1], "api")
        self.assertEqual(cmd[2], "/repos/acme/worker/issues")

    def test_fallback_sets_accept_header(self) -> None:
        cmd = self._run_fallback("/repos/acme/worker/issues")["cmd"]
        self.assertIn("-H", cmd)
        header_value = cmd[cmd.index("-H") + 1]
        self.assertEqual(header_value, "Accept: application/vnd.github+json")

    def test_fallback_serializes_fields_as_f_pairs(self) -> None:
        cmd = self._run_fallback(
            "/repos/acme/worker/issues",
            fields={"state": "open", "labels": "queued", "per_page": "50"},
        )["cmd"]
        # Each field becomes a "-f key=value" pair, in insertion order.
        self.assertIn("-f", cmd)
        pairs = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-f"]
        self.assertEqual(pairs, ["state=open", "labels=queued", "per_page=50"])
        self.assertEqual(cmd.count("-f"), 3)

    def test_fallback_without_fields_has_no_f_flag(self) -> None:
        cmd = self._run_fallback("/repos/acme/worker/issues")["cmd"]
        self.assertNotIn("-f", cmd)

    def test_fallback_parses_json_output(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("agent.poll_once._run", return_value=json.dumps([{"number": 7}])):
                result = poll_once._gh_api_json("/x")
        self.assertEqual(result, [{"number": 7}])

    def test_fallback_empty_output_is_none(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("agent.poll_once._run", return_value=""):
                self.assertIsNone(poll_once._gh_api_json("/x"))

    def test_fallback_invalid_json_raises_runtime_error(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("agent.poll_once._run", return_value="{not json"):
                with self.assertRaisesRegex(RuntimeError, "invalid JSON"):
                    poll_once._gh_api_json("/x")


class TokenRoutingTests(unittest.TestCase):
    """_gh_api_json must route to HTTP when a token exists, CLI otherwise."""

    def test_token_present_uses_http_not_cli(self) -> None:
        with patch.dict(os.environ, {"GITHUB_TOKEN": "t"}, clear=True):
            with patch("agent.poll_once._gh_api_http", return_value=[1]) as http, \
                 patch("agent.poll_once._run") as run:
                self.assertEqual(poll_once._gh_api_json("/x", fields={"a": "b"}), [1])
        http.assert_called_once_with("/x", fields={"a": "b"}, timeout=20)
        run.assert_not_called()

    def test_gh_token_env_also_selects_http(self) -> None:
        with patch.dict(os.environ, {"GH_TOKEN": "t"}, clear=True):
            with patch("agent.poll_once._gh_api_http", return_value=[]) as http, \
                 patch("agent.poll_once._run") as run:
                poll_once._gh_api_json("/x")
        http.assert_called_once()
        run.assert_not_called()

    def test_no_token_uses_cli_not_http(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("agent.poll_once._gh_api_http") as http, \
                 patch("agent.poll_once._run", return_value="[]") as run:
                poll_once._gh_api_json("/x")
        run.assert_called_once()
        http.assert_not_called()


class HttpRequestConstructionTests(unittest.TestCase):
    """The urllib HTTP path must build a correct GET request with auth headers."""

    def _capture_request(self, path, fields=None):
        captured = {}

        def fake_urlopen(req, timeout=20):
            captured["req"] = req
            captured["timeout"] = timeout
            resp = MagicMock()
            resp.read.return_value = b"[]"
            ctx = MagicMock()
            ctx.__enter__.return_value = resp
            return ctx

        with patch.dict(os.environ, {"GITHUB_TOKEN": "secret-token"}, clear=True):
            with patch("agent.poll_once.urllib.request.urlopen", side_effect=fake_urlopen):
                poll_once._gh_api_http(path, fields=fields)
        return captured["req"]

    def test_builds_expected_base_url(self) -> None:
        req = self._capture_request("/repos/acme/worker/issues")
        self.assertEqual(req.full_url, "https://api.github.com/repos/acme/worker/issues")

    def test_encodes_fields_into_query_string(self) -> None:
        req = self._capture_request(
            "/repos/acme/worker/issues",
            fields={"state": "open", "labels": "queued", "per_page": "50"},
        )
        self.assertEqual(
            req.full_url,
            "https://api.github.com/repos/acme/worker/issues"
            "?state=open&labels=queued&per_page=50",
        )

    def test_no_fields_produces_no_query(self) -> None:
        req = self._capture_request("/repos/acme/worker/issues")
        self.assertNotIn("?", req.full_url)

    def test_uses_get_method(self) -> None:
        req = self._capture_request("/x", fields={"a": "b"})
        # urllib infers GET when no data payload is attached; assert we never
        # attach a body (which would flip the method to POST).
        self.assertIsNone(req.data)
        self.assertEqual(req.get_method(), "GET")

    def test_sets_required_headers_including_bearer_auth(self) -> None:
        req = self._capture_request("/x")
        # urllib capitalizes header keys.
        self.assertEqual(req.get_header("Accept"), "application/vnd.github+json")
        self.assertEqual(req.get_header("X-github-api-version"), "2022-11-28")
        self.assertEqual(req.get_header("Authorization"), "Bearer secret-token")

    def test_missing_token_raises_before_any_request(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("agent.poll_once.urllib.request.urlopen") as urlopen:
                with self.assertRaisesRegex(RuntimeError, "not available"):
                    poll_once._gh_api_http("/x")
            urlopen.assert_not_called()


class HttpErrorHandlingTests(unittest.TestCase):
    """HTTP failures must be surfaced as RuntimeError with useful context."""

    def test_http_error_includes_status_and_body(self) -> None:
        err = urllib.error.HTTPError(
            url="https://api.github.com/x",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=None,
        )
        err.read = MagicMock(return_value=b'{"message":"rate limited"}')
        with patch.dict(os.environ, {"GITHUB_TOKEN": "t"}, clear=True):
            with patch("agent.poll_once.urllib.request.urlopen", side_effect=err):
                with self.assertRaisesRegex(RuntimeError, "GitHub API error 403"):
                    poll_once._gh_api_http("/x")

    def test_url_error_is_wrapped(self) -> None:
        with patch.dict(os.environ, {"GITHUB_TOKEN": "t"}, clear=True):
            with patch(
                "agent.poll_once.urllib.request.urlopen",
                side_effect=urllib.error.URLError("dns down"),
            ):
                with self.assertRaisesRegex(RuntimeError, "request failed: dns down"):
                    poll_once._gh_api_http("/x")

    def test_invalid_json_body_is_wrapped(self) -> None:
        resp = MagicMock()
        resp.read.return_value = b"<html>not json</html>"
        ctx = MagicMock()
        ctx.__enter__.return_value = resp
        with patch.dict(os.environ, {"GITHUB_TOKEN": "t"}, clear=True):
            with patch("agent.poll_once.urllib.request.urlopen", return_value=ctx):
                with self.assertRaisesRegex(RuntimeError, "invalid JSON"):
                    poll_once._gh_api_http("/x")

    def test_empty_body_returns_none(self) -> None:
        resp = MagicMock()
        resp.read.return_value = b""
        ctx = MagicMock()
        ctx.__enter__.return_value = resp
        with patch.dict(os.environ, {"GITHUB_TOKEN": "t"}, clear=True):
            with patch("agent.poll_once.urllib.request.urlopen", return_value=ctx):
                self.assertIsNone(poll_once._gh_api_http("/x"))


if __name__ == "__main__":
    unittest.main()
