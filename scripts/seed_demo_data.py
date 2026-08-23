"""
Demo Data Seeder for Development and Hackathon Demonstration.

Loads synthetic records and runs them through the complete risk assessment pipeline
so that the live database has active review queue items, resolved cases, and chained audit logs.
Explicitly labelled as SYNTHETIC DEMO DATA.
"""

import os
import sys
import datetime
import pandas as pd
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.schemas.domain import (
    CustomerBase,
    OrderBase,
    ReturnRequestBase,
    RiskAssessmentRequest,
    ProductCategory,
    PaymentMethod,
    ReturnReason,
    ItemCondition,
    HumanDecisionSubmission,
    HumanDecisionType,
    UserRole,
)
from backend.app.services.risk_service import RiskService
from backend.app.services.review_service import ReviewService
from ml.data.generator import generate_synthetic_return_dataset


def seed_demo_database(num_records: int = 40):
    print("=" * 70)
    print("SEEDING AI RISK MANAGER DEMO DATABASE")
    print("=" * 70)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    risk_svc = RiskService(db)
    review_svc = ReviewService(db)

    print(f"\n[1/3] Generating {num_records} realistic demo cases...")
    df = generate_synthetic_return_dataset(num_samples=num_records, random_seed=101)

    created_assessments = []

    print("\n[2/3] Processing cases through Risk Assessment Engine...")
    for idx, row in df.iterrows():
        order_ts = datetime.datetime.fromisoformat(row["order_timestamp"])
        del_ts = datetime.datetime.fromisoformat(row["delivery_timestamp"])
        req_ts = datetime.datetime.fromisoformat(row["request_timestamp"])

        cust = CustomerBase(
            customer_id=row["customer_id"],
            account_age_days=int(row["customer_account_age_days"]),
            total_order_count=int(row["customer_order_count_lifetime"]),
            historical_return_count=int(row["customer_return_count_lifetime"]),
            historical_return_rate=float(row["historical_return_rate"]),
            historical_refund_amount=float(row["historical_refund_amount"]),
            historical_dispute_count=int(row["customer_dispute_count"]),
            orders_last_7d=int(row.get("orders_last_7d", 1)),
            orders_last_30d=int(row["orders_last_30d"]),
            orders_last_90d=int(row.get("orders_last_90d", 3)),
            returns_last_7d=int(row.get("returns_last_7d", 0)),
            returns_last_30d=int(row["returns_last_30d"]),
            returns_last_90d=int(row["returns_last_90d"]),
            customer_avg_order_value=float(row["customer_avg_order_value"]),
        )

        order = OrderBase(
            order_id=row["order_id"],
            customer_id=row["customer_id"],
            order_timestamp=order_ts,
            order_amount=float(row["order_amount"]),
            item_count=int(row["item_count"]),
            product_category=ProductCategory(row["product_category"]),
            discount_amount=float(row["discount_amount"]),
            payment_method=PaymentMethod(row["payment_method"]),
            delivery_region=row["delivery_region"],
            fulfillment_method=row["fulfillment_method"],
            delivery_timestamp=del_ts,
        )

        ret_req = ReturnRequestBase(
            return_id=row["return_id"],
            order_id=row["order_id"],
            request_timestamp=req_ts,
            return_reason=ReturnReason(row["return_reason"]),
            item_condition_declared=ItemCondition(row["item_condition_declared"]),
            refund_amount_requested=float(row["refund_amount_requested"]),
            return_method=row["return_method"],
        )

        req = RiskAssessmentRequest(
            customer=cust,
            order=order,
            return_request=ret_req,
            idempotency_key=f"SEED_DEMO_{row['return_id']}",
            target_currency="INR",
        )

        res = risk_svc.assess_return_risk(req)
        created_assessments.append(res)

    print(f"  -> Successfully evaluated {len(created_assessments)} risk assessments.")

    # 3. Simulate resolving some human review cases
    print("\n[3/3] Simulating historical human review analyst decisions...")
    pending_cases = review_svc.list_review_cases()
    resolved_count = 0

    for i, case in enumerate(pending_cases[:8]):
        if i % 2 == 0:
            decision = HumanDecisionSubmission(
                decision=HumanDecisionType.APPROVE_RETURN,
                reason="Customer provided valid purchase receipt and packaging photos verified.",
                reviewer_id="ANALYST_PRIYA",
                reviewer_role=UserRole.RISK_ANALYST,
            )
        else:
            decision = HumanDecisionSubmission(
                decision=HumanDecisionType.REQUEST_ADDITIONAL_VERIFICATION,
                reason="High return velocity spike. Requested physical return drop-off at partner hub.",
                reviewer_id="ANALYST_RAHUL",
                reviewer_role=UserRole.RISK_ANALYST,
            )
        try:
            review_svc.submit_human_decision(case.case_id, decision)
            resolved_count += 1
        except Exception as e:
            pass

    print(f"  -> Resolved {resolved_count} sample review cases.")
    
    # Verify audit chain integrity
    ver = risk_svc.audit.verify_audit_chain()
    print(f"\nAudit Chain Status: {ver.status} ({ver.total_events_checked} events cryptographically chained)")
    print("=" * 70)


if __name__ == "__main__":
    seed_demo_database()
