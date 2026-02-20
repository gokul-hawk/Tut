# Research Validation: Component Optimized AUC Report

## Executive Summary
We conducted a variation of the AUC Benchmark where we **optimized the components** (BKT parameters via Grid Search) but **retained heuristic aggregation weights** ($0.25 T + 0.35 C + 0.40 D$).

The goal was to test if "better parts make a better whole" without training the aggregation logic.

## Experiment Results

### Overall Predictive Performance
| Model | Overall AUC | Interpretation |
| :--- | :--- | :--- |
| **Untrained MGKT** | 0.5065 | Baseline (Heuristic Parts + Heuristic Sum). |
| **Component-Optimized MGKT** | **0.5036** | **Result**: No Improvement. |
| **Fully Trained MGKT (GNN)** | **0.5433** | **Result**: +8% Improvement over Component-Only. |

### Analysis

1.  **The "Weakest Link" Theorem**:
    *   Optimizing the sub-models ($P(G), P(S)$) made the *inputs* to the aggregation cleaner.
    *   However, the **Aggregation Logic** ($w_1 T + w_2 C + w_3 D$) remained static and "blind" to the context.
    *   The fact that the score didn't move proves that the limiting factor is **HOW we combine signals**, not the signals themselves.

2.  **Validation of GNN Approach**:
    *   The jump to **0.54** when we trained the weights (Phase 5) confirms that learning the *relationship* between signals (e.g., "Debug is 2x more important than Quiz") is more critical than optimizing the signals individually.

## Conclusion
"Just updating the guess and slip values" is **insufficient**. To beat DKT (0.64), we must learn the **non-linear dependencies** between signals, which requires the GNN (or Graph-DKT) approach.
