import sys
import os
import numpy as np

# Mock GKT Model with 2 Independent Concepts
class MockGKT:
    def __init__(self):
        self.concepts = ["Node A", "Node B"]
        self.num_concepts = 2
        self.adj_matrix = np.zeros((2, 2)) # Independent
        
    def _get_user_vector(self, user_email):
        # Allow checking persistent state or mock state
        if hasattr(self, 'mock_state'):
            return self.mock_state
        return np.array([0.1, 0.1]) 

# Mock Recommendation Service importing MockGKT
class MockRecService:
    def __init__(self):
        self.gkt = MockGKT()

    def get_recommendation(self, current_vector):
        self.gkt.mock_state = current_vector
        candidates = []
        for idx, concept in enumerate(self.gkt.concepts):
            mastery = current_vector[idx]
            # No prereqs -> Readiness = 1.0
            readiness = 1.0 
            candidates.append({
                "concept": concept,
                "readiness": readiness,
                "current_mastery": mastery
            })
            
        # The EXACT logic from recommendation_service.py
        # candidates.sort(key=lambda x: (x["readiness"], -x["current_mastery"]), reverse=True)
        candidates.sort(key=lambda x: (x["readiness"], -x["current_mastery"]), reverse=True)
        return candidates[0]

def test_tiebreak():
    print("--- Testing Recommendation Logic on Failure ---")
    rec = MockRecService()
    
    # State 0: Both Equal
    # A=0.1, B=0.1
    state_0 = np.array([0.1, 0.1])
    # Tie-break might depend on stable sort or list order. Python sort is stable.
    # List: [A, B]. Tie. Stable sort preserves A first.
    
    print(f"State 0: Node A ({state_0[0]}), Node B ({state_0[1]})")
    choice_0 = rec.get_recommendation(state_0)
    print(f" -> System Recommends: {choice_0['concept']}")
    
    # State 1: User attempts A and FAILS
    # Mastery drops from 0.1 -> 0.05
    # B remains 0.1
    state_1 = np.array([0.05, 0.1])
    print(f"\nState 1: FAILS Node A. Mastery drops.")
    print(f"Current State: Node A ({state_1[0]}), Node B ({state_1[1]})")
    
    choice_1 = rec.get_recommendation(state_1)
    
    print(f" -> System Recommends: {choice_1['concept']}")
    
    if choice_1['concept'] == "Node A":
        print("\nCONCLUSION: The system is PERSISTENT. It retries the failed node (Lower Mastery).")
    else:
        print("\nCONCLUSION: The system SWITCHE. It picked the other node.")

if __name__ == "__main__":
    test_tiebreak()
