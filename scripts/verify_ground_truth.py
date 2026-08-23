import json
import sqlite3
import pandas as pd
import numpy as np
import os

print("=== 1. DATASET & TEMPORAL SPLIT VERIFICATION ===")
metadata_path = "ml/data/dataset_metadata.json"

with open(metadata_path, "r") as f:
    meta = json.load(f)

print(f"Metadata File: {metadata_path}")
print(f"Row Count: {meta.get('row_count')}")
print(f"Positive Count: {meta.get('positive_count')}")
print(f"Negative Count: {meta.get('negative_count')}")
print(f"Calculated Overall Prevalence: {meta.get('positive_count') / meta.get('row_count'):.4f} ({meta.get('positive_count') / meta.get('row_count') * 100:.2f}%)")
print(f"Reported Metadata Prevalence: {meta.get('prevalence'):.4f}")

# Check the actual CSV dataset
csv_path = "ml/data/return_abuse_dataset.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(f"\nActual CSV ({csv_path}):")
    print(f"Total Rows: {len(df)}")
    pos = int(df['is_abusive'].sum())
    neg = len(df) - pos
    print(f"Positives: {pos}")
    print(f"Negatives: {neg}")
    print(f"Overall Prevalence: {pos/len(df):.4f} ({pos/len(df)*100:.2f}%)")
    
    # Check splits
    df['request_timestamp'] = pd.to_datetime(df['request_timestamp'])
    df = df.sort_values('request_timestamp').reset_index(drop=True)
    train_df = df.iloc[:3500]
    val_df = df.iloc[3500:4250]
    test_df = df.iloc[4250:]
    
    print(f"\nTemporal Splits:")
    print(f"Train: N={len(train_df)}, Positives={train_df['is_abusive'].sum()}, Prev={train_df['is_abusive'].mean()*100:.2f}%, Max Time={train_df['request_timestamp'].max()}")
    print(f"Val: N={len(val_df)}, Positives={val_df['is_abusive'].sum()}, Prev={val_df['is_abusive'].mean()*100:.2f}%, Min Time={val_df['request_timestamp'].min()}, Max Time={val_df['request_timestamp'].max()}")
    print(f"Test: N={len(test_df)}, Positives={test_df['is_abusive'].sum()}, Prev={test_df['is_abusive'].mean()*100:.2f}%, Min Time={test_df['request_timestamp'].min()}, Max Time={test_df['request_timestamp'].max()}")
    print(f"Strict Ordering Valid: {train_df['request_timestamp'].max() < val_df['request_timestamp'].min() < val_df['request_timestamp'].max() < test_df['request_timestamp'].min()}")

print("\n=== 2. HELD-OUT EVALUATION ARTIFACTS ===")
model_comp_path = "frontend/public/evaluation_artifacts/model_comparison.json"
with open(model_comp_path, "r") as f:
    comp = json.load(f)

hgb = comp['models']['candidate_hist_gradient_boosting']
logreg = comp['models']['baseline_logistic_regression']

print("Champion (HGB) Metrics @ Opt Threshold:")
print(f"Optimal Threshold: {hgb['optimal_threshold']}")
metrics = hgb['metrics_at_opt_threshold']
cm = metrics['confusion_matrix']
print(f"Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
print(f"Recall: {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
print(f"F1: {metrics['f1_score']:.4f}")
print(f"PR-AUC: {metrics['pr_auc']:.4f}")
print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
print(f"Brier: {metrics['brier_score']:.4f}")
print(f"Confusion Matrix: TP={cm['true_positives']}, FP={cm['false_positives']}, FN={cm['false_negatives']}, TN={cm['true_negatives']}")
print(f"CM Sum: {cm['true_positives'] + cm['false_positives'] + cm['false_negatives'] + cm['true_negatives']}")
print(f"Actual Positives (TP+FN): {cm['true_positives'] + cm['false_negatives']}")
print(f"Actual Negatives (FP+TN): {cm['false_positives'] + cm['true_negatives']}")

print("\nBaseline (LogReg) Metrics @ Opt Threshold:")
print(f"Optimal Threshold: {logreg['optimal_threshold']}")
metrics_lr = logreg['metrics_at_opt_threshold']
cm_lr = metrics_lr['confusion_matrix']
print(f"Precision: {metrics_lr['precision']:.4f} ({metrics_lr['precision']*100:.2f}%)")
print(f"Recall: {metrics_lr['recall']:.4f} ({metrics_lr['recall']*100:.2f}%)")
print(f"F1: {metrics_lr['f1_score']:.4f}")
print(f"PR-AUC: {metrics_lr['pr_auc']:.4f}")
print(f"ROC-AUC: {metrics_lr['roc_auc']:.4f}")
print(f"Brier: {metrics_lr['brier_score']:.4f}")

print("\n=== 3. CONFIDENCE INTERVALS ARTIFACT ===")
ci_path = "frontend/public/evaluation_artifacts/confidence_intervals.json"
with open(ci_path, "r") as f:
    ci = json.load(f)
print(json.dumps(ci, indent=2))

print("\n=== 4. ECONOMIC MODEL VALUES IN ARTIFACT ===")
print("HGB Costs @ Opt Threshold:")
print(json.dumps(hgb['costs_at_opt_threshold'], indent=2))

print("\n=== 5. DEMO CASE IN DATABASE ===")
db_path = "risk_manager.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
    SELECT a.assessment_id, a.return_id, a.order_id, a.customer_id, a.risk_probability, a.risk_level, a.expected_loss, a.currency, a.model_recommendation, a.top_risk_factors_json, r.case_id, r.status, r.human_decision, r.decision_reason
    FROM risk_assessments a
    LEFT JOIN review_cases r ON a.assessment_id = r.assessment_id
    WHERE a.return_id = 'RET_E2E_99' OR a.assessment_id = 'ASSMT_6F3B808BCD72'
""")
demo_row = cur.fetchone()
if demo_row:
    print(f"Demo Case Found:")
    print(f"Assessment ID: {demo_row[0]}")
    print(f"Return ID: {demo_row[1]}")
    print(f"Order ID: {demo_row[2]}")
    print(f"Customer ID: {demo_row[3]}")
    print(f"Risk Probability: {demo_row[4]}")
    print(f"Risk Level: {demo_row[5]}")
    print(f"Expected Loss: {demo_row[6]} {demo_row[7]}")
    print(f"Policy Recommendation: {demo_row[8]}")
    print(f"Review Case ID: {demo_row[10]}")
    print(f"Review Status: {demo_row[11]}")
    print(f"Human Decision: {demo_row[12]}")
    print(f"Decision Reason: {demo_row[13]}")
else:
    print("Demo case NOT found in DB!")

print("\n=== 6. AUDIT CHAIN VERIFICATION ===")
cur.execute("SELECT COUNT(*) FROM audit_events")
total_events = cur.fetchone()[0]
print(f"Total Audit Events in DB: {total_events}")

from backend.app.services.audit import AuditService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine("sqlite:///./risk_manager.db")
Session = sessionmaker(bind=engine)
session = Session()
audit_service = AuditService(session)
verify_res = audit_service.verify_audit_chain()
print(f"Audit Chain Verification Status: {verify_res.status}")
print(f"Total Events Checked: {verify_res.total_events_checked}")
print(f"Message: {verify_res.message}")
print(f"Corrupted Event ID: {verify_res.corrupted_event_id}")
session.close()

conn.close()
