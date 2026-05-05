import json
import os
import sys
import urllib.request

from env_utils import load_dotenv_file

API_BASE = "https://api.github.com"


def _request(method, url, token, data=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "repo-history-tool"
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


def _get_env(name):
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val


def get_milestone_map(owner, repo, token):
    milestones = _request("GET", f"{API_BASE}/repos/{owner}/{repo}/milestones?state=all", token)
    return {m["title"]: m["number"] for m in milestones}


def list_issues(owner, repo, token):
    # return list of existing issues (first page -> sufficient for this replay)
    return _request("GET", f"{API_BASE}/repos/{owner}/{repo}/issues?state=all&per_page=100", token)


def main():
    load_dotenv_file()
    owner = _get_env("GITHUB_OWNER")
    repo = _get_env("GITHUB_REPO_NAME")
    default_token = _get_env("GITHUB_TOKEN_1")

    with open("issues.json", "r", encoding="utf-8") as f:
        issues_payload = json.load(f)
    issues = issues_payload.get("issues", issues_payload.get("issues_sample", []))

    milestone_map = get_milestone_map(owner, repo, default_token)

    issue_map = {}
    existing = list_issues(owner, repo, default_token) or []
    title_map = {i.get("title"): i.get("number") for i in existing}

    for issue in issues:
        title = issue["title"]
        # build body with original dates annotated at top to preserve timeline info
        created_date = issue.get("created_date")
        closed_date = issue.get("closed_date")
        timeline_lines = []
        if created_date:
            timeline_lines.append(f"**Original created:** {created_date}")
        if closed_date:
            timeline_lines.append(f"**Original closed:** {closed_date}")
        header = "\n".join(timeline_lines)
        full_body = (header + "\n\n" + issue.get("body", "")).strip()

        payload = {
            "title": title,
            "body": full_body,
            "labels": issue.get("labels", [])
        }
        milestone_title = issue.get("milestone")
        if milestone_title and milestone_title in milestone_map:
            payload["milestone"] = milestone_map[milestone_title]

        if title in title_map:
            actual_number = title_map[title]
            # update body/labels to ensure metadata is present
            _request("PATCH", f"{API_BASE}/repos/{owner}/{repo}/issues/{actual_number}", default_token, {"body": full_body, "labels": payload["labels"]})
        else:
            created = _request("POST", f"{API_BASE}/repos/{owner}/{repo}/issues", default_token, payload)
            actual_number = created.get("number")
            title_map[title] = actual_number

        issue_map[str(issue["number"])] = actual_number

        # avoid reposting duplicate comments: fetch existing comments and compare bodies
        existing_comments = _request("GET", f"{API_BASE}/repos/{owner}/{repo}/issues/{actual_number}/comments", default_token) or []
        existing_bodies = {c.get("body") for c in existing_comments}
        for comment in issue.get("comments", []):
            if comment.get("body") not in existing_bodies:
                _request(
                    "POST",
                    f"{API_BASE}/repos/{owner}/{repo}/issues/{actual_number}/comments",
                    default_token,
                    {"body": comment["body"]}
                )

        if issue.get("state") == "closed":
            _request("PATCH", f"{API_BASE}/repos/{owner}/{repo}/issues/{actual_number}", default_token, {"state": "closed"})

    with open("issue_map.json", "w", encoding="utf-8") as f:
        json.dump(issue_map, f, indent=2)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"create_issues failed: {exc}")
        sys.exit(1)
    print("create_issues complete")
