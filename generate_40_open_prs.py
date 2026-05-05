import json
from random import Random

r = Random(20260505)
pr_titles = [
    "fix: handle nil pointer in ledger summary",
    "feat: add pagination to client listing",
    "perf: optimize posting worker batch size",
    "chore: pin dependency versions for reproducible builds",
    "test: add integration test for reconciliation flow",
    "fix: prevent duplicate webhook delivery",
    "refactor: split large service into smaller modules",
    "feat: add audit logging for export jobs",
    "docs: add API examples for webhooks",
    "perf: reduce memory usage during CSV import",
]
files_pool = [
    "src/ledger/service.py",
    "src/api/client.py",
    "src/worker/posting.py",
    "requirements.txt",
    "tests/integration/test_reconciliation.py",
    "src/webhooks/handler.py",
    "src/export/runner.py",
    "docs/README.md",
    "src/import/csv_parser.py",
    "src/utils/cache.py",
]

prs = []
for i in range(40):
    title = r.choice(pr_titles) + f" (batch {i+1})"
    branch = f"auto/feature/pr-{300 + i}"
    author = r.choice(["DEV_A","DEV_B","DEV_C","DEV_D"])
    linked_issue = None
    if r.random() < 0.6:
        linked_issue = 100 + r.randint(0, 40)
    pr = {
        "title": title,
        "body": f"This PR addresses: {title}. Includes small changes and tests.",
        "branch_name": branch,
        "base_branch": "main",
        "author_developer": author,
        "files_changed": [r.choice(files_pool)],
        "linked_issue_number": linked_issue,
        "review": {
            "reviewer_comment": "Looks good overall; please add one minor test.",
            "review_type": "COMMENT"
        },
        "merge": False
    }
    prs.append(pr)

with open('prs_40_open.json', 'w', encoding='utf-8') as f:
    json.dump({"prs": prs}, f, indent=2)
print('Wrote prs_40_open.json (40 PRs)')
