
import sys
import os
import random
import numpy as np
from sklearn.metrics import roc_auc_score

# Ensure backend modules are efficient
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- 1. MOCK MODELS (Simplified for Batch Run) ---

class MockBKT:
    def __init__(self):
        self.mastery = 0.1
        self.p_L = 0.1
        self.p_T = 0.1
        self.p_G = 0.25
        self.p_S = 0.1
        
        # Load learned params if available
        try:
            import json
            params_path = os.path.join(os.path.dirname(__file__), "bkt_learned_params.json")
            if os.path.exists(params_path):
                with open(params_path, "r") as f:
                    params = json.load(f)
                    self.p_L = params.get("p_L", 0.1)
                    self.p_G = params.get("p_G", 0.25)
                    self.p_S = params.get("p_S", 0.1)
        except Exception:
            pass # Fallback to defaults
    
    def reset(self): self.mastery = 0.1
    
    def update(self, is_correct, source=None):
        curr = self.mastery
        if is_correct:
            num = curr * (1 - self.p_S)
            den = num + (1 - curr) * self.p_G
        else:
            num = curr * self.p_S
            den = num + (1 - curr) * (1 - self.p_G)
        posterior = num / (den + 1e-9)
        self.mastery = posterior + (1 - posterior) * self.p_T
        return self.mastery

class MockDKT:
    def __init__(self):
        self.history = []
        self.mastery = 0.1
        
    def reset(self):
        self.history = []
        self.mastery = 0.1
        
    def update(self, is_correct, source=None):
        val = 1.0 if is_correct else 0.0
        self.history.append(val)
        if len(self.history) > 10: self.history.pop(0)
        weights = np.linspace(0.1, 1.0, len(self.history))
        weighted_avg = np.average(self.history, weights=weights)
        self.mastery = 1 / (1 + np.exp(-5 * (weighted_avg - 0.5)))
        return self.mastery

class MockGKT:
    def __init__(self):
        self.node_mastery = 0.1
        self.neighbor_mastery = 0.1
        self.bkt = MockBKT()
        
    def reset(self):
        self.node_mastery = 0.1
        self.neighbor_mastery = 0.1
        self.bkt.reset()

    @property
    def mastery(self):
        return (self.node_mastery + self.neighbor_mastery) / 2
        
    def update(self, is_correct, source=None):
        self.node_mastery = self.bkt.update(is_correct)
        self.neighbor_mastery += (self.node_mastery - self.neighbor_mastery) * 0.2
        return self.mastery

import torch
import torch.nn as nn
import torch.nn.functional as F

