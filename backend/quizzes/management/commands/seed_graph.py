from django.core.management.base import BaseCommand
from neomodel import db

class Command(BaseCommand):
    help = 'Seeds the Neo4j database with a Rich Python Knowledge Graph'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Knowledge Graph...")
        
        # CLEAR DB
        db.cypher_query("MATCH (n) DETACH DELETE n")

        # DEFINE CURRICULUM
        # Format: (Concept, List of Prerequisites)
        curriculum = {
            # LEVEL 1: BASICS
            "Variables": [],
            "Data Types": ["Variables"],
            "Integers": ["Data Types"],
            "Floats": ["Data Types"],
            "Booleans": ["Data Types"],
            "Conditionals": ["Booleans"],
            "Loops": ["Conditionals"],
            "While Loops": ["Loops"],
            "For Loops": ["Loops", "Lists"], # Cross-link
            "Functions": ["Loops"],
            "Parameters": ["Functions"],
            "Return Values": ["Functions"],
            "Scope": ["Functions", "Variables"],

            # LEVEL 2: INTERMEDIATE
            "Lists": ["Data Types"],
            "List Slicing": ["Lists"],
            "List Comprehension": ["Lists", "For Loops"],
            "Tuples": ["Lists"], # Immutable lists
            "Sets": ["Lists"],
            "Strings": ["Lists"],
            "String Formatting": ["Strings"],
            "Dictionaries": ["Lists"],
            "File I/O": ["Strings"],
            "Context Managers": ["File I/O"], # "with" statement
            "Exception Handling": ["Functions"],
            "Custom Exceptions": ["Exception Handling", "Classes"],

            # LEVEL 3: ADVANCED PYTHON
            "Iterators": ["Loops"],
            "Generators": ["Iterators", "Functions"],
            "Decorators": ["Functions", "Scope"],
            "Lambda Functions": ["Functions"],
            "Map Filter Reduce": ["Lambda Functions", "Lists"],
            "Modules": ["Functions"],
            "Packages": ["Modules"],

            # LEVEL 4: OOP
            "Classes": ["Functions", "Dictionaries"],
            "Objects": ["Classes"],
            "Attributes": ["Objects"],
            "Methods": ["Functions", "Objects"],
            "Inheritance": ["Classes"],
            "Multiple Inheritance": ["Inheritance"],
            "Polymorphism": ["Inheritance"],
            "Encapsulation": ["Classes"],
            "Static Methods": ["Classes", "Decorators"],
            "Magic Methods": ["Classes"], # __init__, __str__

            # LEVEL 5: DATA STRUCTURES
            "Recursion": ["Functions"],
            "Stack Data Structure": ["Lists"],
            "Queue Data Structure": ["Lists"],
            "Hash Tables": ["Dictionaries"],
            "Linked Lists": ["Classes"],
            "Doubly Linked Lists": ["Linked Lists"],
            "Trees": ["Linked Lists", "Recursion"],
            "Binary Search Trees": ["Trees", "Conditionals"],
            "AVL Trees": ["Binary Search Trees"], # Balancing
            "Heaps": ["Trees", "Lists"],
            "Priority Queue": ["Heaps", "Queue Data Structure"],
            "Trie": ["Trees", "Strings"],
            "Graphs": ["Dictionaries", "Trees"],
            "Disjoint Set Union": ["Graphs", "Arrays"], # Arrays handled as lists

            # LEVEL 6: ALGORITHMS
            "Memoization": ["Dictionaries", "Recursion"],
            "Dynamic Programming": ["Recursion", "Memoization"],
            "Knapsack Problem": ["Dynamic Programming"],
            "LCS": ["Dynamic Programming"],
            "DFS": ["Graphs", "Stack Data Structure"],
            "BFS": ["Graphs", "Queue Data Structure"],
            "Topological Sort": ["DFS", "Graphs"],
            "Dijkstra": ["BFS", "Priority Queue"],
            "Bellman Ford": ["Graphs", "Dynamic Programming"],
            "A* Search": ["Dijkstra"],
            "Divide and Conquer": ["Recursion"],
            "Binary Search": ["Divide and Conquer", "Lists"],
            "Merge Sort": ["Divide and Conquer", "Lists"],
            "Quick Sort": ["Divide and Conquer", "Lists"],
            "Backtracking": ["Recursion"],
            "N-Queens Problem": ["Backtracking"],
            
            # LEVEL 7: SYSTEM DESIGN (Bonus)
            "APIs": ["Dictionaries", "functions"],
            "JSON": ["Dictionaries", "File I/O"],
            "REST": ["APIs"],
            "Databases": ["File I/O"],
            "SQL": ["Databases"],
            "NoSQL": ["Databases", "Dictionaries"]
        }
        
        # INSERT NODES
        for concept in curriculum:
            query = "MERGE (c:Concept {name: $name})"
            db.cypher_query(query, {'name': concept})
            
        # INSERT RELATIONSHIPS
        count = 0
        for concept, prereqs in curriculum.items():
            for prereq in prereqs:
                # (Concept) -[:REQUIRES]-> (Prereq)
                # Meaning: To learn Concept, you MUST know Prereq.
                query = """
                MATCH (c:Concept {name: $c_name})
                MATCH (p:Concept {name: $p_name})
                MERGE (c)-[:REQUIRES]->(p)
                """
                db.cypher_query(query, {'c_name': concept, 'p_name': prereq})
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(curriculum)} concepts and {count} dependencies!"))
