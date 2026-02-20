from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from users.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from .services.orchestrator import MainAgentOrchestrator
from .models import AgentSession

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def main_agent_chat(request):
    """
    Main Agent Entry Point. Delegates to Orchestrator.
    """
    try:
        message = request.data.get("message", "")
        if not message:
            return Response({"error": "Message required"}, status=status.HTTP_400_BAD_REQUEST)
        
        orchestrator = MainAgentOrchestrator(request.user)
        result = orchestrator.process_message(message)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def report_success(request):
    """
    Endpoint for tools (Coding/Quiz/Debug) to report success.
    Now fully integrated with the Weighted Scoring Engine.
    """
    try:
        session = AgentSession.objects(user=request.user).first()
        tutor_session = None
        from chatbot.models import TutorSession
        try:
             tutor_session = TutorSession.objects.get(user_email=request.user.email)
        except: pass
        
        # --- SCORING ENGINE INTEGRATION ---
        from .services.scoring_engine import ScoringEngine
        scorer = ScoringEngine()
        
        # Identify Phase/Source
        source = request.data.get("source", "tutor")
        
        # 1. Fetch/Calculate Scores
        score_breakdown = {}
        
        # A. Understanding Phase (Tutor)
        # Fetch stats from TutorSession OR Request Payload (Quiz)
        quiz_stats = request.data.get("quiz_stats")
        if quiz_stats:
            # Direct Quiz Report (Overrides Session)
            tutor_score = scorer.calculate_quiz_score(quiz_stats)
            t_correct = quiz_stats.get('correct', 0)
            t_asked = quiz_stats.get('total', 0)
            print(f"Quiz Report Received: {quiz_stats} -> Score: {tutor_score}")
        else:
            # Fallback to Session Logic
            t_asked = getattr(tutor_session, "tutor_questions_asked", 0) if tutor_session else 0
            t_correct = getattr(tutor_session, "tutor_questions_correct", 0) if tutor_session else 0
            tutor_score = scorer.calculate_tutor_score(t_asked, t_correct)
        
        # B. Applying Phase (Code)
        # Fetch stats from Request Payload (Code)
        code_stats = request.data.get("code_stats")
        if code_stats:
            # Direct Code Report
            # Engine expects a list of questions, so we wrap our single session stat
            code_score = scorer.calculate_code_score([code_stats])
            print(f"Code Report Received: {code_stats} -> Score: {code_score}")
        else:
            # Fallback estimation (e.g. if skipped or legacy call)
            code_score = 0 
        
        # C. Analysis Phase (Debug)
        debug_stats = request.data.get("debug_stats")
        debug_reasoning = request.data.get("debug_reasoning", "full" if source == "debug" else "none")

        if debug_stats:
            # Direct Debug Report
            debug_score = scorer.calculate_debug_score(debug_stats)
            print(f"Debug Report Received: {debug_stats} -> Score: {debug_score}")
        else:
            # Fallback Legacy
            # If source is debug but no stats, assume full pass (legacy behavior) or 0? 
            # Existing code assumed 100 if source==debug.
            debug_score = scorer.calculate_debug_score(debug_reasoning)

        # --- AGGREGATE ---
        # Note: If we are in 'Tutor' phase, we might only have Tutor Score.
        # But for 'Mastery', we might accumulate?
        # For this turn-based system, let's treat the 'Source' as the active phase contributing to the plan.
        
        final_score = scorer.aggregate_final_score(tutor_score, code_score, debug_score)
        
        print(f"--- SCORE REPORT [{source.upper()}] ---")
        print(f"Understanding (Tutor): {tutor_score} (Stats: {t_correct}/{t_asked})")
        print(f"Applying (Code):       {code_score}")
        print(f"Analysis (Debug):      {debug_score}")
        print(f"FINAL WEIGHTED SCORE:  {final_score}")
        print("-----------------------------------")

        # --- BKT UPDATE ---
        from chatbot.services.gkt_model import GKTModel
        gkt = GKTModel()
        req_topic = request.data.get("topic") or (session.current_topic if session else None)
        
        if req_topic:
            # We use the source type to pick the reliability params
            # EFFICIENCY THRESHOLD LOGIC: Score >= 80 is a "Success" for BKT
            
            # CRITICAL FIX: Use component score, not weighted final score
            if source == "tutor":
                signal_score = tutor_score
            elif source == "code":
                signal_score = code_score
            elif source == "debug":
                signal_score = debug_score
            else:
                signal_score = final_score

            is_mastery_signal = float(signal_score) >= 80.0
            gkt.update(request.user.email, req_topic, is_correct=is_mastery_signal, source_type=source)

        # ------------------------------------------------------------------
        # SCENARIO A: INDEPENDENT MODE (No Active Plan)
        # ------------------------------------------------------------------
        if not session or not session.current_plan:
            current_topic = session.current_topic if session else "General"
            
            # State Machine: Quiz -> Tutor -> Code -> Debug -> Dashboard
            if source == "quiz":
                reply_text = f"Diagnosis complete! Let's dive into the theory of **{current_topic}**."
                action_view = "tutor"
            elif source == "tutor":
                reply_text = f"Theory on **{current_topic}** covered. Score: {tutor_score:.1f}. Time to write some code!"
                action_view = "code"
            elif source == "code":
                reply_text = f"Coding challenge passed! Score: {code_score}. Now let's fix a bug."
                action_view = "debugger"
            elif source == "debug":
                reply_text = f"Excellent! Final Weighted Score: **{final_score}**. Returning to dashboard."
                action_view = "dashboard"
            else:
                reply_text = f"Step completed. Continuing with **{current_topic}**."
                action_view = "tutor" 

            result = {
                "reply": reply_text,
                "action": {
                    "type": "SWITCH_TAB",
                    "view": action_view,
                    "data": {"topic": current_topic}
                }
            }
            
            if session:
                session.chat_history.append({"sender": "bot", "text": reply_text})
                session.save()
                
            return Response(result, status=status.HTTP_200_OK)

        # ------------------------------------------------------------------
        # SCENARIO B: ACTIVE PLAN MODE
        # ------------------------------------------------------------------
        
        # 1. Complete current step
        completed_step = session.current_plan.pop(0)

        # 2. Capture Failed Topics (if any)
        failed_topics = request.data.get("failed_topics", [])
        if failed_topics:
            session.failed_prereqs = failed_topics
        else:
            session.failed_prereqs = [] 

        session.last_step_result = {
            "step": completed_step, 
            "status": "completed", 
            "failed_topics": failed_topics,
            "score": final_score  # Store the score!
        }
        session.save()
        
        # 3. Trigger next step immediately via Orchestrator
        orchestrator = MainAgentOrchestrator(request.user)
        msg = f"Step {completed_step.get('topic')} completed. Score: {final_score}."
        
        if failed_topics:
            safe_topics = [str(t) for t in failed_topics]
            msg += f" User FAILED prerequisites: {', '.join(safe_topics)}."
            
            # Re-queue current step to preserve flow
            session.current_plan.insert(0, completed_step)
            session.save()
            
            # Direct switch to Tutor for Revision
            from chatbot.services.persistent_tutor import start_new_topic
            topic = failed_topics
            start_res = start_new_topic(request.user, topic, is_revision=True)
            
            reply_text = f"Prerequisite failure detected. Let's do a quick revision of **{topic}**."
            session.chat_history.append({"sender": "bot", "text": reply_text})
            session.save()
            
            result = {
                "reply": reply_text,
                "action": {
                    "type": "SWITCH_TAB",
                    "view": "tutor",
                    "data": {"topic": topic, "initialMessage": start_res["reply"]}
                }
            }
            return Response(result, status=status.HTTP_200_OK)
            
        else:
             # PROMOTION LOGIC based on Score
             # If just finished Code, check if we need Debug or Promote
             if source == "code":
                 decision = scorer.determine_promotion(final_score) # Uses aggregate, but mainly code influence
                 if decision == "DEBUG":
                      msg += " (Review suggested: Debugging)"
                 elif decision == "REMEDIATE":
                      msg += " (Score too low - Remediation)"
            
             msg += " User PASSED."
             result = orchestrator.advance_plan(msg)
             return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    """
    Returns the persistent chat history for the user's Agent Session.
    """
    try:
        session = AgentSession.objects(user=request.user).first()
        if not session:
             return Response([], status=status.HTTP_200_OK)
             
        # Return last 50 messages strictly
        return Response(session.chat_history[-50:], status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from chatbot.services.groq_service import GroqService 
groq_service = GroqService()

from Code.models import UserQuestion

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def welcome_message(request):
    """
    Main Agent Welcome.
    """
    user = request.user
    
    # 1. Get Context from Session & Graph
    try:
        session = AgentSession.objects(user=user).first()
        current_topic = session.current_topic if session else "General"
    except:
        current_topic = "General"
        
    from chatbot.services.recommendation_service import RecommendationService
    rec_service = RecommendationService()
    
    # Ask Brain for the absolute best next step
    recommended_topic = rec_service.get_next_best_step(user.email, current_topic)
    
    if not recommended_topic:
        recommended_topic = "Python Basics"

    # Dynamic Conversational Prompt for Main Agent
    prompt = f"""
    You are the Main Orchestrator of CobraTutor.
    User: {user.username}
    Current Focus: {current_topic}
    AI Recommendation: {recommended_topic}
    
    Task:
    Generate a welcome message that proactively pushes the user towards the recommended topic.
    
    Structure (Strictly follow this layout):
    "Hi {user.username}! 🧠 I've analyzed your Knowledge Graph.
    
    I strongly recommend we focus on: **{recommended_topic}**.
    
    Here is the optimal plan:
    - 📖 **Theory**: Master the concepts of {recommended_topic}.
    - 💻 **Code**: Solve a challenge on {recommended_topic}.
    - 🐞 **Debug**: Fix a broken implementation.
    
    Shall we start with the Theory?"
    
    Guidelines:
    - Be encouraging but authoritative (you are the expert AI).
    - If the recommendation is specific, hype it up!
       
    Output strictly JSON:
    {{
      "message": "..."
    }}
    """
    try:
        response_text = groq_service.generate_content(prompt)
        import re, json
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
             # Fallback
             data = {
                 "message": f"Hi {user.username}! 🧠 I've analyzed your Knowledge Graph.\n\nI strongly recommend we focus on: **{recommended_topic}**.\n\nShall we start?"
             }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            "message": f"Hi {user.username}! Ready to learn **{recommended_topic}**?"
        }, status=status.HTTP_200_OK)