# Re-define the GAT architecture locally for inference
class GATLayer(nn.Module):
    def __init__(self, in_features, out_features, alpha):
        super(GATLayer, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.W = nn.Parameter(torch.zeros(size=(in_features, out_features)))
        self.a = nn.Parameter(torch.zeros(size=(2*out_features, 1)))
        nn.init.xavier_uniform_(self.W.data, gain=1.414)
        nn.init.xavier_uniform_(self.a.data, gain=1.414)
        self.leakyrelu = nn.LeakyReLU(alpha)

    def forward(self, input, adj):
        h = torch.mm(input, self.W)
        N = h.size()[0]
        a_input = torch.cat([h.repeat(1, N).view(N * N, -1), h.repeat(N, 1)], dim=1).view(N, -1, 2 * self.out_features)
        e = self.leakyrelu(torch.matmul(a_input, self.a).squeeze(2))
        zero_vec = -9e15*torch.ones_like(e)
        attention = torch.where(adj > 0, e, zero_vec)
        attention = F.softmax(attention, dim=1)
        return torch.matmul(attention, h)

class MGKT_GNN(nn.Module):
    def __init__(self, nfeat, nhid, nheads):
        super(MGKT_GNN, self).__init__()
        self.attentions = nn.ModuleList([GATLayer(nfeat, nhid, alpha=0.2) for _ in range(nheads)])
        self.out_att = GATLayer(nhid * nheads, 1, alpha=0.2)

    def forward(self, x, adj):
        x = torch.cat([att(x, adj) for att in self.attentions], dim=1)
        return torch.sigmoid(self.out_att(x, adj))

class MockMGKT:
    def __init__(self):
        # 4 Nodes in our graph: Basics, Loops, Recursion, Debugging
        self.adj = torch.tensor([
            [1, 1, 0, 0], [0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1]
        ], dtype=torch.float32)
        
        # Latent BKT states for each node
        self.node_states = torch.tensor([[0.1, 0.1, 0.1]] * 4, dtype=torch.float32)
        self.active_node = 0
        self.cached_preds = torch.tensor([0.1] * 4)
        
        # Load GAT Model
        self.gnn = MGKT_GNN(nfeat=3, nhid=8, nheads=2)
        try:
            model_path = os.path.join(os.path.dirname(__file__), "mgkt_gat_model.bin")
            if os.path.exists(model_path):
                self.gnn.load_state_dict(torch.load(model_path))
                self.gnn.eval()
                self._recompute_mastery()
        except: pass

    def reset(self):
        self.node_states = torch.tensor([[0.1, 0.1, 0.1]] * 4, dtype=torch.float32)
        self.active_node = 0
        self._recompute_mastery()

    def _recompute_mastery(self):
        with torch.no_grad():
            self.cached_preds = self.gnn(self.node_states, self.adj)

    @property
    def mastery(self):
        # Return the mastery of the ACTIVE concept
        return self.cached_preds[self.active_node].item()
        
    def update(self, is_correct, source="tutor"):
        # Map source to column: Tutor=0, Code=1, Debug=2
        src_map = {"tutor": 0, "code": 1, "debug": 2}
        col = src_map.get(source, 0)
        
        # Determine active node (Matching the trainer's logic)
        # We need a way to track the step count locally to stay in sync
        # Since 'update' doesn't receive 'step', we'll infer it or track internally
        # But for AUC benchmark, we can just use the source to pick the most likely node
        if source == "tutor": self.active_node = 0
        elif source == "code": self.active_node = 1 # Simplified, could be 1 or 2
        elif source == "debug": self.active_node = 3
        
        if is_correct:
            self.node_states[self.active_node, col] = min(0.95, self.node_states[self.active_node, col] + 0.2)
        else:
            self.node_states[self.active_node, col] = max(0.05, self.node_states[self.active_node, col] - 0.1)
        
        self._recompute_mastery()
        return self.mastery

# --- 2. DATA GENERATOR (Graph Random Walk) ---
def generate_student_data(n_students=1000, n_steps=20):
    dataset = []
    
    for _ in range(n_students):
        student_id = random.randint(1000, 9999)
        # Latent Ability: Some students are smart (0.8), some struggle (0.3)
        ability = np.random.beta(5, 2) # Skewed towards 0.7
        
        history = []
        mastered_prereqs = False # Start cold
        
        for step in range(n_steps):
            # Phase 1: Prereqs (Tutor)
            if step < 5:
                source = "tutor"
                # Constant difficulty for standard KT evaluation
                difficulty = 0.4 
            # Phase 2: Application (Code)
            elif step < 15:
                source = "code"
                difficulty = 0.5 
                if not mastered_prereqs: difficulty += 0.3 # Penalty, not randomness
            # Phase 3: Analysis (Debug)
            else:
                source = "debug"
                difficulty = 0.6
            
            # Outcome
            # IRT-like: Prob = Sigmoid(Ability - Difficulty)
            # Simplified: Linear approximation with bounds
            prob_success = ability - difficulty + 0.5
            if mastered_prereqs: prob_success += 0.2
            
            # Clamp
            prob_success = min(0.95, max(0.05, prob_success))
            
            is_correct = random.random() < prob_success
            
            if source == "tutor" and is_correct: 
                mastered_prereqs = True 
                
            history.append((source, is_correct, step+1 < n_steps))
            
        dataset.append(history)
    return dataset

# --- 3. BENCHMARK RUNNER ---
def run_auc_benchmark():
    print(f"{'AUC BENCHMARK REPORT (N=1000 Students)':^80}")
    print("="*80)
    
    data = generate_student_data(1000, 20)
    
    models = {
        "BKT": MockBKT(),
        "DKT": MockDKT(),
        "GKT": MockGKT(),
        "MGKT": MockMGKT()
    }
    
    # Results dictionary now tracks by split as well
    # Structure: results[model][source] = {y_true, y_pred}
    splits = ["Overall", "tutor", "code", "debug"]
    results = {m: {s: {"y_true": [], "y_pred": []} for s in splits} for m in models.keys()}
    
    for history in data:
        for m in models.values(): m.reset()
        
        for i, (source, is_correct, _) in enumerate(history):
            if i == 0: continue
            
            y_i = 1 if is_correct else 0
            
            for name, model in models.items():
                pred = model.mastery
                
                # Store in Overall
                results[name]["Overall"]["y_true"].append(y_i)
                results[name]["Overall"]["y_pred"].append(pred)
                
                # Store in Specific Source
                results[name][source]["y_true"].append(y_i)
                results[name][source]["y_pred"].append(pred)
                
            for model in models.values():
                model.update(is_correct, source)

    # Print Table
    headers = f"{'Model':<10} | {'Overall':<8} | {'Tutor':<8} | {'Code':<8} | {'Debug':<8}"
    print(headers)
    print("-" * len(headers))
    
    report_lines = []
    
    for name in models.keys():
        row = f"{name:<10} | "
        res_row = f"| {name} | "
        
        for s in splits:
            true_vals = results[name][s]["y_true"]
            pred_vals = results[name][s]["y_pred"]
            
            if len(set(true_vals)) < 2: # Need both classes for AUC
                auc_str = "N/A"
            else:
                auc = roc_auc_score(true_vals, pred_vals)
                auc_str = f"{auc:.4f}"
            
            row += f"{auc_str:<8} | "
            res_row += f"{auc_str} | "
            
        print(row)
        report_lines.append(res_row)

    # Generate Report
    final_report = f"""# Research Validation: AUC Benchmark (Detailed)

## Results (AUC by Agent)
| Model | Overall | Tutor | Code | Debug |
| :--- | :--- | :--- | :--- | :--- |
{chr(10).join(report_lines)}
"""


    with open("backend/auc_results.txt", "w") as f:
        f.write(final_report)

if __name__ == "__main__":
    run_auc_benchmark()
