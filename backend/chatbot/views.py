# views.py (or wherever your view lives)
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .models import TutorSession
from rest_framework.permissions import IsAuthenticated
from users.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
import os
from main_agent.models import AgentSession
from Code.models import UserQuestion
# import google.generativeai as genai (REMOVED)
from .services.groq_service import GroqService

# configure genai for other endpoints (summarize/quiz)
# genai.configure... (REMOVED)
groq_service = GroqService()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_session(request):
    try:
        TutorSession.objects.filter(user_email=request.user.email).delete()
        return Response({"message": "Session reset successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def welcome_message(request):
    user = request.user
    
    # 1. Fetch Context
    # Get last active session
    last_session = AgentSession.objects(user=user).order_by('-updated_at').first()
    
    # Get recent questions
    recent_questions = UserQuestion.objects.filter(user=user).order_by('-created_at')[:3]
    recent_topics = [q.topic for q in recent_questions]
    
    # 2. Construct Prompt for Agent
    prompt = f"""
    You are the welcome module for an AI Python Tutor.
    User Context:
    - Name: {user.username}
    - Recent Topics Practiced: {", ".join(recent_topics) if recent_topics else "None"}
    - Last Active Session Topic: {last_session.current_topic if last_session and last_session.current_topic else "None"}
    
    Task:
    1. Generate a short, warm, personalized welcome message (max 2 lines).
    2. Explicitly state you are a **Dedicated Theory Tutor** here to help them master concepts deeply.
    3. Do NOT mention "Plan" or "Practice" or "Coding Challenges" (those are handled by other agents).
    4. Provide 3 specific topic recommendations to start learning now.
       
    Output strictly JSON:
    {{
      "message": "...",
      "recommendations": ["Topic A", "Topic B", "Topic C"]
    }}
    """

    
    try:
        response_text = groq_service.generate_content(prompt)
        # Clean JSON
        import re
        import json
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            # Fallback
            data = {
                "message": f"Welcome back, {user.username}! Ready to learn something new?",
                "recommendations": ["Python Basics", "Data Structures", "Web Development"]
            }
            
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Welcome Error: {e}")
        return Response({
            "message": "Hi! I'm your AI Tutor. How can I help you today?",
            "recommendations": ["Python", "JavaScript", "React"] 
        }, status=status.HTTP_200_OK)



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def tutor_chat(request):
    user = request.user
    message = request.data.get("message", "")
    if not message:
        return Response({"error": "Message required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .services.persistent_tutor import handle_persistent_chat
        result = handle_persistent_chat(user, message)
        
        return Response(
            {
                "reply": result.get("reply"),
                "visualization": result.get("visualization"),
                "awaiting_reply": bool(result.get("awaiting_reply", False)),
                "is_complete": bool(result.get("is_complete", False)),
                "ended": bool(result.get("ended", False)),
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Summarize conversation endpoint (unchanged except small validation improvement)
from rest_framework.permissions import IsAuthenticated

# model = genai.GenerativeModel("gemini-2.5-flash") (REMOVED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def summarize_conversation(request):
    try:
        messages = request.data.get("messages", [])
        if not messages or not isinstance(messages, list):
            return Response({"error": "Missing or invalid 'messages' list."}, status=status.HTTP_400_BAD_REQUEST)

        full_text = "\n".join(messages)

        prompt = f"""
        You are an educational summarizer. Summarize the following tutor conversation
        into clear, structured learning notes. Highlight main ideas, definitions,
        and examples in a concise form suitable for quick revision.

        Conversation content:
        {full_text}
        """

        # response = model.generate_content(prompt)
        # summary_text = getattr(response, "text", None)
        summary_text = groq_service.generate_content(prompt)
        summary_text = summary_text.strip() if summary_text else "No summary generated."

        return Response({"summary": summary_text}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Summary generation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_quiz(request):
    try:
        messages = request.data.get("messages", [])
        if not messages:
            return Response({"error": "No messages provided"}, status=status.HTTP_400_BAD_REQUEST)

        text_context = "\n".join([m.get("text", "") for m in messages if m.get("sender") == "bot"])

        prompt = f"""
        Based on the following tutoring conversation:
        {text_context}

        Generate 5 multiple-choice quiz questions that test understanding.
        Return them in JSON format like:
        [
          {{
            "question": "...",
            "options": ["A", "B", "C", "D"],
            "answer": "A"
          }},
          ...
        ]
        """

        # model = genai.GenerativeModel("gemini-2.0-flash")
        # result = model.generate_content(prompt)
        # text = getattr(result, "text", "") or ""
        text = groq_service.generate_content(prompt)

        import json, re
        json_match = re.search(r"\[.*\]", text, re.DOTALL)
        quiz_data = json.loads(json_match.group()) if json_match else []

        return Response({"quiz": quiz_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_key_concepts(request):
    try:
        user = request.user
        # Get active tutor session
        session = TutorSession.objects.filter(user_email=user.email).first()
        
        if session and session.subtopics:
            # Return the subtopics as key concepts
            return Response(session.subtopics, status=status.HTTP_200_OK)
        else:
            # Default concepts if no session
            return Response(["Start a topic to see concepts!", "Python Basics", "Algorithms"], status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def regenerate_visualization_view(request):
    try:
        topic = request.data.get("topic")
        
        # If no topic provided, try to infer from session
        if not topic:
             session = TutorSession.objects.filter(user_email=request.user.email).first()
             if session:
                 # Use current subtopic if active, else broad topic
                 # Note: session object might not have current_subtopic as a direct field if it's just a list index
                 # But let's assume valid fields for now based on earlier code
                 if session.subtopics and 0 <= session.current_index < len(session.subtopics):
                     topic = session.subtopics[session.current_index]
                 else:
                     topic = session.current_topic
        
        if not topic:
            return Response({"error": "No topic provided or active session found."}, status=status.HTTP_400_BAD_REQUEST)
            
        from .services.persistent_tutor import regenerate_visualization
        html_code = regenerate_visualization(topic)
        
        return Response({"visualization": html_code}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_graph_data(request):
    """
    Returns the Knowledge Graph for Visualization.
    Nodes: Concepts (color-coded by mastery).
    Edges: Prerequisites (thickness by attention/weight).
    """
    try:
        from .services.gkt_model import GKTModel
        gkt = GKTModel()
        user_email = request.user.email
        
        # 1. Get State
        mastery_vector = gkt._get_user_vector(user_email)
        concepts = gkt.concepts
        adj = gkt.adj_matrix
        
        nodes = []
        edges = []
        
        # 2. Build Nodes (ReactFlow format)
        # Simple Auto-Layout (Levels)
        # We calculate "Depth" of each node (number of ancestors)
        # This is a hacky layout. Frontend 'dagre' is better, but let's give a baseline.
        depths = {}
        for i in range(len(concepts)):
            depths[i] = 0
            
        # 10 passes to propagate depth
        for _ in range(10):
            for i in range(len(concepts)):
                prereqs = [j for j in range(len(concepts)) if adj[i][j] > 0]
                if prereqs:
                    max_p = max([depths[p] for p in prereqs])
                    depths[i] = max_p + 1
                    
        # Group by depth for X coordinates
        level_counts = {}
        
        for i, concept in enumerate(concepts):
            mastery = float(mastery_vector[i])
            
            d = depths[i]
            if d not in level_counts: level_counts[d] = 0
            x_pos = level_counts[d] * 150 + (d % 2 * 75)
            y_pos = d * 100
            level_counts[d] += 1
            
            nodes.append({
                "id": str(i), # Use Index as ID for simplicity in edges
                "type": "default", # ReactFlow type
                "data": { 
                    "label": concept, 
                    "mastery": mastery,
                    "status": "mastered" if mastery > 0.8 else "in-progress" if mastery > 0.1 else "locked"
                },
                "position": { "x": x_pos, "y": y_pos }
            })
            
        # 3. Build Edges
        # adj[v][u] = 1 means u -> v
        for v in range(len(concepts)):
            for u in range(len(concepts)):
                if adj[v][u] > 0:
                    weight = 1.0 # Default/Attention
                    # If we had attention, we'd query it here.
                    # For now, thickness = base weight.
                    
                    edges.append({
                        "id": f"e{u}-{v}",
                        "source": str(u),
                        "target": str(v),
                        "animated": True,
                        "style": { "stroke": "#b1b1b7", "strokeWidth": 2 },
                    })
                    
        return Response({"nodes": nodes, "edges": edges}, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
