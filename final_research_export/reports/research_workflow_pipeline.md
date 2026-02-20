# Research Workflow Pipeline (Linear Flow)

This document maps the **exact sequential flow** of the MGKT system with a concrete example.

---

### The Pipeline Structure
$$ \text{Interaction} \rightarrow \text{Signal Processing} \rightarrow \text{MGKT Model} \rightarrow \text{Mastery Update} \rightarrow \text{Recommendation} $$

---

### Step 1: Learner Interaction
**Action**: Student ("Alex") attempts a **Coding Task** on the topic **"Loops"**.
*   **Behavior**:
    *   Submits code 3 times (2 Failures, 1 Success).
    *   Uses 1 Hint.
    *   Time taken: 150 seconds.

### Step 2: Signal Processing (Multisignal Extraction)
The system converts raw behavior into a **Multisignal Vector ($S_t$)**. The extraction logic depends on the Agent:

#### A. AgentTutor (The Conceptual Check)
*   **Structure**: 10 Conversations per Topic $\times$ 4 Quizzes each.
*   **Points**: 1 Point per Conversation (if $\ge 50\%$ correct).
*   **Example**: Student gets 3/4 correct.
    *   $y_t = 0.75$ (Sent to BKT as "Soft Success").

#### B. AgentCode (The Application Check)
*   **Formula**: Continuous Deduction.
    $$ y_t = \text{Ratio} - (0.01 \times \text{Attempts}) - (0.02 \times \text{Hints}) $$
*   **Example**: Student passes 5/5 tests, but uses 3 attempts and 1 hint.
    *   $y_t = 1.0 - 0.03 - 0.02 = \mathbf{0.95}$.

#### C. AgentDebug (The Reasoning Check)
*   **Structure**: 5 Questions (Bug Fixes).
*   **Formula**: Correct ($+1$) or Wrong Attempt (**$-0.1$ Penalty**).
*   **Example**: Student fixes bug on 2nd try (1 wrong attempt).
    *   $y_t = 1.0 - 0.1 = \mathbf{0.9}$.

### Step 3: MGKT Model (The Mathematical Update)
The core engine processes the signal ($y_t$) using **Three-Channel BKT** and **Graph Propagation**.

#### A. Local Mastery Update (BKT - Application Channel)
We update the probability $P(L_{Code})$ for the active concept "Loops".
*   **Parameters**: Code Mode ($P(G)=0.05, P(S)=0.10, P(T)=0.3$).
*   **BKT Formula**:
    $$ P(L_{Code} | y_t) = \frac{P(L) \cdot (1 - P(S))}{P(L) \cdot (1 - P(S)) + (1 - P(L)) \cdot P(G)} $$
*   **Result**: Prior ($0.40$) $\xrightarrow{\text{Update}}$ Posterior ($\mathbf{0.946}$).

#### B. Global Knowledge Propagation (GAT)
We propagate the new mastery to dependent nodes (e.g., "Functions").
*   **Formula**: $M(\text{Func}) \leftarrow M(\text{Func}) + \alpha \cdot (A_{Loops \to Func} \cdot M_{Total}(\text{Loops}))$.

### Step 4: Mastery State Update ($H_t$)
The System recalculates the **Total Mastery** using the Stratified Formula.
1.  **Update "Loops" Total**:
    $$ M_{Total} = (M_{Tutor} \times 0.25) + (M_{Code} \times 0.35) + (M_{Debug} \times 0.40) $$
    *   *Assume Tutor & Debug also completed*:
    *   $M_{Total} = (1.0 \times 0.25) + (0.946 \times 0.35) + (1.0 \times 0.40) = \mathbf{0.98}$.
2.  **Update Neighbor "Functions"**:
    *   **Readiness**: Jumps to $\mathbf{0.98}$ (Dependencies Met).

### Step 5: Recommendation Engine
The system re-evaluates the "Next Best Action" based on the new state.
1.  **Filter**: "Loops" is now $>0.85$ (Mastered) $\rightarrow$ Removed from candidates.
2.  **Rank**: "Functions" has max Readiness ($0.89$) and low Mastery ($0.10$).
3.  **Output**: **Recommend "Functions"**.
