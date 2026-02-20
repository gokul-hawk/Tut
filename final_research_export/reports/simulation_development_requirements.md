# Simulation Development Requirements Report

## 1. Executive Summary
While the **validation scenarios** (e.g., "Deep Struggle", "Instant Expert") are successfully implemented in `simulate_full_comparison.py`, the **generative training pipeline** described in the research is currently missing. To fully replicate the research methodology, we need to develop a system that generates synthetic data from the Knowledge Graph topology and trains the GNN weights, rather than relying on heuristics.

## 2. Missing Core Components

### A. Graph-Constrained Data Generator
*   **Current State**: Hand-coded scenarios (`generate_lucky_guesser_cases`).
*   **Research Requirement**: A Monte Carlo generator that produces $N=500$ trajectories using the formula:
    $$P(Success | V_i) = w_1 \cdot \theta_k + w_2 \cdot \left( \frac{1}{|P_i|} \sum_{j \in P_i} M_j \right) + \epsilon$$
*   **Development Needed**:
    *   Script: `generate_graph_dataset.py`
    *   Input: `chatbot/services/user_state.json` (or Neo4j Graph export).
    *   Output: `dataset/synthetic_trajectories.json` containing sequences of `(concept_id, signal_type, is_correct)`.

### B. GNN Training Loop
*   **Current State**: `RealGKT` class uses random/heuristic weights.
*   **Research Requirement**: A PyTorch/TensorFlow loop that trains the Attention Weights ($W$) using the generated dataset.
*   **Development Needed**:
    *   Script: `train_gnn_weights.py`
    *   Model: `GATNetwork` class (PyTorch).
    *   Loss Function: Binary Cross Entropy on prediction of next-step correctness.
    *   Output: `backend/chatbot/services/gnn_weights.json` (Real weights to replace random init).

### C. Large-Scale Evaluation Runner
*   **Current State**: `run_batch_simulation` runs 80 manual cases.
*   **Research Requirement**: Validation on the held-out test set ($20\%$ of synthetic data).
*   **Development Needed**:
    *   Update `simulate_full_comparison.py` to load the trained `gnn_weights.json` instead of using the mock `RealGKT`.

## 3. Development Roadmap
1.  **Extract Graph Topology**: Create a utility to export the Neo4j concept graph into a static adjacency matrix/JSON for the simulator.
2.  **Implement Data Generator**: Translate the mathematical formula into a Python script.
3.  **Implement GKT Trainer**: Create a simple PyTorch GAT to learn from this data.
4.  **Integrate**: Feed the learned weights back into the `RealMGKTWrapper` and `RealGKT` classes.
