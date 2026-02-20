import numpy as np
import random
import sys
import os

# Ensure backend modules are efficient
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulate_real_bkt import RealBKT
from simulate_real_gkt import RealGKT
from simulate_real_dkt import SimpleRNN

class RealDKTWrapper:
    """ Wrapper to make RNN behave like an incremental updater for the sim """
    def __init__(self, name="RealDKT"):
        self.name = name
        # Input: [Correct, Incorrect, Debug, Code] (Feature rich to be fair)
        # But standard DKT often just sees Correct/Incorrect.
        # We give it [Correct, Incorrect] to be standard DKT.
        self.rnn = SimpleRNN(input_size=2, hidden_size=16, output_size=1)
        self.history = []
        self.mastery = 0.1 # Public prop
        
    def reset(self):
        self.history = []
        self.mastery = 0.1
        # Re-init weights slightly to avoid state persistence
        self.rnn = SimpleRNN(input_size=2, hidden_size=16, output_size=1)

    def update(self, is_correct, signal_type):
        # DKT sees binary correctness mostly
        feat = [1, 0] if is_correct else [0, 1]
        self.history.append(feat)
        
        # Forward pass on whole history
        # (Inefficient O(N^2) but fine for simulation)
        outputs, _ = self.rnn.forward(np.array(self.history))
        self.mastery = outputs[-1][0][0] # Last output

class RealMGKTWrapper(RealBKT):
    """
    Our Model: Real BKT Math + Signal Weighting + Graph Propagation
    """
    def __init__(self, name="RealMGKT"):
        super().__init__(name)
        self.neighbor_mastery = 0.1

    def reset(self):
        super().reset()
        self.neighbor_mastery = 0.1

    def update(self, is_correct, signal_type):
        # 1. Dynamic Parameter Swapping (The innovation)
        if signal_type == "debug":
            # Debugging proves deep understanding -> High Transit, Low Guess
            self.p_g = 0.01 
            self.p_t = 0.5  # Jump!
        elif signal_type == "code":
             self.p_g = 0.05
             self.p_t = 0.3
        else: # Tutor (Standard BKT params)
             self.p_g = 0.25
             self.p_t = 0.1
             
        # 2. Standard BKT Update (The Math)
        super().update(is_correct, signal_type)
        
        # 3. Graph Propagation (The Graph part)
        # If we learned something, propagate it.
        # Simple heuristic: Neighbor attracts towards Self
        if is_correct:
            # Determine propagation strength based on signal
            strength = 0.5 if signal_type == "debug" else 0.2
            gain = (self.mastery - self.neighbor_mastery) * strength
            if gain > 0:
                self.neighbor_mastery += gain

# --- SCENARIO GENERATORS (Same as before) ---
def generate_lucky_guesser_cases(n=20):
    cases = []
    for i in range(n):
        guesses = [("tutor", True, "Guess")] * random.randint(2, 6)
        if random.random() < 0.7: expose = ("code", False, "Code Fail")
        else: expose = ("debug", False, "Debug Fail")
        cases.append((f"Lucky Guesser #{i+1}", guesses + [expose]))
    return cases

def generate_instant_expert_cases(n=20):
    cases = []
    for i in range(n):
        r = random.random()
        if r < 0.33: traj = [("code", True, "Code Success")]
        elif r < 0.66: traj = [("debug", True, "Debug Success")]
        else: traj = [("code", True, "Code Success"), ("debug", True, "Debug Success")]
        cases.append((f"Instant Expert #{i+1}", traj))
    return cases

def generate_deep_struggle_cases(n=20):
    cases = []
    for i in range(n):
        fails = [("tutor", False, "Fail")] * random.randint(3, 8)
        redeem = ("debug", True, "Eureka Moment")
        cases.append((f"Deep Struggle #{i+1}", fails + [redeem]))
    return cases

def generate_inconsistent_cases(n=20):
    cases = []
    for i in range(n):
        length = random.randint(5, 8)
        traj = []
        for _ in range(length):
            if random.random() < 0.7: traj.append(("tutor", False, "Theory Fail"))
            else: traj.append(("code", True, "Practical Success"))
        traj.append(("debug", True, "Final Debug"))
        cases.append((f"Inconsistent #{i+1}", traj))
    return cases

def run_batch_simulation():
    print(f"--- Running REAL LOGIC Batch Simulation (80 Cases) ---\n")
    
    # Instantiate Real Learners
    dkt_agent = RealDKTWrapper("RealDKT")
    bkt_agent = RealBKT("RealBKT") # Baseline
    gkt_agent = RealGKT("RealGKT")
    mgkt_agent = RealMGKTWrapper("OurModel")
    
    models = [bkt_agent, dkt_agent, gkt_agent, mgkt_agent]
    
    # Generate all cases
    all_scenarios = {
        "Lucky Guesser (False Positives)": generate_lucky_guesser_cases(20),
        "Instant Expert (Cold Start)": generate_instant_expert_cases(20),
        "Deep Struggle (Breakthrough)": generate_deep_struggle_cases(20),
        "Inconsistent (Noisy Signal)": generate_inconsistent_cases(20)
    }
    
    # Header
    print(f"{'Scenario':<30} | {'Metric':<10} | {'BKT':<8} | {'DKT':<8} | {'GKT':<8} | {'MGKT':<8}")
    print("-" * 90)
    
    for category, cases in all_scenarios.items():
        results = {m.name: [] for m in models}
        
        for name, traj in cases:
            # Reset
            for m in models: m.reset()
            
            # Run
            for sig, corr, desc in traj:
                for m in models:
                    m.update(corr, sig)
            
            # Log
            for m in models:
                results[m.name].append(m.mastery)
                
        # Stats
        means = {k: np.mean(v) for k,v in results.items()}
        stds = {k: np.std(v) for k,v in results.items()}
        
        
        # Save to dict
        scenario_results[category] = {
            "BKT": f"{means['RealBKT']:.3f} (+/- {stds['RealBKT']:.3f})",
            "DKT": f"{means['RealDKT']:.3f} (+/- {stds['RealDKT']:.3f})",
            "GKT": f"{means['RealGKT']:.3f} (+/- {stds['RealGKT']:.3f})",
            "MGKT": f"{means['OurModel']:.3f} (+/- {stds['OurModel']:.3f})"
        }

    import json
    with open('backend/results.json', 'w') as f:
        json.dump(scenario_results, f, indent=2)
    print("Results saved to backend/results.json")

if __name__ == "__main__":
    scenario_results = {}
    run_batch_simulation()

