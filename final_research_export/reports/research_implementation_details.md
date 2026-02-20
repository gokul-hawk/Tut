# Research Implementation Details (Technical Cheat Sheet)

This document provides the exact technical answers for your defense questionnaire, based on the codebase analysis.

---

## 1. System Type (Implementation)
*   **Answer**: **Full End-to-End System**.
*   **Architecture**:
    *   **Frontend**: React.js (Interactive UI, Agent Chat, Code Editor).
    *   **Backend**: Django (API, Orchestrator).
    *   **AI Service**: Python `services/` module (BKT, GAT, Neo4j, LLM).

## 2. Data Flow (Input Source)
*   **Answer**: **Real-Time Interactive Stream**.
*   **Flow**:
    1.  User interacts with Frontend (Answer Quiz / Run Code).
    2.  Frontend sends JSON payload to Django API (`/api/submit/`).
    3.  Django routes data to `GKTService.update_mastery()`.
    4.  BKT Service computes posterior probability.
    5.  GAT Service propagates updates to Neo4j/State File.

## 3. Signal Extraction
*   **Answer**: **Deterministic Rule-Based Extraction**.
*   **Formulas**:
    *   **Correctness (Quiz)**: `1.0 if Option == Correct else 0.0`
    *   **Correctness (Code)**: `(Passed/Total) - (Hints*0.02) - (Attempts*0.01)`
    *   **Response Time**: `EndTime - StartTime` (seconds)
    *   **Hint Usage**: `Count(Hint_Requests)`
    *   **Interaction Type**: `Enum("quiz", "code", "debug")`

## 4. BKT Implementation
*   **Storage**: **Hybrid (JSON + In-Memory)**.
    *   *Implementation*: `state_vector = self.user_states[email]` (Dictionary of Lists).
    *   *Persistence*: Serialized to `gkt_state.json`.
*   **Parameters**: **Dynamic & Context-Aware**.
    *   *Not Fixed*: We swap $(P(G), P(S), P(T))$ based on `InteractionType` (See Methodology).
    *   *Init*: Masteries initialized to $0.1$ (Prior).

## 5. Graph Storage
*   **Storage**: **Neo4j Graph Database**.
    *   *Role*: Stores static structure (Nodes `(:Concept)` and Edges `[:REQUIRES]`).
    *   *Runtime*: Loaded into `self.adj_matrix` (NumPy) for fast matrix operations.
*   **Size**: Scalable (Currently seeded with ~50 core Python concepts, but supports thousands).

## 6. Graph Propagation Logic (GAT)
*   **Logic**: **Heuristic Graph Attention (Inference-Only)**.
*   **Formula**:
    $$ H_{next} = H_{current} + \alpha \cdot (A \cdot H_{current}) $$
    *   *Implementation*: `neighbor_signal = np.dot(adj_matrix, mastery_vector)` via `GKTService.get_recommendations`.
    *   *Weighting*: $\alpha = 0.5$ (`self.W_prop`).

## 7. Recommendation Engine
*   **Logic**: **ZPD Utility Function**.
*   **Parameters**:
    *   **Mastery Threshold ($\theta$)**: **0.85** (If mastery > 0.85, do not recommend).
    *   **Readiness ($\delta$)**: No hard threshold; we sort by `DESC(Readiness)`.
    *   **Formula**:
        $$ Score = (Readiness \times 0.5) + ((1.0 - Mastery) \times 0.2) $$
        *(We prioritize Readiness, but verify the student doesn't already know it)*.

## 8. Task Generation & Prompt Crafting
*   **Method**: **Dynamic LLM Generation (RAG-lite)**.
*   **Engine**: **Groq (Llama 3 / Mixtral)** or **Gemini 1.5 Pro**.
*   **Process**:
    1.  **Context Retrieval**: System identifies the target concept (e.g., "Recursion").
    2.  **Prompt Assembly**: A structured system prompt is injected with the concept.
    3.  **JSON Enforcement**: The prompt strictly demands a JSON schema for machine parsing.

### A. Quiz Generation Prompt
```text
"You are an expert Python educator.
Generate exactly 2 unique multiple-choice questions on the topic: '{topic}'.
Difficulty: beginner to intermediate.
Output JSON format:
[
  {
    'question': 'What is X?',
    'options': ['A', 'B', 'C', 'D'],
    'correct_answer': 'A'
  }
]"
```

### B. Coding Task Prompt
```text
"Generate a unique competitive programming question on the topic: {topic}.
The output should be in strict JSON format:
{
  'question': 'Problem Description...',
  'test_cases': [
    {'input': '...', 'expected': '...'}
  ]
}
### C. Pedagogical Logic (Bloom's Taxonomy)
The system does not just "generate questions"; it targets specific cognitive levels:

*   **AgentTutor (Quiz)**: Targets **Remember & Understand**.
    *   *Context*: "Based on the user's current conversation/confusion."
    *   *Goal*: Validating the user *knows* the concept.
*   **AgentCode (Coding)**: Targets **Apply & Analyze**.
    *   *Context*: "Situation-Based Application."
    *   *Goal*: Ensuring the learner knows **How to Implement** (Procedural) and **When to Use** (Conditional/Transfer) the concept in different problems.
    *   *Prompt Strategy*: We explicitly ask for "Competitive Programming" style questions to force application in novel contexts, not just syntax recall.



## 9. Feedback Loop
*   **Frequency**: **Real-Time (Online Update)**.
*   **Cycle**:
    *   **Immediate**: After *every single* question/submission.
    *   **Why**: To adapt the *very next* recommendation instantly.
