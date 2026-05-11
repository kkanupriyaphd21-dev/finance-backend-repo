from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, List


CURRENT_BUCKET = "current"
WATCHLIST_BUCKET = "watchlist"
DELINQUENT_BUCKET = "delinquent"
SERIOUS_BUCKET = "serious"
CRITICAL_BUCKET = "critical"


@dataclass(frozen=True)
class LoanSnapshot:
    account_no: str
    borrower_name: str
    branch_code: str
    principal_outstanding: Decimal
    days_past_due: int = 0
    payment_count_30d: int = 0
    is_group_loan: bool = False
    risk_override: str = ""


@dataclass(frozen=True)
class CollectionAction:
    account_no: str
    borrower_name: str
    bucket: str
    action: str
    priority_score: int
    reason: str


def _safe_days(days_past_due: int) -> int:
    return max(int(days_past_due or 0), 0)


def delinquency_bucket(days_past_due: int) -> str:
    days = _safe_days(days_past_due)
    if days == 0:
        return CURRENT_BUCKET
    if days <= 7:
        return WATCHLIST_BUCKET
    if days <= 30:
        return DELINQUENT_BUCKET
    if days <= 60:
        return SERIOUS_BUCKET
    return CRITICAL_BUCKET


def recommended_action(days_past_due: int) -> str:
    bucket = delinquency_bucket(days_past_due)
    if bucket == CURRENT_BUCKET:
        return "monitor"
    if bucket == WATCHLIST_BUCKET:
        return "send_reminder"
    if bucket == DELINQUENT_BUCKET:
        return "call_borrower"
    if bucket == SERIOUS_BUCKET:
        return "field_visit"
    return "escalate_to_recovery"


def _balance_weight(principal_outstanding: Decimal) -> int:
    amount = Decimal(principal_outstanding or 0)
    if amount <= 0:
        return 0
    return min(int(amount // Decimal("100")), 500)


def priority_score(snapshot: LoanSnapshot) -> int:
    days = _safe_days(snapshot.days_past_due)
    score = days * 5
    score += _balance_weight(snapshot.principal_outstanding)
    if snapshot.is_group_loan:
        score += 12
    if snapshot.payment_count_30d == 0 and days > 0:
        score += 18
    if snapshot.risk_override == "force_escalation":
        score += 40
    elif snapshot.risk_override == "review":
        score += 10
    return score


def collection_reason(snapshot: LoanSnapshot) -> str:
    bucket = delinquency_bucket(snapshot.days_past_due)
    parts = [f"{snapshot.days_past_due} days past due -> {bucket}"]
    if snapshot.is_group_loan:
        parts.append("group loan")
    if snapshot.payment_count_30d == 0 and snapshot.days_past_due > 0:
        parts.append("no payment in 30 days")
    if snapshot.risk_override:
        parts.append(f"override={snapshot.risk_override}")
    return "; ".join(parts)


def build_collection_action(snapshot: LoanSnapshot) -> CollectionAction:
    return CollectionAction(
        account_no=snapshot.account_no,
        borrower_name=snapshot.borrower_name,
        bucket=delinquency_bucket(snapshot.days_past_due),
        action=recommended_action(snapshot.days_past_due),
        priority_score=priority_score(snapshot),
        reason=collection_reason(snapshot),
    )


def build_collection_plan(snapshots: Iterable[LoanSnapshot]) -> List[CollectionAction]:
    actions = [build_collection_action(snapshot) for snapshot in snapshots]
    return sorted(
        actions,
        key=lambda action: (-action.priority_score, action.bucket, action.account_no),
    )


def summarize_portfolio(snapshots: Iterable[LoanSnapshot]) -> Dict[str, object]:
    summary = {
        "accounts": 0,
        "total_outstanding": Decimal("0"),
        "current": 0,
        "watchlist": 0,
        "delinquent": 0,
        "serious": 0,
        "critical": 0,
    }

    for snapshot in snapshots:
        summary["accounts"] += 1
        summary["total_outstanding"] += Decimal(snapshot.principal_outstanding or 0)
        bucket = delinquency_bucket(snapshot.days_past_due)
        summary[bucket] += 1

    summary["risk_accounts"] = (
        summary["watchlist"] + summary["delinquent"] + summary["serious"] + summary["critical"]
    )
    return summary


def build_branch_report(branch_code: str, snapshots: Iterable[LoanSnapshot]) -> Dict[str, object]:
    branch_snapshots = [snapshot for snapshot in snapshots if snapshot.branch_code == branch_code]
    plan = build_collection_plan(branch_snapshots)
    summary = summarize_portfolio(branch_snapshots)
    return {
        "branch_code": branch_code,
        "summary": summary,
        "top_actions": plan[:10],
        "needs_escalation": any(action.action == "escalate_to_recovery" for action in plan),
    }
