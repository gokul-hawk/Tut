
import sys
import os
import torch
import numpy as np
from simulate_auc_benchmark import MockBKT, MockDKT, MockMGKT

def simulate_expert_streak():
    print(f"{'BEHAVIOR TEST: EXPERT STREAK (Tutor -> Code -> Debug)':^80}")
    print("="*80)
    
    models = {
        "BKT": MockBKT(),
        "DKT": MockDKT(),
        "MGKT-GAT": MockMGKT()
    }
    
    # Define the streak
    # 5 Tutor -> 10 Code -> 5 Debug
    sequence = [("tutor", True)] * 5 + [("code", True)] * 10 + [("debug", True)] * 5
    
    # Results storage
    history = {name: [] for name in models.keys()}
    
    print(f"{'Step':<5} | {'Source':<10} | {'BKT':<10} | {'DKT':<10} | {'MGKT-GAT':<10}")
    print("-" * 60)
    
    for i, (source, is_correct) in enumerate(sequence):
        row = f"{i+1:<5} | {source:<10} | "
        
        for name, model in models.items():
            # Update
            model.update(is_correct, source)
            val = model.mastery
            history[name].append(val)
            row += f"{val:.4f}     | "
        
        print(row)
    
    print("\n" + "="*80)
    print("BEHAVIOR ANALYSIS")
    print("-" * 80)
    
    # Summarize findings
    mgkt_final = history["MGKT-GAT"][-1]
    bkt_final = history["BKT"][-1]
    dkt_final = history["DKT"][-1]
    
    print(f"Final Mastery (MGKT-GAT): {mgkt_final:.4f}")
    print(f"Final Mastery (BKT):      {bkt_final:.4f}")
    print(f"Final Mastery (DKT):      {dkt_final:.4f}")
    
    print("\nKey Observations:")
    print("1. Tutor Phase:  Does the GAT respect the slower learning rate of theoretical quiz data?")
    print("2. Code Phase:   Does the GAT accelerate mastery when the student starts applying knowledge?")
    print("3. Debug Phase:  Does the 'Eureka' signal from debugging drive mastery to ceiling levels?")
    
    # Save results to a report file
    with open("backend/expert_streak_results.txt", "w") as f:
        f.write("# Behavior Analysis: Expert Streak\n\n")
        f.write("| Step | Source | BKT | DKT | MGKT-GAT |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for i, (source, _) in enumerate(sequence):
            f.write(f"| {i+1} | {source} | {history['BKT'][i]:.4f} | {history['DKT'][i]:.4f} | {history['MGKT-GAT'][i]:.4f} |\n")

if __name__ == "__main__":
    simulate_expert_streak()
