from django.db import models
from django.conf import settings

class TutorSession(models.Model):
    STATUS_CHOICES = [
        ("IDLE", "Idle"),
        ("TEACHING", "Teaching"),
        ("AWAITING_ANSWER", "Awaiting Answer"),
        ("AWAITING_SWITCH_CONFIRMATION", "Awaiting Switch Confirmation"),
        ("AWAITING_PLAN_APPROVAL", "Awaiting Plan Approval"),
    ]

    # Storing user_id as string because User model is MongoDB (non-relational mixed with SQL)
    user_email = models.EmailField(unique=True, null=True, blank=True) 
    # We use email as the unique identifier since ObjectIds might be tricky to manage in mixed queries
    current_topic = models.CharField(max_length=255, blank=True, null=True)
    subtopics = models.JSONField(default=list, blank=True)  # List of strings
    current_index = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="IDLE")
    switch_topic_buffer = models.CharField(max_length=255, blank=True, null=True) # Stores the proposed new topic while awaiting confirmation
    last_question = models.TextField(blank=True, null=True) # Stores the last question asked by the bot for context
    
    # metrics for Scoring Engine (Understanding Phase)
    tutor_questions_asked = models.IntegerField(default=0)
    tutor_questions_correct = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.current_topic} ({self.status})"

