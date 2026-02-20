import json
import random

# ----------------------------
# 1. Topic Vocabulary (Exact)
# ----------------------------
TOPICS = [
    "Python Basics", "Memory Management", "Variables & References", "Garbage Collection",
    "Mutable vs Immutable", "Data Types", "Integers & Floats", "Strings", "String Interning",
    "F-Strings", "Control Flow", "Conditionals", "Loops", "Iterables", "Iterators",
    "Generators", "Yield Keyword", "Functions", "Recursion", "Lambda Functions", "Closure",
    "Decorators", "Start Args (*args, **kwargs)", "Type Hinting", "Scope", "LEGB Rule",
    "Modules & Packages", "Import System", "Circular Imports", "Error Handling",
    "Context Managers (with)", "Concurrency Basics", "Threading", "Global Interpreter Lock (GIL)",
    "Multiprocessing", "Race Conditions", "Locks & Semaphores", "AsyncIO", "Coroutines",
    "Event Loop", "Await Keyword", "OOP Concepts", "Classes & Objects", "Instance Methods",
    "Class Variables vs Instance Variables", "Inheritance", "Multiple Inheritance",
    "MRO (Method Resolution Order)", "Mixins", "Polymorphism", "Duck Typing",
    "Operator Overloading", "Encapsulation", "Property Decorators (@property)", "Name Mangling",
    "Abstraction", "Abstract Base Classes (ABC)", "Interfaces", "Magic Methods (Dunder)",
    "Metaclasses", "Dataclasses", "Arrays", "Lists", "Slicing", "List Comprehensions",
    "Linked Lists", "Doubly Linked List", "Circular Linked List", "Stacks", "Queues", "Deque",
    "Hashing", "Hash Functions", "Collisions", "Hash Maps (Dicts)", "Sets", "Trees",
    "Binary Trees", "Binary Search Trees (BST)", "Heaps (Priority Queues)", "Trie (Prefix Tree)",
    "Graphs", "Adjacency Matrix", "Adjacency List", "Complexity Analysis", "Big O Notation",
    "Space Complexity", "Sorting", "Merge Sort", "Quick Sort", "Searching", "Binary Search",
    "Two Pointers", "Sliding Window", "Graph Traversal", "BFS", "DFS", "Shortest Path",
    "Dijkstra", "Bellman-Ford", "Minimum Spanning Tree", "Prim's Algorithm", "Kruskal's Algorithm",
    "Union Find", "Dynamic Programming", "Memoization", "Tabulation", "Knapsack Problem", "Backtracking"
]

