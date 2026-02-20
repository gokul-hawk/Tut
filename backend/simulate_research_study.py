import sys
import os
import random
import json
import numpy as np

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports from existing files
try:
    from main_agent.services.scoring_engine import ScoringEngine
    from simulate_real_bkt import RealBKT
    from simulate_real_gkt import RealGKT
    from simulate_real_dkt import SimpleRNN
except ImportError:
    # Fallback
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.main_agent.services.scoring_engine import ScoringEngine
    from backend.simulate_real_bkt import RealBKT
    from backend.simulate_real_gkt import RealGKT
    from backend.simulate_real_dkt import SimpleRNN

# --- Wrappers (Copied from simulate_full_comparison.py to ensure consistency) ---
class RealDKTWrapper:
    def __init__(self, name="RealDKT"):
        self.name = name
        self.rnn = SimpleRNN(input_size=2, hidden_size=16, output_size=1)
        self.history = []
        self.mastery = 0.1
        
    def reset(self):
        self.history = []
        self.mastery = 0.1
        self.rnn = SimpleRNN(input_size=2, hidden_size=16, output_size=1)

    def update(self, is_correct, signal_type):
        feat = [1, 0] if is_correct else [0, 1]
        self.history.append(feat)
        outputs, _ = self.rnn.forward(np.array(self.history))
        self.mastery = outputs[-1][0][0]

class RealMGKTWrapper(RealBKT):
    def __init__(self, name="RealMGKT"):
        super().__init__(name)
        self.neighbor_mastery = 0.1

    def reset(self):
        super().reset()
        self.neighbor_mastery = 0.1

    def update(self, is_correct, signal_type):
        if signal_type == "debug":
            self.p_g = 0.01; self.p_t = 0.5
        elif signal_type == "code":
             self.p_g = 0.05; self.p_t = 0.3
        else:
             self.p_g = 0.25; self.p_t = 0.1
        super().update(is_correct, signal_type)
        if is_correct:
            strength = 0.5 if signal_type == "debug" else 0.2
            gain = (self.mastery - self.neighbor_mastery) * strength
            if gain > 0: self.neighbor_mastery += gain

# --- Data Generation ---
def generate_dataset(num_per_category=20):
    dataset = []
    
    # 1. Lucky Guesser (False Positive)
    # High tutor score (guessing), but heavily penalized in code/debug.
    # Ground Truth: They DON'T know the concept.
    for i in range(num_per_category):
        student = {
            "id": f"lucky_{i}", "category": "Lucky Guesser",
            "ground_truth_mastery": 0, # They are guessing!
            "events": [], 
            "scoring": {
                "tutor": {"total": 0, "correct": 0}, 
                "code": [], 
                "debug": {"attempts":0, "explanation_len":0}
            }
        }
        # Tutor Phase: Lucky guessing (Range 3-5)
        n_tutor = random.randint(3, 5)
        n_correct = n_tutor # All correct by guessing
        student["scoring"]["tutor"] = {"total": n_tutor, "correct": n_correct}
        student["events"].extend([("tutor", True)] * n_correct)
        
        # Code Phase: Exposed triggers (At least 3)
        # They pass code but with high AI usage
        for _ in range(3):
            student["events"].append(("code", True))
            student["scoring"]["code"].append({
                "difficulty": "easy", "passed": True, "ai_usage": 15, "test_failures": 0 
            })
            
        # Debug Phase: (At least 5)
        # They make many attempts but provide empty explanations (guessing)
        for _ in range(5):
             student["events"].append(("debug", False)) # Fail most
        student["scoring"]["debug"] = {"attempts": 5, "explanation_len": 5} # Low quality
        
        dataset.append(student)

    # 2. Instant Expert (Ideal)
    # Ground Truth: They KNOW the concept.
    for i in range(num_per_category):
        student = {
             "id": f"expert_{i}", "category": "Instant Expert",
             "ground_truth_mastery": 1,
             "events": [], 
             "scoring": {
                 "tutor": {"total": 0, "correct": 0}, 
                 "code": [], 
                 "debug": {"attempts":1, "explanation_len":60}
             }
        }
        # Tutor Phase: Range 3-5
        n_tutor = random.randint(3, 5)
        n_correct = n_tutor
        student["scoring"]["tutor"] = {"total": n_tutor, "correct": n_correct}
        student["events"].extend([("tutor", True)] * n_correct)
        
        # Code: 3 Perfect Code tasks
        for _ in range(3):
             student["events"].append(("code", True))
             student["scoring"]["code"].append({"difficulty": "hard", "passed": True, "ai_usage": 0, "test_failures": 0})
        
        # Debug: 5 Perfect Debug tasks
        for _ in range(5):
            student["events"].append(("debug", True))
            
        student["scoring"]["debug"] = {"attempts": 1, "explanation_len": 80} # High quality
        dataset.append(student)

    # 3. Deep Struggle (Hidden Potential)
    # Ground Truth: They eventually LEARNED it (Late Master).
    for i in range(num_per_category):
        student = {
             "id": f"struggle_{i}", "category": "Deep Struggle",
             "ground_truth_mastery": 1, # They got it in the end!
             "events": [], 
             "scoring": {
                 "tutor": {"total": 0, "correct": 0}, 
                 "code": [], 
                 "debug": {"attempts":2, "explanation_len":40}
             }
        }
        # Fails Tutor (Range 3-5, mostly fail)
        n_tutor = random.randint(3, 5)
        n_correct = max(0, n_tutor - 3) # At most 2 correct if 5, else 0 or 1
        # Let's say they get ~20-30% correct
        n_correct = int(n_tutor * 0.3)
        
        student["scoring"]["tutor"] = {"total": n_tutor, "correct": n_correct}
        student["events"].extend([("tutor", False)] * (n_tutor - n_correct) + [("tutor", True)] * n_correct)
        
        # Fails Code (3 attempts)
        for _ in range(3):
            student["events"].append(("code", False))
            student["scoring"]["code"].append({"difficulty": "medium", "passed": False, "ai_usage": 5, "test_failures": 8})
        
        # Success in Debug (Eureka) (5 attempts total, mostly correct now)
        # They struggled before but nailed the debug logic.
        for _ in range(5):
            student["events"].append(("debug", True))
            
        student["scoring"]["debug"] = {"attempts": 6, "explanation_len": 50} 
        dataset.append(student)

    # 4. Inconsistent (Noisy)
    # Ground Truth: They DON'T really know it (0).
    for i in range(num_per_category):
        student = {
             "id": f"inconsistent_{i}", "category": "Inconsistent",
             "ground_truth_mastery": 0,
             "events": [], 
             "scoring": {
                 "tutor": {"total": 0, "correct": 0}, 
                 "code": [], 
                 "debug": {"attempts":3, "explanation_len":15}
             }
        }
        # Random mix (Range 3-5)
        n_tutor = random.randint(3, 5)
        # ~50% correct
        n_correct = int(n_tutor * 0.5)
        student["scoring"]["tutor"] = {"total": n_tutor, "correct": n_correct}
        
        # Mix true/false
        tutor_events = [("tutor", True)] * n_correct + [("tutor", False)] * (n_tutor - n_correct)
        random.shuffle(tutor_events)
        student["events"].extend(tutor_events)
        
        # Code (3 mixed)
        student["events"].append(("code", True))
        student["scoring"]["code"].append({"difficulty": "easy", "passed": True, "ai_usage": 8, "test_failures": 2})
        student["events"].append(("code", False))
        student["scoring"]["code"].append({"difficulty": "hard", "passed": False, "ai_usage": 2, "test_failures": 5})
        student["events"].append(("code", True))
        student["scoring"]["code"].append({"difficulty": "medium", "passed": True, "ai_usage": 5, "test_failures": 1})
        
        # Debug (5 mixed)
        for _ in range(2): student["events"].append(("debug", True))
        for _ in range(3): student["events"].append(("debug", False))
        
        student["scoring"]["debug"] = {"attempts": 8, "explanation_len": 20}
        
        dataset.append(student)

    return dataset

