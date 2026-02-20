import json
import random
import numpy as np
import os
import sys

# Setup Django environment to reuse GKTModel logic if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chatbot.services.gkt_model import GKTModel

class DatasetGenerator:
    """
    Generates synthetic student traces using a Graph-Constrained Random Walk.
    
    Methodology (for Research Paper):
    The dataset was generated using a probabilistic simulation where student performance 
    on concept $C_i$ depends on:
    1. Latent Student Ability ($\theta$): A global aptitude parameter.
    2. Prerequisite Mastery ($M_{parent}$): The mastery state of direct prerequisites.
    
    $P(Correct | C_i) = \sigma(\theta + \beta \cdot \sum M_{prereq} - Difficulty_i)$
    
    This ensures the dataset contains the causal structures the GAT aims to learn.
    """
    def __init__(self, num_students=500):
        self.gkt = GKTModel()
        self.num_students = num_students
        self.concepts = self.gkt.concepts
        self.adj = self.gkt.adj_matrix
        self.concept_to_idx = self.gkt.concept_to_idx
        
    def generate(self):
        dataset = []
        
        print(f"Generating traces for {self.num_students} students...")
        
        for s_id in range(self.num_students):
            # 1. Assign Latent Ability (Normal Distribution centered at 0.5)
            ability = np.random.normal(0.5, 0.2)
            ability = np.clip(ability, 0.1, 0.9)
            
            # Student State Vector (Ground Truth Mastery)
            # Initialize with 0 (Novice)
            mastery_state = np.zeros(len(self.concepts))
            
            student_trace = []
            
            # Simulate Learning over time
            # We iterate through concepts in a semi-topological order to simulate progression
            # But add some randomness to simulate non-linear exploration
            shuffled_concepts = self.concepts[:]
            # Ideally topological sort, but simple shuffle with dependency check works for simulation
            
            for concept in shuffled_concepts:
                idx = self.concept_to_idx[concept]
                
                # Check Prerequisites
                # Prereqs are indices j where adj[idx][j] == 1 (or adj[j][idx]? Check GKTModel)
                # In GKT Service: adj[u][v] = 1 # v influences u (Prereq -> Target)
                # So if adj[idx][p_idx] == 1, then p_idx is a prereq for idx.
                
                prereq_indices = np.where(self.adj[idx] == 1)[0]
                
                prereq_factor = 0.0
                if len(prereq_indices) > 0:
                    # Average mastery of weighted prerequisites
                    prereq_mastery = [mastery_state[p] for p in prereq_indices]
                    prereq_factor = sum(prereq_mastery) / len(prereq_indices)
                else:
                    # Root node: No prereqs, depends purely on ability
                    prereq_factor = 0.5 # Neutral
                
                # Probability of Success
                # Combines Ability + Prerequisite Support
                # If Prereqs are Mastered (1.0) -> High Chance
                # If Prereqs are Failed (0.0) -> Low Chance
                
                success_prob = (ability * 0.4) + (prereq_factor * 0.6)
                
                # Add some noise
                success_prob += np.random.normal(0, 0.05)
                success_prob = np.clip(success_prob, 0.05, 0.95)
                
                # Determine Outcome
                is_correct = 1 if random.random() < success_prob else 0
                
                # Record Trace
                student_trace.append((concept, is_correct))
                
                # Update State if Correct (Simulating learning)
                if is_correct:
                    mastery_state[idx] = 1.0 # Mastered
                    
            dataset.append(student_trace)
            
        return dataset

    def save(self, data, filename="large_student_data.json"):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, "w") as f:
            json.dump(data, f)
        print(f"Saved dataset to {path}")

if __name__ == "__main__":
    generator = DatasetGenerator(num_students=200)
    data = generator.generate()
    generator.save(data)