# ----------------------------
# 2. Prerequisite Graph (Success only)
# ----------------------------
PREREQUISITES = {
    # Fundamentals
    "Variables & References": ["Python Basics"],
    "Memory Management": ["Variables & References"],
    "Garbage Collection": ["Memory Management"],
    "Mutable vs Immutable": ["Variables & References"],
    "Data Types": ["Python Basics"],
    "Integers & Floats": ["Data Types"],
    "Strings": ["Data Types"],
    "String Interning": ["Strings"],
    "F-Strings": ["Strings"],
    "Control Flow": ["Python Basics"],
    "Conditionals": ["Control Flow"],
    "Loops": ["Control Flow"],
    "Iterables": ["Loops"],
    "Iterators": ["Iterables"],
    "Generators": ["Iterators"],
    "Yield Keyword": ["Generators"],
    "Functions": ["Python Basics"],
    "Recursion": ["Functions"],
    "Lambda Functions": ["Functions"],
    "Closure": ["Functions", "Scope"],
    "Decorators": ["Functions", "Closure"],
    "Start Args (*args, **kwargs)": ["Functions"],
    "Type Hinting": ["Functions"],
    "Scope": ["Variables & References"],
    "LEGB Rule": ["Scope"],
    "Modules & Packages": ["Python Basics"],
    "Import System": ["Modules & Packages"],
    "Circular Imports": ["Import System"],
    "Error Handling": ["Python Basics"],
    "Context Managers (with)": ["Error Handling"],
    "Concurrency Basics": ["Python Basics"],
    "Threading": ["Concurrency Basics"],
    "Global Interpreter Lock (GIL)": ["Threading"],
    "Multiprocessing": ["Threading"],
    "Race Conditions": ["Threading"],
    "Locks & Semaphores": ["Race Conditions"],
    "AsyncIO": ["Concurrency Basics"],
    "Coroutines": ["AsyncIO"],
    "Event Loop": ["AsyncIO"],
    "Await Keyword": ["Coroutines"],
    "OOP Concepts": ["Python Basics"],
    "Classes & Objects": ["OOP Concepts"],
    "Instance Methods": ["Classes & Objects"],
    "Class Variables vs Instance Variables": ["Classes & Objects"],
    "Inheritance": ["Classes & Objects"],
    "Multiple Inheritance": ["Inheritance"],
    "MRO (Method Resolution Order)": ["Multiple Inheritance"],
    "Mixins": ["Multiple Inheritance"],
    "Polymorphism": ["Inheritance"],
    "Duck Typing": ["Polymorphism"],
    "Operator Overloading": ["Classes & Objects"],
    "Encapsulation": ["Classes & Objects"],
    "Property Decorators (@property)": ["Encapsulation"],
    "Name Mangling": ["Encapsulation"],
    "Abstraction": ["OOP Concepts"],
    "Abstract Base Classes (ABC)": ["Abstraction"],
    "Interfaces": ["Abstract Base Classes (ABC)"],
    "Magic Methods (Dunder)": ["Classes & Objects"],
    "Metaclasses": ["Classes & Objects", "Magic Methods (Dunder)"],
    "Dataclasses": ["Classes & Objects"],
    "Arrays": ["Data Types"],
    "Lists": ["Arrays"],
    "Slicing": ["Lists"],
    "List Comprehensions": ["Lists", "Loops"],
    "Linked Lists": ["Classes & Objects"],
    "Doubly Linked List": ["Linked Lists"],
    "Circular Linked List": ["Linked Lists"],
    "Stacks": ["Lists"],
    "Queues": ["Lists"],
    "Deque": ["Queues"],
    "Hashing": ["Data Types"],
    "Hash Functions": ["Hashing"],
    "Collisions": ["Hash Functions"],
    "Hash Maps (Dicts)": ["Hashing", "Collisions"],
    "Sets": ["Hash Maps (Dicts)"],
    "Trees": ["Classes & Objects"],
    "Binary Trees": ["Trees"],
    "Binary Search Trees (BST)": ["Binary Trees"],
    "Heaps (Priority Queues)": ["Trees"],
    "Trie (Prefix Tree)": ["Trees"],
    "Graphs": ["Classes & Objects"],
    "Adjacency Matrix": ["Graphs"],
    "Adjacency List": ["Graphs"],
    "Complexity Analysis": ["Python Basics"],
    "Big O Notation": ["Complexity Analysis"],
    "Space Complexity": ["Big O Notation"],
    "Sorting": ["Lists"],
    "Merge Sort": ["Sorting", "Recursion"],
    "Quick Sort": ["Sorting", "Recursion"],
    "Searching": ["Lists"],
    "Binary Search": ["Searching", "Sorting"],
    "Two Pointers": ["Lists"],
    "Sliding Window": ["Lists", "Loops"],
    "Graph Traversal": ["Graphs"],
    "BFS": ["Graph Traversal", "Queues"],
    "DFS": ["Graph Traversal", "Recursion"],
    "Shortest Path": ["Graph Traversal"],
    "Dijkstra": ["Shortest Path", "Heaps (Priority Queues)"],
    "Bellman-Ford": ["Shortest Path"],
    "Minimum Spanning Tree": ["Graphs"],
    "Prim's Algorithm": ["Minimum Spanning Tree", "Heaps (Priority Queues)"],
    "Kruskal's Algorithm": ["Minimum Spanning Tree", "Union Find"],
    "Union Find": ["Classes & Objects"],
    "Dynamic Programming": ["Recursion", "Memoization", "Tabulation"],
    "Memoization": ["Recursion", "Functions"],
    "Tabulation": ["Lists"],
    "Knapsack Problem": ["Dynamic Programming"],
    "Backtracking": ["Recursion"]
}

