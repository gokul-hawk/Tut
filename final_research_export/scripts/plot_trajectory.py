
import sys
import os
import torch
import numpy as np
import matplotlib.pyplot as plt

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from simulate_auc_benchmark import MockBKT, MockDKT, MockMGKT

def plot_trajectory():
    print("Generating Trajectory Graph...")
    
    models = {
        "BKT": MockBKT(),
        "DKT": MockDKT(),
        "MGKT-GAT": MockMGKT()
    }
    
    # Sequence: 5 Tutor -> 10 Code -> 5 Debug
    sequence = [("tutor", True)] * 5 + [("code", True)] * 10 + [("debug", True)] * 5
    
    history = {name: [0.1] for name in models.keys()} # Start at 0.1
    
    for source, is_correct in sequence:
        for name, model in models.items():
            model.update(is_correct, source)
            history[name].append(model.mastery)
            
    # Plotting
    plt.figure(figsize=(12, 6))
    steps = range(len(sequence) + 1)
    
    for name, vals in history.items():
        plt.plot(steps, vals, label=name, marker='o', linewidth=2)
        
    # Phase Markers
    plt.axvspan(0, 5, alpha=0.1, color='blue', label='Phase 1: Tutor')
    plt.axvspan(5, 15, alpha=0.1, color='green', label='Phase 2: Code')
    plt.axvspan(15, 20, alpha=0.1, color='red', label='Phase 3: Debug')
    
    plt.title("Expert Trajectory: Learning Curve Comparison", fontsize=16)
    plt.xlabel("Interaction Step", fontsize=12)
    plt.ylabel("Mastery Probability", fontsize=12)
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Save the plot
    os.makedirs("plots", exist_ok=True)
    plot_path = "plots/learning_curve.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")
    
    # Also save to artifacts directory for embedding
    # The artifact directory is provided in the system prompt.
    # Note: I'll use the relative path for now as I can't easily get the abs path of .gemini here without hardcoding.
    # Actually the system instructions say: "copy the file to the artifacts directory before embedding it."
    # I will copy it in the next step.

if __name__ == "__main__":
    plot_trajectory()
