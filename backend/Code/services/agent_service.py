# services/agent_service.py
import random
import random
import json
import re
from typing import Dict, Any
# from langchain.agents import initialize_agent, Tool, AgentType (REMOVED)
# from langchain.memory import ConversationBufferMemory (REMOVED)
from chatbot.services.groq_service import GroqService
from Code.models import QuestionB, Plan, TestCase

# Initialize Groq model
groq = GroqService()

# ─────────────────────────────
# TOOL 1: Intent classification
# ─────────────────────────────
# Helper for robust JSON extraction
def clean_json_blocks(text):
    if not text:
        return None
    text = text.strip()
    
    # 1. Remove <think> blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # 2. Try direct parse first (if it looks like JSON)
    if text.startswith("{") or text.startswith("["):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # 3. Regex search for generic JSON object/array (greedy match)
    # captures from first { to last }
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        candidate = match.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 4. Fallback to code block extraction (only if regex failed)
    if "```json" in text:
        try:
             candidate = text.split("```json")[1].split("```")[0].strip()
             return json.loads(candidate)
        except:
             pass
    elif "```" in text:
        try:
             candidate = text.split("```")[1].split("```")[0].strip()
             return json.loads(candidate)
        except:
             pass

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"JSON Parse Error: {text}")
        return None

# ─────────────────────────────
# TOOL 1: Intent classification
# ─────────────────────────────
def decide_intent_tool(user_query: str) -> Dict[str, Any]:
    """
    Uses LLM to understand what the user wants.
    """
    prompt = f"""
    You are an intelligent study planner. Analyze this user's query and return a JSON describing their intent.

    Example outputs:
    {{"type": "plan", "topic": "arrays", "count": 5, "intent": "interview", "company": "Google"}}
    {{"type": "Learn", "topic": "recursion", "count": 8, "intent": "practice", "company": "Practice"}}
    
    User query: "{user_query}"
    """
    resp = groq.generate_content(prompt)
    data = clean_json_blocks(resp)
    
    if data:
        return data
        
    print(f"Intent parsing error, Response: {resp}")
    # fallback random defaults
    return {"type": "single", "topic": "general", "count": 1, "intent": "explore"}

# ─────────────────────────────
# TOOL 2: Question generator
# ─────────────────────────────
def generate_question_tool(topic: str, difficulty: str = "medium") -> Dict[str, Any]:
    prompt = f"""
    Generate a {difficulty} coding question about "{topic}".
    
    The question should strictly follow this difficulty level:
    - Easy: Basic syntax, loops, inbuilt functions allowed unless specified otherwise.
    - Medium: Logic building, standard algorithms, optimal time complexity.
    - Hard: Advanced algorithms, edge cases, strict constraints.

    Return ONLY strict JSON with keys: 
    - "title": Short title.
    - "description": Detailed problem statement in Markdown. Include Input/Output format, constraints, and Examples.
    - "difficulty": "{difficulty}" (ensure this matches).
    - "testcases": List of objects with "input_data" and "expected_output" (strings).
    """
    resp = groq.generate_content(prompt)
    data = clean_json_blocks(resp)
    
    if data:
        print("Generated question JSON:", data)
        return data
        
    print(f"Question parsing error, Response: {resp}")
    return {"title": f"{topic} Problem", "description": resp, "difficulty": difficulty, "testcases": []}

