
import sys
import os
import random
import numpy as np
from sklearn.metrics import roc_auc_score
from simulate_auc_benchmark import generate_student_data, MockBKT

# Ensure backend modules are efficient
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def train_bkt():
    print(f"{'TRAINING BKT (Grid Search)':^80}")
    print("="*80)
    
    # 1. Generate Training Data
    print("Generating 500 student logs...")
    data = generate_student_data(500, 20)
    
    # Flatten data for fast eval: List of (is_correct_prev, is_correct_curr)
    # Actually BKT is sequential. We just run the full sequence.
    
    # 2. Define Parameter Grid
    # P(Init) usually 0.1
    # P(Learn) in [0.05, 0.3]
    # P(Guess) in [0.1, 0.4]
    # P(Slip) in [0.05, 0.3]
    
    best_auc = 0
    best_params = {}
    
    # Coarse Grid
    learn_rates = [0.05, 0.1, 0.2, 0.3]
    guess_rates = [0.1, 0.2, 0.3, 0.4]
    slip_rates = [0.05, 0.1, 0.2]
    
    total_iter = len(learn_rates) * len(guess_rates) * len(slip_rates)
    curr_iter = 0
    
    for l in learn_rates:
        for g in guess_rates:
            for s in slip_rates:
                curr_iter += 1
                if curr_iter % 10 == 0: print(f"Progress: {curr_iter}/{total_iter}...")
                
                # Instantiate Model
                model = MockBKT()
                model.p_L = l
                model.p_G = g
                model.p_S = s
                
                # Evaluate
                y_true = []
                y_pred = []
                
                for history in data:
                    model.reset()
                    for i, (src, corr, _) in enumerate(history):
                        if i == 0: continue
                        
                        y_i = 1 if corr else 0
                        pred = model.mastery # Prediction for this step
                        
                        y_true.append(y_i)
                        y_pred.append(pred)
                        
                        model.update(corr)
                
                try:
                    auc = roc_auc_score(y_true, y_pred)
                except:
                    auc = 0.5
                    
                if auc > best_auc:
                    best_auc = auc
                    best_params = {"p_L": l, "p_G": g, "p_S": s}
                    # print(f"New Best: {best_auc:.4f} {best_params}")

    print("-" * 80)
    print(f"BKT TRAINING COMPLETE.")
    print(f"Best AUC: {best_auc:.4f}")
    print(f"Optimal Parameters: {best_params}")
    
    # Save to JSON
    import json
    with open("backend/bkt_learned_params.json", "w") as f:
        json.dump(best_params, f, indent=2)
    print("Saved to backend/bkt_learned_params.json")

if __name__ == "__main__":
    train_bkt()
