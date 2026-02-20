import json
import random
import os

INPUT_FILE = os.path.join(os.path.dirname(__file__), "student_data.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "large_student_data.json")
TARGET_SIZE = 5000

def expand_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Please paste your 50 records there first.")
        return

    print(f"Loading seed data from {INPUT_FILE}...")
    with open(INPUT_FILE, "r") as f:
        seed_data = json.load(f)

    if not seed_data:
        print("Seed data is empty.")
        return

    print(f"Found {len(seed_data)} seed patterns. Expanding to {TARGET_SIZE}...")
    
    expanded_data = []
    
    while len(expanded_data) < TARGET_SIZE:
        # 1. Pick a random base pattern from the high-quality LLM seed
        base_pattern = random.choice(seed_data)
        
        # 2. Create a variation (Data Augmentation)
        new_pattern = []
        for topic, is_correct in base_pattern:
            # 5% chance to flip the answer (Noise)
            # This creates diversity while keeping the core correlation logic
            if random.random() < 0.05:
                new_val = 1 - is_correct
                new_pattern.append([topic, new_val])
            else:
                new_pattern.append([topic, is_correct])
        
        expanded_data.append(new_pattern)

    print(f"Saving {len(expanded_data)} records to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(expanded_data, f)
    print("Done! You now have a massive dataset.")

if __name__ == "__main__":
    expand_data()
