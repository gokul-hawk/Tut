import torch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from simulate_auc_benchmark import MockMGKT

def test_gnn():
    model = MockMGKT()
    print("Initial Cached Preds (All nodes at 0.1 state):")
    print(model.cached_preds)
    
    # Boost node 0 (Basics) modality 0 (Tutor)
    print("\nBoosting Basics (Node 0) to 0.9 state...")
    model.node_states[0, 0] = 0.9
    model._recompute_mastery()
    print("Preds after Basics boost:")
    print(model.cached_preds)
    
    # Boost node 1 (Loops) modality 1 (Code)
    print("\nBoosting Loops (Node 1) to 0.9 state...")
    model.node_states[1, 1] = 0.9
    model._recompute_mastery()
    print("Preds after Loops boost:")
    print(model.cached_preds)
    
    print("\nAdjacency Matrix:")
    print(model.adj)

if __name__ == "__main__":
    test_gnn()
