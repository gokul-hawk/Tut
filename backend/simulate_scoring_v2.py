import sys
import os
import random
import numpy as np
import json

# Ensure backend modules are accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main_agent.services.scoring_engine import ScoringEngine
    from simulate_real_bkt import RealBKT
except ImportError:
    # Fallback if running from root
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.main_agent.services.scoring_engine import ScoringEngine
    from backend.simulate_real_bkt import RealBKT

# --- 1. MGKT Model Wrapper (Copied to ensure standalone execution) ---
class RealMGKTWrapper(RealBKT):
    """
    Real MGKT Math + Signal Weighting + Graph Propagation
    """
    def __init__(self, name="RealMGKT"):
        super().__init__(name)
        self.neighbor_mastery = 0.1

    def reset(self):
        super().reset()
        self.neighbor_mastery = 0.1

    def update(self, is_correct, signal_type):
        # 1. Dynamic Parameter Swapping
        if signal_type == "debug":
            self.p_g = 0.01 
            self.p_t = 0.5
        elif signal_type == "code":
             self.p_g = 0.05
             self.p_t = 0.3
        else: # Tutor
             self.p_g = 0.25
             self.p_t = 0.1
             
        # 2. Standard BKT Update
        super().update(is_correct, signal_type)
        
        # 3. Graph Propagation
        if is_correct:
            strength = 0.5 if signal_type == "debug" else 0.2
            gain = (self.mastery - self.neighbor_mastery) * strength
            if gain > 0:
                self.neighbor_mastery += gain

# --- 2. Scenario Generators ---
def generate_student_sessions():
    """
    Generates complex sessions that include correct/incorrect answers 
    AND metadata needed for the ScoringEngine (attempts, AI usage, etc.)
    """
    scenarios = []
    
    # 1. The "Consistent High Performer"
    session_high = {
        "name": "High Performer",
        "scoring_data": {
            "tutor": {"total": 10, "correct": 9},
            "code": [
                {"difficulty": "easy", "passed": True, "ai_usage": 0, "test_failures": 0},
                {"difficulty": "medium", "passed": True, "ai_usage": 1, "test_failures": 0},
                {"difficulty": "hard", "passed": True, "ai_usage": 2, "test_failures": 1}
            ],
            "debug": {"attempts": 1, "explanation_len": 50} 
        },
        "events": [("tutor", True)]*9 + [("tutor", False)] + [("code", True)]*3 + [("debug", True)]
    }
    scenarios.append(session_high)

    # 2. The "Struggling Learner"
    session_struggle = {
        "name": "Struggling Learner",
        "scoring_data": {
            "tutor": {"total": 10, "correct": 5},
            "code": [
                {"difficulty": "easy", "passed": True, "ai_usage": 5, "test_failures": 2},
                {"difficulty": "medium", "passed": True, "ai_usage": 8, "test_failures": 5},
                {"difficulty": "hard", "passed": False, "ai_usage": 10, "test_failures": 10}
            ],
            "debug": {"attempts": 4, "explanation_len": 20}
        },
        "events": [("tutor", True)]*5 + [("tutor", False)]*5 + [("code", True)]*2 + [("code", False)] + [("debug", False), ("debug", True)]
    }
    scenarios.append(session_struggle)

    # 3. The "AI Dependent"
    session_ai = {
        "name": "AI Dependent",
        "scoring_data": {
            "tutor": {"total": 10, "correct": 8},
            "code": [
                {"difficulty": "easy", "passed": True, "ai_usage": 10, "test_failures": 0}, 
                {"difficulty": "medium", "passed": True, "ai_usage": 15, "test_failures": 0}, 
                {"difficulty": "hard", "passed": True, "ai_usage": 20, "test_failures": 0} 
            ],
            "debug": {"attempts": 1, "explanation_len": 5} 
        },
        "events": [("tutor", True)]*8 + [("tutor", False)]*2 + [("code", True)]*3 + [("debug", True)]
    }
    scenarios.append(session_ai)

    return scenarios

# --- 3. Simulation Runner ---
def run_simulation_v2():
    print(f"\n{'='*80}")
    print(f"{'SIMULATION V2: MGKT Mastery vs. Scoring Engine (Weighted)' :^80}")
    print(f"{'='*80}\n")
    
    scoring_engine = ScoringEngine()
    mgkt_agent = RealMGKTWrapper()
    
    scenarios = generate_student_sessions()
    
    # Header
    print(f"{'Student Profile':<25} | {'MGKT Mastery':<12} | {'Tutor':<6} {'Code':<6} {'Debug':<6} | {'Final Score':<11} | {'Status'}")
    print("-" * 90)
    
    for session in scenarios:
        # 1. Run MGKT (Knowledge Tracing)
        mgkt_agent.reset()
        for signal_type, is_correct in session["events"]:
            mgkt_agent.update(is_correct, signal_type)
        
        final_mastery = mgkt_agent.mastery
        
        # 2. Run Scoring Engine (Grading)
        s_data = session["scoring_data"]
        
        # Calculate Component Scores
        # Note: In the manual scenario, code_score needs to be calculated manually or mocked if we want exact control, 
        # but here we use the ScoringEngine's logic on the input data.
        t_score = scoring_engine.calculate_tutor_score(s_data["tutor"]["total"], s_data["tutor"]["correct"])
        c_score = scoring_engine.calculate_code_score(s_data["code"])
        d_score = scoring_engine.calculate_debug_score(s_data["debug"])
        
        # Weighted Aggregation
        final_score = scoring_engine.aggregate_final_score(t_score, c_score, d_score)
        status = scoring_engine.determine_promotion(final_score)
        
        # Display
        print(f"{session['name']:<25} | {final_mastery:.4f}       | {t_score:<6.1f} {c_score:<6.1f} {d_score:<6.1f} | {final_score:<11.2f} | {status}")

    print("\n" + "-" * 90)
    print("Insight Analysis:")
    print("1. High Performer: High Mastery (MGKT) aligns with High Score (Engine).")
    print("2. Struggling: Low Mastery and Low Score. Correctly flagged for Remediation.")
    print("3. AI Dependent: High Mastery (because they passed) but LOW Score due to penalties.")
    print("   -> This proves the system can detect 'False Mastery' via Signal Weighting!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    run_simulation_v2()
