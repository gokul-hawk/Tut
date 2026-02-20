from django.urls import path
from . import views


urlpatterns = [
    path("", views.tutor_chat, name="tutor_chat"), 
    path("summarize/", views.summarize_conversation, name="summarize_conversation"),
    path("generate_quiz/", views.generate_quiz, name="generate_quiz"),
    path("welcome/", views.welcome_message, name="welcome_message"),
    path("key_concepts/", views.get_key_concepts, name="get_key_concepts"),
    path("regenerate_visualization/", views.regenerate_visualization_view, name="regenerate_visualization"),
    path("reset_session/", views.reset_session, name="reset_session"),
    path("gkt/graph/", views.get_graph_data, name="get_graph_data"),
]