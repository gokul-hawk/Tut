# quiz/services/neo4j_service.py
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, ClientError
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jService:
    def __init__(self, database=None, uri=None, auth=None):
        _uri = uri or settings.NEO4J_URI
        _auth = auth or (settings.NEO4J_USER, os.getenv('NEO4J_PASSWORD'))
        
        self.driver = GraphDatabase.driver(
            _uri,
            auth=_auth
        )
        self.database = "dsa"

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        """
        Executes a generic Cypher query.
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            print(f"Neo4j Query Error: {e}")
            return []

    def get_direct_prerequisites(self, concept_name: str):
        query = """
        MATCH (c:Concept {name: $concept})-[:REQUIRES]->(p:Concept)
        RETURN p.name AS prerequisite
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, concept=concept_name)
                return [record["prerequisite"] for record in result]
        except (ServiceUnavailable, AuthError, ClientError) as e:
            # ClientError covers "label does not exist" warnings.
            print(f"Neo4j Warning/Error: {e}")
            return []
        except Exception as e:
            print(f"Neo4j Unexpected Error: {e}")
            return []

    def get_all_prerequisites(self, concept_name: str):
        query = """
        MATCH (c:Concept {name: $concept})-[:REQUIRES*]->(p:Concept)
        RETURN DISTINCT p.name AS prerequisite
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, concept=concept_name)
                return [record["prerequisite"] for record in result]
        except (ServiceUnavailable, AuthError) as e:
            raise Exception(f"Neo4j connection error: {e}")

    def get_prerequisite_subgraph(self, concept_name: str):
        """
        Fetches all prerequisites and their relationships for a subgraph.
        Returns a list of tuples: (source, target), meaning source -> target (source REQUIRES target).
        Note: logic is (concept)-[:REQUIRES]->(prereq). So 'concept' depends on 'prereq'.
        To learn 'concept', you must first learn 'prereq'.
        Dependency Direction: concept -> prereq.
        Learning Order: prereq -> concept.
        """
        query = """
        MATCH path = (c:Concept {name: $concept})-[:REQUIRES*]->(p:Concept)
        UNWIND relationships(path) AS r
        RETURN startNode(r).name AS source, endNode(r).name AS target
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, concept=concept_name)
                # Returns list of (dependent, requirement)
                # e.g. ("Advanced Graph", "Graph Basics")
                return list(set([(record["source"], record["target"]) for record in result]))
        except Exception as e:
            print(f"Neo4j Subgraph Error: {e}")
            return []