# MGKT Simulation Workflow

This workflow details how to execute the full MGKT simulation, including the steps to developed the missing components.

## 1. Prerequisites
*   Python 3.10+
*   `numpy`, `networkx`
*   `torch` (for GNN training)

## 2. Execution Steps

### Step 1: Generate Synthetic Data (TODO)
**Goal**: Create a dataset of 500 student trajectories based on the Graph Topology.
1.  Run the (future) generator script:
    ```bash
    python backend/generate_graph_dataset.py --n_students 500 --output backend/data/synthetic_500.json
    ```
2.  **Verify**: Check `backend/data/synthetic_500.json` contains list of `(concept, signal, correct)` tuples.

### Step 2: Train the GNN Weights (TODO)
**Goal**: Learn the optimal attention weights ($W$) from the synthetic data.
1.  Run the (future) training script:
    ```bash
    python backend/train_gnn_weights.py --input backend/data/synthetic_500.json --epochs 50
    ```
2.  **Verify**: Check `backend/chatbot/services/gnn_weights.json` is created.

### Step 3: Run the Comparative Simulation
**Goal**: Benchmark MGKT (with trained weights) against BKT/DKT.
1.  Run the existing comparison script:
    ```bash
    python backend/simulate_full_comparison.py
    ```
2.  **Analyize**: Review `backend/results.json` to see Mean Mastery probabilities for each scenario.

### Step 4: Run the Scoring Engine Integration
**Goal**: Validation the end-to-end "Tutor -> Code -> Debug" scoring flow.
1.  Run the scoring simulator:
    ```bash
    python backend/simulate_scoring_v2.py
    ```
2.  **Verify**: Check console output for "High Performer", "Struggling", and "AI Dependent" profiles.

## 3. Development Checklist
- [ ] Create `generate_graph_dataset.py`
- [ ] Create `train_gnn_weights.py`
- [ ] Update `RealMGKTWrapper` to load `gnn_weights.json`