def run_study():
    # 1. Generate & Save
    dataset = generate_dataset(20) # 80 total
    with open('backend/research_dataset.json', 'w') as f:
        json.dump(dataset, f, indent=2)
    print("Dataset generated/saved to backend/research_dataset.json (N=80)")

    # 2. Initialize Models
    models = {
        "BKT": RealBKT("BKT"),
        "DKT": RealDKTWrapper("DKT"),
        "GKT": RealGKT("GKT"),
        "MGKT": RealMGKTWrapper("MGKT")
    }
    scoring_engine = ScoringEngine()

    # 3. Evaluation Loop
    results = {cat: {"BKT": [], "DKT": [], "GKT": [], "MGKT": [], "Score": []} 
               for cat in ["Lucky Guesser", "Instant Expert", "Deep Struggle", "Inconsistent"]}

    print("\n--- Running Research Benchmarks ---")
    for student in dataset:
        cat = student["category"]
        
        # Reset Models
        for m in models.values(): m.reset()
        
        # Feed Events to KT Models
        for signal, correct in student["events"]:
            for m in models.values():
                m.update(correct, signal)
        
        # Capture End Mastery
        for name, m in models.items():
            results[cat][name].append(m.mastery)

        # Feed Data to Scoring Engine
        s = student["scoring"]
        t_score = scoring_engine.calculate_tutor_score(s["tutor"]["total"], s["tutor"]["correct"])
        c_score = scoring_engine.calculate_code_score(s["code"])
        d_score = scoring_engine.calculate_debug_score(s["debug"])
        final_score = scoring_engine.aggregate_final_score(t_score, c_score, d_score)
        
        results[cat]["Score"].append(final_score)

    # 4. Print Table
    print(f"{'Category':<20} | {'BKT':<8} | {'DKT':<8} | {'GKT':<8} | {'MGKT':<8} | {'SCORE (New)':<12}")
    print("-" * 85)
    
    for cat, metrics in results.items():
        row = f"{cat:<20} | "
        for m_name in ["BKT", "DKT", "GKT", "MGKT"]:
            avg = np.mean(metrics[m_name])
            row += f"{avg:.3f}    | "
        
        avg_score = np.mean(metrics["Score"])
        row += f"{avg_score:.2f}"
        print(row)
        
    print("-" * 85)

if __name__ == "__main__":
    run_study()
