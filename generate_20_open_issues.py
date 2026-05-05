#!/usr/bin/env python3
"""Generate 20 open issues (2024-2026) to add to the repo."""
import json
from datetime import datetime, timedelta
import random

random.seed(123)

TOKENS = ["TOKEN_1", "TOKEN_2", "TOKEN_3", "TOKEN_4"]
LABEL_BANK = [
    "bug", "enhancement", "performance", "documentation", "good first issue",
    "help wanted", "question", "critical", "backend", "frontend", "database",
]

TITLE_TEMPLATES = [
    "{component} shows incorrect calculation with decimal precision",
    "API endpoint {endpoint} returns 500 error under concurrent load",
    "{feature} missing validation for edge case {edge_case}",
    "Database query {query} takes {time}ms instead of target {target}ms",
    "UI component {component} not responsive on mobile devices",
    "{service} memory leak when processing {scenario}",
    "Authentication fails when {condition}",
    "Documentation {doc} is outdated and needs refresh",
    "{feature} should support {capability}",
    "Test coverage for {module} is below 80%",
]

COMPONENTS = [
    "Ledger posting", "Receipt processing", "Payment gateway", "Client onboarding",
    "Savings withdrawal", "Loan approval", "Group management", "Reconciliation engine",
    "Export utility", "Dashboard", "Search", "Reporting"
]

FEATURES = [
    "bulk processing", "real-time sync", "offline mode", "audit logging",
    "multi-currency", "webhooks", "API rate limiting", "caching layer"
]

EDGE_CASES = [
    "zero amount", "negative balance", "duplicate transaction", "timezone change",
    "concurrent update", "deleted reference", "null value", "overflow"
]

SCENARIOS = [
    "high transaction volume", "large CSV imports", "batch reconciliation",
    "concurrent API calls", "long-running reports"
]

CONDITIONS = [
    "using OAuth with certain providers",
    "password contains special characters",
    "email domain is delegated",
    "MFA is enabled"
]

ENDPOINTS = ["POST /transfers", "GET /balance", "DELETE /account", "PATCH /profile"]
QUERIES = ["account balance lookup", "transaction history", "group member listing"]
TIMES = ["500", "1200", "800", "2000"]
TARGETS = ["100", "200", "300", "150"]
MODULES = ["core.ledger", "api.payments", "models.client", "services.reconciliation"]
DOCS = ["setup guide", "API reference", "migration notes", "troubleshooting FAQ"]
CAPABILITIES = ["webhooks", "bulk import", "custom filters", "export to CSV"]

def generate_issue_title():
    template = random.choice(TITLE_TEMPLATES)
    kwargs = {}
    
    if "{component}" in template:
        kwargs["component"] = random.choice(COMPONENTS)
    if "{endpoint}" in template:
        kwargs["endpoint"] = random.choice(ENDPOINTS)
    if "{feature}" in template:
        kwargs["feature"] = random.choice(FEATURES)
    if "{edge_case}" in template:
        kwargs["edge_case"] = random.choice(EDGE_CASES)
    if "{query}" in template:
        kwargs["query"] = random.choice(QUERIES)
    if "{time}" in template:
        kwargs["time"] = random.choice(TIMES)
    if "{target}" in template:
        kwargs["target"] = random.choice(TARGETS)
    if "{service}" in template:
        kwargs["service"] = random.choice(COMPONENTS)
    if "{scenario}" in template:
        kwargs["scenario"] = random.choice(SCENARIOS)
    if "{condition}" in template:
        kwargs["condition"] = random.choice(CONDITIONS)
    if "{doc}" in template:
        kwargs["doc"] = random.choice(DOCS)
    if "{module}" in template:
        kwargs["module"] = random.choice(MODULES)
    if "{capability}" in template:
        kwargs["capability"] = random.choice(CAPABILITIES)
    
    return template.format(**kwargs)

def main():
    start = datetime(2024, 1, 1)
    end = datetime(2026, 5, 5)
    
    issues = {
        "metadata": {
            "generated": True,
            "count": 20,
            "state": "open",
            "span": [start.isoformat(), end.isoformat()]
        },
        "issues": []
    }
    
    for i in range(1, 21):
        # Random date between 2024-2026
        random_days = random.randint(0, (end - start).days)
        created_dt = start + timedelta(days=random_days)
        created_str = created_dt.strftime("%Y-%m-%dT%H:%M:%S")
        
        creator = random.choice(TOKENS)
        title = generate_issue_title()
        labels = random.sample(LABEL_BANK, k=random.randint(1, 3))
        
        issue = {
            "number": 100 + i,  # Starting from 100+ to avoid conflicts
            "title": title,
            "body": f"""## Summary
{title}

## Description
This is an open issue that needs investigation and resolution.

## Steps to reproduce
1. Identify the scenario
2. Observe the behavior
3. Compare to expected result

## Expected behavior
The system should handle this case gracefully.

## Actual behavior
Currently experiencing unexpected behavior as described.

## Environment
- Date discovered: {created_str}
- Status: Open for investigation
""",
            "labels": labels,
            "state": "open",
            "filed_by_developer": creator.replace('TOKEN_', 'DEV_'),
            "github_token_env": creator.replace('TOKEN_', 'GITHUB_TOKEN_'),
            "created_date": created_str,
            "closed_date": None,
            "closed_reason": None,
            "milestone": random.choice(["v2.0", "v2.1", "backlog", "future"]),
            "comments": [
                {
                    "by": creator,
                    "body": "Initial report. Needs triage and prioritization."
                },
                {
                    "by": random.choice([t for t in TOKENS if t != creator]),
                    "body": "Confirmed. This needs investigation in the next sprint."
                }
            ]
        }
        issues["issues"].append(issue)
    
    with open("issues_20_open.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2)
    
    print(f"✓ Generated 20 open issues in issues_20_open.json")

if __name__ == "__main__":
    main()
