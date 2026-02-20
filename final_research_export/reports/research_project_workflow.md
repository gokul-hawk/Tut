# MGKT Project Workflow: The "Life of a Student Interaction"

This document details the step-by-step workflow of the system, from a student logging in to receive their next recommendation.

---

## 1. The High-Level Flow (Textual Diagram)

```mermaid
graph TD
    A[Student Login] --> B{Is New Student?}
    B -- Yes --> C[Cold Start Initialization]
    B -- No --> D[Load Existing Profile]
    
    C --> E[Assessment / Graph Prior]
    D --> E
    
    E --> F[Recommendation Engine (ZPD Selection)]
    F --> G[Select Concept $C_{next}$]
    
    subgraph "The Mastery Cycle (Three-Stage)"
        G --> H[Phase 1: AgentTutor]
        H -->|Understand (Quiz)| H_Success{Pass?}
        H_Success -- Yes --> I[Phase 2: AgentCode]
        H_Success -- No --> H_Fail[Remediation]
        
        I -->|Apply (Code)| I_Success{Pass?}
        I_Success -- Yes --> J[Phase 3: AgentDebug]
        I_Success -- No --> I_Fail[Hint/Retry]
        
        J -->|Analyze (Fix Bug)| J_Success{Pass?}
    end
    
    J_Success -- Yes --> K[Mastery Achieved!]
    K --> L[Update Knowledge Graph]
    L --> F
```

---

## 2. Detailed Workflow Steps

### Step 1: Initialization (Student Entry)
*   **Trigger**: Student logs into the system.
*   **Action**:
    *   **New Student**: The system initializes a latent mastery vector $\theta$.
    *   **Graph Prior**: The Knowledge Graph instantly calculates the **Readiness Score** for every node based on the empty state.
    *   **Result**: Foundation topics (Root Nodes) have $Readiness=1.0$.

### Step 2: The Recommendation Engine (Selection)
*   **Trigger**: System needs to show the next task.
*   **Logic**:
    1.  **Filter**: Remove topics with Mastery $> 0.85$.
    2.  **Filter**: Remove topics with Readiness $< 0.60$.
    3.  **Sort**: Rank remaining candidates by **Max Readiness**.
    4.  **Tie-Breaker**: Pick Lowest Current Mastery (Gap Filling).
*   **Output**: The system selects the optimal concept $C_{next}$.

### Step 3: The Three-Stage Mastery Cycle
Instead of a single interaction, the student progresses through three distinct agents for the selected concept:

#### Phase A: Understanding (AgentTutor)
*   **Goal**: Prove conceptual knowledge.
*   **Action**: Socratic Dialogue + Conceptual Quiz.
*   **Pass Condition**: Correctly answers quiz.
*   **Update**: Local BKT Update (Small Mastery Gain).

#### Phase B: Application (AgentCode)
*   **Goal**: Prove implementation skill.
*   **Action**: Write code to solve a problem regarding $C_{next}$.
*   **Pass Condition**: Code compiles and passes test cases.
*   **Update**: Local BKT Update (Medium Mastery Gain).

#### Phase C: Analysis (AgentDebug)
*   **Goal**: Prove deep understanding.
*   **Action**: Fix a broken code snippet provided by the system.
*   **Pass Condition**: Successfully identify and resolve the bug.
*   **Update**: Local BKT Update (**High Mastery Gain**).

### Step 4: System Integration (MGKT Core)
*   **Global Propagation (GAT)**:
    *   Only after passing Phase C (Debugging) is the concept considered fully "Mastered".
    *   The high-fidelity mastery signal propagates to neighbor nodes, unlocking new ZPD candidates.

### Step 5: Loop
*   The system returns to **Step 2**, now with expanded options.

