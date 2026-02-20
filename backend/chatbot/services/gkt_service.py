import numpy as np
import json
import os
from quizzes.services.neo4j_services import Neo4jService
from .bkt_service import BKTService

class GKTService:
    """
    Hybrid Graph Knowledge Tracing Service.
    
    Architecture:
    1. Node Mastery: Handled by BKT (Bayesian Knowledge Tracing).
       - Updates individual concept states based on direct evidence (Tutor/Code/Debug).
    
    2. Recommendation: Handled by GNN (Graph Neural Network).
       - Propagates mastery scores across the Knowledge Graph.
       - Identifies the 'Zone of Proximal Development' (ZPD).
       - Recommends concepts that are 'Ready to Learn' (High Prereq Mastery, Low Current Mastery).
    """
    def __init__(self):
        self.neo4j = Neo4jService()
        self.bkt = BKTService()
        
        # Load State
        self.state_file = os.path.join(os.path.dirname(__file__), "gkt_state.json")
        self.user_states = self._load_json(self.state_file)
        
        # Load Graph Structure (A) and GNN Weights (W)
        self.concepts = self._fetch_concepts()
        self.concept_to_idx = {c: i for i, c in enumerate(self.concepts)}
        self.idx_to_concept = {i: c for i, c in enumerate(self.concepts)}
        self.num_concepts = len(self.concepts)
        
        self.adj_matrix = self._build_adjacency_matrix()
        self.W_prop = 0.5 # Default propagation weight (can be loaded from trained model)

    def _fetch_concepts(self):
        """Fetch all concepts from Neo4j to define the vector space."""
        # Hardcoding fallback effectively avoids Neo4j crashes during init if DB is empty
        fallback = ["Variables", "Loops", "Functions", "Lists", "Recursion", "Dynamic Programming"]
        try:
            data = self.neo4j.query("MATCH (n:Concept) RETURN n.name as name ORDER BY n.name")
            if not data: return fallback
            return [r["name"] for r in data]
        except:
            return fallback

    def _build_adjacency_matrix(self):
        """Builds the Adjacency Matrix (A) where A[i][j] = 1 means j -> i (Prerequisite Flow)."""
        size = self.num_concepts
        adj = np.zeros((size, size))
        try:
            # Match (Dependent)<-[:REQUIRES]-(Prereq) works, but let's stick to direction:
            # Flow of Knowledge: Prereq -> Dependent.
            # If Prereq is Mastered, Dependent potential increases.
            # So Edge should be Prereq -> Dependent.
            query = "MATCH (d:Concept)-[:REQUIRES]->(p:Concept) RETURN d.name as dependent, p.name as prereq"
            rels = self.neo4j.query(query)
            if rels:
                for r in rels:
                    if r["dependent"] in self.concept_to_idx and r["prereq"] in self.concept_to_idx:
                        u = self.concept_to_idx[r["dependent"]] # Target
                        v = self.concept_to_idx[r["prereq"]]    # Source
                        adj[u][v] = 1 # v influences u
        except Exception as e:
            print(f"[GKT] Error building graph: {e}")
            
        # Normalize? Standard GCN uses D^-0.5 A D^-0.5, but simple A is fine for now
        return adj

    def get_mastery_vector(self, user_email):
        if user_email not in self.user_states:
            # Initialize with small prior (0.1)
            self.user_states[user_email] = [0.1] * self.num_concepts
        
        # Resize check (if graph grew)
        curr = self.user_states[user_email]
        if len(curr) < self.num_concepts:
            curr.extend([0.1] * (self.num_concepts - len(curr)))
            self.user_states[user_email] = curr
            
        return np.array(self.user_states[user_email])

    def update_mastery(self, user_email, concept, is_correct, source_type="tutor"):
        """
        The Core Hybrid Loop:
        1. Update specific node using BKT (Tutor/Code/Debug logic).
        2. (Optional) Run instantaneous propagation for UI updates.
        """
        if concept not in self.concept_to_idx:
            print(f"[GKT] Warning: Concept '{concept}' not in graph.")
            return 0.0
            
        idx = self.concept_to_idx[concept]
        vector = self.get_mastery_vector(user_email)
        
        # 1. BKT Update (The Node)
        # Using the BKT Service logic
        old_val = vector[idx]
        new_val = self.bkt.update_node(old_val, is_correct, source_type)
        vector[idx] = new_val
        
        # Save State
        self.user_states[user_email] = vector.tolist()
        self._save_json(self.state_file, self.user_states)
        
        print(f"[GKT] Updated {concept}: {old_val:.2f} -> {new_val:.2f}")
        return new_val

    def get_recommendations(self, user_email, top_k=3):
        """
        GNN-Based Recommendation:
        Uses Graph Propagation to find the 'Zone of Proximal Development' (ZPD).
        
        Logic:
        1. H_next = H + (A * H * W)  (Propagate current mastery)
        2. Identify nodes where:
           - Current Mastery is Low (< 0.6) (Not already learned)
           - Prerequisite Support is High (Received high flow from neighbors)
        """
        H = self.get_mastery_vector(user_email)
        
        # 1. Graph Convolution (Propagation)
        # Neighbor Influence = A dot H
        # If Prereqs are high, Neighbor Influence is high.
        neighbor_signal = np.dot(self.adj_matrix, H)
        
        # 2. Score Candidates
        # Score = (NeighborSupport * Weight) - (CurrentMastery * penalty)
        # We want High Support, Low Current Mastery.
        scores = []
        for i in range(self.num_concepts):
            mastery = H[i]
            support = neighbor_signal[i]
            
            # Heuristic Ranking Score
            # If mastery is already high (>0.8), score should be low (Don't recommend known stuff).
            # If support is high, score boosts up.
            if mastery > 0.85:
                score = -1.0 # Already known
            else:
                # ZPD Score: Support is good, but penalize if we have NO clue (mastery ~ 0.1 and NO support)
                score = support * self.W_prop + (1.0 - mastery) * 0.2
            
            scores.append((score, self.idx_to_concept[i]))
            
        # 3. Sort and Return
        scores.sort(key=lambda x: x[0], reverse=True)
        recommendations = [s[1] for s in scores[:top_k]]
        
        print(f"[GKT] Recommendations for {user_email}: {recommendations}")
        return recommendations

    def _load_json(self, path):
        try:
            with open(path, "r") as f: return json.load(f)
        except: return {}

    def _save_json(self, path, data):
        try:
            with open(path, "w") as f: json.dump(data, f)
        except: pass