# Build canonical learning path (topological order approximation)
def build_canonical_path():
    mastered = set()
    path = []
    remaining = set(TOPICS)
    
    # Start with basics
    basics = ["Python Basics", "Variables & References", "Data Types", "Control Flow", "Functions", "Lists", "OOP Concepts", "Complexity Analysis"]
    for t in basics:
        if t in remaining:
            path.append(t)
            mastered.add(t)
            remaining.remove(t)
    
    # Iteratively add topics whose prerequisites are met
    changed = True
    while changed and remaining:
        changed = False
        for topic in list(remaining):
            prereqs = PREREQUISITES.get(topic, [])
            if all(p in mastered for p in prereqs):
                path.append(topic)
                mastered.add(topic)
                remaining.remove(topic)
                changed = True
    
    # Append any leftovers (should be minimal)
    path.extend(list(remaining))
    return path

CANONICAL_PATH = build_canonical_path()

# Difficulty tiers (for success probability)
TIER_1 = {"Python Basics", "Variables & References", "Data Types", "Integers & Floats", "Strings", "Control Flow", "Conditionals", "Loops", "Functions", "Lists", "Type Hinting", "Scope", "LEGB Rule"}
TIER_2 = {"Memory Management", "Mutable vs Immutable", "String Interning", "F-Strings", "Iterables", "Iterators", "Generators", "Yield Keyword", "Recursion", "Lambda Functions", "Closure", "Decorators", "Start Args (*args, **kwargs)", "Modules & Packages", "Error Handling", "Context Managers (with)", "Arrays", "Slicing", "List Comprehensions", "Hash Maps (Dicts)", "Sets", "OOP Concepts", "Classes & Objects", "Instance Methods", "Inheritance", "Polymorphism", "Encapsulation", "Complexity Analysis", "Big O Notation", "Sorting", "Searching", "Two Pointers", "Sliding Window"}
TIER_3 = {"Garbage Collection", "Circular Imports", "Import System", "Concurrency Basics", "Threading", "Multiprocessing", "Race Conditions", "Locks & Semaphores", "AsyncIO", "Coroutines", "Event Loop", "Await Keyword", "Global Interpreter Lock (GIL)", "Class Variables vs Instance Variables", "Multiple Inheritance", "MRO (Method Resolution Order)", "Mixins", "Duck Typing", "Operator Overloading", "Property Decorators (@property)", "Name Mangling", "Abstraction", "Abstract Base Classes (ABC)", "Interfaces", "Magic Methods (Dunder)", "Dataclasses", "Linked Lists", "Doubly Linked List", "Circular Linked List", "Stacks", "Queues", "Deque", "Hashing", "Hash Functions", "Collisions", "Trees", "Binary Trees", "Binary Search Trees (BST)", "Heaps (Priority Queues)", "Trie (Prefix Tree)", "Graphs", "Adjacency Matrix", "Adjacency List", "Space Complexity", "Merge Sort", "Quick Sort", "Binary Search", "Graph Traversal", "BFS", "DFS", "Shortest Path", "Union Find", "Memoization", "Tabulation"}
TIER_4 = {"Metaclasses", "Minimum Spanning Tree", "Prim's Algorithm", "Kruskal's Algorithm", "Dijkstra", "Bellman-Ford", "Dynamic Programming", "Knapsack Problem", "Backtracking"}

def get_tier(topic):
    if topic in TIER_4:
        return 4
    elif topic in TIER_3:
        return 3
    elif topic in TIER_2:
        return 2
    else:
        return 1

