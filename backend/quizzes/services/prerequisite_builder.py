# services/prerequisite_builder.py

from .neo4j_services import Neo4jService
from .gemini_service import GeminiService

class PrerequisiteBuilder:
    def __init__(self, neo4j_db="neo4j"):
        self.neo4j = Neo4jService(database=neo4j_db)
        self.gemini = GeminiService()
        self.visited = set()

    def fetch_prerequisites(self, concept):
        """Fetch prerequisites from Neo4j, fallback to Gemini if not in graph"""
        prereqs = self.neo4j.get_direct_prerequisites(concept)
        if not prereqs:  # fallback
            prereqs = self.gemini.get_prerequisites(concept)
        return prereqs

    def build_chain(self, concept):
        """
        Builds a learning path using Topological Sort.
        Returns a list of concepts in the order they should be learned.
        """
        # 1. Fetch the dependency graph (Edges: Dependent -> Prerequisite)
        # We need to invert this to (Prerequisite -> Dependent) to find the learning order.
        edges = self.neo4j.get_prerequisite_subgraph(concept)
        
        # Fallback if no graph data found
        if not edges:
            print(f"No graph found for {concept}, checking direct prereqs or Gemini.")
            direct = self.fetch_prerequisites(concept)
            if not direct:
                return [concept]
            # If we have direct prereqs but no subgraph edges, it implies a shallow graph.
            # We can just return direct + concept.
            return direct + [concept]

        # 2. Build Adjacency List (Prerequisite -> Dependent) for Learning Order
        adj = {}
        in_degree = {}
        all_nodes = set()

        # Initialize
        for u, v in edges:
            # Neo4j: u (Dependent) -> v (Prerequisite)
            # Learning Graph: v (Prereq) -> u (Topic)
            all_nodes.add(u)
            all_nodes.add(v)
            
            if v not in adj: adj[v] = []
            if u not in adj: adj[u] = []
            
            # Edge v -> u
            adj[v].append(u)
            
            # Track in-degree for u (how many things does u depend on?)
            in_degree[u] = in_degree.get(u, 0) + 1
            if v not in in_degree: in_degree[v] = 0

        # 3. Kahn's Algorithm for Topological Sort
        queue = [n for n in all_nodes if in_degree[n] == 0]
        # Sort queue to have deterministic output for same-level nodes (optional)
        queue.sort() 
        
        sorted_path = []
        
        while queue:
            node = queue.pop(0)
            sorted_path.append(node)
            
            if node in adj:
                for neighbor in adj[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
                        
        # 4. Filter: The user asked for 'concept'. We should output the path UP TO 'concept'.
        # The graph might contain things 'concept' is a prerequisite FOR (if the query was broader).
        # But our Neo4j query `(c:Concept {name: $concept})-[:REQUIRES*]->(p:Concept)` 
        # only fetches prerequisites OF `concept`. So `concept` should be at the END of the topo sort.
        
        if len(sorted_path) < len(all_nodes):
            print("Cycle detected in prerequisites! Fallback to partial path.")
        
        # Ensure the target concept is in the list
        if concept not in sorted_path:
             # It might be isolated if it has no incoming/outgoing in the subgraph?
             # But the query guarantees connected limits.
             sorted_path.append(concept)
             
        # Only return items that are ancestors of 'concept' or 'concept' itself.
        # (Topological sort might include disconnected components if the query was loose, 
        # but here the query is rooted at 'concept').
        
        return sorted_path
