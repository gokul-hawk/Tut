
import numpy as np
from .gkt_model import GKTModel

class RecommendationService:
    """
    Dynamic Recommendation Engine.
    uses GKT Mastery State + Graph Structure to recommend the next best step.
    """
    def __init__(self):
        self.gkt = GKTModel()

    def get_next_best_step(self, user_email, topic_name):
        """
        Determines the next optimal concept to teach.
        Strategy:
        1. Identify all concepts related to 'topic_name' (Subgraph).
        2. Filter out concepts that are already Mastered (Score > 0.85).
        3. Among the remaining, find the one with the highest "Readiness":
           - Readiness = Average Mastery of its Prerequisites.
           - If Prereqs are not mastered, we shouldn't teach this yet.
        """
        # 1. Get User State
        vectors = self.gkt._get_user_vectors(user_email)
        
        # Use 'tutor' vector for Prerequisite Readiness (Conceptual Understanding)
        # If 'tutor' key missing (legacy), try to use 'vectors' itself if it's a list
        if isinstance(vectors, dict):
             tutor_vec = vectors.get("tutor", [])
        elif isinstance(vectors, list):
             tutor_vec = vectors
        else:
             tutor_vec = []

        candidates = []
        for idx, concept in enumerate(self.gkt.concepts):
            # Safe Access
            if idx >= len(tutor_vec):
                mastery = 0.0
            else:
                mastery = tutor_vec[idx]
            
            if mastery >= 0.85:
                continue # Already mastered
                
            # Check Prerequisites (Incoming Edges in Adj Matrix)
            # Adj[v][u] = 1 means u -> v (u is prereq for v)
            # Wait, in GKTModel: adj[u][v] = 1 # Edge from Prereq(v) to Dependent(u)
            # So looking at row 'u' (Dependent), we see columns 'v' (Prereqs) where adj[u][v] == 1
            
            prereq_indices = np.where(self.gkt.adj_matrix[idx] > 0)[0]
            
            if len(prereq_indices) == 0:
                # No prereqs? It's a foundational concept. High readiness.
                readiness = 1.0
            else:
                # Avg mastery of prereqs
                # Safe Access with tutor_vec (handling potential index out of bounds if graph grew)
                prereq_masteries = []
                for p_idx in prereq_indices:
                     if p_idx < len(tutor_vec):
                         prereq_masteries.append(tutor_vec[p_idx])
                     else:
                         prereq_masteries.append(0.0)

                readiness = sum(prereq_masteries) / len(prereq_indices)
            
            # Additional Heuristic: Is this concept related to the requested "topic"?
            if topic_name.lower() in getattr(concept, 'lower', lambda: str(concept).lower())(): 
                 pass # Could boost here

            candidates.append({
                "concept": concept,
                "readiness": readiness,
                "current_mastery": mastery
            })
            
        # 3. Sort by Readiness (Desc) then Mastery (Asc - teach undefined things first)
        if not candidates:
            return None # All mastered!
            
        # Sort: Highest Readiness first. Tie-break: Low mastery.
        candidates.sort(key=lambda x: (x["readiness"], -x["current_mastery"]), reverse=True)
        
        best_candidate = candidates[0]
        
        print(f"[Recommender] Best Step: {best_candidate['concept']} (Readiness: {best_candidate['readiness']:.2f})")
        return best_candidate["concept"]