def success_prob(archetype, tier):
    probs = {
        'expert':     {1: 0.99, 2: 0.95, 3: 0.90, 4: 0.75},
        'steady':     {1: 0.90, 2: 0.80, 3: 0.60, 4: 0.35},
        'beginner':   {1: 0.70, 2: 0.50, 3: 0.30, 4: 0.10},
        'jumper':     {1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00}  # jumpers only fail
    }
    return probs[archetype][tier]

def has_prereqs(topic, mastered):
    if topic not in PREREQUISITES:
        return True
    return all(p in mastered for p in PREREQUISITES[topic])

# ----------------------------
# 3. Generate One Trace
# ----------------------------
def generate_trace(archetype):
    trace = []
    mastered = set()
    last_failed = None
    canonical_index = 0
    max_length = 150

    # Advanced topics for jumpers
    advanced_topics = [t for t in TOPICS if get_tier(t) >= 3]

    while len(trace) < max_length:
        topic = None
        force_failure = False

        if archetype == 'beginner':
            if last_failed and random.random() < 0.7:
                topic = last_failed
            else:
                if canonical_index < len(CANONICAL_PATH):
                    topic = CANONICAL_PATH[canonical_index]
                else:
                    break

        elif archetype == 'expert':
            if canonical_index < len(CANONICAL_PATH):
                topic = CANONICAL_PATH[canonical_index]
            else:
                break

        elif archetype == 'steady':
            if last_failed and random.random() < 0.6:
                topic = last_failed
            else:
                if canonical_index < len(CANONICAL_PATH):
                    topic = CANONICAL_PATH[canonical_index]
                else:
                    break

        elif archetype == 'jumper':
            if random.random() < 0.3 and len(advanced_topics) > 0:
                topic = random.choice(advanced_topics)
                force_failure = True
            else:
                if canonical_index < len(CANONICAL_PATH):
                    topic = CANONICAL_PATH[canonical_index]
                else:
                    break

        if topic is None:
            break

        # Determine outcome
        if force_failure:
            outcome = 0
        else:
            tier = get_tier(topic)
            p = success_prob(archetype, tier)
            outcome = 1 if random.random() < p else 0

        # For non-jumpers, enforce prerequisite rule on success
        if outcome == 1 and archetype != 'jumper':
            if not has_prereqs(topic, mastered):
                # Skip invalid success; try next topic
                if archetype in ['expert', 'steady']:
                    canonical_index += 1
                continue

        trace.append([topic, outcome])
        if outcome == 1:
            mastered.add(topic)
            last_failed = None
            if topic in CANONICAL_PATH:
                idx = CANONICAL_PATH.index(topic)
                canonical_index = max(canonical_index, idx + 1)
        else:
            last_failed = topic

        # Termination condition: mastered Backtracking (final topic)
        if "Backtracking" in mastered:
            break

    return trace

# ----------------------------
# 4. Generate Full Dataset
# ----------------------------
def main():
    total = 500
    traces = []

    # Archetype distribution
    n_steady = int(0.40 * total)   # 200
    n_beginner = int(0.30 * total) # 150
    n_expert = int(0.10 * total)   # 50
    n_jumper = total - n_steady - n_beginner - n_expert  # 100

    archetypes = (
        ['steady'] * n_steady +
        ['beginner'] * n_beginner +
        ['expert'] * n_expert +
        ['jumper'] * n_jumper
    )
    random.shuffle(archetypes)

    for i, arch in enumerate(archetypes):
        trace = generate_trace(arch)
        traces.append(trace)
        if (i + 1) % 50 == 0:
            print(f"Generated {i+1}/{total} traces...")

    # Save to JSON
    with open('student_traces.json', 'w') as f:
        json.dump(traces, f, indent=2)
    print("✅ Dataset saved to 'student_traces.json'")

if __name__ == "__main__":
    main()