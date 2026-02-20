import json
from chatbot.services.groq_service import GroqService
from .vector_router import VectorRouter

class RouterAgent:
    def __init__(self):
        self.groq = GroqService()
        self.vector_router = VectorRouter()

    def route(self, message):
        """
        Classifies the user's message into one of three categories:
        1. PLAN: User wants to learn a new topic.
        2. ACTION: User wants to practice, code, debug, or take a quiz.
        3. CHAT: User wants to ask a question or have something explained.

        Returns:
        {
            "route": "PLAN" | "ACTION" | "CHAT",
            "topic": "extracted topic or None"
        }
        """
        # 0. Fast Path: Vector Search
        vector_result = self.vector_router.route(message)
        if vector_result:
            intent = vector_result["route"]
            # Short-circuit for CHAT or Simple Commands (where topic is likely implied)
            # If message is long, we might miss a topic change, so use LLM.
            # Heuristic: Short message (< 5 words) + Vector Hit = Safe to short-circuit.
            if len(message.split()) < 5:
                print(f"[Router] Fast Path Triggered: {intent}")
                return {"route": intent, "topic": None, "style": "comprehensive"}
        
        prompt = f"""
        You are the Router for an AI Tutor.
        Classify the User Message into one of these intents:

        1. PLAN: Choose this if the user wants to LEARN a topic, START a lesson, or mentions a specific subject (e.g. "Teach me X", "I want to learn Y", "Start Z", "Let's do BFS").
        2. ACTION: Choose this ONLY if the user explicitly asks for a tool (e.g. "Give me a quiz", "I want to code", "Practice", "Debug").
        3. CHAT: Choose this for Greetings ("Hi", "Hello") or specific questions ("What is a variable?", "Why is sky blue?"). 
           **CRITICAL**: If the user mentions a broad topic like "Recursion" or "Machine Learning" without a specific question, assume they want a PLAN to learn it.

        Also detect the LEARNING STYLE:
        - "comprehensive" (default): Standard deep dive.
        - "concise": User wants "quick", "fast", "summary".
        - "test_prep": User mentions "test tomorrow", "exam", "theory".
        - "practical_prep": User mentions "practicals", "lab", "code only".

        User Message: "{message}"

        Return strictly JSON:
        {{
            "route": "PLAN" | "ACTION" | "CHAT",
            "topic": "The extracted technical topic (e.g. 'Recursion') or null if none found",
            "style": "comprehensive" | "concise" | "test_prep" | "practical_prep"
        }}
        """
        
        try:
            response = self.groq.generate_content(prompt)
            print(f"DEBUG: Raw Router Response: '{response}'")
            
            # Robust JSON Extraction
            import re
            
            # 1. Remove <think> blocks if present
            clean_text = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
            
            # 2. Extract JSON from code blocks if present
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1].split("```")[0].strip()
            
            # 3. If still not pure JSON, try finding first '{' and last '}'
            json_match = re.search(r"\{.*\}", clean_text, re.DOTALL)
            if json_match:
                clean_text = json_match.group()
                
            data = json.loads(clean_text)
            return data
        except Exception as e:
            print(f"Router Error: {e}")
            return {"route": "CHAT", "topic": None, "style": "comprehensive"} # Default fallback