# ─────────────────────────────
# TOOL 3: Plan generator
# ─────────────────────────────
def create_plan_tool(topic: str, intent: str, count: int, company:str) -> Dict[str, Any]:
    """
    Generate a learning plan with N question titles or descriptions.
    """
    # Force 'Learn' intent to use the Phased approach if generic
    if intent.lower() == "learn" or intent.lower() == "practice":
        prompt = f"""
        You are an expert Data Structures & Algorithms curriculum designer.

Your task is to generate a step-by-step coding practice plan for the topic: "{topic}".

CORE TEACHING PRINCIPLE:
- The plan must progress naturally from absolute basics to interview-level mastery.
- Each new question must be understandable using only what was learned before.
- Each question must introduce exactly ONE new idea or pattern.
- Earlier concepts should be reinforced implicitly in later questions.

PHASE GENERATION RULES:
- You must decide how many phases are needed.
- Phases must emerge logically based on concept complexity.
- Each phase should represent a clear conceptual jump (not arbitrary grouping).
- Phase numbering must start from Phase 0 and increase sequentially.

QUESTION DESIGN RULES:
- Each phase must contain 2-3 carefully chosen coding problems.
- Prefer well-known problems (LeetCode / GFG equivalents).
- Difficulty must increase gradually across phases.
- Do NOT assume prior knowledge.
- Do NOT skip intermediate reasoning steps.
- Do NOT hardcode or predefine phase themes.

OUTPUT FORMAT (STRICT):
Return ONLY a valid JSON object in the following format:
        Example Output:
        {{
            "plan": [
                {{"title": "Phase 0: Build Array from Permutation", "difficulty": "easy", "description": "Practice zero-based indexing and mapping."}},
                {{"title": "Phase 1: Running Sum of 1d Array", "difficulty": "easy", "description": "Learn accumulator pattern."}}
            ]
        }}
        
        Generate at least 6-8 steps covering the full depth of {topic}.
        """
    else: 
         # Legacy / Interview specific fallback
         prompt = f"""
         Create a coding practice plan for topic '{topic}' (intent: {intent}).
         Target Company/Style: {company}.
         Count: {count} problems.
         
         Return JSON: {{"plan":[{{"title":"...","difficulty":"..."}},...]}}
         """

    resp = groq.generate_content(prompt)
    data = clean_json_blocks(resp)
    
    if data:
        print("Generated plan JSON:", data)
        return data

    print(f"Plan parsing error, Response: {resp}")
    # Fallback
    return {"plan": [{"title": f"Phase {i}: {topic} Practice", "difficulty": "medium"} for i in range(count)]}

# build_agent REMOVED

# build_agent Logic Removed


# ─────────────────────────────
# MAIN ENTRY FUNCTION
# ─────────────────────────────

# ─────────────────────────────
# TOOL 2b: Structured Batch Generator (User Request)
# ─────────────────────────────
def generate_structured_batch_tool(topic: str) -> list:
    """
    Generates exactly 3 structured questions as requested.
    """
    prompt = f"""
    Generate exactly three coding questions for the topic "{topic}" such that:

    Question 1 – Structural Application
    Requires the learner to implement the core abstraction or mechanism of {topic} from first principles.
    Must include edge cases or constraints that force correct conceptual understanding.

    Question 2 – Constraint-Driven Selection
    Presents a practical problem where {topic} is the natural solution due to its defining property.
    The learner must choose and use the topic intentionally (not by instruction).
    The question must let him understand why.

    Question 3 – Conceptual Transfer
    Requires using the key property of {topic} to solve a different but related problem.
    Avoid trivial repetition of Question 2.

    OUTPUT FORMAT:
    Return a JSON object with a key "questions" containing a list of 3 question objects.
    Each question object must follow this schema:
    {{
        "title": "Short Title",
        "description": "Full problem description...",
        "difficulty": "medium",
        "testcases": [ {{"input_data": "...", "expected_output": "..."}} ]
    }}
    """
    resp = groq.generate_content(prompt)
    data = clean_json_blocks(resp)
    
    if data and "questions" in data:
        return data["questions"]
        
    # Fallback if parsing fails
    print(f"Batch generation failed, falling back. Resp: {resp}")
    return [
        {"title": f"{topic} (Structural)", "description": "Implement core concepts.", "difficulty": "medium", "testcases": []},
        {"title": f"{topic} (Selection)", "description": "Apply in practical scenario.", "difficulty": "medium", "testcases": []},
        {"title": f"{topic} (Transfer)", "description": "Solve related problem.", "difficulty": "hard", "testcases": []}
    ]

