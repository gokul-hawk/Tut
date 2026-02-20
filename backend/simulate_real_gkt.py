import numpy as np

class RealGKT:
    """
    Graph Knowledge Tracing (Nakagawa et al., 2019).
    Implementation using simplified Graph Nerual Network (GNN) propagation in NumPy.
    
    Update Rule:
    h_self(t+1) = Update(h_self(t), input)
    h_neighbor(t+1) = Propagate(h_neighbor(t), h_self(t+1))
    """
    def __init__(self, name="RealGKT"):
        self.name = name
        self.hidden_dim = 16
        
        # State Vectors (Hidden State h)
        self.h_self = np.zeros(self.hidden_dim)
        self.h_neighbor = np.zeros(self.hidden_dim)
        
        # Weights (Random Initialization fixed for consistency)
        np.random.seed(42)
        self.W_in = np.random.randn(self.hidden_dim, 2) * 0.1 # Input: [Correct, Incorrect]
        self.W_self = np.random.randn(self.hidden_dim, self.hidden_dim) * 0.1
        self.W_prop = np.random.randn(self.hidden_dim, self.hidden_dim) * 0.2 # Propagation Weight
        self.b = np.zeros(self.hidden_dim)
        
        # Output Projection (Sigmoid)
        self.W_out = np.random.randn(1, self.hidden_dim) * 0.1

    @property
    def mastery(self):
        # Decode state to probability
        return self._sigmoid(np.dot(self.W_out, self.h_self))[0]

    @property
    def neighbor_mastery(self):
        return self._sigmoid(np.dot(self.W_out, self.h_neighbor))[0]

    def reset(self):
        self.h_self = np.zeros(self.hidden_dim)
        self.h_neighbor = np.zeros(self.hidden_dim)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def update(self, is_correct, signal_type):
        # 1. Prepare Input Vector (Binary Correctness)
        # GKT is Signal Blind: Treats 'debug' same as 'tutor'
        x = np.array([1, 0]) if is_correct else np.array([0, 1])
        
        # 2. Update Self (Recurrent Step)
        # h_t = tanh(W_in*x + W_self*h_{t-1} + b)
        update_signal = np.dot(self.W_in, x) + np.dot(self.W_self, self.h_self)
        self.h_self = np.tanh(update_signal + self.b)
        
        # 3. Propagate to Neighbor (Graph Step)
        # h_neighbor = h_neighbor + W_prop * h_self
        # (Simplified GAT-like update)
        propagation = np.dot(self.W_prop, self.h_self)
        self.h_neighbor = np.tanh(self.h_neighbor + propagation)

    def set_weights(self, weights_dict):
        self.W_in = np.array(weights_dict['W_in'])
        self.W_self = np.array(weights_dict['W_self'])
        self.W_prop = np.array(weights_dict['W_prop'])
        self.W_out = np.array(weights_dict['W_out'])
        self.b = np.array(weights_dict['b'])

    def fit_to_stats(self, dataset):
        print("Training GKT (Statistical Weighting)...")
        # 1. Calc Success Rates per Source
        stats = {"tutor": [], "code": [], "debug": []}
        for student in dataset:
            for src, res in student.get("events", []):
                if src in stats: stats[src].append(1 if res else 0)
        
        avgs = {k: np.mean(v) if v else 0.5 for k, v in stats.items()}
        print(f"  -> GKT Observed Success: {avgs}")
        
        # 2. Heuristic: Propagation Weight ~ Reliability
        # If Debug is hard but you pass, implies high mastery -> Strong Prop
        # If Code is easy and you pass, low info -> Weak Prop
        # We model "Influence" as inverse success rate (Rare events matter more)
        
        # Base magnitude
        base_mag = 0.2
        
        # Adjust W_prop based on average difficulty
        # Higher difficulty (lower success) -> Higher weight
        avg_diff = np.mean(list(avgs.values()))
        scaling_factor = 1.0 + (0.5 - avg_diff) # >1 if hard, <1 if easy
        
        # Update W_prop
        self.W_prop *= scaling_factor
        
        print(f"  -> Scaled GKT Propagation by {scaling_factor:.4f}")
        
        return {
            'W_in': self.W_in.tolist(),
            'W_self': self.W_self.tolist(),
            'W_prop': self.W_prop.tolist(),
            'W_out': self.W_out.tolist(),
            'b': self.b.tolist()
        }
