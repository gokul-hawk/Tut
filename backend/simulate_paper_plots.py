import json
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, mean_squared_error
from math import pi

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

# --- PLOTTING FUNCTIONS ---

def plot_learning_curves(learning_curves, output_dir):
    plt.figure(figsize=(10, 6))
    
    # Calculate Avg RMSE per opportunity across all students
    # learning_curves[model][opp_idx] = [err1, err2, ...]
    
    for model_name, opp_data in learning_curves.items():
        opps = sorted(opp_data.keys())
        rmse_values = []
        for op in opps:
            errors = opp_data[op]
            rmse = np.sqrt(np.mean(np.array(errors)**2))
            rmse_values.append(rmse)
            
        plt.plot(opps, rmse_values, label=model_name, linewidth=2, marker='o', markersize=4)

    plt.title("Learning Curve: Error Decay over Time", fontsize=14)
    plt.xlabel("Opportunity (Interaction Step)", fontsize=12)
    plt.ylabel("RMSE (vs Ground Truth)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(output_dir, "learning_curve.png"))
    plt.close()
    print("Generated learning_curve.png")

def plot_radar_chart(category_metrics, output_dir):
    # category_metrics[category][model] = AUC
    categories = list(category_metrics.keys())
    models = list(category_metrics[categories[0]].keys())
    
    # Number of variables
    N = len(categories)
    
    # What will be the angle of each axis in the plot?
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    
    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], categories, color='grey', size=10)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], color="grey", size=7)
    plt.ylim(0, 1)
    
    # Plot data
    for model in models:
        values = []
        for cat in categories:
            values.append(category_metrics[cat].get(model, 0))
        values += values[:1] # Close the loop
        
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=model)
        ax.fill(angles, values, alpha=0.1)
        
    plt.title("Model Expertise Areas (Accuracy by Category)", size=14, y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.savefig(os.path.join(output_dir, "radar_chart.png"))
    plt.close()
    print("Generated radar_chart.png")

def plot_trajectory(student_id, trajectories, student_events, output_dir):
    # trajectories[model] = [p1, p2, p3...]
    
    plt.figure(figsize=(12, 6))
    
    steps = range(len(student_events))
    
    # Plot Ground Truth (Step Functionish)
    # We can't easily plot continuous ground truth, but we can color background?
    # Or just plot traces.
    
    for model, trace in trajectories.items():
        plt.plot(steps, trace, label=model, linewidth=2)
        
    # Mark events
    for i, event in enumerate(student_events):
        source, result = event[0], event[1]
        color = 'green' if result else 'red'
        marker = '^' if source == 'tutor' else ('o' if source == 'code' else 's')
        # Plot event markers at y=1.05 or something?
        plt.scatter(i, 1.02, c=color, marker=marker, s=50, alpha=0.6)
        if i % 3 == 0: # label occasional to avoid clutter
            plt.text(i, 1.05, source, fontsize=8, rotation=45)

    plt.title(f"Mastery Trajectory: Student {student_id}", fontsize=14)
    plt.xlabel("Step Sequence", fontsize=12)
    plt.ylabel("P(Mastery)", fontsize=12)
    plt.ylim(0, 1.1)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, "trajectory_case_study.png"))
    plt.close()
    print("Generated trajectory_case_study.png")

def run_plots_generation():
    print(f"\n{'='*80}")
    print(f"{'GENERATING RESEARCH PLOTS' :^80}")
    print(f"{'='*80}\n")
    
    data_path = "backend/research_dataset.json"
    output_dir = "backend/plots"
    
    if not os.path.exists(data_path):
        print("Dataset not found!")
        return

    with open(data_path, "r") as f:
        dataset = json.load(f)

    # Initialize Models with Trained Parameters
    param_path = "backend/trained_models.json"
    trained_params = {"bkt": {}} 
    if os.path.exists(param_path):
        with open(param_path, "r") as f:
            trained_params = json.load(f)
        print(f"Loaded trained parameters for plots.")
        
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
    
    # Data Collectors
    learning_curves = {m.name: {} for m in models} # {model: {opp: [errors]}}
    category_acc = {cat: {m.name: [] for m in models} for cat in ["Lucky Guesser", "Deep Struggle", "Instant Expert", "Inconsistent"]}
    
    # Case Study Storage
    target_student_id = "struggle_0" # First deep struggle student
    trajectory_data = {m.name: [] for m in models}
    target_student_events = []
    
    for student in dataset:
        category = student.get("category", "")
        ground_truth = student.get("ground_truth_mastery", 0)
        events = student.get("events", [])
        sid = student.get("id", "")
        
        is_target = (sid == target_student_id)
        if is_target:
            target_student_events = events
            
        for m in models: m.reset()
        
        opp = 0
        for event in events:
            source = event[0]
            is_correct = event[1]
            opp += 1
            
            # Synthesize Metadata
            metadata = {}
            if category == "Lucky Guesser" and source == "code":
                 metadata["ai_usage"] = 15
            elif category == "Deep Struggle" and source == "code" and not is_correct:
                 metadata["test_failures"] = 6
            
            for m in models:
                # Prediction
                y_pred = m.mastery
                if is_target:
                    trajectory_data[m.name].append(y_pred)
                
                # Metrics Collection
                # 1. Learning Curve
                err = abs(ground_truth - y_pred)
                if opp not in learning_curves[m.name]: learning_curves[m.name][opp] = []
                learning_curves[m.name][opp].append(err)
                
                # 2. Radar Data (Accuracy per category)
                # We'll compute accuracy at the end
                if category in category_acc:
                    # Accuracy: round y_pred to 0/1 vs ground_truth
                    acc_hit = 1 if round(y_pred) == ground_truth else 0
                    category_acc[category][m.name].append(acc_hit)
                
                # Update
                if isinstance(m, ContextAwareMGKT):
                    # APPLY FIX HERE: The simulation in simulate_paper_plots.py
                    # calls m.update_with_context. Since it imports the class,
                    # the fix in simulate_advanced_mgkt.py will already be present.
                    m.update_with_context(is_correct, source, metadata)
                else:
                    try:
                        m.update(is_correct, source=source)
                    except TypeError:
                         m.update(is_correct, source)

    # Aggregations
    # Radar: Avg Accuracy per category
    radar_data = {}
    for cat, model_data in category_acc.items():
        radar_data[cat] = {}
        for m_name, hits in model_data.items():
            radar_data[cat][m_name] = np.mean(hits) if hits else 0
            
    # --- GENERATE PLOTS ---
    plot_learning_curves(learning_curves, output_dir)
    plot_radar_chart(radar_data, output_dir)
    plot_trajectory(target_student_id, trajectory_data, target_student_events, output_dir)
    
if __name__ == "__main__":
    run_plots_generation()
