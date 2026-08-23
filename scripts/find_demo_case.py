import sqlite3
import json

conn = sqlite3.connect("risk_manager.db")
cursor = conn.cursor()

# Find high-risk assessments with MANUAL_REVIEW policy recommendation and review case
cursor.execute("""
    SELECT 
        a.assessment_id, 
        a.return_id, 
        a.order_id, 
        a.customer_id, 
        a.risk_probability, 
        a.risk_level, 
        a.expected_loss, 
        a.currency, 
        a.model_recommendation, 
        a.top_risk_factors_json,
        r.case_id,
        r.status
    FROM risk_assessments a
    LEFT JOIN review_cases r ON a.assessment_id = r.assessment_id
    WHERE a.risk_level = 'HIGH' AND a.model_recommendation = 'MANUAL_REVIEW'
    ORDER BY a.risk_probability DESC
    LIMIT 5
""")

rows = cursor.fetchall()
print(f"Found {len(rows)} candidate demo cases:")
for row in rows:
    print("-" * 50)
    print(f"Assessment ID: {row[0]}")
    print(f"Return ID: {row[1]}")
    print(f"Order ID: {row[2]}")
    print(f"Customer ID: {row[3]}")
    print(f"Risk Probability: {row[4]:.4f} ({row[4]*100:.1f}%)")
    print(f"Risk Level: {row[5]}")
    print(f"Expected Loss: {row[6]} {row[7]}")
    print(f"Policy Recommendation: {row[8]}")
    print(f"Review Case ID: {row[10]} (Status: {row[11]})")
    factors = json.loads(row[9])
    print(f"Top Risk Factors ({len(factors)}):")
    for f in factors:
        print(f"  - {f.get('feature_name')}: {f.get('feature_value')} ({f.get('human_readable_reason')})")

conn.close()
