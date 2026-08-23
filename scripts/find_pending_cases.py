import sqlite3

conn = sqlite3.connect("risk_manager.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT r.case_id, r.assessment_id, r.return_id, r.status, a.risk_probability, a.expected_loss
    FROM review_cases r
    JOIN risk_assessments a ON r.assessment_id = a.assessment_id
    WHERE r.status = 'PENDING_REVIEW'
    LIMIT 5
""")

rows = cursor.fetchall()
print(f"Found {len(rows)} pending review cases:")
for row in rows:
    print(f"Case ID: {row[0]}, Assessment: {row[1]}, Return: {row[2]}, Status: {row[3]}, Prob: {row[4]:.4f}, Expected Loss: {row[5]}")

conn.close()
