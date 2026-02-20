from django.conf import settings
from chatbot.models import TutorSession
# from chatbot.models import TutorSession
# import google.generativeai as genai (REMOVED)
import os
import json
import re
from .groq_service import GroqService
from .rl_selector import RLSelector
from .gkt_model import GKTModel

# Configure Groq
# genai.configure... (REMOVED)
# model = genai.GenerativeModel("gemini-2.5-flash") (REMOVED)
groq_service = GroqService()
rl_agent = RLSelector()
gkt_model = GKTModel()

from .recommendation_service import RecommendationService
recommendation_service = RecommendationService()


def get_or_create_session(user):
    # User is a Mongo Document. We use email as the stable key.
    email = user.email
    session, created = TutorSession.objects.get_or_create(user_email=email)
    return session

def clean_json_response(text):
    if not text:
        return None
    text = text.strip()
    
    # 1. Remove <think> blocks if present
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    
    # 2. Extract JSON from code blocks if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    # 3. Last resort: regex find JSON object
    # Try array first then object
    json_match = re.search(r"(\{|\[).+(\}|\])", text, re.DOTALL)
    if json_match:
        text = json_match.group()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"JSON Parse Error: {text}")
        return None

def generate_subtopics_python(topic, **kwargs):
    prompt = f"""
    You are an expert Computer Science Curriculum Designer for strictly python.
    Create a highly structured, emoji-rich learning roadmap for "{topic}".
    
    Structure the roadmap into Levels (Level 1, Level 2, etc.) progressing for Beginner.
    
    Output strictly a JSON object with two keys:
    1. "roadmap_md": A string containing the beautiful Markdown representation.
       - Use headers "🟢 {topic} COMPLETE ROADMAP".
       - Use "Level X - Title" format.
       - Use bullet points with formatting.
       - Mark important concepts with "🔥".
    
    2. "steps": A flat list of strings representing the granular individual lessons to teach.
       - Each string should correspond to a sub-bullet in your roadmap.
       - This list will be used by the teaching bot to iterate 1-by-1.
       
    Example Output Format:
    {{
      "roadmap_md": "🟢 STACK ROADMAP\\n\\nLevel 1 - Basics\\n* Definition\\n* LIFO Principle...",
      "steps": ["Stack Definition", "LIFO Principle", "Push/Pop Operations", ...]
    }}
    """
    if kwargs.get('is_revision'):
        prompt = f"""
        You are an expert Computer Science Tutor.
        The user FAILED a diagnostic quiz on "{topic}".
        Create a FAST TRACK REVISION checklist for "{topic}" to help them fill gaps quickly.
        
        Structure:
        - Focus ONLY on Key Concepts and Common Pitfalls.
        - Be concise. No fluff.
        - Emoji-rich but professional.
        
        Output strictly a JSON object with two keys:
        1. "roadmap_md": A string containing the Markdown representation.
           - Header: "⚡ REVISION: {topic}"
           - Use simple bullet points.
        
        2. "steps": A flat list of strings representing the key concepts to review.
           - Keep it under 5 steps if possible.
           
        Example Output Format:
        {{
          "roadmap_md": "⚡ REVISION: STACKS\\n* 🔑 Concept: LIFO\\n* ⚠️ Pitfall: Overflow",
          "steps": ["LIFO Concept", "Stack Operations", "Common Errors"]
        }}
        """
    text = groq_service.generate_content(prompt)
    data = clean_json_response(text)
    
    if data and "roadmap_md" in data and "steps" in data:
        return data["roadmap_md"], data["steps"]
    
    # Fallback
    fallback_steps = data if isinstance(data, list) else ["Basics", "Core Concepts", "Advanced", "Summary"]
    fallback_md = f"**{topic} Roadmap**\n\n" + "\n".join([f"* {s}" for s in fallback_steps])
    return fallback_md, fallback_steps

