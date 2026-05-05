#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from textwrap import dedent

SOURCE = Path("/Users/bhriguverma/code/localllmapplication/finanace/issues.json")
OUTPUT = Path("/Users/bhriguverma/code/localllmapplication/finanace/realistic-micro-finance")

CYCLE_NOTES = [
    "The branch team raised it while closing out the morning queue.",
    "It showed up after a slow retry in the afternoon payment run.",
    "Support brought it back after comparing the report with the ledger export.",
    "Someone spotted it while reconciling backdated entries for month end.",
    "It came up during a training run on a staging account.",
]

LOCATIONS = [
    "NAGPUR-02",
    "PUNE-01",
    "AURANGABAD-03",
    "NASHIK-02",
    "SOLAPUR-01",
]

REPORTER_LINES = {
    "DEV_A": "I ran into this while checking the branch queue.",
    "DEV_B": "This came up after a second pass through the form.",
    "DEV_C": "I could reproduce it from the office side as well.",
    "DEV_D": "I saw the same thing while reviewing the customer record.",
}

REVIEWER_LINES = [
    "I can reproduce this locally. The problem looks like it is in the validation path, not the save itself.",
    "Thanks for the detail. I checked the flow and the edge case is real.",
    "This is consistent with what support described. The current behavior needs a guardrail.",
    "I have a short fix in mind, but I want one regression test around the edited path first.",
]

DEV_BY_AUTHOR = {
    "DEV_A": "Anita",
    "DEV_B": "Bhavesh",
    "DEV_C": "Chitra",
    "DEV_D": "Deepak",
}


