import json
import random
import os

# File to store Q-values (Action -> Value)
RL_DATA_FILE = os.path.join(os.path.dirname(__file__), "rl_q_values.json")

class RLSelector:
    """
    Multi-Armed Bandit (MAB) Agent using Epsilon-Greedy Strategy.
    Actions: "socratic", "practical", "analogy", "expert"
    """
    def __init__(self, epsilon=0.2):
        self.epsilon = epsilon
        self.actions = ["socratic", "practical", "analogy", "expert"]
        self.q_values = self._load_data()

    def _load_data(self):
        if os.path.exists(RL_DATA_FILE):
            try:
                with open(RL_DATA_FILE, "r") as f:
                    return json.load(f)
            except:
                return {a: 0.0 for a in self.actions}
        return {a: 0.0 for a in self.actions}

    def _save_data(self):
        with open(RL_DATA_FILE, "w") as f:
            json.dump(self.q_values, f)

    def get_action(self, topic):
        """
        Selects a teaching style.
        Explore (Random) vs Exploit (Best Q-value).
        """
        # Explore
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
            print(f"[RL] Exploring: {action}")
            return action
        
        # Exploit
        best_action = max(self.q_values, key=self.q_values.get)
        print(f"[RL] Exploiting: {best_action} (Score: {self.q_values[best_action]})")
        return best_action

    def update(self, action, reward):
        """
        Updates Q-value for the action using simple average or learning rate.
        Q(a) = Q(a) + alpha * (reward - Q(a))
        """
        alpha = 0.5 # Learning rate
        old_val = self.q_values.get(action, 0.0)
        new_val = old_val + alpha * (reward - old_val)
        
        self.q_values[action] = new_val
        self._save_data()
        print(f"[RL] Updated {action}: {old_val:.2f} -> {new_val:.2f} (Reward: {reward})")