def teach_content(subtopic, style="Socratic"):
    style_instruction = ""
    if style == "socratic":
         style_instruction = "Style: SOCRATIC. Do NOT give the answer. Ask guiding questions to lead the user to understanding."
    elif style == "practical":
         style_instruction = "Style: PRACTICAL. minimal theory. Show code immediately and explain line-by-line."
    elif style == "analogy":
         style_instruction = "Style: ANALOGY-HEAVY. Use real-world metaphors for everything."
    else:
         style_instruction = "Style: EXPERT TEACHER. Balanced theory, analogy, and code."

    prompt = f"""
    You are an expert Computer Science teacher with 20 years of experience who is Humorous and jokeful in nature. And YOu are strictly a python Tutor IF asked for any other subject just say It is not our course.
    Topic: "{subtopic}"
    {style_instruction}

    Your goal is to teach this specific subtopic clearly and effectively.
    
    STRUCTURE:
    1. **Explanation**: Explain the concept clearly using metaphors, code examples, and humor.
    2. **Check for Understanding**: End with **EXACTLY ONE** specific question to check if the user understood. Do NOT ask multiple questions.
    
    OUTPUT FORMAT:
    Please provide the response in two clearly marked blocks. Do not use JSON.
    
    [CONTENT]
    (Your explanation text here. Use markdown for formatting.)
    
    (Your single follow-up question here)
    [/CONTENT]
    
    [VISUALIZATION]
     You are a specialized Visualization Code Generator.

Your task is to generate a complete, self-contained **single-page HTML document** (one file) that visually and interactively demonstrates the requested algorithm or data structure.

RULES:
1. Respond ONLY with the plain HTML document as a single string (start with <!DOCTYPE html> and include <html> ...). Do NOT wrap the output in JSON, Markdown, comments, or any additional text.
2. The document MUST include Tailwind CSS loaded via CDN (https://cdn.tailwindcss.com) and use Tailwind utility classes for styling. Do NOT include external CSS files other than the Tailwind CDN.
3. Use Vanilla JavaScript for simple logic. **For Graph/Tree/Network visualizations, YOU MUST USE D3.js (v7)** via CDN (https://d3js.org/d3.v7.min.js).
   - Use **Force-Directed Layout** (d3.forceSimulation) for connected data.
   - Use **Tree Layout** (d3.tree) for hierarchies.
   - Make it beautiful and animated.
4. The page MUST include at least two visible controls labeled "Next Step" and "Reset" to control the visualization, and display the current step index.
5. The HTML should be self-contained and runnable inside an iframe (no module imports, no ESM import/export statements, no external network calls other than the Tailwind CDN).
6. Ensure all DOM element IDs and classes are unique and descriptive to avoid collisions when embedded in an iframe.
7. The visual output should be responsive and usable on common desktop/mobile widths.
8. Include a small legend explaining colors/states used in the visualization (e.g., comparing, swapping, sorted).
9. Keep the code robust: sanitize inputs if accepting user input, avoid using `eval`, and do not depend on server-side resources.
10. The HTML must be ready to render as-is; the user should be able to paste it into an iframe or file and see the fully working visualization without modifications.
11.The input should be from the user 
12.The visualization should also say what is happening at each step
13.Every step should be understandable visually
14.Add animation how they connect or change in real time
15.Visualize the problem first before visualizing the algorithm and then change the visualization to show how the algorithm works
16.provide how the datastructureschange if It needed in the problem 
17.Make sure the illustrattion of how a real code algorithm would work
18.do the swapping or changing of datastructures in real time.
Do not add any additional commentary — output only the HTML document.

Steps:
1. Get the problem or algorithm from the user
2. identify the problem or algorithm
3. Find the best method or implementation of the solution for the problem
4. Identify the Datastructures needed for the problem
5. now plan the blocks to get input
6 now plan all possible interaction in the HTML
7. now plan all the code, data structure and explaination of each step in the HTML
8. now plan the final code
9. provide code snippet 
10. now generate html with clean code and provide best animaation for with tailwind css
    [/VISUALIZATION]
    
    Guidelines for Content:
    1. Teach the content with human-like sentences.
    2. Be a tutor, not a textbook.
    3. Include all important points.
    4. Share personal experience or common pitfalls.
    5. Use humor.
    6. Provide step-by-step guidance.
    7. Adjust depth as needed (definition, example, math).
    8. For algorithms, explain the logic step-by-step.
    9.Heavily comment the coding programs as tutor explaining everyline why it is needed and what it do.
    
    Guidelines for Visualization:
    - The HTML will be rendered in a safe iframe.
    - Make it visually appealing (modern, clean).
    - It should help the student UNDERSTAND the concept (e.g., sorting animation, tree traversal).
    - Use clean vanilla JS.
    """
    response_text = groq_service.generate_content(prompt)
    if not response_text:
        return {"content": f"I apologize, I'm having trouble retrieving the lesson for **{subtopic}** right now. Could we try again?", "visualization": None}

    # Parse Blocks using Regex
    content_match = re.search(r'\[CONTENT\](.*?)\[/CONTENT\]', response_text, re.DOTALL)
    viz_match = re.search(r'\[VISUALIZATION\](.*?)\[/VISUALIZATION\]', response_text, re.DOTALL)
    
    content = content_match.group(1).strip() if content_match else response_text
    visualization = viz_match.group(1).strip() if viz_match else None
    
    # Validation: If content effectively empty, use fallback
    if len(content) < 10:
        content = f"**{subtopic}**\n\nLet's get started. What do you already know about this?"

    # Generic cleanup for empty viz
    if visualization and len(visualization) < 20: 
        visualization = None
        
    # Remove any markdown code blocks from viz if present (e.g. ```html ... ```)
    if visualization:
        visualization = re.sub(r'^```html\s*', '', visualization)
        visualization = re.sub(r'^```\s*', '', visualization)
        visualization = re.sub(r'\s*```$', '', visualization)
    
    return {"content": content, "visualization": visualization}