def repeated_context(number: int) -> str:
    return CYCLE_NOTES[(number - 1) // 14]


def location_for(number: int) -> str:
    return LOCATIONS[(number - 1) % len(LOCATIONS)]


def cycle_for(number: int) -> int:
    return ((number - 1) // 14) + 1


def theme_for(issue: dict) -> str:
    labels = set(issue.get("labels", []))
    title = issue.get("title", "").lower()
    if "loan" in labels or "guarantor" in title:
        return "loan_bug" if "bug" in labels else "loan_enhancement"
    if "payment" in labels:
        return "payment_bug" if "bug" in labels else "payment_enhancement"
    if "ledger" in labels:
        return "ledger_bug" if "bug" in labels else "ledger_enhancement"
    if "receipt" in labels:
        return "receipt_bug" if "bug" in labels else "receipt_enhancement"
    if "client" in labels:
        return "client_bug" if "bug" in labels else "client_enhancement"
    if "savings" in labels:
        return "savings_bug"
    if "group" in labels:
        return "group_bug"
    if "question" in labels:
        return "approval_question"
    if "docs" in labels:
        return "docs_task"
    return "general"


def build_title(issue: dict) -> str:
    number = issue["number"]
    theme = theme_for(issue)
    location = location_for(number)
    cycle = cycle_for(number)

    mapping = {
        "loan_bug": [
            "Loan edit form crashes when guarantors are cleared",
            "Loan save path fails if the guarantor list is empty",
            "Editing a loan without guarantors throws a server error",
        ],
        "loan_enhancement": [
            "Add a preview panel before final loan submission",
            "Show the installment breakdown before saving a loan",
            "Surface loan terms earlier in the approval flow",
        ],
        "payment_bug": [
            "Duplicate payment can slip through on retry",
            "Retrying a payment can create a zero-value row",
            "A second submit can record the same payment twice",
        ],
        "payment_enhancement": [
            "Add clearer payment hints for branch operators",
            "Improve the guidance shown on the payment form",
            "Make the payment entry copy easier to follow",
        ],
        "ledger_bug": [
            "Ledger totals no longer match the receipt summary",
            "Month-end ledger export drifts after a receipt is removed",
            "Ledger roll-up is off by one after receipt cleanup",
        ],
        "ledger_enhancement": [
            "Add optional branch filtering to the ledger export",
            "Let the ledger export be filtered by branch",
            "Make the ledger report accept a branch filter",
        ],
        "receipt_bug": [
            "Receipt list shows a duplicate row after retry",
            "Receipt grid renders the same item twice after a failed print",
            "Receipt listing duplicates an entry after resubmission",
        ],
        "receipt_enhancement": [
            "Add a reprint action to the receipt list",
            "Allow receipts to be reprinted from the list view",
            "Put a reprint shortcut on the receipt table",
        ],
        "client_bug": [
            "Client edit form drops the selected branch after saving",
            "Saving a client can reset the branch selection",
            "Client update path loses the branch choice",
        ],
        "client_enhancement": [
            "Remember the last branch in client search",
            "Keep the last branch selected for client lookups",
            "Persist the branch choice between client searches",
        ],
        "savings_bug": [
            "Savings withdrawal can go negative after an edit",
            "Editing a savings transaction can bypass the balance check",
            "Partial savings edits can save an overdrawn amount",
        ],
        "group_bug": [
            "Approved group loan still shows the old rate",
            "Group approval preview does not refresh the interest rate",
            "Group loan rate lags behind the approval change",
        ],
        "approval_question": [
            "Should we document the branch approval flow?",
            "Do we need a short guide for loan approvals?",
            "Can we document the approval path for branch staff?",
        ],
        "docs_task": [
            "Docs: add setup notes for local branch testing",
            "Docs: fill in the missing local setup steps",
            "Docs: improve the branch testing instructions",
        ],
    }

    return mapping.get(theme, [issue.get("title", "")])[(cycle - 1) % 3]


def build_body(issue: dict) -> str:
    number = issue["number"]
    theme = theme_for(issue)
    location = location_for(number)
    context = repeated_context(number)
    context_clause = (context[0].lower() + context[1:]).rstrip(".")
    reported_note = f"{DEV_BY_AUTHOR.get(issue.get('filed_by_developer', ''), 'A teammate')} noted that {context_clause}"
    cycle = cycle_for(number)
    reported_by = DEV_BY_AUTHOR.get(issue.get("filed_by_developer", ""), "A teammate")

    if theme == "loan_bug":
        return dedent(f"""
        A branch operator reported this while editing an active loan record in the branch desk workflow. The form loads normally, but once the guarantor list is cleared the save action fails with a 500 and the operator loses the changes they were making.

        Steps to reproduce:
        1. Open an existing loan from the branch queue.
        2. Remove every guarantor from the record.
        3. Save the form without adding a replacement.

        Expected:
        The form should stop the save, explain what is missing, and keep the record on screen.

        Actual:
        The request falls through to an unhandled error and the user gets bounced back to the list view.

        Notes:
        {reported_note}. It is reproducible on {location} and the failure shows up before any database write is completed.
        """).strip()

    if theme == "loan_enhancement":
        return dedent(f"""
        The loan entry flow would be easier to review if the operator could see the repayment preview before the final submit. At the moment the team has to rely on the office calculator or re-open the record after saving, which adds a lot of back-and-forth on busy days.

        Desired behavior:
        Show the amount, tenure, interest breakdown, and the first due date before the loan is committed.

        Why this came up:
        {reported_note}. The team said the current flow is accurate, but it is not especially easy to verify at the counter.

        Discussion notes:
        A lightweight preview should be enough here; it does not need to change the save behavior or the underlying repayment logic.
        """).strip()

    if theme == "payment_bug":
        return dedent(f"""
        One of the payment clerks hit this while resubmitting a payment after the page paused on a slow connection. The first click goes through, but a second submit can create a zero-value entry that still looks like a normal payment in the history panel.

        Steps to reproduce:
        1. Open a payment form for an existing account.
        2. Submit it once, then immediately retry from the browser or by clicking again.
        3. Check the saved entry in the list view.

        Expected:
        The second submit should be rejected as a duplicate.

        Actual:
        A second row is created and the amount is not what the operator entered.

        Notes:
        {reported_note}. This only seems to happen when the browser stays responsive long enough for the duplicate click to land.
        """).strip()

    if theme == "payment_enhancement":
        return dedent(f"""
        The payment form is functional, but a few branch staff asked for better inline guidance around date entry and rounding. Right now the field labels are clear if you already know the process, but a newer operator can still hesitate at the counter and ask for help.

        Desired outcome:
        Make the hints more explicit without changing the validation rules.

        Why now:
        {reported_note}. This showed up most clearly during a training session where the operator knew the numbers but not the exact format the form expected.

        Discussion notes:
        Small helper text would probably solve most of this. There is no need to redesign the entire page.
        """).strip()

    if theme == "ledger_bug":
        return dedent(f"""
        After a receipt is removed or marked inactive, the month-end ledger export no longer matches the receipt summary that the branch uses for reconciliation. The mismatch is small at first, but it becomes obvious once the team compares the totals side by side.

        Steps to reproduce:
        1. Open a branch with a few backdated entries.
        2. Remove one stale receipt from the report set.
        3. Compare the summary total with the detailed ledger export.

        Expected:
        Both views should show the same totals for the same date range.

        Actual:
        One of the totals shifts and the team ends up reconciling the report by hand.

        Notes:
        {reported_note}. The issue is easiest to see in {location} because the branch has enough history to make the drift visible.
        """).strip()

    if theme == "ledger_enhancement":
        return dedent(f"""
        The ledger export would be more useful if the branch code could be supplied as an optional filter. Right now the office exports the full report and trims it in a spreadsheet, which is workable but slow when they only need one location.

        Acceptance criteria:
        - the branch filter should be optional
        - the report should behave exactly as it does today when the filter is blank
        - the PDF layout should not change

        Notes:
        {reported_note}. This came up while the team was preparing a month-end packet and trying to pull only {location}.
        """).strip()

    if theme == "receipt_bug":
        return dedent(f"""
        A failed print or retry flow can leave the receipt table showing the same row twice. The duplicate does not exist in the database, which made the first report confusing because the operator assumed the data had been written twice.

        Steps to reproduce:
        1. Open the receipt list.
        2. Start a print or action flow that takes long enough to retry.
        3. Refresh the page immediately after the first attempt fails.

        Expected:
        One row per receipt.

        Actual:
        The same receipt is rendered twice until the page is refreshed again.

        Notes:
        {reported_note}. This looks like a front-end rendering problem more than a persistence issue.
        """).strip()

    if theme == "receipt_enhancement":
        return dedent(f"""
        Support asked for a quicker way to reprint receipts from the list view. At the moment the operator has to open the record first, which is fine for a short queue but awkward when the desk is busy and the customer is still standing there.

        Requested behavior:
        Add a reprint action to each row or the row menu.

        Notes:
        {reported_note}. The team wants this to stay lightweight so it does not crowd the screen on smaller laptops.
        """).strip()

    if theme == "client_bug":
        return dedent(f"""
        Editing a client record can unexpectedly reset the selected branch if the operator touches the address fields first. The record saves, but when it is reopened the branch has fallen back to the default and the staff member has to correct it manually.

        Steps to reproduce:
        1. Open a client profile.
        2. Update the address details.
        3. Change the branch and save.
        4. Re-open the record and check the selected branch.

        Expected:
        The branch choice should stay attached to the client record.

        Actual:
        The selection is lost during the save path.

        Notes:
        {reported_note}. This is most visible when the record is edited quickly between two separate tasks.
        """).strip()

    if theme == "client_enhancement":
        return dedent(f"""
        Branch users asked for the client lookup screen to remember the last branch they were working in. It is a small change, but it would remove a lot of repeated selection work for staff who stay on one branch throughout the day.

        Request:
        Persist the branch choice per session or per user, so the next lookup starts from the same place.

        Notes:
        {reported_note}. The current flow is usable, but it adds friction every time a new search begins.
        """).strip()

    if theme == "savings_bug":
        return dedent(f"""
        A savings transaction can be edited into an overdrawn state if the operator reopens an existing entry instead of entering a fresh one. The original save path checks the balance, but the edit path does not appear to re-run the same guard.

        Steps to reproduce:
        1. Open an existing savings withdrawal.
        2. Change the amount without adjusting the available balance.
        3. Save the record again.

        Expected:
        The balance check should still block the edit.

        Actual:
        The edit is accepted and the ledger ends up negative.

        Notes:
        {reported_note}. The issue is visible on the edit flow, not on first-time entry.
        """).strip()

    if theme == "group_bug":
        return dedent(f"""
        When a group loan moves from pending to approved, the preview pane can keep showing the previous rate until the page is reloaded. That makes the first review misleading and the branch manager has to stop and refresh before they can trust the numbers.

        Steps to reproduce:
        1. Open a pending group loan.
        2. Approve it.
        3. Watch the preview area without refreshing.

        Expected:
        The interest rate should update as soon as the approval is saved.

        Actual:
        The old rate remains visible until the browser is refreshed.

        Notes:
        {reported_note}. The behavior is subtle, but it is enough to slow down approvals in {location}.
        """).strip()

    if theme == "approval_question":
        return dedent(f"""
        We keep getting the same support question about where loan approvals live and which screen records the history. The team knows the workflow, but branch staff keep asking for a simple reference they can use without calling the office.

        Question:
        Should we document the approval flow in the main guide, or is there already a better place for it?

        Context:
        {reported_note}. A concise explanation would probably save a lot of repeat support questions.

        Discussion:
        The answer does not need to be technical; it just needs to tell people where to look and what they are allowed to do.
        """).strip()

    if theme == "docs_task":
        return dedent(f"""
        The setup notes are missing a few steps that matter when someone is trying to run the app against a local test branch. The main install instructions are there, but the handoff from install to first branch test still leaves people guessing.

        Scope:
        Add the missing local setup notes and a short troubleshooting section for branch testing.

        Notes:
        {reported_note}. The gap shows up most often when a new team member is trying to compare a local run with the branch office workflow.
        """).strip()

    return issue.get("body", "").strip()


def build_comments(issue: dict) -> list:
    comments = []
    number = issue["number"]
    authors = [c.get("author_developer", "DEV_A") for c in issue.get("comments", [])]
    dates = [c.get("date") for c in issue.get("comments", [])]
    count = max(1, len(issue.get("comments", [])))
    title = issue.get("title", "").lower()

    reporter_opening = {
        "DEV_A": "I can confirm this from the desk side.",
        "DEV_B": "I reproduced it while testing the same flow again.",
        "DEV_C": "I saw the same behavior in the branch queue.",
        "DEV_D": "I checked the record and the problem is real.",
    }

    if count == 1:
        # Single comment issues usually read like a quick note or a triage update.
        author = authors[0] if authors else "DEV_D"
        comment_body = {
            "DEV_A": "This is worth fixing soon because it affects the day-to-day counter flow.",
            "DEV_B": "I have a small fix in mind, but I want to add coverage for the edit path.",
            "DEV_C": "We should keep the change narrow so it does not affect the existing workflow.",
            "DEV_D": "I can reproduce this, and it looks limited to the branch-facing path.",
        }[author]
        comments.append({"author_developer": author, "date": dates[0] if dates else None, "body": comment_body})
        return comments

    first_author = authors[0] if authors else "DEV_D"
    second_author = authors[1] if len(authors) > 1 else "DEV_B"

    if first_author == "DEV_D":
        first = "I checked this against a live record and the failure is consistent with the report."
    elif first_author == "DEV_C":
        first = "I can reproduce the issue and it happens before the operator gets any useful feedback."
    elif first_author == "DEV_B":
        first = "I hit the same edge case after retrying the action, so the report looks accurate."
    else:
        first = "I saw the same problem and it does not seem tied to a one-off data problem."

    second = REVIEWER_LINES[(number - 1) % len(REVIEWER_LINES)]
    comments.append({"author_developer": first_author, "date": dates[0] if dates else None, "body": first})
    comments.append({"author_developer": second_author, "date": dates[1] if len(dates) > 1 else None, "body": second})

    if count > 2:
        comments.append({
            "author_developer": "DEV_A",
            "date": dates[2] if len(dates) > 2 else None,
            "body": "Please keep the fix focused and make sure the edited path is covered by a regression test.",
        })

    return comments[:count]


def convert_issue(issue: dict) -> dict:
    converted = {
        "number": issue["number"],
        "title": build_title(issue),
        "body": build_body(issue),
        "labels": issue.get("labels", []),
        "state": issue.get("state", "open"),
        "filed_by_developer": issue.get("filed_by_developer"),
        "created_date": issue.get("created_date"),
        "closed_date": issue.get("closed_date"),
        "closed_reason": issue.get("closed_reason"),
        "linked_pr_number": issue.get("linked_pr_number"),
        "milestone": issue.get("milestone"),
        "comments": build_comments(issue),
    }
    return converted


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    issues = data.get("issues", [])

    converted = [convert_issue(issue) for issue in issues]
    repo_data = {
        "metadata": {
            "target_issues": len(converted),
            "start_issues_date": data.get("metadata", {}).get("start_issues_date"),
            "end_issues_date": data.get("metadata", {}).get("end_issues_date"),
            "notes": "Cleaned issue archive with natural-sounding support and engineering discussion."
        },
        "issues": converted,
    }

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    (OUTPUT / "README.md").write_text(
        dedent("""
        # Micro Finance Issue Archive

        This repository contains a cleaned, natural-language version of the historical issue archive.
        The issue bodies and discussion threads are rewritten to read like real support and engineering
        conversation, while preserving the original dates, labels, and issue numbering.

        Files:
        - `issues.json`: cleaned issue archive
        - `README.md`: repo overview
        """).strip() + "\n",
        encoding="utf-8",
    )
    (OUTPUT / ".gitignore").write_text("__pycache__/\n.DS_Store\n", encoding="utf-8")
    (OUTPUT / "issues.json").write_text(json.dumps(repo_data, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote cleaned repo to {OUTPUT}")
    print(f"Issues: {len(converted)}")


if __name__ == "__main__":
    main()
