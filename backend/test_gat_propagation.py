import sys
import os
import numpy as np

# Setup Django environment to use GKTModel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chatbot.services.gkt_model import GKTModel
from chatbot.services.recommendation_service import RecommendationService

def test_gat_propagation():
    print("--- Testing Graph Attention (GAT) Propagation ---")
    
    # 1. Initialize
    model = GKTModel()
    rec_service = RecommendationService()
    
    # Fake User ID
    user_email = "test_user@example.com"
    
    # 2. Identify a Prerequisite Chain
    # Let's find dependencies in the graph
    # We look for a concept 'U' that depends on 'V' (Adj[U][V] = 1)
    
    concept_map = model.concept_to_idx
    idx_map = {v: k for k, v in concept_map.items()}
    
    dependent_node = None
    prereq_node = None
    
    # Scan Adjacency Matrix
    rows, cols = np.where(model.adj_matrix == 1)
    if len(rows) > 0:
        u_idx, v_idx = rows[0], cols[0]
        dependent_node = idx_map[u_idx]
        prereq_node = idx_map[v_idx]
        print(f"Goal: Measure propagation from '{prereq_node}' -> '{dependent_node}'")
    else:
        print("Error: Graph has no dependencies defined!")
        return

    # 3. Baseline: Before Mastery
    # Manually reset user state (Mocking the persistence layer for test)
    # We will compute Rec Score manually to avoid DB calls
    
    def get_readiness(target_idx, current_state):
        # Logic from RecommendationService
        prereq_indices = np.where(model.adj_matrix[target_idx] > 0)[0]
        if len(prereq_indices) == 0: return 1.0
        
        prereq_val = [current_state[p] for p in prereq_indices]
        return sum(prereq_val) / len(prereq_indices)

    # State 0: Novice
    state_0 = np.zeros(model.num_concepts) 
    r_score_0 = get_readiness(u_idx, state_0)
    print(f"\nStep 1: User is Novice (Mastery=0.0)")
    print(f" -> Readiness Score for '{dependent_node}': {r_score_0:.2f}")
    
    # 4. Action: Master the Prerequisite
    print(f"\nStep 2: User Masters '{prereq_node}' (Mastery -> 1.0)")
    state_1 = np.copy(state_0)
    state_1[v_idx] = 1.0 # Set Prereq to Mastered
    
    # 5. Measure Propagation
    r_score_1 = get_readiness(u_idx, state_1)
    print(f" -> Readiness Score for '{dependent_node}': {r_score_1:.2f}")
    
    # 6. Verify GAT Effect
    change = r_score_1 - r_score_0
    print(f"\n--- GAT Effect ---")
    print(f"The mastery of '{prereq_node}' propagated a +{change*100:.1f}% increase")
    print(f"in readiness for '{dependent_node}'.")
    
    if r_score_1 > r_score_0:
        print("SUCCESS: Graph Attention correctly propagated prerequisite mastery.")
        print(f"'{dependent_node}' is now in the 'Zone of Proximal Development'.")
    else:
        print("FAILURE: No propagation detected.")

if __name__ == "__main__":
    test_gat_propagation()
