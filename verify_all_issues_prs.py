#!/usr/bin/env python3
"""Get ALL issues and PRs from GitHub with proper pagination."""
import json
import urllib.request
import os
from env_utils import load_dotenv_file

API_BASE = "https://api.github.com"

def _request_paginated(method, url, token, per_page=100):
    """Fetch all results with pagination."""
    all_results = []
    page = 1
    while True:
        paginated_url = f"{url}{'&' if '?' in url else '?'}page={page}&per_page={per_page}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "repo-history-tool"
        }
        req = urllib.request.Request(paginated_url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8") or "[]")
                if not data:
                    break
                all_results.extend(data)
                if len(data) < per_page:
                    break
                page += 1
        except Exception as exc:
            print(f"Error on page {page}: {exc}")
            break
    return all_results

def main():
    load_dotenv_file()
    owner = os.getenv("GITHUB_OWNER", "kkanupriyaphd21-dev")
    repo = os.getenv("GITHUB_REPO_NAME", "finance-backend-repo")
    token = os.getenv("GITHUB_TOKEN_1")
    
    if not token:
        print("ERROR: GITHUB_TOKEN_1 not set")
        return
    
    print(f"Fetching ALL issues and PRs from {owner}/{repo}...\n")
    
    # Get all issues with pagination
    issues = _request_paginated("GET", f"{API_BASE}/repos/{owner}/{repo}/issues?state=all", token)
    closed_issues = [i for i in issues if i["state"] == "closed"]
    open_issues = [i for i in issues if i["state"] == "open"]
    
    # Get all PRs with pagination
    prs = _request_paginated("GET", f"{API_BASE}/repos/{owner}/{repo}/pulls?state=all", token)
    merged_prs = [p for p in prs if p["merged_at"]]
    open_prs = [p for p in prs if not p["merged_at"] and p["state"] == "open"]
    
    print(f"{'='*70}")
    print(f"GitHub Repo Verification: {owner}/{repo}")
    print(f"{'='*70}\n")
    
    print(f"📊 ISSUES (Total: {len(issues)}):")
    print(f"   Open:   {len(open_issues)}")
    print(f"   Closed: {len(closed_issues)}")
    
    print(f"\n📊 PULL REQUESTS (Total: {len(prs)}):")
    print(f"   Merged: {len(merged_prs)}")
    print(f"   Open:   {len(open_prs)}")
    
    print(f"\n📋 RECENT ISSUES (last 10):")
    for i in sorted(issues, key=lambda x: x['number'], reverse=True)[:10]:
        state_badge = "✓" if i['state'] == "closed" else "○"
        print(f"   {state_badge} #{i['number']:3d} {i['title'][:55]}")
    
    print(f"\n📋 RECENT PRs (last 10):")
    for p in sorted(prs, key=lambda x: x['number'], reverse=True)[:10]:
        merged_badge = "✓" if p["merged_at"] else "○"
        print(f"   {merged_badge} #{p['number']:3d} {p['title'][:55]}")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
