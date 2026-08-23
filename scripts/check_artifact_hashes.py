import hashlib
import os

files_to_check = [
    "ml/models/candidate/return-risk-hgb-v1.joblib",
    "ml/models/candidate/return-risk-hgb-v1_calibrated.joblib",
    "ml/models/baseline/return-risk-logreg-v1.joblib",
    "ml/models/baseline/return-risk-logreg-v1_calibrated.joblib",
    "ml/data/raw/synthetic_return_requests.csv",
    "ml/data/splits/train.csv",
    "ml/data/splits/val.csv",
    "ml/data/splits/held_out_test.csv",
    "ml/data/dataset_metadata.json",
    "ml/evaluation/results/model_comparison.json",
    "frontend/public/evaluation_artifacts/model_comparison.json"
]

print("=== GROUND TRUTH ARTIFACT INTEGRITY HASHES ===")
for f in files_to_check:
    if os.path.exists(f):
        with open(f, "rb") as fo:
            h = hashlib.sha256(fo.read()).hexdigest()
        print(f"{f}: {h[:16]}... ({os.path.getsize(f):,} bytes)")
    else:
        print(f"{f}: NOT FOUND")
