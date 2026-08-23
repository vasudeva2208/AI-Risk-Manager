import json

print("=== CHECKING THRESHOLD & COST ARTIFACTS ===")
with open("ml/evaluation/results/threshold_analysis.json", "r") as f:
    ta = json.load(f)

print("HGB Threshold Analysis (Validation Set):")
for t in ta.get('hgb_thresholds', []):
    if t['threshold'] in [0.20, 0.25, 0.30, 0.35, 0.40]:
        print(f"  T={t['threshold']:.2f} | Val Net Benefit INR: {t.get('net_benefit_inr', 0):,.2f} | Precision: {t['precision']*100:.2f}% | Recall: {t['recall']*100:.2f}% | F1: {t['f1_score']:.4f}")

with open("ml/evaluation/results/cost_sensitivity.json", "r") as f:
    cs = json.load(f)

print("\nCost Sensitivity Scenarios (Validation Data):")
for s in cs.get('scenarios', []):
    print(f"  FP Cost: {s['fp_cost_inr']:,.2f} INR (${s['fp_cost_usd']:.2f} USD) -> Optimal T={s['optimal_threshold_hgb']:.2f}, Max Benefit INR: {s['max_benefit_inr']:,.2f}")
