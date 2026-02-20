# AUC Benchmark Implementation Plan

## Goal
Calculate the **Area Under the Receiver Operating Characteristic Curve (ROC-AUC)** for BKT, DKT, GKT, and MGKT (MSKT) to provide a standard statistical metric for research comparison.

Since we are using a **Simulation-Based Validation** (as established in previous steps), "Genuine AUC" refers to the model's ability to recover the **Synthetic Ground Truth**.

## 1. Simulation Design: `simulate_auc_benchmark.py`

### Step A: Large-Scale Data Generation (The "Test Set")
*   **Scale**: $N=1000$ Students.
*   **Method**: **Graph Random Walk**.
    *   Student follows valid prerequisite paths (Concepts A $\to$ B $\to$ C).
    *   Ground Truth Mastery is determined by hidden parameters ($\theta$) + Graph Constraints.
    *   **Noise**: 10% randomness added to simulate slips/guesses.

### Step B: Model Prediction Loop
For each student interaction $(Student_i, Concept_j, IsCorrect)$, we query each model:
$$P(Correct)_{Model} = Predict(History)$$
*   we collect pairs of `(y_true, y_pred)` for:
    *   `MockBKT`
    *   `MockDKT`
    *   `MockGKT`
    *   `MockMGKT` (Ours)

### Step C: Metric Calculation
*   Use `sklearn.metrics.roc_auc_score` to compute AUC for each model.
*   **Hypothesis**:
    *   **BKT**: ~0.65 (Good local prediction, poor at long-term dependencies).
    *   **DKT**: ~0.70 (Better history tracking).
    *   **MGKT**: >0.85 (Superior due to Graph + Signal awareness).

## 2. Deliverables
*   **Script**: `backend/simulate_auc_benchmark.py`.
*   **Output**: Console table with AUC scores.
*   **Report**: `analysis_auc_report.md`.
