import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

_REPO_SEGMENT = re.compile(r"[A-Za-z0-9_.-]+")


def _run(cmd: list[str], timeout: int = 20) -> str:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Command not found: {cmd[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Command timed out after {timeout}s: {' '.join(cmd)}") from exc
    if proc.returncode != 0:
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        detail = []
        if stdout:
            detail.append(f"STDOUT:\n{stdout}")
        if stderr:
            detail.append(f"STDERR:\n{stderr}")
        detail_text = "\n".join(detail) if detail else "No output captured."
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{detail_text}")
    return proc.stdout.strip()


def _github_token() -> str | None:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    return token.strip() if token else None


def _gh_api_http(path: str, fields: dict[str, str] | None = None, timeout: int = 20) -> Any:
    token = _github_token()
    if not token:
        raise RuntimeError("GITHUB_TOKEN/GH_TOKEN not available for HTTP API call.")
    query = f"?{urllib.parse.urlencode(fields)}" if fields else ""
    url = f"https://api.github.com{path}{query}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8") if exc.fp else ""
        raise RuntimeError(f"GitHub API error {exc.code}: {err_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc
    try:
        return json.loads(body) if body else None
    except json.JSONDecodeError as exc:
        raise RuntimeError("GitHub API returned invalid JSON.") from exc


def _gh_api_json(path: str, fields: dict[str, str] | None = None, timeout: int = 20) -> Any:
    token = _github_token()
    if token:
        print("Using GITHUB_TOKEN for GitHub API requests.")
        return _gh_api_http(path, fields=fields, timeout=timeout)
    print("GITHUB_TOKEN not found, falling back to gh CLI.")
    cmd = ["gh", "api", path, "-H", "Accept: application/vnd.github+json"]
    if fields:
        for key, value in fields.items():
            cmd.extend(["-f", f"{key}={value}"])
    output = _run(cmd, timeout=timeout)
    try:
        return json.loads(output) if output else None
    except json.JSONDecodeError as exc:
        raise RuntimeError("gh CLI returned invalid JSON.") from exc


def _validate_repo_segment(value: str, name: str) -> str:
    value = value.strip()
    if not value or not _REPO_SEGMENT.fullmatch(value):
        raise RuntimeError(f"Invalid GitHub {name}: {value!r}")
    return value


def _repo_from_env() -> tuple[str, str]:
    repo_full = os.getenv("GITHUB_REPOSITORY", "").strip()
    if repo_full and repo_full.count("/") == 1:
        owner, repo = repo_full.split("/", 1)
    else:
        owner = os.getenv("GITHUB_OWNER", "Coding-Autopilot-System")
        repo = os.getenv("GITHUB_REPO", "ci-autopilot")
    return _validate_repo_segment(owner, "owner"), _validate_repo_segment(repo, "repository")


def main() -> int:
    try:
        owner, repo = _repo_from_env()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"CI Autopilot poll_once starting for {owner}/{repo}")
    print("Listing queued issues via GitHub API...")
    try:
        issues = _gh_api_json(
            f"/repos/{owner}/{repo}/issues",
            fields={"state": "open", "labels": "queued", "per_page": "50"},
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if issues is None:
        issues = []
    if not isinstance(issues, list):
        print("ERROR: GitHub API returned an unexpected issues response.")
        return 1
    queued = [it for it in issues if isinstance(it, dict) and "pull_request" not in it]
    print(f"Found {len(queued)} queued issues")
    for it in queued[:5]:
        num = it.get("number")
        title = it.get("title")
        url = it.get("html_url")
        print(f"- #{num} {title}")
        print(f"  {url}")

    print("poll_once complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())