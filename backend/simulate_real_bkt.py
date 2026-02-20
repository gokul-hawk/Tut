import numpy as np

class RealBKT:
    """
    Standard Bayesian Knowledge Tracing (Corbett & Anderson, 1995).
    mathematically rigorous HMM implementation.
    """
    def __init__(self, name="RealBKT", p_init=0.1, p_transit=0.1, p_guess=0.2, p_slip=0.2):
        self.name = name
        self.p_l = p_init  # P(L_t)
        self.p_t = p_transit
        self.p_g = p_guess
        self.p_s = p_slip
        
        # Neighbor tracking is NOT part of BKT (Independent HMMs)
        # We track it purely for simulation table compatibility, but it never updates.
        self.neighbor_mastery = 0.1 
        self.mastery = p_init

    def reset(self):
        self.p_l = 0.1
        self.neighbor_mastery = 0.1
        self.mastery = 0.1

    def update(self, is_correct, signal_type):
        """
        Bayesian Update Rule:
        1. Calculate P(L_t | Evidence)
        2. Calculate P(L_{t+1}) = P(L_t|E) + (1 - P(L_t|E)) * P(T)
        """
        # BKT is signal-blind: It ignores 'signal_type' and uses fixed G/S params
        
        if is_correct:
            # P(L|Correct) = [P(L) * (1-P(S))] / [P(L)*(1-P(S)) + (1-P(L))*P(G)]
            likelihood = (self.p_l * (1 - self.p_s)) / \
                         (self.p_l * (1 - self.p_s) + (1 - self.p_l) * self.p_g)
        else:
            # P(L|Incorrect) = [P(L) * P(S)] / [P(L)*P(S) + (1-P(L))*(1-P(G))]
            likelihood = (self.p_l * self.p_s) / \
                         (self.p_l * self.p_s + (1 - self.p_l) * (1 - self.p_g))
                         
        # Transition Step: Learning happens AFTER the observation
        self.p_l = likelihood + (1 - likelihood) * self.p_t
        
        # Output Interface
        self.mastery = self.p_l # Update public property

