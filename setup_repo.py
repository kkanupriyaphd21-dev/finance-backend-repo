import json
import os
import sys
import urllib.error
import urllib.request

from env_utils import load_dotenv_file

API_BASE = "https://api.github.com"


def _request_with_status(method, url, token, data=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "repo-setup-tool"
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            payload = resp.read().decode("utf-8") or "{}"
            return resp.status, json.loads(payload)
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8") or "{}"
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {"message": payload}
        return exc.code, data


def _request(method, url, token, data=None):
    status, data = _request_with_status(method, url, token, data)
    if status in (200, 201):
        return data
    return {}


def _get_env(name):
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val


def _create_repo_if_missing(token, owner, repo, repo_config):
    status, _ = _request_with_status("GET", f"{API_BASE}/repos/{owner}/{repo}", token)
    if status == 200:
        return
    if status != 404:
        raise RuntimeError(f"Failed to check repo status: HTTP {status}")

    create_payload = {
        "name": repo,
        "description": repo_config.get("description", ""),
        "private": repo_config.get("private", False),
        "has_issues": repo_config.get("has_issues", True),
        "has_projects": repo_config.get("has_projects", False),
        "has_wiki": repo_config.get("has_wiki", False),
        "default_branch": repo_config.get("default_branch", "main")
    }

    status, _ = _request_with_status("POST", f"{API_BASE}/user/repos", token, create_payload)
    if status in (200, 201):
        return

    status, _ = _request_with_status("POST", f"{API_BASE}/orgs/{owner}/repos", token, create_payload)
    if status not in (200, 201):
        raise RuntimeError(f"Failed to create repo: HTTP {status}")


def configure_repo():
    load_dotenv_file()
    token = _get_env("GITHUB_TOKEN_1")
    owner = _get_env("GITHUB_OWNER")
    repo = _get_env("GITHUB_REPO_NAME")

    with open("repo_meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    repo_config = meta.get("repo_config", {})
    labels = meta.get("labels", [])
    milestones = meta.get("milestones", [])

    _create_repo_if_missing(token, owner, repo, repo_config)
    _request("PATCH", f"{API_BASE}/repos/{owner}/{repo}", token, repo_config)

    existing_labels = _request("GET", f"{API_BASE}/repos/{owner}/{repo}/labels", token)
    existing_label_names = {l.get("name") for l in (existing_labels or [])}
    for label in labels:
        if label["name"] in existing_label_names:
            _request("PATCH", f"{API_BASE}/repos/{owner}/{repo}/labels/{label['name']}", token, label)
        else:
            _request("POST", f"{API_BASE}/repos/{owner}/{repo}/labels", token, label)

    existing_milestones = _request("GET", f"{API_BASE}/repos/{owner}/{repo}/milestones?state=all", token)
    existing_titles = {m.get("title") for m in (existing_milestones or [])}
    for ms in milestones:
        if ms["title"] not in existing_titles:
            _request("POST", f"{API_BASE}/repos/{owner}/{repo}/milestones", token, ms)

    if os.getenv("ENABLE_BRANCH_PROTECTION") == "1":
        protection = {
            "required_status_checks": None,
            "enforce_admins": False,
            "required_pull_request_reviews": {
                "dismiss_stale_reviews": True,
                "required_approving_review_count": 1
            },
            "restrictions": None
        }
        default_branch = repo_config.get("default_branch", "main")
        _request("PUT", f"{API_BASE}/repos/{owner}/{repo}/branches/{default_branch}/protection", token, protection)


if __name__ == "__main__":
    try:
        configure_repo()
    except Exception as exc:
        print(f"setup_repo failed: {exc}")
        sys.exit(1)
    print("setup_repo complete")
