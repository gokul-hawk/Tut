
import json
import os
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score

# --- 1. MODEL DEFINITIONS ---

class RealBKT:
    """Standard Bayesian Knowledge Tracing."""
    def __init__(self, params):
        self.p_l = params.get("p_learn", 0.1)
        self.p_t = params.get("p_transit", 0.1)
        self.p_g = params.get("p_guess", 0.2)
        self.p_s = params.get("p_slip", 0.2)
        self.mastery = 0.1

    def reset(self):
        self.mastery = 0.1

    def update(self, is_correct, signal_type=None):
        if is_correct:
            likelihood = (self.mastery * (1 - self.p_s)) / \
                         (self.mastery * (1 - self.p_s) + (1 - self.mastery) * self.p_g)
        else:
            likelihood = (self.mastery * self.p_s) / \
                         (self.mastery * self.p_s + (1 - self.mastery) * (1 - self.p_g))
        self.mastery = likelihood + (1 - likelihood) * self.p_t
        return self.mastery

class RealDKT:
    """RNN-based DKT (NumPy Implementation)."""
    def __init__(self, weights):
        self.input_size = 4
        self.hidden_size = 16
        self.output_size = 1
        
        # Load weights
        self.Wxh = np.array(weights['Wxh'])
        self.Whh = np.array(weights['Whh'])
        self.Why = np.array(weights['Why'])
        self.bh = np.array(weights['bh'])
        self.by = np.array(weights['by'])
        
        self.h = np.zeros((self.hidden_size, 1))
        self.mastery = 0.1

    def reset(self):
        self.h = np.zeros((self.hidden_size, 1))
        self.mastery = 0.1

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def update(self, is_correct, source="tutor"):
        feats = [0, 0, 0, 1 if is_correct else 0]
        if source == "tutor": feats[0] = 1
        elif source == "code": feats[1] = 1
        elif source == "debug": feats[2] = 1
        
        x = np.array(feats).reshape(-1, 1)
        
        # RNN Step
        self.h = np.tanh(np.dot(self.Wxh, x) + np.dot(self.Whh, self.h) + self.bh)
        y = self.sigmoid(np.dot(self.Why, self.h) + self.by)
        
        self.mastery = float(y[0][0])
        return self.mastery

class RealGKT:
    """Graph Knowledge Tracing (NumPy Implementation)."""
    def __init__(self, weights):
        self.hidden_dim = 16
        self.W_in = np.array(weights['W_in'])
        self.W_self = np.array(weights['W_self'])
        self.W_prop = np.array(weights['W_prop'])
        self.W_out = np.array(weights['W_out'])
        self.b = np.array(weights['b'])
        
        self.h_self = np.zeros(self.hidden_dim)
        self.h_neighbor = np.zeros(self.hidden_dim)

    def reset(self):
        self.h_self = np.zeros(self.hidden_dim)
        self.h_neighbor = np.zeros(self.hidden_dim)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    @property
    def mastery(self):
        return self._sigmoid(np.dot(self.W_out, self.h_self))[0]

    def update(self, is_correct, signal_type=None):
        x = np.array([1, 0]) if is_correct else np.array([0, 1])
        
        update_signal = np.dot(self.W_in, x) + np.dot(self.W_self, self.h_self)
        self.h_self = np.tanh(update_signal + self.b)
        
        propagation = np.dot(self.W_prop, self.h_self)
        self.h_neighbor = np.tanh(self.h_neighbor + propagation)
        return self.mastery

