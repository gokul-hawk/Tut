import numpy as np

class BKTService:
    """
    Bayesian Knowledge Tracing (BKT) Service.
    
    Responsibility:
    - Update individual node mastery (Probability 0.0 to 1.0) based on immediate feedback.
    - Handle different 'signals' (Tutor, Code, Debug) with different reliability weights.
    
    Logic:
    - Standard BKT: Prior -> Likelihood -> Posterior -> Transit.
    - Multi-Signal: 'Code-Agent' and 'Debugger' signals have lower 'Slip' probability than 'Tutor' signals,
      meaning a success there is stronger evidence of true mastery.
    """
    def __init__(self):
        # Base Parameters (Standard BKT)
        # P(L0): Initial learning probability (useless for running updates, used for init)
        # P(T):  Transition probability (learning from the step)
        # P(S):  Slip probability (Mastered but failed)
        # P(G):  Guess probability (Not mastered but guessed right)
        self.default_params = {
            "p_transit": 0.1,    # Chance they learned something new this step
            "p_slip": 0.1,       # Chance they messed up despite knowing it
            "p_guess": 0.2       # Chance they guessed correctly
        }

    def update_node(self, current_mastery, is_correct, source_type="tutor"):
        """
        Updates the mastery probability for a single node.
        
        Args:
            current_mastery (float): Prior probability (0.0 - 1.0).
            is_correct (bool): Did they get it right?
            source_type (str): "tutor" (Socratic), "code" (Agent), "debug" (Reasoning).
            
        Returns:
            float: Posterior mastery probability.
        """
        # 1. Select Parameters based on Source Reliability
        params = self.default_params.copy()
        
        if source_type == "code":
            # Applying Phase (Heavy Weightage)
            # Success here implies strong application skills.
            params["p_guess"] = 0.05
            params["p_slip"] = 0.10   # Lower slip than before
            params["p_transit"] = 0.3 # High learning value (Application)
            
        elif source_type == "debug":
            # Analysis Phase (Heavy Weightage)
            # Success here implies deep understanding/reasoning.
            params["p_guess"] = 0.01 
            params["p_slip"] = 0.05   # Very low slip (Hard to fake)
            params["p_transit"] = 0.4 # Very high learning value (Analysis)
            
        elif source_type == "tutor":
            # Understanding Phase (Standard)
            # Multiple choice or simple Q&A has higher guess factor.
            params["p_guess"] = 0.25 
            params["p_slip"] = 0.15
            
        # 2. Bayesian Update (The Math)
        prior = current_mastery
        p_s = params["p_slip"]
        p_g = params["p_guess"]
        p_t = params["p_transit"]
        
        if is_correct:
            # P(L|Correct) = (P(Correct|L) * P(L)) / P(Correct)
            # P(Correct|L) = 1 - P(Slip)
            # P(Correct|~L) = P(Guess)
            likelihood = (prior * (1 - p_s)) / (prior * (1 - p_s) + (1 - prior) * p_g)
        else:
            # P(L|Incorrect) = (P(Incorrect|L) * P(L)) / P(Incorrect)
            # P(Incorrect|L) = P(Slip)
            # P(Incorrect|~L) = 1 - P(Guess)
            likelihood = (prior * p_s) / (prior * p_s + (1 - prior) * (1 - p_g))
            
        # 3. Transition (Learning) Update
        # P(L_next) = P(L_current) + P(T)*(1 - P(L_current))
        posterior = likelihood + (1 - likelihood) * p_t
        
        # 4. Clamp to avoid 0.0 or 1.0 lock-in
        posterior = max(0.01, min(0.99, posterior))
        
        print(f"[BKT] Node Update ({source_type}): {prior:.2f} -> {posterior:.2f} (Correct={is_correct})")
        return posterior
