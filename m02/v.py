"""Loan collections view-model helpers.

The repository is growing out of a generated scaffold. This module stays
framework-agnostic so the collections logic can be validated independently and
wired into Django views later.
"""

try:
	from .services import CollectionAction, LoanSnapshot, build_branch_report, build_collection_plan
except ImportError:  # pragma: no cover - direct execution fallback
	from services import CollectionAction, LoanSnapshot, build_branch_report, build_collection_plan


def build_collection_dashboard(branch_code, snapshots):
	plan = build_collection_plan(snapshots)
	report = build_branch_report(branch_code, snapshots)
	return {
		"branch_code": branch_code,
		"plan": plan,
		"summary": report["summary"],
		"needs_escalation": report["needs_escalation"],
	}


def next_collection_action(snapshots):
	plan = build_collection_plan(snapshots)
	return plan[0] if plan else None


def high_priority_actions(snapshots, minimum_score=60):
	return [action for action in build_collection_plan(snapshots) if action.priority_score >= minimum_score]

