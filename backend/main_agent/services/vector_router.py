import math
import re

class VectorRouter:
    """
    Simulates Semantic Vector Search for fast intent routing.
    Uses 'Bag of Words' style embeddings to find nearest neighbor intent.
    """
    def __init__(self):
        # 1. Define "Centroids" for each intent using keywords
        # In a real system, these would be high-dimensional embeddings.
        self.intents = {
            "PLAN": ["learn", "study", "teach", "explain", "concept", "theory", "roadmap", "start", "lesson"],
            "CODE": ["code", "practice", "write", "implement", "program", "function", "class", "challenge"],
            "DEBUG": ["debug", "fix", "error", "bug", "issue", "crash", "wrong", "fail", "exception"],
            "QUIZ": ["quiz", "test", "exam", "check", "knowledge", "assessment"],
            "CHAT": ["hi", "hello", "thanks", "goodbye", "help", "who", "what"]
        }
        
    def _get_embedding(self, text):
        """
        Converts text to a simple 'keyword presence' vector.
        Real system would use SentenceTransformers.
        """
        tokens = set(re.findall(r'\w+', text.lower()))
        vector = {}
        for intent, keywords in self.intents.items():
            score = 0
            for k in keywords:
                if k in tokens:
                    score += 1
            vector[intent] = score
        return vector

    def route(self, message):
        """
        Returns the best intent if confidence is high.
        """
        vector = self._get_embedding(message)
        
        # Find Max Score
        best_intent = "CHAT"
        max_score = 0
        
        for intent, score in vector.items():
            if score > max_score:
                max_score = score
                best_intent = intent
                
        # Threshold: Need at least 1 keyword match
        if max_score > 0:
            print(f"[VectorRouter] Hit: {best_intent} (Score: {max_score})")
            return {"route": best_intent, "confidence": 1.0, "source": "vector_search"}
            
        print("[VectorRouter] Miss (Low Confidence)")
        return None