# ─────────────────────────────
# MAIN ENTRY FUNCTION
# ─────────────────────────────
def process_user_query(user_query: str, user):
    """
    Handles full logic — one entry point for the Django view.
    """
    # 1️⃣ Decide intent
    intent_info = decide_intent_tool(user_query)
    print("Intent decided:", intent_info)

    topic = intent_info.get("topic", "general")
    plan_type = intent_info.get("type", "Learn")
    # We ignore 'count' because we are overriding for AgentCode
    intent = intent_info.get("intent", "practice")
    company = intent_info.get("company","Practice")
    
    # Check if this is a "Plan" request
    if plan_type == "plan" or plan_type == "Learn":
         # ... (Existing plan logic handled in separate if-block, not modifying here for now) ...
         # For brevity of this patch, I'm just focusing on the "else" block (single/practice) replacement
         # But wait, original code has the if plan_type == "plan" block. 
         # I need to match the original structure or I'll delete code.
         pass # Handled below by not replacing the if-block

    # Logic for Plan Generation (Existing)
    if plan_type == "plan" or plan_type == "Learn":
        count_val = intent_info.get("count")
        count = int(count_val) if count_val else 1
        plan_data = create_plan_tool(topic, intent, count, company)
        
        try:
            plan_doc = Plan(
                user=user,
                intent=intent,
                topic=topic,
                questions=[], 
                plan_content=plan_data.get("plan", []),
                total_questions=str(len(plan_data.get("plan", [])))
            )
            plan_doc.save()
            print(f"Saved Plan Structure: {plan_doc.id}")
        except Exception as e:
            print("Error saving plan document:", e)
            return {"error": "Failed to save plan"}

        plan_steps = plan_data.get("plan", [])
        if not plan_steps:
             return {"type": "plan", "plan_id": str(plan_doc.id), "questions": [], "total_phases": 0}

        first_step = plan_steps[0]
        first_phase_title = first_step.get("title", "").split(":")[0].strip()
        phase_steps = [s for s in plan_steps if s.get("title", "").split(":")[0].strip() == first_phase_title]
        
        print(f"Generating batch for {first_phase_title} ({len(phase_steps)} questions)")
        
        results = []
        for step in phase_steps:
            try:
                # We still use individual generator for PLANS as they have specific phases
                qdata = generate_question_for_step(topic, step)
                
                testcases = []
                for tc in qdata.get("testcases", []):
                        testcases.append(TestCase(input_data=tc.get("input_data"), expected_output=tc.get("expected_output")))

                qdoc = QuestionB(
                    user=user,
                    topic=topic,
                    title=qdata["title"],
                    description=qdata["description"],
                    difficulty=qdata.get("difficulty", "medium").lower(),
                    testcases=testcases
                )
                qdoc.save()
                
                plan_doc.questions.append(str(qdoc.id))
                results.append(qdata)
            except Exception as e:
                print(f"Error saving question {step['title']}: {e}")
        
        plan_doc.save()
        return {"type": "plan", "plan_id": str(plan_doc.id), "questions": results, "total_phases": len(plan_steps)}

    # 3️⃣ Else single/practice -> USE NEW 3-QUESTION LOGIC
    else:
        # User requested per "AgentCode" rules: 3 structured questions.
        print(f"Generatign Structured Batch for topic: {topic}")
        questions_data = generate_structured_batch_tool(topic)
        
        saved_questions = []
        
        for qdata in questions_data:
            testcases_data = qdata.get("testcases", [])
            if isinstance(testcases_data, str):
                try:
                   testcases_data = json.loads(testcases_data)
                except:
                   testcases_data = []

            testcases = []
            for tc in testcases_data:
                 inp = tc.get("input_data") or tc.get("input") or ""
                 out = tc.get("expected_output") or tc.get("expected") or ""
                 testcases.append(TestCase(input_data=inp, expected_output=out))
            
            qdoc = QuestionB(
                user=user,
                topic=topic,
                title=qdata.get("title", "Practice Question"),
                description=qdata.get("description", "No description"),
                difficulty=qdata.get("difficulty", "medium"),
                testcases=testcases
            )
            qdoc.save()
            saved_questions.append(qdata)
            
        # Return as "plan" type so views.py handles a list, OR as valid single if frontend expects it
        # But since we generated 3, returning them as a list under "questions" is safest if views.py logic supports it.
        # Code/views.py logic:
        # if type == "single": takes "question" dict
        # if type == "plan": takes "questions" list
        
        return {"type": "plan", "questions": saved_questions, "topic": topic}


def generate_question_for_step(main_topic, step_data):
    """
    Helper to generate a specific question from a plan step.
    """
    step_topic = f"{main_topic}: {step_data.get('title')}"
    qdata = generate_question_tool(step_topic, step_data.get("difficulty", "medium"))
    
    # Normalize testcases
    testcases_data = qdata.get("testcases", [])
    if isinstance(testcases_data, str):
        try:
            testcases_data = json.loads(testcases_data)
        except:
            testcases_data = []
            
    normalized_tcs = []
    for tc in testcases_data:
        inp = tc.get("input_data") or tc.get("input") or ""
        out = tc.get("expected_output") or tc.get("expected") or ""
        normalized_tcs.append({"input_data": inp, "expected_output": out})
        
    qdata["testcases"] = normalized_tcs
    return qdata
