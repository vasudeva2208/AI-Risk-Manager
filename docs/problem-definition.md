# Problem Definition: E-Commerce Return Abuse & Friendly Return Fraud

## 1. Single Targeted Problem Scope
This system is dedicated exclusively to one clearly bounded financial loss problem:
**E-commerce Return Abuse / Friendly Return Fraud Risk Detection**.

In online retail, return abuse occurs when customers exploit return and refund policies for unfair financial gain or unentitled value, causing substantial operational, inventory, and margin loss.

### Target Behaviors Detected:
1. **Wardrobing / Free Renting:** Purchasing high-value items with the premeditated intent to use them briefly (e.g., events, social media) and return them for a full refund.
2. **False Claims / Empty Box / Missing Items:** Claiming an item was defective, not received, or missing from the box when the item was actually intact.
3. **Bracketing & Velocity Exploitation:** Ordering multiple high-value variants with abnormal historical return frequencies that exceed legitimate size-sampling norms.
4. **Reseller Arbitrage & Return Churn:** Buying inventory during flash sales or promotions, returning unsold stock at the merchant's expense.

---

## 2. Supervised Learning Target Definition

The target variable is a binary indicator:
$$\text{return\_abuse} \in \{0, 1\}$$

### Deterministic Labeling Rules (Ground Truth Formulation):
An historical return request is labeled positive (`return_abuse = 1`) if and only if **at least one** of the following verifiable historical conditions occurred during post-return warehouse processing or financial reconciliation:

1. **Physical Inspection Mismatch:** Warehouse inspection confirmed the returned package contained an empty box, incorrect item, counterfeit substitute, or deliberate damage not reported prior to shipping.
2. **Merchant Loss Recovery / Chargeback Contestation:** The return was followed by a contested chargeback where dispute evidence established fraudulent misrepresentation by the buyer.
3. **Confirmed Policy Violation:** Verified secondary proof that the merchandise was worn, altered, or used extensively prior to return when returned under "Unopened / New" condition.

Otherwise, the return is labeled negative (`return_abuse = 0`):
* Standard size/fit mismatches.
* Legitimate manufacturing defects confirmed upon inspection.
* Buyer remorse returns received in original, re-sellable condition.

---

## 3. Defense-Only Boundary
The system is constructed strictly to protect merchants. It is impossible to use this system to:
* Optimize evasion of merchant fraud filters.
* Adversarially discover threshold vulnerabilities.
* Generate automated synthetic refund requests.
* Provide user-facing bypass advice.

All model explanations, score factors, and risk assessments are strictly internal to authorized merchant risk analysts and compliance officers.

---

## 4. Class Imbalance & Economic Realities
* **Prevalence in Real E-Commerce:** Typically 3% to 8% of all returns exhibit abusive characteristics.
* **Cost Asymmetry:**
  * **False Positive (FP):** Inconveniences a high-value loyal customer, risking customer lifetime value (LTV) and loyalty ($C_{FP} \approx \$35-\$50$).
  * **False Negative (FN):** Merchant loses the product value + shipping + inspection labor + restocking write-down ($C_{FN} \approx \text{Item Price} + \$8.50$).
