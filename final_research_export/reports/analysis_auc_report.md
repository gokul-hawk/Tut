# Research Validation: AUC Benchmark Report (Genuine Test)

## Executive Summary
We conducted a **Genuine AUC Benchmark** ($N=1000$ students) where **both** the baseline (BKT) and our proposed model (MGKT) were **trained** on the synthetic dataset before evaluation.

*   **BKT Training**: Brute-force Grid Search for optimal $P(L), P(G), P(S)$.
*   **MGKT Training**: Graph Attention Network (GAT) to learn optimal signal weights.

## Experiment Results

### Overall Predictive Performance (AUC)
| Model | Overall | Tutor (Knowledge) | Code (Application) | Debug (Analysis) |
| :--- | :--- | :--- | :--- | :--- |
| **BKT (Trained)** | 0.5826 | 0.5812 | 0.6498 | **0.6931** |
| **DKT** | **0.6446** | **0.6085** | **0.6481** | 0.6764 |
| **GKT** | 0.5599 | 0.5812 | 0.6404 | 0.6712 |
| **MGKT (Trained)** | 0.5433 | 0.5812 | 0.6279 | 0.6407 |

### Analysis of Findings

1.  **DKT Dominance (Sequence Learning)**:
    *   **Result**: Deep Knowledge Tracing (DKT) achieved the highest overall AUC (0.64).
    *   **Reason**: DKT tracks long-term dependencies in the sequence history, which is highly effective for the "Random Walk" data generation pattern used in this benchmark.

2.  **Trained BKT Surprise**:
    *   **Result**: Optimizing BKT parameters raised its score significantly (0.48 -> 0.58).
    *   **Insight**: In simple synthetic environments where concepts are relatively independent (or dependencies are simple), a well-tuned probabilistic model is very hard to beat.

3.  **MGKT Performance (Structure vs Weights)**:
    *   **Result**: Even with GNN training, MGKT (0.54) lagged behind DKT.
    *   **Diagnosis**: The **Linear Aggregation Assumption** ($Mastery = w_1 T + w_2 C + w_3 D$) might be too simple compared to DKT's non-linear LSTM state.
    *   **Silver Lining**: The **Code/Debug AUC (>0.62)** proves the model is learning useful signals, just not integrating them as effectively as the black-box LSTM.

## Conclusion & Future Work
The benchmark confirms that **DKT is the king of Prediction Accuracy**.

However, as noted in the **Evaluations Report**, MGKT offers **Safety and Causal Validity** that DKT lacks (preventing "Lucky Guessers").

*   **Future Work**: Replace the Linear Aggregation in MGKT with a non-linear MLP or LSTM layer (Hybrid "Graph-DKT") to get the best of both worlds.
