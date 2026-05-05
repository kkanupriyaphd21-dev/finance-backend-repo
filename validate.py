import json
import os
import sys
import urllib.request
from datetime import datetime

API_BASE = "https://api.github.com"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_dt(value):
    return datetime.fromisoformat(value)


def check_commit_plan(path):
    data = load_json(path)
    meta = data.get("metadata", {})
    commits = data.get("commits") or data.get("commits_sample") or []

    errors = []
    warnings = []

    if not commits:
        errors.append("No commits found in commit_plan.json")
        return errors, warnings, 0

    dates = [c.get("date") for c in commits if c.get("date")]
    if len(dates) != len(set(dates)):
        errors.append("Duplicate commit timestamps detected")

    start = meta.get("date_start")
    end = meta.get("date_end")
    if start and end:
        start_dt = parse_dt(f"{start}T00:00:00")
        end_dt = parse_dt(f"{end}T23:59:59")
        for c in commits:
            dt = parse_dt(c["date"])
            if dt < start_dt or dt > end_dt:
                errors.append(f"Commit {c.get('commit_id')} out of date range: {c['date']}")

    target = meta.get("target_commits")
    if target and len(commits) < target:
        warnings.append(f"Commit plan contains {len(commits)} entries, target is {target}")

    return errors, warnings, len(commits)


def check_issues(path):
    data = load_json(path)
    issues = data.get("issues") or data.get("issues_sample") or []
    meta = data.get("metadata", {})

    errors = []
    warnings = []

    if not issues:
        errors.append("No issues found in issues.json")
        return errors, warnings, 0

    target = meta.get("target_issues")
    if target and len(issues) < target:
        warnings.append(f"Issues list contains {len(issues)} entries, target is {target}")

    return errors, warnings, len(issues)


def check_prs(path):
    data = load_json(path)
    prs = data.get("prs") or data.get("prs_sample") or []
    meta = data.get("metadata", {})

    errors = []
    warnings = []

    if not prs:
        errors.append("No PRs found in prs.json")
        return errors, warnings, 0

    target = meta.get("target_prs")
    if target and len(prs) < target:
        warnings.append(f"PR list contains {len(prs)} entries, target is {target}")

    return errors, warnings, len(prs)


def request(method, url, token, data=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "repo-validation-tool"
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        if resp.status in (200, 201):
            return json.loads(resp.read().decode("utf-8") or "{}")
        return {}


def remote_validate():
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO_NAME")
    token = os.getenv("GITHUB_TOKEN_1")
    if not owner or not repo or not token:
        return ["Remote validation skipped (missing GITHUB_OWNER/GITHUB_REPO_NAME/GITHUB_TOKEN_1)."], []

    notes = []
    errors = []

    issues = request("GET", f"{API_BASE}/repos/{owner}/{repo}/issues?state=all&per_page=100", token)
    prs = request("GET", f"{API_BASE}/repos/{owner}/{repo}/pulls?state=all&per_page=100", token)

    if isinstance(issues, list):
        issue_count = sum(1 for i in issues if "pull_request" not in i)
        notes.append(f"Remote issues count (first page): {issue_count}")
    else:
        errors.append("Failed to read issues from GitHub API")

    if isinstance(prs, list):
        notes.append(f"Remote PR count (first page): {len(prs)}")
    else:
        errors.append("Failed to read PRs from GitHub API")

    return notes, errors


def main():
    errors = []
    warnings = []

    commit_errors, commit_warnings, commit_count = check_commit_plan("commit_plan.json")
    issue_errors, issue_warnings, issue_count = check_issues("issues.json")
    pr_errors, pr_warnings, pr_count = check_prs("prs.json")

    errors.extend(commit_errors + issue_errors + pr_errors)
    warnings.extend(commit_warnings + issue_warnings + pr_warnings)

    remote_notes = []
    remote_errors = []
    if os.getenv("VALIDATE_REMOTE") == "1":
        remote_notes, remote_errors = remote_validate()
        errors.extend(remote_errors)

    print("Validation summary")
    print("------------------")
    print(f"Commits: {commit_count}")
    print(f"Issues:  {issue_count}")
    print(f"PRs:     {pr_count}")

    if remote_notes:
        print("Remote checks:")
        for note in remote_notes:
            print(f"- {note}")

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"- {w}")

    if errors:
        print("Errors:")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
