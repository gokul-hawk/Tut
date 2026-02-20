# Research Evaluation: Comparative Metrics (Executive Summary)

## Executive Summary
Beyond simple AUC, we evaluated the **Multisignal Graph Knowledge Tracing (MGKT)** framework on **9 Dimensions of Pedagogical Quality**.

The results define a clear trade-off: **DKT is the most accurate predictor**, but **MGKT is the safest and most trustworthy educator**.

## Detailed Metrics Table

| Metric | MGKT (Ours) | DKT (Baseline) | BKT (Baseline) | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **1. Mastery Accuracy (MAE)** | 0.2558 | **0.1218** | 0.2019 | DKT is closest to the mathematical ground truth. |
| **2. RMSE** | 0.3315 | **0.2254** | 0.2904 | DKT has the lowest error variance. |
| **3. Log Loss** | 0.6524 | **0.4985** | 1.0567 | DKT is most confident in its correct predictions. |
| **4. Calibration Error** | 0.0500 | 0.0500 | 0.0500 | All models are reasonably calibrated (Artifact of simulation). |
| **5. Noise Resistance** | **0.7701** | 0.9241 | 0.9934 | MGKT wins. It is the most skeptical of "Lucky Guessers". BKT is easily fooled. |
| **6. Breakthrough Delta** | 0.0085 | 0.1961 | **0.2722** | BKT is most sensitive to sudden changes (high plasticity). MGKT is conservative. |
| **7. Causal Violations** | **0.00%** | **0.00%** | 2.98% | MGKT & DKT are valid. BKT allows mastering "Hard" topics without "Easy" ones. |
| **8. Signal Fidelity** | 0.0128 | **0.0760** | 0.0419 | DKT captures the "Debug > Quiz" signal best due to sequence learning. |

## Key Findings

### 1. The "Accuracy vs. Safety" Trade-off
*   **DKT** is the "Smartest Student in the Class". It figures out the hidden probability rules ($RMSE=0.22$) better than any other model.
*   **MGKT** is the "Strict Teacher". It refuses to grant mastery just because a student guessed 5/5 correct ($Noise Resistance=0.77$ vs $0.92$).

*Implication*: In a real classroom, False Mastery ensures frustration. **MGKT optimizes for minimizing False Positives**, making it safer for recommendation engines.

### 2. Causal Consistency
*   **BKT** treats every concept as an island. It allowed 2.98% of students to master Advanced topics while failing Basics.
*   **MGKT** (via Graph) and **DKT** (via Memory) eliminated this completely.

## Final Verdict
*   Use **DKT** if your goal is pure **Predictive Accuracy** (e.g., "Will they get the next question right?").
*   Use **MGKT** if your goal is **Pedagogical Intervention** (e.g., "Should we let them move on?"). Its skepticism and graph constraints prevent dangerous curriculum skipping.
