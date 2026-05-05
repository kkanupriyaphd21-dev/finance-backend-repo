#!/usr/bin/env python3
"""Verify 100 issues and PR posting to GitHub."""
import json
import urllib.request
import os
from env_utils import load_dotenv_file

API_BASE = "https://api.github.com"

def _request(method, url, token):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "repo-history-tool"
    }
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8") or "{}")
    except Exception as exc:
        print(f"Error: {exc}")
        return {}

def main():
    load_dotenv_file()
    owner = os.getenv("GITHUB_OWNER", "kkanupriyaphd21-dev")
    repo = os.getenv("GITHUB_REPO_NAME", "finance-backend-repo")
    token = os.getenv("GITHUB_TOKEN_1")
    
    if not token:
        print("ERROR: GITHUB_TOKEN_1 not set")
        return
    
    # Get all issues
    issues = _request("GET", f"{API_BASE}/repos/{owner}/{repo}/issues?state=all&per_page=100", token) or []
    closed_issues = [i for i in issues if i["state"] == "closed"]
    open_issues = [i for i in issues if i["state"] == "open"]
    
    # Get all PRs
    prs = _request("GET", f"{API_BASE}/repos/{owner}/{repo}/pulls?state=all&per_page=100", token) or []
    merged_prs = [p for p in prs if p["merged_at"]]
    open_prs = [p for p in prs if not p["merged_at"] and p["state"] == "open"]
    
    print(f"\n{'='*60}")
    print(f"GitHub Repo Verification: {owner}/{repo}")
    print(f"{'='*60}")
    print(f"\n📊 ISSUES:")
    print(f"  Total:  {len(issues)}")
    print(f"  Open:   {len(open_issues)}")
    print(f"  Closed: {len(closed_issues)}")
    
    print(f"\n📊 PULL REQUESTS:")
    print(f"  Total:  {len(prs)}")
    print(f"  Merged: {len(merged_prs)}")
    print(f"  Open:   {len(open_prs)}")
    
    print(f"\n📋 SAMPLE ISSUES (first 5):")
    for i in issues[:5]:
        print(f"   #{i['number']:3d} [{i['state']:6s}] {i['title'][:50]}")
    
    print(f"\n📋 SAMPLE PRs (first 5):")
    for p in prs[:5]:
        state = "merged" if p["merged_at"] else p["state"]
        print(f"   #{p['number']:3d} [{state:6s}] {p['title'][:50]}")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    main()
