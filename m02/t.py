from decimal import Decimal
import unittest

try:
    from .services import LoanSnapshot, build_branch_report, build_collection_plan, delinquency_bucket, summarize_portfolio
    from .v import build_collection_dashboard, high_priority_actions, next_collection_action
except ImportError:  # pragma: no cover - direct execution fallback
    from services import LoanSnapshot, build_branch_report, build_collection_plan, delinquency_bucket, summarize_portfolio
    from v import build_collection_dashboard, high_priority_actions, next_collection_action


class CollectionPlanTests(unittest.TestCase):

    def setUp(self):
        self.snapshots = [
            LoanSnapshot(
                account_no="LN-001",
                borrower_name="Asha",
                branch_code="BR-01",
                principal_outstanding=Decimal("15000"),
                days_past_due=0,
                payment_count_30d=2,
            ),
            LoanSnapshot(
                account_no="LN-002",
                borrower_name="Bharat",
                branch_code="BR-01",
                principal_outstanding=Decimal("21000"),
                days_past_due=12,
                payment_count_30d=0,
            ),
            LoanSnapshot(
                account_no="LN-003",
                borrower_name="Charu",
                branch_code="BR-01",
                principal_outstanding=Decimal("9000"),
                days_past_due=67,
                payment_count_30d=0,
                is_group_loan=True,
                risk_override="force_escalation",
            ),
        ]

    def test_delinquency_bucket_mapping(self):
        self.assertEqual(delinquency_bucket(0), "current")
        self.assertEqual(delinquency_bucket(5), "watchlist")
        self.assertEqual(delinquency_bucket(18), "delinquent")
        self.assertEqual(delinquency_bucket(45), "serious")
        self.assertEqual(delinquency_bucket(90), "critical")

    def test_collection_plan_orders_highest_risk_first(self):
        plan = build_collection_plan(self.snapshots)

        self.assertEqual([action.account_no for action in plan], ["LN-003", "LN-002", "LN-001"])
        self.assertEqual(plan[0].action, "escalate_to_recovery")
        self.assertIn("override=force_escalation", plan[0].reason)

    def test_summary_counts_and_totals(self):
        summary = summarize_portfolio(self.snapshots)

        self.assertEqual(summary["accounts"], 3)
        self.assertEqual(summary["total_outstanding"], Decimal("45000"))
        self.assertEqual(summary["current"], 1)
        self.assertEqual(summary["delinquent"], 1)
        self.assertEqual(summary["critical"], 1)
        self.assertEqual(summary["risk_accounts"], 2)

    def test_branch_report_extracts_only_requested_branch(self):
        report = build_branch_report("BR-01", self.snapshots)

        self.assertEqual(report["branch_code"], "BR-01")
        self.assertTrue(report["needs_escalation"])
        self.assertEqual(report["summary"]["accounts"], 3)
        self.assertEqual(len(report["top_actions"]), 3)

    def test_dashboard_helpers_wrap_the_same_plan(self):
        dashboard = build_collection_dashboard("BR-01", self.snapshots)

        self.assertEqual(dashboard["branch_code"], "BR-01")
        self.assertEqual(dashboard["summary"]["accounts"], 3)
        self.assertEqual(next_collection_action(self.snapshots).account_no, "LN-003")
        self.assertEqual([action.account_no for action in high_priority_actions(self.snapshots, minimum_score=200)], ["LN-003", "LN-002"])


if __name__ == "__main__":
    unittest.main()
