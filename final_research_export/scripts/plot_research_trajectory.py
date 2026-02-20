
import sys
import os
import json
import torch
import numpy as np
import matplotlib.pyplot as plt

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from simulate_auc_benchmark import MockBKT, MockDKT, MockMGKT

def plot_research_trajectory():
    print("Extracting Research Trajectory for expert_0...")
    
    # Load dataset
    with open('backend/research_dataset.json', 'r') as f:
        data = json.load(f)
    
    # Extract expert_0 events
    student = [s for s in data if s['id'] == 'expert_0'][0]
    sequence = student['events'] # List of [source, is_correct]
    
    print(f"Student: {student['id']} | Category: {student['category']}")
    print(f"Sequence Length: {len(sequence)}")
    
    models = {
        "BKT": MockBKT(),
        "DKT": MockDKT(),
        "MGKT-GAT": MockMGKT()
    }
    
    history = {name: [0.1] for name in models.keys()}
    
    for source, is_correct in sequence:
        for name, model in models.items():
            model.update(is_correct, source)
            history[name].append(model.mastery)
            
    # Plotting
    plt.figure(figsize=(12, 6))
    steps = range(len(sequence) + 1)
    
    for name, vals in history.items():
        plt.plot(steps, vals, label=name, marker='x', linewidth=2)
        
    plt.title(f"Research Trajectory: Learning Curve for {student['id']} ({student['category']})", fontsize=16)
    plt.xlabel("Interaction Step", fontsize=12)
    plt.ylabel("Mastery Probability", fontsize=12)
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Phase highlighting based on source changes in the data
    # (Optional, but adds flavor)
    
    os.makedirs("plots", exist_ok=True)
    plot_path = "plots/research_learning_curve.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")

if __name__ == "__main__":
    plot_research_trajectory()