# --- MGKT Components (PyTorch GAT) ---
class GATLayer(nn.Module):
    def __init__(self, in_features, out_features, dropout, alpha, concat=True):
        super(GATLayer, self).__init__()
        self.dropout = dropout
        self.in_features = in_features
        self.out_features = out_features
        self.alpha = alpha
        self.concat = concat
        self.W = nn.Parameter(torch.zeros(size=(in_features, out_features)))
        nn.init.xavier_uniform_(self.W.data, gain=1.414)
        self.a = nn.Parameter(torch.zeros(size=(2*out_features, 1)))
        nn.init.xavier_uniform_(self.a.data, gain=1.414)
        self.leakyrelu = nn.LeakyReLU(self.alpha)

    def forward(self, input, adj):
        h = torch.mm(input, self.W)
        N = h.size()[0]
        a_input = torch.cat([h.repeat(1, N).view(N * N, -1), h.repeat(N, 1)], dim=1).view(N, -1, 2 * self.out_features)
        e = self.leakyrelu(torch.matmul(a_input, self.a).squeeze(2))
        zero_vec = -9e15*torch.ones_like(e)
        attention = torch.where(adj > 0, e, zero_vec)
        attention = F.softmax(attention, dim=1)
        # attention = F.dropout(attention, self.dropout, training=self.training) # Disable dropout for inference
        h_prime = torch.matmul(attention, h)
        return F.elu(h_prime) if self.concat else h_prime

class MGKT_GNN(nn.Module):
    def __init__(self, nfeat, nhid, nclass, dropout, alpha, nheads):
        super(MGKT_GNN, self).__init__()
        self.dropout = dropout
        
        self.attentions = []
        for i in range(nheads):
            att = GATLayer(nfeat, nhid, dropout=dropout, alpha=alpha, concat=True)
            self.attentions.append(att)
            self.add_module('attention_{}'.format(i), att)

        self.out_att = GATLayer(nhid * nheads, nclass, dropout=dropout, alpha=alpha, concat=False)

    def forward(self, x, adj):
        # x = F.dropout(x, self.dropout, training=self.training)
        x = torch.cat([att(x, adj) for att in self.attentions], dim=1)
        # x = F.dropout(x, self.dropout, training=self.training)
        return torch.sigmoid(self.out_att(x, adj))

class RealMGKT:
    def __init__(self, mgkt_params):
        # 4 Nodes: Basics, Loops, Recursion, Debugging
        self.adj = torch.tensor([
            [1, 1, 0, 0], [0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1]
        ], dtype=torch.float32)
        
        self.node_states = torch.tensor([[0.1, 0.1, 0.1]] * 4, dtype=torch.float32)
        self.active_node = 0
        self.cached_preds = torch.tensor([0.1] * 4)
        
        # Load params for each modality
        self.params = {
            "tutor": mgkt_params.get("tutor", {}),
            "code": mgkt_params.get("code", {}),
            "debug": mgkt_params.get("debug", {})
        }
        
        # Load GNN
        self.gnn = MGKT_GNN(nfeat=3, nhid=64, nclass=1, dropout=0.0, alpha=0.2, nheads=8)
        model_path = os.path.join(os.path.dirname(__file__), "mgkt_gat_model.bin")
        if os.path.exists(model_path):
            self.gnn.load_state_dict(torch.load(model_path))
            self.gnn.eval()
        else:
            print("Warning: MGKT GNN model not found, using untrained weights.")
        self._recompute_mastery()

    def reset(self):
        self.node_states = torch.tensor([[0.1, 0.1, 0.1]] * 4, dtype=torch.float32)
        self._recompute_mastery()

    def _recompute_mastery(self):
        with torch.no_grad():
            self.cached_preds = self.gnn(self.node_states, self.adj)

    def update(self, is_correct, source="tutor"):
        # Map source to node index (approximate logic for this dataset)
        # Assuming current event targets the concept of the "active node"
        # Since dataset doesn't have node_id, we infer or assume a sequence.
        # But wait, the dataset is just events. MGKT needs a graph.
        # We'll use a simplified mapping: 
        # - tutor -> Basics (0)
        # - code -> Loops (1) or Recursion (2) (Randomly pick or alternate?)
        # - debug -> Debugging (3)
        # For consistency with training script:
        if source == "tutor": node_idx = 0
        elif source == "code": node_idx = 1 # Simplified to Loops
        elif source == "debug": node_idx = 3
        else: node_idx = 0
        
        src_map = {"tutor": 0, "code": 1, "debug": 2}
        col = src_map.get(source, 0)
        
        p = self.params.get(source, self.params["tutor"])
        p_s = p.get("p_slip", 0.1)
        p_g = p.get("p_guess", 0.2)
        p_t = p.get("p_transit", 0.1)
        
        curr = self.node_states[node_idx, col].item()
        if is_correct:
            num = curr * (1 - p_s)
            den = num + (1 - curr) * p_g
        else:
            num = curr * p_s
            den = num + (1 - curr) * (1 - p_g)
        
        posterior = num / (den + 1e-9)
        self.node_states[node_idx, col] = posterior + (1 - posterior) * p_t
        
        self._recompute_mastery()
        # Return probability of success for the NEXT step (or current mastery)
        # AUC usually compares prediction BEFORE event to outcome.
        return self.cached_preds[node_idx].item()

