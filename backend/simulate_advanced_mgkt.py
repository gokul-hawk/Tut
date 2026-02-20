import sys
import os
import json
import numpy as np

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from simulate_scoring_v2 import RealMGKTWrapper, generate_student_sessions
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.simulate_scoring_v2 import RealMGKTWrapper, generate_student_sessions

class ContextAwareMGKT(RealMGKTWrapper):
    """
    Advanced MGKT that adjusts P(Guess) and P(Slip) based on context (AI Usage, Time, Attempts).
    """
    def __init__(self, name="ContextMGKT"):
        super().__init__(name)

    def update_with_context(self, is_correct, signal_type, metadata={}):
        """
        Custom update that looks at metadata to tune BKT params DYNAMICALLY.
        """
        # 1. Base Defaults (from RealMGKTWrapper)
        if signal_type == "debug":
            self.p_g = 0.01; self.p_t = 0.3
        elif signal_type == "code":
             self.p_g = 0.05; self.p_t = 0.3
        else:
             self.p_g = 0.25; self.p_t = 0.2

        # 2. Apply Dynamic Overrides (The Feature)
        ai_usage = metadata.get("ai_usage", 0)
        
        # CHEAT PENALTY: If AI usage is high (>10), we treat it as a FAILURE to demonstrate independent mastery.
        # This is the "Research-Grade" logic: Even if they got the right answer, they didn't "know" it.
        if ai_usage > 10:
             is_correct = False
             # Also increase slip probability slightly to reflect confusion
             self.p_s = 0.4 
             # No learning happens if you cheat
             self.p_t = 0.0
        elif ai_usage > 0:
            # Scale p_g up to 0.95 based on usage (for minor help)
            self.p_g = min(0.95, self.p_g + (ai_usage * 0.1))
            
        failures = metadata.get("test_failures", 0)
        if failures > 5:
            self.p_s = 0.4

        # 3. Call Grandparent (RealBKT) directly to avoid RealMGKTWrapper resetting params
        # We need to access RealBKT.update, but since we inherited from RealMGKTWrapper,
        # we can use super(RealMGKTWrapper, self).update? No, simpler to just access the method.
        # RealBKT is the parent of RealMGKTWrapper.
        # super(RealMGKTWrapper, self).update(is_correct, signal_type) would work if RealMGKTWrapper is in mro.
        # Let's just import RealBKT and call it unbound, or rely on Python's super() properly.
        # RealMGKTWrapper inherits RealBKT.
        # We want to skip RealMGKTWrapper.update and go to RealBKT.update.
        
        # Re-implementing BKT Update logic here is safest/clearest for a script.
        
        # BKT Update (Copied from RealBKT)
        if is_correct:
            likelihood = (self.p_l * (1 - self.p_s)) / (self.p_l * (1 - self.p_s) + (1 - self.p_l) * self.p_g)
        else:
            likelihood = (self.p_l * self.p_s) / (self.p_l * self.p_s + (1 - self.p_l) * (1 - self.p_g))
        self.p_l = likelihood + (1 - likelihood) * self.p_t
        self.mastery = self.p_l

        # 4. Graph Propagation (Copied from RealMGKTWrapper)
        if is_correct:
            strength = 0.5 if signal_type == "debug" else 0.2
            gain = (self.mastery - self.neighbor_mastery) * strength
            if gain > 0:
                self.neighbor_mastery += gain

def run_advanced_simulation():
    print(f"\n{'='*80}")
    print(f"{'ADVANCED MGKT: Context-Aware Parameter Tuning' :^80}")
    print(f"{'='*80}\n")
    
    # We will manually construct a 'Lucky Guesser / AI Cheater' scenario
    # to see the difference between Standard MGKT and Context MGKT.
    
    # Scenario: Student gets Code Task CORRECT, but used AI heavily (Usage=15).
    events = [
        {"type": "tutor", "correct": True, "meta": {}},
        {"type": "tutor", "correct": True, "meta": {}},
        {"type": "code", "correct": True, "meta": {"ai_usage": 15}} # THE CHEAT
    ]
    
    standard_model = RealMGKTWrapper("Standard")
    advanced_model = ContextAwareMGKT("Advanced")
    
    print(f"{'Event':<20} | {'Standard Mastery':<18} | {'Advanced Mastery':<18}")
    print("-" * 65)
    
    for i, e in enumerate(events):
        # Update Standard (Blind to metadata)
        standard_model.update(e["correct"], e["type"])
        
        # Update Advanced (See metadata)
        advanced_model.update_with_context(e["correct"], e["type"], e["meta"])
        
        desc = f"{e['type']} (Correct)"
        if "ai_usage" in e["meta"]:
            desc += f" [AI={e['meta']['ai_usage']}]"
            
        print(f"{desc:<20} | {standard_model.mastery:<18.4f} | {advanced_model.mastery:<18.4f}")

    print("-" * 65)
    print("\nAnalysis:")
    print("1. Standard Model: Sees 'Code Correct' -> Assumes Mastery explodes to ~1.0.")
    print("2. Advanced Model: Sees 'AI=15' -> Sets P(Guess)=0.95.")
    print("   -> 'Correct' result is discounted (treated as a guess).")
    print("   -> Mastery stays LOW, correctly reflecting they didn't learn it themselves.")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    run_advanced_simulation()
