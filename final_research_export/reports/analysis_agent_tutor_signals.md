# Analysis: AgentTutor Signal Gaps

We inspected the `TutorSession` model in `backend/chatbot/models.py`.

## 1. Current Implementation
The only signals currently tracked are:
```python
tutor_questions_asked = models.IntegerField(default=0)
tutor_questions_correct = models.IntegerField(default=0)
```
This allows for a simple **Accuracy Ratio** ($\frac{Correct}{Total}$), but nothing else.

## 2. Missing Signals (Promised in Research)
The Research Report claims BKT uses "Multisignal" inputs for the Tutor phase. However, the following are **MISSING**:

### A. Hint Usage
*   **Gap**: There is no field to track if the user asked for a hint during a quiz.
*   **Impact**: A student who answers correctly *after* a hint is treated the same as one who answered immediately. This inflates mastery.

### B. Response Time (Latency)
*   **Gap**: No timestamp tracking for question delivery vs. user response.
*   **Impact**: Cannot detect "Rapid Guessing" (answering in <2s) or "Struggle" (taking >60s).

### C. Question Taxonomy (Bloom's Level)
*   **Gap**: We treat all questions as generic "Tutor Questions".
*   **Impact**: We cannot differentiate between "Recall" (easy) and "Understand" (hard) to weight the BKT update.

## 3. Required Schema Update
To match the research, we need to upgrade `TutorSession` to store a log of interactions:

```python
interaction_log = [
  {
    "question_id": "...",
    "category": "recall",
    "hints_used": 1, 
    "time_taken_sec": 12,
    "is_correct": True
  },
  ...
]
```
This is required to calculate the **Penalized Score** defined in the report.
