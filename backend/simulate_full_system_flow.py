
import sys
import os
import random
import numpy as np

# Ensure backend modules are efficient
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main_agent.services.scoring_engine import ScoringEngine
except ImportError:
    # Fallback if running from root
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.main_agent.services.scoring_engine import ScoringEngine

# INLINED MOCK BKT LOGIC (To avoid dependency hell)
class MockBKTSingle:
    """
    Standaard BKT Logic for a single node.
    """
    def __init__(self, name="MockBKT"):
        self.p_L = 0.1 # Prior Mastery
        self.p_T = 0.1 # Transit
        self.p_G = 0.25 # Guess
        self.p_S = 0.1 # Slip
        self.mastery = self.p_L

    def reset(self):
        self.mastery = 0.1

    def update(self, is_correct):
        """
        Standard BKT Update Formula
        """
        curr = self.mastery
        
        # 1. Inference Step
        if is_correct:
            num = curr * (1 - self.p_S)
            den = num + (1 - curr) * self.p_G
        else:
            num = curr * self.p_S
            den = num + (1 - curr) * (1 - self.p_G)
            
        posterior = num / (den + 1e-9)
        
        # 2. Learning Step
        self.mastery = posterior + (1 - posterior) * self.p_T
        return self.mastery

class MockGKT:
    """
    Mock of GKTModel that implements the Stratified Mastery Logic
    Logic: (Tutor * 0.25) + (Code * 0.35) + (Debug * 0.40)
    """
    def __init__(self):
        # We use simple float values to represent a "Single Concept" mastery
        # In reality, these are vectors, but for sim we track one concept.
        self.tutor_bkt = MockBKTSingle("TutorBKT")
        self.code_bkt = MockBKTSingle("CodeBKT")
        self.debug_bkt = MockBKTSingle("DebugBKT")
        
        # Initial State (Cold Start)
        self.tutor_bkt.reset()
        self.code_bkt.reset()
        self.debug_bkt.reset()

    def get_mastery(self):
        m_tutor = self.tutor_bkt.mastery
        m_code = self.code_bkt.mastery
        m_debug = self.debug_bkt.mastery
        
        # STRATIFIED FORMULA
        total = (m_tutor * 0.25) + (m_code * 0.35) + (m_debug * 0.40)
        return total, m_tutor, m_code, m_debug

    def update(self, source_type, is_correct):
        """
        Updates ONLY the specific component based on source.
        """
        if source_type == "tutor":
            self.tutor_bkt.update(is_correct)
        elif source_type == "code":
            self.code_bkt.update(is_correct)
        elif source_type == "debug":
            self.debug_bkt.update(is_correct)
            
        return self.get_mastery()


def run_full_system_trace():
    output_lines = []
    
    scoring_engine = ScoringEngine()
    
    # Define Scenarios
    scenarios = [
        {
            "name": "Scenario 1: The 'Theory Master' (Understanding Phase)",
            "actions": [
                {"type": "tutor", "data": {"total": 5, "correct": 5}, "desc": "Perfect Quiz (5/5)"},
                {"type": "tutor", "data": {"total": 5, "correct": 4}, "desc": "Good Quiz (4/5)"},
                {"type": "code",  "data": {"passed": False, "ai_usage": 5, "test_failures": 3, "difficulty": "easy"}, "desc": "Fail Code (Too many hints)"}
            ]
        },
        {
            "name": "Scenario 2: The 'Practical Hacker' (Applying Phase)",
            "actions": [
                {"type": "tutor", "data": {"total": 5, "correct": 2}, "desc": "Bad Quiz (2/5)"},
                {"type": "code",  "data": {"passed": True, "ai_usage": 0, "test_failures": 0, "difficulty": "easy"}, "desc": "Perfect Code (Easy)"},
                {"type": "code",  "data": {"passed": True, "ai_usage": 1, "test_failures": 1, "difficulty": "medium"}, "desc": "Good Code (Medium)"}
            ]
        },
        {
            "name": "Scenario 3: The 'Analyst' (Analysis Phase)",
            "actions": [
                {"type": "debug", "data": {"attempts": 1, "reasoning": "full"}, "desc": "Perfect Debug"},
                {"type": "debug", "data": {"attempts": 5, "reasoning": "none"}, "desc": "Struggle Debug"}
            ]
        }
    ]

    for scenario in scenarios:
        output_lines.append(f"\n>>> {scenario['name']}")
        output_lines.append(f"{'-'*120}")
        output_lines.append(f"{'Action':<30} | {'Raw Score':<10} | {'Threshold (>80)':<15} | {'BKT Update?':<12} | {'New Mastery (Total | T/C/D)':<35}")
        output_lines.append(f"{'-'*120}")
        
        gkt = MockGKT()
        
        for action in scenario["actions"]:
            source = action["type"]
            data = action["data"]
            
            # 1. SCORING ENGINE
            if source == "tutor":
                score = scoring_engine.calculate_tutor_score(data["total"], data["correct"])
            elif source == "code":
                score = scoring_engine.calculate_code_score([data]) # Expects list
            elif source == "debug":
                 if "reasoning" in data:
                     debug_stats = {"attempts": data["attempts"], "explanation_len": 50 if data["reasoning"] == "full" else 0}
                     score = scoring_engine.calculate_debug_score(debug_stats)
                 else:
                     score = 0
                
            # 2. THRESHOLD CHECK (The Logic in Views.py)
            is_mastery_signal = float(score) >= 80.0
            
            # 3. BKT UPDATE 
            # Note: The view passes is_mastery_signal as 'is_correct' to GKT.update
            total_m, mt, mc, md = gkt.update(source, is_mastery_signal)
            
            # Log
            bkt_status = "Positive" if is_mastery_signal else "Negative"
            
            output_lines.append(f"{action['desc']:<30} | {score:<10.2f} | {str(is_mastery_signal):<15} | {bkt_status:<12} | {total_m:.2f} ({mt:.2f}/{mc:.2f}/{md:.2f})")

    output_lines.append(f"\n{'='*100}")
    output_lines.append("INSIGHTS:")
    output_lines.append("1. 'Negative' BKT Update means the mastery DROPPED because the score < 80.")
    output_lines.append("   -> Just 'passing' the code isn't enough; you need a HIGH Quality Score.")
    output_lines.append("2. Notice how 'Perfect Debug' drastically spikes the Total Score?")
    output_lines.append("   -> Debug weight is 0.40, effectively lifting the entire mastery ceiling.")
    output_lines.append(f"{'='*100}\n")
    
    # Print for user + Write to file
    final_output = "\n".join(output_lines)
    print(final_output)
    
    with open("backend/simulation_output.txt", "w") as f:
        f.write(final_output)

if __name__ == "__main__":
    run_full_system_trace()
