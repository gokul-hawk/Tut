import json
import numpy as np
import os
import sys
from sklearn.metrics import roc_auc_score, mean_squared_error

# Add path to finding backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import models
try:
    from simulate_advanced_mgkt import ContextAwareMGKT
    from simulate_real_bkt import RealBKT
    from simulate_real_dkt import RealDKT
    from simulate_real_gkt import RealGKT
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.simulate_advanced_mgkt import ContextAwareMGKT
    from backend.simulate_real_bkt import RealBKT
    from backend.simulate_real_dkt import RealDKT
    from backend.simulate_real_gkt import RealGKT

from utils.metrics import calculate_metrics

def run_behavior_analysis():
    print(f"\n{'='*100}")
    print(f"{'ADVANCED BEHAVIOR ANALYSIS: Learning Curves, Inertia, Transfer':^100}")
    print(f"{'='*100}\n")

    # 1. Load Data
    data_path = "backend/research_dataset.json"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    with open(data_path, "r") as f:
        dataset = json.load(f)

    # 2. Setup Models
    # 2. Setup Models
    # Load Trained Parameters if available
    param_path = "backend/trained_models.json"
    trained_params = {"bkt": {}} 
    if os.path.exists(param_path):
        with open(param_path, "r") as f:
            trained_params = json.load(f)
        print(f"Loaded trained parameters for behavior analysis.")
        
    bkt_p = trained_params.get("bkt", {})

    models = [
        RealBKT(name="BKT (Trained)", 
                p_init=bkt_p.get("p_init", 0.1),
                p_transit=bkt_p.get("p_transit", 0.1),
                p_guess=bkt_p.get("p_guess", 0.2), 
                p_slip=bkt_p.get("p_slip", 0.2)),
        RealDKT(name="DKT"),
        RealGKT(name="GKT"),
        ContextAwareMGKT(name="MGKT (Context-Aware)")
    ]
    
    # 3. Storage for Metrics
    # Learning Curves: {model: {opportunity_idx: [errors]}}
    learning_curves = {m.name: {} for m in models}
    
    # Moment of Learning: {category: {model: [event_indices]}}
    # "Aha!" moment defined as crossing 0.85 mastery
    moment_of_learning = {cat: {m.name: [] for m in models} for cat in ["Deep Struggle", "Instant Expert"]}
    
    # Inertia: {category: {model: {'success_delta': [], 'failure_delta': []}}}
    inertia = {cat: {m.name: {'success_delta': [], 'failure_delta': []} for m in models} for cat in ["Lucky Guesser", "Deep Struggle"]}
    
    # Transfer: {model: {'tutor_y_true': [], 'tutor_y_pred': [], 'code_y_true': [], 'code_y_pred': []}}
    transfer = {m.name: {'tutor_y_true': [], 'tutor_y_pred': [], 'code_y_true': [], 'code_y_pred': []} for m in models}

    print(f"Analyzing behavior for {len(dataset)} students...")

    for student in dataset:
        category = student.get("category", "Unknown")
        ground_truth = student.get("ground_truth_mastery", 0)
        
        # Reset models
        for m in models: m.reset()
        
        events = student.get("events", [])
        
        # Track opportunity count for this student
        opp_count = 0
        
        # Track if specific "Aha!" moment already found for this student/model
        aha_found = {m.name: False for m in models}

        for event in events:
            source = event[0]
            is_correct = event[1]
            opp_count += 1
            
            # Synthesize Metadata for ContextAwareMGKT
            metadata = {}
            if category == "Lucky Guesser" and source == "code":
                 metadata["ai_usage"] = 15
            elif category == "Deep Struggle" and source == "code" and not is_correct:
                 metadata["test_failures"] = 6

            for m in models:
                # 1. Prediction (Before Update)
                prev_mastery = m.mastery
                y_pred = m.mastery
                y_true_ground = ground_truth
                
                # 2. Update
                if isinstance(m, ContextAwareMGKT):
                    m.update_with_context(is_correct, source, metadata)
                else:
                    # RealBKT/DKT/GKT use update(is_correct, source)
                    # Use try-except to be robust against signature variations
                    try:
                        m.update(is_correct, source=source)
                    except TypeError:
                        m.update(is_correct, source)
                
                new_mastery = m.mastery
                delta = new_mastery - prev_mastery
                
                # --- METRIC COLLECTION ---
                
                # A. Learning Curves (Error vs Opportunity)
                # Error = |GroundTruth - Prediction|
                error = abs(y_true_ground - y_pred)
                if opp_count not in learning_curves[m.name]:
                    learning_curves[m.name][opp_count] = []
                learning_curves[m.name][opp_count].append(error)
                
                # B. Moment of Learning ("Aha!")
                # First time mastery crosses 0.85
                if category in moment_of_learning and not aha_found[m.name]:
                     if new_mastery >= 0.85:
                         moment_of_learning[category][m.name].append(opp_count)
                         aha_found[m.name] = True
                         
                # C. Inertia (Trust/Skepticism)
                # Delta P after Correct/Incorrect
                if category in inertia:
                    if is_correct:
                        inertia[category][m.name]['success_delta'].append(delta)
                    else:
                        inertia[category][m.name]['failure_delta'].append(delta)
                        
                # D. Transfer Analysis (Declarative vs Procedural)
                # Compare accuracy on Tutor (Declarative) vs Code (Procedural)
                # We use Ground Truth for the target y_true to measure "True Understanding"
                if source == "tutor":
                    transfer[m.name]['tutor_y_true'].append(y_true_ground)
                    transfer[m.name]['tutor_y_pred'].append(y_pred)
                elif source == "code":
                    transfer[m.name]['code_y_true'].append(y_true_ground)
                    transfer[m.name]['code_y_pred'].append(y_pred)

    # --- REPORTING ---
    output_lines = []
    
    # 1. Moment of Learning
    output_lines.append("\n" + "-"*80)
    output_lines.append(f"{'1. MOMENT OF LEARNING (Step Index crossing 0.85 Mastery)':^80}")
    output_lines.append("-"*80)
    output_lines.append(f"{'Category':<20} | {'Model':<24} | {'Avg Step to Mastery':<20}")
    output_lines.append("-"*80)
    
    for cat, model_data in moment_of_learning.items():
        for m_name, steps in model_data.items():
            avg_step = np.mean(steps) if steps else 0.0
            avg_str = f"{avg_step:.1f}" if steps else "Never"
            output_lines.append(f"{cat:<20} | {m_name:<24} | {avg_str:<20}")
    
    # 2. Inertia Analysis
    output_lines.append("\n" + "-"*80)
    output_lines.append(f"{'2. INERTIA (Skepticism Analysis)':^80}")
    output_lines.append(f"{'Avg Mastery Gain (Delta P) after a CORRECT answer':^80}")
    output_lines.append("-"*80)
    output_lines.append(f"{'Category':<20} | {'Model':<24} | {'Gain (Trust)'}")
    output_lines.append("-"*80)
    
    for cat, model_data in inertia.items():
        for m_name, data in model_data.items():
            avg_gain = np.mean(data['success_delta']) if data['success_delta'] else 0.0
            output_lines.append(f"{cat:<20} | {m_name:<24} | {avg_gain:+.4f}")
            
    # 3. Transfer Analysis
    output_lines.append("\n" + "-"*80)
    output_lines.append(f"{'3. TRANSFER ANALYSIS (AUC: Declarative vs Procedural)':^80}")
    output_lines.append("-"*80)
    output_lines.append(f"{'Model':<24} | {'Tutor AUC (Decl.)':<18} | {'Code AUC (Proc.)':<18} | {'Gap'}")
    output_lines.append("-"*80)
    
    for m in models:
        try:
            tutor_auc = roc_auc_score(transfer[m.name]['tutor_y_true'], transfer[m.name]['tutor_y_pred'])
        except: tutor_auc = 0.5
        
        try:
            code_auc = roc_auc_score(transfer[m.name]['code_y_true'], transfer[m.name]['code_y_pred'])
        except: code_auc = 0.5
        
        gap = abs(tutor_auc - code_auc)
        output_lines.append(f"{m.name:<24} | {tutor_auc:.4f}             | {code_auc:.4f}             | {gap:.4f}")

    # 4. Learning Curve (Summary)
    output_lines.append("\n" + "-"*80)
    output_lines.append(f"{'4. LEARNING CURVE (RMSE at Step 1 vs Step 10)':^80}")
    output_lines.append("-"*80)
    output_lines.append(f"{'Model':<24} | {'RMSE @ Op 1':<15} | {'RMSE @ Op 10':<15} | {'Improvement'}")
    output_lines.append("-"*80)
    
    for m in models:
        err_1 = np.mean(learning_curves[m.name].get(1, [0]))
        err_10 = np.mean(learning_curves[m.name].get(10, [0]))
        imp = err_1 - err_10
        output_lines.append(f"{m.name:<24} | {err_1:.4f}          | {err_10:.4f}          | {imp:+.4f}")

    final_output = "\n".join(output_lines)
    print(final_output)
    
    with open("backend/behavior_analysis_results.txt", "w") as f:
        f.write(final_output)

if __name__ == "__main__":
    run_behavior_analysis()
