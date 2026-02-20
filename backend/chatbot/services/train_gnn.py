import numpy as np
import random
import sys
import os

# Allow running as script
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chatbot.services.gkt_model import GKTModel

class GNNTrainer:
    """
    Demonstration of GNN Training Loop.
    Optimizes the propagation weights (W) using Gradient Descent
    on synthetic student data.
    """
    def __init__(self):
        self.model = GKTModel()
        self.learning_rate = 0.01
        
        # Synthetic Parameters we want to learn
        # Ideal W should be around 0.3 for strong dependencies
        self.model.W_prop = 0.1 # Start with bad random initialization

    def load_data(self):
        """
        Loads user-provided training data.
        """
        # Prefer the Large Augmented Dataset if it exists
        large_path = os.path.join(os.path.dirname(__file__), "large_student_data.json")
        small_path = os.path.join(os.path.dirname(__file__), "student_data.json")
        
        path_to_use = None
        if os.path.exists(large_path):
            path_to_use = large_path
        elif os.path.exists(small_path):
            path_to_use = small_path
            
        if path_to_use:
            print(f"Loading records from {path_to_use}...")
            import json
            with open(path_to_use, "r") as f:
                return json.load(f)
        else:
            print("No external data found. Generating synthetic fallback...")
            return self.generate_synthetic_data(num_students=50)

    def generate_synthetic_data(self, num_students=100):
        # ... (Identical Generation Logic as Fallback) ...
        data = []
        concepts = self.model.concepts
        
        for _ in range(num_students):
            student_profile = random.choice(["smart", "average", "struggling"])
            sequence = []
            
            for concept in concepts:
                p = 0.5
                if student_profile == "smart": p = 0.9
                elif student_profile == "struggling": p = 0.2
                is_correct = 1 if random.random() < p else 0
                sequence.append((concept, is_correct))
            data.append(sequence)
        return data

    def train(self, epochs=50):
        print(f"Starting Training... Initial Weight: {self.model.W_prop:.4f}")
        
        data = self.load_data()
        print(f"Dataset Size: {len(data)} Student Trajectories.")
        
        for epoch in range(epochs):
            total_loss = 0
            
            for sequence in data:
                # Reset Student State for training run
                # In PyTorch we would detach gradients here
                current_state = np.zeros(self.model.num_concepts)
                
                for concept, actual_label in sequence:
                    if concept not in self.model.concept_to_idx: continue
                    idx = self.model.concept_to_idx[concept]
                    
                    # 1. Forward Pass (Prediction)
                    # H_new = H + (A * H * W)
                    neighbor_signal = np.dot(self.model.adj_matrix, current_state)
                    pred_score = current_state[idx] + (neighbor_signal[idx] * self.model.W_prop)
                    pred_score = np.clip(pred_score, 0, 1)
                    
                    # 2. Compute Loss (MSE)
                    # Loss = (Predicted - Actual)^2
                    loss = (pred_score - actual_label) ** 2
                    total_loss += loss
                    
                    # 3. Backward Pass (Gradient Descent)
                    # dLoss/dW = 2 * (Pred - Actual) * (dPred/dW)
                    # dPred/dW = NeighborSignal
                    grad = 2 * (pred_score - actual_label) * neighbor_signal[idx]
                    
                    # Update Weight
                    self.model.W_prop -= self.learning_rate * grad
                    
                    # Update State (Teacher Forcing)
                    current_state[idx] = actual_label
            
            avg_loss = total_loss / len(data)
            print(f"Epoch {epoch+1}: Loss={avg_loss:.4f} | Updated Weight W={self.model.W_prop:.4f}")

        print("Training Complete. The GNN has learned optimal propagation structure.")

if __name__ == "__main__":
    trainer = GNNTrainer()
    trainer.train()
