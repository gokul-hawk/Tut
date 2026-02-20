# Implementation Plan - Real Simulators for Comparison

The user wants to replace "mock" classes in `simulate_full_comparison.py` with specific, rigorous algorithmic implementations for BKT and GKT, matching the level of detail we used for the "Real DKT" (NumPy RNN).

## User Review Required
> [!NOTE]
> This adds complexity to the simulation scripts but ensures the "Results" section of the paper is defensible as "Algorithmically Accurate" rather than "Heuristically Simulated."

## Proposed Changes

### 1. Create `backend/simulate_real_bkt.py`
*   Implement `RealBKT` class.
*   **Logic**: Full Bayesian Update formula.
    *   $P(L_t|Obs) \propto P(Obs|L_t) * P(L_t)$
    *   $P(L_{t+1}) = P(L_t|Obs) + (1 - P(L_t|Obs)) * P(T)$
*   **Constants**: Standard Corbet & Anderson parameters ($P(G)=0.2, P(S)=0.2, P(T)=0.1$).

### 2. Create `backend/simulate_real_gkt.py`
*   Implement `RealGKT` class.
*   **Logic**:
    *   **Self Update**: Uses Neural/Logistic update based on input ($y_t, c_t$).
    *   **Graph Update**: $h_{neighbor} = \alpha * h_{neighbor} + \beta * h_{target}$.
    *   Uses a simple adjacency matrix for the simulation concepts.

## Phase 5: GNN Training with GAT Layer

We are transitioning from heuristic weights ($0.25, 0.35, 0.40$) to a learned **Graph Attention Network (GAT)**.

### 5.1 GAT Architecture
*   **Input Features**: Stratified mastery vectors ($\text{Tutor}, \text{Code}, \text{Debug}$).
*   **Attention Mechanism**: Query-Key-Value attention to dynamically weight signal importance based on current student state.
*   **Propagation**: Message-passing over the Knowledge Graph to update "Readiness" scores of dependent concepts.
*   **Non-Linearity**: LeakyReLU activations to capture complex pedagogical transitions.

### 5.2 Training Workflow
1.  **Dataset**: Use the synthetic Graph Random Walk dataset.
2.  **Loss Function**: Binary Cross-Entropy (BCE) to minimize prediction error vs Ground Truth binary success.
3.  **Optimization**: Adam optimizer with a learning rate of $0.001$.
4.  **Artifact**: Save trained weights to `gnn_learned_weights.json`.

## Phase 6: Sensitivity & Ablation (Completed)
- [x] **Sensitivity Analysis**: Proven MGKT > BKT in noise resistance.
- [x] **Ablation Study**: Proven all components (Graph, Weights, Prereqs) are necessary.

## Phase 7: AUC Benchmark (Trained)
- [x] **Genuine Test**: Comparative AUC for BKT, DKT, GKT, and MGKT.
- [x] **Insight**: DKT is top for prediction; MGKT is top for pedagogical safety.

