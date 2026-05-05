#!/usr/bin/env python3
"""Generate 100 backdated issues and PRs (2021-2023) for replay scripts.

Produces two files in the repo root:
- issues_generated.json
- prs_generated.json

Designed to be deterministic and varied for high-fidelity training data.
"""
import json
from datetime import datetime, timedelta
import random

OUT_ISSUES = "issues_generated.json"
OUT_PRS = "prs_generated.json"

random.seed(42)

TOKENS = ["TOKEN_1", "TOKEN_2", "TOKEN_3", "TOKEN_4"]
LABEL_BANK = [
    "bug", "backend", "api", "performance", "data-integrity",
    "reliability", "postgresql", "ui", "docs", "priority:high",
]

FILE_POOL = [
    "m03/models.py", "m03/views.py", "m03/forms.py",
    "savings/views.py", "loans/views.py", "templates/generalledger.html",
    "templates/listof_receipts.html", "src/ledger/posting_engine.py",
    "src/risk/exposure.py", "src/api/routes.py",
]


def month_range(start, end):
    cur = start.replace(day=1)
    while cur <= end:
        yield cur
        if cur.month == 12:
            cur = cur.replace(year=cur.year + 1, month=1)
        else:
            cur = cur.replace(month=cur.month + 1)


def choose_title(i):
    templates = [
        "{component} memory amplification under skewed distribution",
        "{component} advisory lock collisions across partitions",
        "Idempotency eviction race causes duplicate {entity} events",
        "Reconciliation API non-deterministic ordering breaks checksum",
        "{component} export misses timezone normalization for DST zones",
        "Batch job OOM when group cardinality spikes",
        "Search endpoint returns stale results after cache warmup",
        "Mobile: client update loses branch selection on slow network",
        "Receipt reprint flow shows duplicate row when print fails",
        "Payment retry flow accepts zero amount on duplicate submit",
    ]
    t = random.choice(templates)
    comp = random.choice(["Ledger", "Risk aggregation", "Posting worker", "Reconciliation", "Export"])
    entity = random.choice(["disbursement", "receipt", "transaction"])
    return t.format(component=comp, entity=entity)


def build_comment_rounds(created_by):
    # three comments: reporter, reviewer, reporter reply
    commenter2 = random.choice([t for t in TOKENS if t != created_by])
    commenter3 = random.choice([t for t in TOKENS if t not in (created_by, commenter2)])
    return [
        {"by": created_by, "body": "Initial report: observed during weekly run, reproduces reliably on branch data."},
        {"by": commenter2, "body": "I can reproduce locally; adding traces and a temporary mitigation for investigation."},
        {"by": commenter3, "body": "Agree with the mitigation. Recommend a test-case and a follow-up PR to harden."},
    ]


def main():
    start = datetime(2021, 1, 1)
    end = datetime(2023, 12, 31)
    months = list(month_range(start, end))

    issues = {"metadata": {"generated": True, "count": 100, "span": [start.isoformat(), end.isoformat()]}, "issues": []}
    prs = {"metadata": {"generated": True, "count": 0}, "prs": []}

    pr_counter = 1
    for i in range(1, 101):
        # spread across months
        m = random.choice(months)
        day = random.randint(1, 28)
        created_dt = datetime(m.year, m.month, day, random.randint(8, 17), random.randint(0, 59), 0)
        created_str = created_dt.strftime("%Y-%m-%dT%H:%M:%S")

        creator = random.choice(TOKENS)
        title = choose_title(i)
        labels = random.sample(LABEL_BANK, k=random.randint(2, 4))

        # decide closed or open (70% closed)
        closed = random.random() < 0.7
        closed_str = None
        linked_pr = None
        if closed:
            # closed a few days later
            closed_dt = created_dt + timedelta(days=random.randint(1, 21))
            closed_str = closed_dt.strftime("%Y-%m-%dT%H:%M:%S")
            linked_pr = pr_counter
            pr_counter += 1

        issue = {
            "number": i,
            "title": title,
            "body": f"Detailed report and analysis for issue {i}.\n\nSteps to reproduce:\n1. Run the nightly batch\n2. Observe the failure\n\nExpected: stable behavior\nObserved: intermittent failure under load\n",
            "labels": labels,
            "state": "closed" if closed else "open",
            "filed_by_developer": creator.replace('TOKEN_', 'DEV_'),
            "github_token_env": creator.replace('TOKEN_', 'GITHUB_TOKEN_'),
            "created_date": created_str,
            "closed_date": closed_str,
            "closed_reason": "fixed" if closed else None,
            "linked_pr_number": linked_pr,
            "milestone": random.choice(["v1.0", "v1.1", "v1.2", "backlog"]),
            "comments": build_comment_rounds(creator),
        }
        issues["issues"].append(issue)

        if closed:
            # build a simple PR entry
            branch = f"auto/pr-{linked_pr}"
            files = random.sample(FILE_POOL, k=random.randint(1, 3))
            pr_created = (created_dt + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%dT%H:%M:%S")
            pr_merged = (created_dt + timedelta(days=random.randint(2, 22))).strftime("%Y-%m-%dT%H:%M:%S")
            author_dev = creator.replace('TOKEN_', 'DEV_')
            prs["prs"].append({
                "number": linked_pr,
                "title": f"fix: {title}",
                "body": f"Fix for issue #{i}.",
                "branch_name": branch,
                "base_branch": "main",
                "state": "merged",
                "author_developer": author_dev,
                "author_token_env": creator.replace('TOKEN_', 'GITHUB_TOKEN_'),
                "reviewer_developer": random.choice([d.replace('TOKEN_', 'DEV_') for d in TOKENS if d != creator]),
                "reviewer_token_env": random.choice([t.replace('TOKEN_', 'GITHUB_TOKEN_') for t in TOKENS if t != creator]),
                "files_changed": files,
                "created_date": pr_created,
                "merged_date": pr_merged,
                "linked_issue_number": i,
                "milestone": random.choice(["v1.0", "v1.1", "v1.2"]),
                "review": {"review_type": "APPROVE", "reviewer_comment": "Looks good; add a regression test."}
            })

    prs["metadata"]["count"] = len(prs["prs"])

    with open(OUT_ISSUES, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2)
    with open(OUT_PRS, "w", encoding="utf-8") as f:
        json.dump(prs, f, indent=2)

    print(f"Wrote {OUT_ISSUES} ({len(issues['issues'])} issues) and {OUT_PRS} ({len(prs['prs'])} prs)")


if __name__ == "__main__":
    main()