# --- MAIN EVALUATION ---

def evaluate():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Load Parameters and Weights
    try:
        with open(os.path.join(base_dir, "trained_params.json"), "r") as f:
            params = json.load(f)
        with open(os.path.join(base_dir, "trained_models.json"), "r") as f:
            models_weights = json.load(f)
    except FileNotFoundError as e:
        print(f"Error loading configuration: {e}")
        return

    # 2. Instantiate Models
    models = {
        "BKT": RealBKT(params.get("BKT", {})),
        "DKT": RealDKT(models_weights.get("dkt", {})),
        "GKT": RealGKT(models_weights.get("gkt", {})),
        "MGKT": RealMGKT(params.get("MGKT", {}))
    }

    # 3. Load Dataset
    data_path = os.path.join(base_dir, "research_dataset.json")
    if not os.path.exists(data_path):
        print("research_dataset.json not found.")
        return
        
    with open(data_path, "r") as f:
        dataset = json.load(f)

    print(f"Loaded {len(dataset)} student traces from research_dataset.json")
    sys.stdout.flush()

    # 4. Run Evaluation
    print("Starting prediction loop...")
    
    # Structure: results[category][model] = {'y_true': [], 'y_pred': []}
    results = {}

    count = 0
    try:
        for student in dataset:
            count += 1
            cat = student.get("category", "Unknown")
            if cat not in results:
                results[cat] = {k: {'y_true': [], 'y_pred': []} for k in models}
                
            for m in models.values(): m.reset()
            
            events = student.get("events", [])
            if not events: continue
            
            for i, event in enumerate(events):
                # Event format: [source, is_correct] (list)
                source, is_correct = event[0], event[1]
                
                # Predict (using state BEFORE update)
                if source == "tutor": node_idx = 0
                elif source == "code": node_idx = 1 
                elif source == "debug": node_idx = 3
                else: node_idx = 0
                
                for name, model in models.items():
                    # Get prediction
                    if name == "MGKT":
                        pred = model.cached_preds[node_idx].item()
                    else:
                        pred = model.mastery
                    
                    results[cat][name]['y_true'].append(1 if is_correct else 0)
                    results[cat][name]['y_pred'].append(pred)
                    
                    # Update model
                    model.update(is_correct, source)
    except Exception as e:
        print(f"CRASH during loop at student {count}: {e}")
        import traceback
        traceback.print_exc()

    print("Finished prediction loop.")
    sys.stdout.flush()

    # 5. Calculate AUC per Category
    print("\n" + "="*80)
    print(f"{'Category':<20} | {'Model':<10} | {'AUC Score':<10} | {'Samples':<10}")
    print("-" * 60)
    
    categories = sorted(results.keys())
    for cat in categories:
        for name in models:
            data = results[cat][name]
            if len(set(data['y_true'])) < 2:
                print(f"{cat:<20} | {name:<10} | {'N/A':<10} | {len(data['y_true']):<10}")
                continue
                
            try:
                auc = roc_auc_score(data['y_true'], data['y_pred'])
                print(f"{cat:<20} | {name:<10} | {auc:.4f}     | {len(data['y_true']):<10}")
            except Exception as e:
                print(f"{cat:<20} | {name:<10} | Error      | {len(data['y_true']):<10}")
    print("="*80)

if __name__ == "__main__":
    evaluate()
