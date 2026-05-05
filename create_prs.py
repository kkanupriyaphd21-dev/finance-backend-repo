import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

from env_utils import load_dotenv_file

API_BASE = "https://api.github.com"


def run(cmd, env=None):
    subprocess.run(cmd, check=True, env=env)


def push_url(owner, repo, token):
    return f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"


def _request(method, url, token, data=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "repo-history-tool",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = resp.read().decode("utf-8") or "{}"
        return json.loads(payload)


def _request_with_status(method, url, token, data=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "repo-history-tool",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8") or "{}"
            return resp.status, json.loads(payload)
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8") or "{}"
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {"message": payload}
        return exc.code, data


def _existing_pr_number(owner, repo, branch, token):
    url = f"{API_BASE}/repos/{owner}/{repo}/pulls?state=all&per_page=100"
    existing = _request("GET", url, token)
    for pull in existing:
        head = pull.get("head", {})
        if head.get("ref") == branch:
            return pull.get("number")
    return None


def load_team():
    with open("team_config.json", "r", encoding="utf-8") as f:
        payload = json.load(f)
    return {dev["id"]: dev for dev in payload["TEAM"]}


def touch_change(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# working file\n")
        return

    ext = os.path.splitext(path)[1].lower()
    with open(path, "a", encoding="utf-8") as f:
        if ext in (".py", ".txt", ".rst"):
            f.write("\n# follow-up change\n")
        elif ext in (".html", ".css", ".js"):
            f.write("\n<!-- follow-up change -->\n")
        else:
            f.write("\n")


def main():
    load_dotenv_file()
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO_NAME")
    default_token = os.getenv("GITHUB_TOKEN_1")
    if not owner or not repo or not default_token:
        raise RuntimeError("Missing required env vars: GITHUB_OWNER, GITHUB_REPO_NAME, GITHUB_TOKEN_1")

    with open("prs.json", "r", encoding="utf-8") as f:
        payload = json.load(f)
    prs = payload.get("prs", payload.get("prs_sample", []))

    issue_map = {}
    if os.path.exists("issue_map.json"):
        with open("issue_map.json", "r", encoding="utf-8") as f:
            issue_map = json.load(f)

    team = load_team()
    run(["git", "stash", "push", "--include-untracked", "-m", "pr-replay-autostash"])

    try:
        for pr in prs:
            author_id = pr["author_developer"]
            author = team.get(author_id, {})
            author_name = author.get("name", author_id)
            author_email = author.get("email", f"{author_id}@example.com")
            author_token = default_token

            base = pr.get("base_branch", "main")
            branch = pr["branch_name"]

            run(["git", "checkout", base])
            run(["git", "checkout", "-B", branch])

            for file_path in pr.get("files_changed", []):
                touch_change(file_path)

            env = os.environ.copy()
            env["GIT_AUTHOR_NAME"] = author_name
            env["GIT_AUTHOR_EMAIL"] = author_email
            env["GIT_COMMITTER_NAME"] = author_name
            env["GIT_COMMITTER_EMAIL"] = author_email
            run(["git", "add"] + pr.get("files_changed", []), env=env)
            run(["git", "commit", "-m", pr["title"]], env=env)
            run(["git", "push", "-f", push_url(owner, repo, author_token), branch], env=env)

            body = pr.get("body", "")
            linked_issue = pr.get("linked_issue_number")
            if linked_issue:
                actual_issue = issue_map.get(str(linked_issue), linked_issue)
                if f"#{actual_issue}" not in body:
                    body = f"Fixes #{actual_issue}.\n\n" + body

            pr_number = _existing_pr_number(owner, repo, branch, author_token)
            if not pr_number:
                created = _request(
                    "POST",
                    f"{API_BASE}/repos/{owner}/{repo}/pulls",
                    author_token,
                    {
                        "title": pr["title"],
                        "body": body,
                        "head": branch,
                        "base": base,
                    },
                )
                pr_number = created.get("number")

            review = pr.get("review", {})
            reviewer_token = default_token
            if pr_number and review:
                review_body = review.get("reviewer_comment", "")
                review_file = review.get("review_comment_file")
                if review_file:
                    review_body = f"{review_body}\n\nFile: {review_file}"
                review_status, _ = _request_with_status(
                    "POST",
                    f"{API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/reviews",
                    reviewer_token,
                    {"body": review_body, "event": review.get("review_type", "COMMENT")},
                )
                if review_status not in (200, 201, 422):
                    raise RuntimeError(f"review failed for PR {pr_number}: HTTP {review_status}")

                if review.get("review_type") == "REQUEST_CHANGES":
                    touch_change(pr["files_changed"][0])
                    run(["git", "add", pr["files_changed"][0]], env=env)
                    run(["git", "commit", "-m", "address review feedback"], env=env)
                    run(["git", "push", "-f", push_url(owner, repo, author_token), branch], env=env)

                    follow_status, _ = _request_with_status(
                        "POST",
                        f"{API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/reviews",
                        reviewer_token,
                        {"body": review.get("final_review_comment", "approved"), "event": review.get("final_review_type", "APPROVE")},
                    )
                    if follow_status not in (200, 201, 422):
                        raise RuntimeError(f"follow-up review failed for PR {pr_number}: HTTP {follow_status}")

            if pr_number:
                # Respect explicit merge flag in PR spec. Default is to merge.
                should_merge = pr.get("merge", True)
                if should_merge:
                    merge_status, _ = _request_with_status(
                        "PUT",
                        f"{API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/merge",
                        author_token,
                        {"merge_method": "merge"},
                    )
                    if merge_status not in (200, 201, 405, 409, 422):
                        raise RuntimeError(f"merge failed for PR {pr_number}: HTTP {merge_status}")
    finally:
        run(["git", "checkout", "main"])
        run(["git", "stash", "pop", "--index"])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"create_prs failed: {exc}")
        sys.exit(1)
    print("create_prs complete")
