
import numpy as np
import os
import json
from quizzes.services.neo4j_services import Neo4jService
from .bkt_service import BKTService
from .gat_service import GATService

class GKTModel:
    """
    Graph Knowledge Tracing (GKT) Facade.
    Coordinates BKTService (Node Updates) and GATService (Propagation).
    """
    def __init__(self, neo4j_uri=None):
        self.neo4j = Neo4jService(uri=neo4j_uri) if neo4j_uri else Neo4jService()
        self.state = self._load_data()
        
        # 1. Build Adjacency Matrix (A) from Neo4j
        self.concepts = self._get_all_concepts()
        self.concept_to_idx = {c: i for i, c in enumerate(self.concepts)}
        self.num_concepts = len(self.concepts)
        self.adj_matrix = self._build_adjacency_matrix()
        
        # 2. Initialize Sub-Services
        self.bkt_service = BKTService()
        self.gat_service = GATService(num_concepts=self.num_concepts)

    def _get_all_concepts(self):
        query = "MATCH (n:Concept) RETURN n.name as name ORDER BY n.name"
        results = self.neo4j.query(query)
        if not results: # Fallback
            return ["Python Basics", "Loops", "Functions"] 
        return [r["name"] for r in results]

    def _build_adjacency_matrix(self):
        size = self.num_concepts
        adj = np.zeros((size, size)) # A[i][j] = 1 if j -> i
        
        
        # Query: (Dependent)-[:REQUIRES]->(Prereq)
        query = "MATCH (d:Concept)-[:REQUIRES]->(p:Concept) RETURN d.name as dependent, p.name as prereq"
        rels = self.neo4j.query(query)
        
        if rels:
            for r in rels:
                if r["dependent"] in self.concept_to_idx and r["prereq"] in self.concept_to_idx:
                    u = self.concept_to_idx[r["dependent"]] # Dependent (Target of Flow)
                    v = self.concept_to_idx[r["prereq"]]    # Prereq (Source of Flow)
                    
                    # Flow: Prereq(v) -> Dependent(u)
                    adj[u][v] = 1
            
            print(f"[GKTModel] Adjacency Matrix Built. Edges Loaded: {np.sum(adj)}")
            print(f"[GKTModel] Concept Count: {len(self.concepts)}")
        return adj
        
    def _load_data(self):
        try:
             with open("chatbot/services/user_state.json", "r") as f:
                 data = json.load(f)
                 # MIGRATION: Convert old List format to Stratified Dict format
                 # Old: {"email": [0.1, 0.2]} -> New: {"email": {"tutor": [...], "code": [...], "debug": [...]}}
                 migrated_data = {}
                 for email, value in data.items():
                     if isinstance(value, list):
                         migrated_data[email] = {
                             "tutor": value,
                             "code": [0.1] * len(value), # Default cold start
                             "debug": [0.1] * len(value)
                         }
                     else:
                         migrated_data[email] = value
                 return migrated_data
        except:
             return {}
             
    def _save_data(self):
        try:
            with open("chatbot/services/user_state.json", "w") as f:
                json.dump(self.state, f)
        except:
            pass

    def _get_user_vectors(self, user_email):
        """
        Returns the Stratified State (Dict of 3 Vectors)
        """
        if user_email not in self.state:
            # Cold Start: Initialize all 3 dimensions
            default_vec = [0.1] * self.num_concepts
            self.state[user_email] = {
                "tutor": default_vec[:],
                "code": default_vec[:],
                "debug": default_vec[:]
            }
        
        # Resize check (if graph grew)
        user_matrices = self.state[user_email]
        current_len = len(user_matrices["tutor"])
        if current_len < self.num_concepts:
            diff = self.num_concepts - current_len
            pad = [0.1] * diff
            user_matrices["tutor"].extend(pad)
            user_matrices["code"].extend(pad)
            user_matrices["debug"].extend(pad)
            
        return self.state[user_email]

    def get_mastery(self, user_email, skill):
        """
        Calculates Stratified Total Mastery:
        M_total = (M_Tutor * 0.25) + (M_Code * 0.35) + (M_Debug * 0.40)
        """
        vectors = self._get_user_vectors(user_email)
        
        if skill in self.concept_to_idx:
            idx = self.concept_to_idx[skill]
            
            m_tutor = vectors["tutor"][idx]
            m_code = vectors["code"][idx]
            m_debug = vectors["debug"][idx]
            
            # THE STRATIFIED FORMULA
            m_total = (m_tutor * 0.25) + (m_code * 0.35) + (m_debug * 0.40)
            return m_total
            
        return 0.0

    def update(self, user_email, skill, is_correct, source_type="tutor"):
        """
        Main Update Loop:
        1. Select specific Vector based on Source (Tutor/Code/Debug)
        2. BKT Update (Targeted Node)
        3. GAT Propagation (Targeted Graph)
        """
        vectors = self._get_user_vectors(user_email)
        
        # Map source to key
        key_map = {
            "tutor": "tutor", "quiz": "tutor",
            "code": "code",
            "debug": "debug", "debugger": "debug"
        }
        target_key = key_map.get(source_type, "tutor") # Default to tutor if unknown
        
        if skill in self.concept_to_idx:
            idx = self.concept_to_idx[skill]
            
            # 1. BKT Update (Specific Dimension)
            # We get the specific vector (e.g., Code Mastery)
            # Note: We convert to numpy for processing, then back to list
            H_t = np.array(vectors[target_key])
            
            H_t[idx] = self.bkt_service.update_node(H_t[idx], is_correct, source_type)
            
            # 2. GAT Propagation (Specific Dimension)
            # Conceptually, practicing Code should propagate to Code Readiness first?
            # Or should it boost EVERYTHING?
            # For simplicity & Research Compliance: We propagate within the SAME dimension.
            H_t = self.gat_service.propagate(H_t, self.adj_matrix, idx)
            
            # Save back specific vector
            vectors[target_key] = H_t.tolist()
            
        # Save State
        self.state[user_email] = vectors
        self._save_data()
        
        new_score = self.get_mastery(user_email, skill)
        print(f"[GKTFacade] Updated {skill} [{source_type}]. New Composite Score: {new_score:.2f}")
        return new_score
