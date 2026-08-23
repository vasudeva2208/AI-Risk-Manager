# Asymmetric Economic Cost Model Specification

> [!WARNING]
> **SYNTHETIC SCENARIO ASSUMPTIONS**  
> Cost parameters represent modeled merchant simulation assumptions and do not reflect observed accounting entries.

---

## 1. Mathematical Formulas & Cost Elements

$$\text{Expected Financial Loss} = P(\text{Abuse}) \times \left( \text{Refund Amount Requested} + C_{\text{Shipping}} \right)$$

### Economic Components:

1. **False Positive Cost ($C_{FP}$):**
   $$C_{FP} = C_{\text{Review Labor}} + C_{\text{Customer Friction}}$$
   * $C_{\text{Review Labor}} = \$15.00$ (₹1,245.00)
   * $C_{\text{Customer Friction}} = \$35.00$ (₹2,905.00) — Modeled lifetime value churn penalty.
   * Total $C_{FP} = \$50.00$ (₹4,150.00)

2. **False Negative Cost ($C_{FN}$):**
   $$C_{FN} = \text{Order Gross Amount} + C_{\text{Return Shipping \& Handling}}$$
   * $C_{\text{Return Shipping \& Handling}} = \$8.50$ (₹705.50)

3. **Manual Review Labor ($C_{\text{Review}}$):**
   * $\$15.00$ (₹1,245.00) per flagged return claim ($TP + FP$).

---

## 2. Global Economic Accounting Equations

1. **Baseline Unmitigated Loss (Do Nothing):**
   $$\text{Loss}_{\text{Baseline}} = \sum_{i \in \text{Actual Abuse}} (\text{Order Amount}_i + C_{\text{Shipping}})$$

2. **Gross Loss Prevented:**
   $$\text{Loss}_{\text{Prevented}} = \sum_{i \in TP} (\text{Order Amount}_i + C_{\text{Shipping}})$$

3. **Total Operational Cost:**
   $$\text{Cost}_{\text{Operational}} = \sum_{i \in FP} C_{FP} + \sum_{i \in FN} (\text{Order Amount}_i + C_{\text{Shipping}}) + \sum_{i \in (TP + FP)} C_{\text{Review}}$$

4. **Net Merchant Economic Benefit:**
   $$\text{Net Benefit} = \text{Loss}_{\text{Baseline}} - \text{Cost}_{\text{Operational}}$$

---

## 3. Review Volume Accounting Rule
$$\text{Review Volume} = TP + FP$$
All transactions flagged by the model at the operating threshold ($P \ge 0.30$) enter the triage workflow and incur review labor overhead.
