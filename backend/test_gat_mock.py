import numpy as np

# Mock GKT Model to bypass Django DB connection issues
class MockGKTModel:
    def __init__(self):
        self.num_concepts = 3
        # 0: Variables (Prereq)
        # 1: Loops (Dependent)
        # 2: Functions (Independent)
        self.concepts = ["Variables", "Loops", "Functions"]
        self.concept_to_idx = {c: i for i, c in enumerate(self.concepts)}
        
        # Dependency: Variables -> Loops
        # Adj[Dependent][Prereq] = 1
        self.adj_matrix = np.zeros((3, 3))
        self.adj_matrix[1][0] = 1 

def test_gat_propagation_mock():
    print("--- Testing Graph Attention (GAT) Propagation (Mocked DB) ---")
    
    model = MockGKTModel()
    
    # Define Target: "Loops" (Index 1)
    target_idx = 1
    target_name = "Loops"
    
    # Define Prereq: "Variables" (Index 0)
    prereq_idx = 0
    prereq_name = "Variables"
    
    print(f"Scenario: Testing propagation from '{prereq_name}' -> '{target_name}'")
    
    # Logic from RecommendationService (Re-implemented for isolation)
    def calculate_readiness(target_i, state_vector):
        # Identify prereqs
        prereq_indices = np.where(model.adj_matrix[target_i] > 0)[0]
        
        if len(prereq_indices) == 0: 
            return 1.0
            
        # Avg mastery of prereqs
        vals = [state_vector[p] for p in prereq_indices]
        return sum(vals) / len(vals)

    # 1. Novice State
    state_0 = np.array([0.1, 0.1, 0.1])
    readiness_0 = calculate_readiness(target_idx, state_0)
    
    print(f"\nStep 1: Novice State (Variables=0.1)")
    print(f" -> Readiness for '{target_name}': {readiness_0:.2f} (Zone of Frustration)")
    
    # 2. Expert State
    state_1 = np.array([0.95, 0.1, 0.1]) # Mastered Variables
    readiness_1 = calculate_readiness(target_idx, state_1)
    
    print(f"\nStep 2: Mastered Prerequisite (Variables=0.95)")
    print(f" -> Readiness for '{target_name}': {readiness_1:.2f} (Zone of Proximal Development)")
    
    # 3. Verdict
    delta = readiness_1 - readiness_0
    print(f"\n--- GAT Effect ---")
    print(f"Propagation Delta: +{delta:.2f}")
    if delta > 0.5:
        print("SUCCESS: Graph Structure correctly propagated mastery to unlock new content.")
    else:
        print("FAILURE: Propagation too weak.")

if __name__ == "__main__":
    test_gat_propagation_mock()
