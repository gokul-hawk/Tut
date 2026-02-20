# MGKT System: End-to-End Working Example

This document provides a concrete, step-by-step walkthrough of the entire system for a single interaction cycle.

---

### The Scenario
*   **Student**: "Alex"
*   **Current State**:
    *   **Variables**: Mastered ($P(L) = 0.95$).
    *   **Loops**: Unlearned ($P(L) = 0.40$).
    *   **Functions**: Unlearned ($P(L) = 0.10$).

---

### Step 1: Recommendation Engine (The Decision)
The system evaluates candidates for the next task.
1.  **Filter**: "Variables" is excluded ($>0.85$).
2.  **Readiness Calculation**:
    *   **Loops**: Requires "Variables" (0.95). $\text{Readiness} = 0.95$.
    *   **Functions**: Requires "Loops" (0.40). $\text{Readiness} = 0.40$.
3.  **Selection**: "Loops" has High Readiness (0.95) and Low Mastery (0.40). It is in the **ZPD**.
    *   **Selected Concept**: `Loops`.

### Step 2: Task Generation (AgentCode)
The Orchestrator invokes **AgentCode** to test "Application" skills (Bloom's Taxonomy).
*   **Prompt**: *"Generate a competitive programming question for 'Loops'."*
*   **Output**:
    *   **Problem**: "Write a function to sum all even numbers from 1 to N."
    *   **Test Cases**: 5 Hidden Cases.

### Step 3: Learner Interaction
Alex attempts the problem.
*   **Action**: Writes a `for` loop but forgets to increment proper step or check modulo correctly.
*   **Submission 1**: Fails. (Attempt 1).
*   **Action**: Asks for a **Hint**. ("Use `range(start, stop, step)`").
*   **Submission 2**: Fails. (Attempt 2).
*   **Submission 3**: Passes!

### Step 4: Signal Extraction ($S_t$)
The system captures the raw behavioral session.
*   **Type**: `Code`
*   **Test Cases Passed**: $5/5$ (Eventually passed).
*   **Attempts**: $3$ (2 Failed).
*   **Hints Used**: $1$.
*   **Time**: $150s$.

### Step 5: Scoring (The Deduction Logic)
We calculate the **Quality of Success** ($y_t$) using the deduction formula:

$$ y_t = \text{Base} - (0.01 \times \text{Attempts}) - (0.02 \times \text{Hints}) $$

*   **Base**: $1.0$ (All tests passed).
*   **Penalty (Attempts)**: $3 \times 0.01 = 0.03$.
*   **Penalty (Hints)**: $1 \times 0.02 = 0.02$.
*   **Final Score**: $1.0 - 0.03 - 0.02 = \mathbf{0.95}$.

### Step 6: Neuro-Symbolic BKT Update
We update the mastery for "Loops".
*   **Parameters** (for `Code`): High Learn ($P(T)=0.3$), Low Guess ($P(G)=0.05$).
*   **Evidence**: $y_t = 0.95$ (Strong Semantic Success).
*   **Update**:
    *   Prior: $0.40$.
    *   Posterior (after evidence): $\approx 0.85$.
    *   Transition (learning step): $\approx 0.89$.
*   **New State**: $M(\text{Loops}) = 0.89$.

### Step 7: Graph Propagation (GAT)
The mastery of "Loops" ($0.89$) ripples forward to its dependent: **Functions**.
*   **Logic**: "Functions" requires "Loops".
*   **Before**: $M(\text{Functions}) = 0.10$.
*   **Readiness Update**: Since Prereq (Loops) is now Mastered, the **Readiness** index for "Functions" jumps from $0.40$ to $0.89$.
*   **Impact**: "Functions" is now unlocked as a candidate for the next cycle.

### Step 8: The Concept Explorer (Safety Check)
*   **Trigger**: If Alex had *failed* Step 3 badly (e.g., Score 0.2), the system would have flagged "Variables" (the parent) as *At-Risk*.
*   **Action**: It would immediately inject a "Variables" micro-quiz to check for **Retroactive Decay**.
*   *(In this successful scenario, this step is skipped).*

---

### Final Outcome
*   **Alex** has mastered **Loops**.
*   **System** has unlocked **Functions**.
*   **Next Recommendation**: **Functions**.