def regenerate_visualization(topic):
    """
    Specifically requests ONLY the visualization for a topic.
    Used when the user clicks 'Regenerate' in the UI.
    """
    prompt = f"""
    You are an Expert Frontend Engineer & CS Educator.
    The user is unsatisfied with the previous visualization for "{topic}". Your goal is to build a STUNNING, INTERACTIVE, and ROBUST visualization.

    REQUIREMENTS:
    1. **Self-Contained**: Must be a single HTML file with embedded CSS/JS.
    2. **Visual Appeal**: Use modern UI. You MAY use TailwindCSS via CDN: <script src="https://cdn.tailwindcss.com"></script>.
       **Use D3.js (v7)** via CDN (https://d3js.org/d3.v7.min.js) for any graph/network animations. Use **Force-Directed Layouts** where applicable.
    3. **Interactivity**: Include buttons (e.g., "Step", "Play", "Reset") to control the animation.
    4. **Robustness**: Handle edge cases (empty input, etc.). NO PLACEHOLDERS like "// code here". Write the FULL logic.
    5. **Educational**: Show the "State" of the algorithm clearly (e.g., highlighting array indices being compared).

    OUTPUT FORMAT:
    [VISUALIZATION]
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
             /* Custom Animations */
             @keyframes highlight {{ 0% {{ background-color: #fef08a; }} 100% {{ background-color: transparent; }} }}
             .highlight-node {{ animation: highlight 1s ease; }}
        </style>
    </head>
    <body class="bg-slate-50 p-4 font-sans text-slate-800">
        <!-- YOUR UI HERE -->
        <script>
            // YOUR FULL LOGIC HERE
        </script>
    </body>
    </html>
    [/VISUALIZATION]
    """
    response_text = groq_service.generate_content(prompt)
    
    viz_match = re.search(r'\[VISUALIZATION\](.*?)\[/VISUALIZATION\]', response_text, re.DOTALL)
    visualization = viz_match.group(1).strip() if viz_match else None
    
    if visualization:
        visualization = re.sub(r'^```html\s*', '', visualization)
        visualization = re.sub(r'^```\s*', '', visualization)
        visualization = re.sub(r'\s*```$', '', visualization)
        
    return visualization

