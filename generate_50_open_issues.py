import json
from random import Random

r = Random(20260505)
components = ["API","Ledger","UI","Export","Import","Auth","Database","Reconciliation","Reporting","Notifications"]
labels_pool = ["bug","enhancement","performance","documentation","backend","frontend","database","good first issue","critical","security"]

issues = []
for i in range(50):
    comp = r.choice(components)
    num = 200 + i
    title = f"{r.choice(['fix','perf','chore','docs','feat'])}: {comp} issue {i+1} - {r.choice(['slow response','incorrect calculation','edge-case failure','missing translation','timeouts'])}"
    body = (
        f"Observed a problem in {comp}. Steps to reproduce:\n1) Prepare dataset\n2) Run the {comp.lower()} flow\n3) Observe failure.\n\nExpected: {comp} should handle this gracefully.\n\nNotes: This was seen in Dec 2023 testing and reproduced in staging."
    )
    labels = r.sample(labels_pool, k=2)
    comments = [
        {"body": "I can reproduce this locally; collecting logs."},
        {"body": "Assigning to backend to investigate index and query plans."}
    ]
    issues.append({
        "number": num,
        "title": title,
        "body": body,
        "labels": labels,
        "assignees": [],
        "state": "open",
        "created_date": "2023-12-20T10:00:00Z",
        "comments": comments
    })

with open('issues_50_open.json', 'w', encoding='utf-8') as f:
    json.dump({"issues": issues}, f, indent=2)
print('Wrote issues_50_open.json (50 issues)')
