# MGKT System Architecture Workflow

This document maps the **Technical Architecture** of the framework, showing how components interact to produce adaptive learning.

---

### High-Level Architecture Diagram
```mermaid
graph TD
    User[Student (Frontend)] <-->|Interacts| UI[React Interace (Chat/Code/Debug)]
    
    subgraph "Application Layer (Django)"
        UI <--> API[API Gateway]
        API --> Orch[Orchestrator Agent]
        
        Orch -->|Selects| AT[AgentTutor]
        Orch -->|Selects| AC[AgentCode]
        Orch -->|Selects| AD[AgentDebug]
    end
    
    subgraph "Cognitive Layer (AI Services)"
        AT & AC & AD <-->|Prompting| LLM[Groq / Gemini 1.5]
        LLM -->|Generates| Content[Quizzes / Tasks / Bugs]
    end
    
    subgraph "State Layer (The Brain)"
        Orch -->|Sends Signals| Engine[MGKT Engine]
        
        Engine -->|Update| BKT[BKT Service (Local)]
        Engine -->|Propagate| GAT[GAT Service (Global)]
        
        BKT <--> DB1[(User State JSON)]
        GAT <--> DB2[(Neo4j Graph DB)]
    end
    
    subgraph "Decision Layer"
        Engine -->|New State| Rec[Recommendation Engine]
        Rec -->|Next Topic| Orch
    end
```

---

### Component Data Flow

#### 1. The Interactive Layer (Frontend)
*   **Role**: Capture raw user behavior.
*   **Components**: `AgentTutor.jsx`, `CodeEditor.jsx`, `Visualizer.jsx`.
*   **Data Sent**: Code, Test Results, Time, Hints.

#### 2. The Application Layer (Orchestrator)
*   **Role**: Route request to the correct Pedagogical Agent.
*   **Logic**:
    *   If `Mode == Tutor` $\rightarrow$ Invoke `AgentTutor`.
    *   If `Mode == Code` $\rightarrow$ Invoke `AgentCode`.

#### 3. The Cognitive Layer (Generative AI)
*   **Role**: Generate dynamic content on-the-fly.
*   **Input**: "Topic: Loops, Type: Debugging".
*   **Output**: JSON Object (Buggy Code + Test Cases).

#### 4. The State Layer (MGKT Engine)
*   **Role**: Update the student model.
*   **Process**:
    1.  **Signal Processing**: Convert `Code Execution` to `Score=0.95`.
    2.  **BKT Update**: Update `Loops` mastery.
    3.  **GAT Update**: Propagate to `Functions`.
    4.  **Storage**: Save to `user_state.json` and Neo4j.

#### 5. The Decision Layer (Recommender)
*   **Role**: Decide the next step.
*   **Input**: Updated Knowledge Graph.
*   **Logic**: Calculate Readiness ($Mean(Prereqs)$).
*   **Output**: "Next Topic: Functions".