def analyze_input(user_input, current_topic, current_subtopic, last_bot_question=None):
    """
    Determine if input is:
    1. ANSWER (to the teaching question)
    2. DOUBT (question about current topic)
    3. SWITCH (request to change topic)
    """
    prompt = f"""
    Context: Python Tutoring.
    Topic: {current_topic}, Subtopic: {current_subtopic}
    Last Bot Message should have asked a question.
    User User Input: "{user_input}"

    Classify the user intent:
    - "ANSWER": If they are answering the question (correctly or incorrectly).
    - "DOUBT": If they are asking for help/explanation or saying "I don't know".
    - "SWITCH": If they clearly ask to learn something else (e.g. "teach me java", "stop").
    - "SKIP": If the user wants to skip the current question or topic (e.g. "skip", "next", "I know this").
    - "FINISH": If the user says "I am done", "Finish", "Complete this", or "I understand everything".

    Output JSON:
    {{
      "intent": "ANSWER" | "DOUBT" | "SWITCH" | "SKIP" | "FINISH",
      "is_correct": boolean (only if ANSWER, true/false),
      "analysis": "Short reason",
      "reply": "If correct ANSWER: say 'Correct!' and brief check. If incorrect ANSWER: explain why. If DOUBT: answer it clearly."
    }}
    """
    return clean_json_response(groq_service.generate_content(prompt))
    
def start_new_topic(user, topic, is_revision=False):
    """
    Forces the Tutor Session to start a new topic immediately.
    Used by Main Agent Orchestrator to sync state.
    """
    session = get_or_create_session(user)
    session.current_topic = topic
    
    # Generate Rich Roadmap
    # Generate Rich Roadmap (Visual Only)
    roadmap_md, _ = generate_subtopics_python(topic, is_revision=is_revision)
    
    # DYNAMIC INIT: Consultant the GAT BRAIN first
    next_step = recommendation_service.get_next_best_step(user.email, topic)
    
    if next_step:
        # GAT found a specific starting point
        session.subtopics = [next_step]
        roadmap_msg = f"Welcome! 🧠 **Knowledge Graph Analysis Complete**.\n\nBased on your mastery profile, the best starting point for **{topic}** is:\n\n# 🚀 **{next_step}**\n\nThe AI predicts you are **100% Ready** for this concept.\n\nShall we start?"
    else:
        # Fallback (Graph empty or topic unknown) -> Use LLM
        roadmap_md, steps = generate_subtopics_python(topic, is_revision=is_revision)
        session.subtopics = steps
        roadmap_msg = f"{roadmap_md}\n\n**Shall we proceed with this roadmap?**"

    session.current_index = -1 
    session.status = "AWAITING_PLAN_APPROVAL"
    session.switch_topic_buffer = None # Clear any pending switches
    session.save()
    
    return {
        "reply": roadmap_msg, 
        "awaiting_reply": True, 
        "is_complete": False
    }



