import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from env_utils import load_dotenv_file


def run(cmd, env=None):
    subprocess.run(cmd, check=True, env=env)


def load_commits():
    with open("commit_plan.json", "r", encoding="utf-8") as f:
        payload = json.load(f)
    if "commits" in payload:
        return payload["commits"]
    return payload.get("commits_sample", [])


def parse_date(value):
    return datetime.fromisoformat(value)


def ensure_file_exists(file_path):
    """Create file and parent directories if they don't exist."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# {file_path}\n# Working file\n")


def touch_file(file_path, item):
    path = Path(file_path)
    ensure_file_exists(file_path)
    marker = f"\n# {item['commit_id']} {item['date']} {item['commit_message']}\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(marker)


def existing_commit_count():
    try:
        output = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], text=True)
    except subprocess.CalledProcessError:
        return 0
    return int(output.strip() or "0")


def main():
    load_dotenv_file()
    owner = os.getenv("GITHUB_OWNER")
    repo_name = os.getenv("GITHUB_REPO_NAME")
    token = os.getenv("GITHUB_TOKEN_1")
    commits = load_commits()
    commits.sort(key=lambda c: parse_date(c["date"]))
    start_index = existing_commit_count()

    for item in commits[start_index:]:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = item.get("developer")
        env["GIT_AUTHOR_EMAIL"] = f"{item.get('developer')}@example.com"
        env["GIT_AUTHOR_DATE"] = item["date"]
        env["GIT_COMMITTER_NAME"] = env["GIT_AUTHOR_NAME"]
        env["GIT_COMMITTER_EMAIL"] = env["GIT_AUTHOR_EMAIL"]
        env["GIT_COMMITTER_DATE"] = item["date"]

        files = item.get("files", [])
        if not files:
            continue

        # Ensure all files exist and get a change before adding
        for file_path in files:
            touch_file(file_path, item)

        run(["git", "add"] + files, env=env)

        msg = item.get("commit_message", "update")
        body = item.get("commit_body", "")
        if body:
            run(["git", "commit", "-m", msg, "-m", body], env=env)
        else:
            run(["git", "commit", "-m", msg], env=env)

    if owner and repo_name and token:
        push_url = f"https://x-access-token:{token}@github.com/{owner}/{repo_name}.git"
        run(["git", "push", push_url, "main", "--force"])
    else:
        run(["git", "push", "origin", "main", "--force"])


if __name__ == "__main__":
    main()