def handle_persistent_chat(user, message):
    session = get_or_create_session(user)
    


    # 1. HANDLE SWITCH CONFIRMATION (Legacy internal switch)
    if session.status == "AWAITING_SWITCH_CONFIRMATION":
        if any(w in message.lower() for w in ["yes", "yeah", "ok", "sure", "yup"]):
            new_topic = session.switch_topic_buffer
            session.current_topic = new_topic
            session.subtopics = generate_subtopics_python(new_topic)
            # Unpack roadmap
            roadmap_md, steps = generate_subtopics_python(new_topic)
            
            session.current_topic = new_topic
            session.subtopics = steps
            session.current_index = -1
            session.status = "AWAITING_PLAN_APPROVAL"
            session.switch_topic_buffer = None
            session.save()
            
            return {
                "reply": f"Ok! Switching to **{new_topic}**.\n\n{roadmap_md}\n\n**Does this roadmap look good?** (Type 'Yes' to start or suggest changes)", 
                "awaiting_reply": True, 
                "is_complete": False
            }
        else:
            session.status = "AWAITING_ANSWER" # Revert to teaching
            session.switch_topic_buffer = None
            session.save()
            return {"reply": "Cancelled switch. Let's continue with the current topic. What is your answer?", "awaiting_reply": True, "is_complete": False}

    # 2. PLAN APPROVAL FLOW
    if session.status == "AWAITING_PLAN_APPROVAL":
        # Check if user approves or wants changes
        prompt = f"""
        User Input: "{message}"
        Context: The user is reviewing a learning plan.
        Task: Determine if the user is APPROVING (Yes, Ok, Start) or REQUESTING CHANGES.
        Output JSON: {{ "intent": "APPROVE" | "MODIFY", "modification_request": "..." }}
        """
        analysis = clean_json_response(groq_service.generate_content(prompt))
        intent = analysis.get("intent", "APPROVE") if analysis else "APPROVE"
        
        if intent == "APPROVE" or any(w in message.lower() for w in ["yes", "ok", "ready", "start", "good"]):
            session.current_index = 0
            session.status = "TEACHING"
            session.save()
            
            # Determine Style via RL Agent
            # style = "expert"
            # if "practical" in message.lower(): style = "practical"
            # elif "socratic" in message.lower(): style = "socratic"
            # elif "analogy" in message.lower(): style = "analogy"
            
            # Use RL Agent to pick the best style for this topic user
            style = rl_agent.get_action(session.current_topic)
            session.last_style_used = style # SAVE STATE for reward
            session.save()
            
            teaching_data = teach_content(session.subtopics[0], style=style)
            content = teaching_data.get("content", "")
            visualization = teaching_data.get("visualization")
            
            # --- EXTRACT QUESTION FROM CONTENT ---
            # We assume the prompt "End with EXACTLY ONE specific question" logic works.
            # We'll take the last paragraph as a heuristic for the question.
            last_question_text = content.split('\n')[-1] if content else ""
            session.last_question = last_question_text
            
            session.status = "AWAITING_ANSWER"
            session.save()
            return {
                "reply": f"Great! Let's start with **{session.subtopics[0]}**.\n\n{content}", 
                "visualization": visualization,
                "awaiting_reply": True, 
                "is_complete": False
            }
        else:
            # Modify Plan
            mod_request = analysis.get("modification_request") or message
            
            # Regenerate subtopics with feedback - Request Rich Format again for consistency
            mod_prompt = f"""
            The user wants to modify the roadmap for "{session.current_topic}".
            Current Steps: {json.dumps(session.subtopics)}
            User Feedback: "{mod_request}"
            
            Task: Represents the UPDATED roadmap.
            Output JSON: {{ "roadmap_md": "...", "steps": [...] }}
            """
            text = groq_service.generate_content(mod_prompt)
            data = clean_json_response(text)
            
            if data and "steps" in data:
                session.subtopics = data["steps"]
                session.save()
                roadmap_view = data.get("roadmap_md", "Updated Plan:\n" + "\n".join(data["steps"]))
                
                return {
                    "reply": f"Refined Roadmap based on your feedback:\n\n{roadmap_view}\n\n**Good to go?**", 
                    "awaiting_reply": True, 
                    "is_complete": False
                }
            else:
                 return {"reply": "I couldn't understand how to modify the plan. Could you clarify?", "awaiting_reply": True, "is_complete": False}

    # 3. NEW SESSION / IDLE
    if session.status == "IDLE" or not session.current_topic:
        topic = message
        session.current_topic = topic
        
        # DYNAMIC INIT: Consultant the GAT BRAIN first
        next_step = recommendation_service.get_next_best_step(user.email, topic)
        
        if next_step:
            # GAT found a specific starting point
            session.subtopics = [next_step]
            roadmap_msg = f"Welcome! 🧠 **Knowledge Graph Analysis Complete**.\n\nBased on your mastery profile, the best starting point for **{topic}** is:\n\n# 🚀 **{next_step}**\n\nThe AI predicts you are **100% Ready** for this concept.\n\nShall we start?"
        else:
            # Fallback (Graph empty or topic unknown) -> Use LLM
            roadmap_md, steps = generate_subtopics_python(topic)
            session.subtopics = steps
            roadmap_msg = f"{roadmap_md}\n\n**Shall we proceed with this roadmap?**"
             
        session.current_index = -1 
        session.status = "AWAITING_PLAN_APPROVAL"
        session.save()
        
        return {
            "reply": roadmap_msg, 
            "awaiting_reply": True, 
            "is_complete": False
        }

    # 4. TEACHING FLOW
    
    # Check bounds
    if session.current_index >= len(session.subtopics):
        # Already done?
        return {"reply": "Topic completed.", "awaiting_reply": False, "is_complete": True}

    current_sub = session.subtopics[session.current_index]
    
    # Analyze Intent
    # Pass the last question asked by the bot (if any) for better context
    last_bot_question = getattr(session, "last_question", None)
    
    analysis = analyze_input(message, session.current_topic, current_sub, last_bot_question=last_bot_question)
    if not analysis:
        return {"reply": "I didn't catch that. Could you repeat?", "awaiting_reply": True, "is_complete": False}
        
    intent = analysis.get("intent")
    
    if intent == "SWITCH": 
        session.switch_topic_buffer = message 
        session.status = "AWAITING_SWITCH_CONFIRMATION"
        session.save()
        return {"reply": f"Are you sure you want to stop learning **{session.current_topic}** and switch topics?", "awaiting_reply": True, "is_complete": False}
        
    if intent == "FINISH":
        session.status = "IDLE"
        session.save()
        return {
            "reply": f"Understood! Marking **{session.current_topic}** as complete.\n\n(Reporting completion to Main Agent...)", 
            "awaiting_reply": False, 
            "is_complete": True
        }

    if intent == "SKIP":
        session.current_index += 1
        if session.current_index >= len(session.subtopics):
            session.status = "IDLE"
            session.save()
            return {"reply": "Skipped to end. Topic completed!", "awaiting_reply": False, "is_complete": True}
        
        next_sub = session.subtopics[session.current_index]
        session.save()
        teaching_data = teach_content(next_sub) 
        content = teaching_data.get("content", "")
        visualization = teaching_data.get("visualization")
        
        return {
            "reply": f"Skipping ahead!\n\n{content}", 
            "visualization": visualization,
            "awaiting_reply": True, 
            "is_complete": False
        }

    # --------------------------------------------------------------------------------------
    # DYNAMIC RECOMMENDATION LOGIC (Replaces Linear List)
    # --------------------------------------------------------------------------------------
    
    if intent == "ANSWER":
        # 1. Update Graph Knowledge Tracing (GKT) Model (GNN)
        if is_correct:
            # 1. Update Graph Knowledge Tracing (GKT) Model (GNN)
            new_mastery = gkt_model.update(user.email, current_sub, is_correct, source_type="tutor")
            mastery_pct = int(new_mastery * 100)
            
            # POSITIVE REWARD
            last_style = getattr(session, "last_style_used", None)
            if last_style:
                rl_agent.update(last_style, reward=1.0)
                
            # --- METRICS UPDATE ---
            session.tutor_questions_asked = (session.tutor_questions_asked or 0) + 1
            session.tutor_questions_correct = (session.tutor_questions_correct or 0) + 1
            session.save()
            # ----------------------

            # Check Mastery Threshold (e.g., 0.85)
            if new_mastery < 0.85:
                return {
                    "reply": f"{analysis.get('reply')}\n\nCorrect! But mastery is only **{mastery_pct}%**. Let's practice this concept a bit more.",
                    "awaiting_reply": True,
                    "is_complete": False
                }
            else:
                # MASTERED -> SIGNAL COMPLETION TO ORCHESTRATOR
                success_msg = f"🎉 Fantastic! Mastery: **{mastery_pct}%**. You've grasped the core concepts of **{current_sub}**!"
                return {
                    "reply": f"{analysis.get('reply')}\n\n{success_msg}", 
                    "awaiting_reply": False, 
                    "is_complete": True 
                }
        else:
            # INCORRECT ANSWER
            # Update GKT (False)
            new_mastery = gkt_model.update(user.email, current_sub, False, source_type="tutor")
            mastery_pct = int(new_mastery * 100)

            # NEGATIVE REWARD
            last_style = getattr(session, "last_style_used", None)
            if last_style:
                rl_agent.update(last_style, reward=-0.5)

            # --- METRICS UPDATE ---
            session.tutor_questions_asked = (session.tutor_questions_asked or 0) + 1
            # Do NOT increment correct
            session.save()
            # ----------------------

            return {"reply": f"{analysis.get('reply')}\n\n(Mastery: {mastery_pct}%) Try again?", "awaiting_reply": True, "is_complete": False}

            
    if intent == "DOUBT":
        # Neutral/Negative Reward - Teaching wasn't clear enough?
        last_style = getattr(session, "last_style_used", None)
        if last_style:
            rl_agent.update(last_style, reward=-0.2)
            
        # Answer doubt, do not advance
        return {"reply": analysis.get("reply"), "awaiting_reply": True, "is_complete": False}

    return {"reply": "I'm confused. Let's continue.", "awaiting_reply": True, "is_complete": False}
