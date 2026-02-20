# Individual Scoring Mechanisms: The "Three-Agent" Logic

This document defines the exact scoring algorithm used by each pedagogical agent before the signal is sent to the BKT Engine.

**Note on Precision**: All Agents calculate scores as **High-Precision Decimals** (e.g., $0.63, 0.34$) to ensure granular differentiation. These decimals are then thresholded or used as "Soft Evidence" for the BKT update.


---

## 1. AgentTutor (The Meaning Check)
**Role**: Assess Conceptual Knowledge.
**Session Structure**:
*   A Topic consists of **10 Conversations**.
*   Each Conversation has **4 Quiz Questions**.
*   **Total Points**: $10 \times 4 = 40$ Points.
**Scoring**:
*   Correct: $+1$.
*   Incorrect: $0$ (or negative if strict mode).

## 2. AgentCode (The Implementation Check)
**Role**: Assess Application.
**Scoring Formula** (Continuous Deduction):
$$ Score = Score_{Base} - (Attempts \times 0.01) - (Hints \times 0.02) $$
*   **Base**: Ratio of passed test cases.
*   **Penalty**: Small deductions for inefficiency (-0.01) and assistance (-0.02).

## 3. AgentDebug (The Analysis Check)
**Role**: Assess Deep Understanding (Fixing Bugs).
**Session Structure**: **5 Questions** per session.
**Scoring**:
*   **Correct Fix**: $+1$ Point.
*   **Wrong Attempt**: **-0.1 Penalty** per failed submission.
*   **Reasoning**: "You must reason explicitly before fixing. Trial-and-error is penalized."
*   **BKT Confidence**: **Highest ($P(G)=0.01$)**.

---

## Summary Table

| Agent | Input Typ | Scoring Formula | Pass Threshold | BKT Reliability |
| :--- | :--- | :--- | :--- | :--- |
| **AgentTutor** | Choices | $\frac{Correct}{Total}$ | $\ge 0.5$ | Low ($P(G)=0.25$) |
| **AgentCode** | Code | $\frac{Tests_{Passed}}{Tests_{Total}}$ | $= 1.0$ | Medium ($P(G)=0.10$) |
| **AgentDebug** | Code Edit | Binary Fix | True | **High** ($P(G)=0.01$) |

---

## 4. Negative Scoring & Penalties (AgentCode Specific)
You have implemented a **Granular Negative Grading System** for the Coding Phase to discourage "Gaming the System".

### A. The "Cost of Help" (Hint Penalty)
*   **Mechanism**: Dynamic deduction based on dependency.
*   **Penalty**: **-2 Points per Hint**.
*   **Cap**: Maximum deduction of **-20 Points**.
*   **Logic**: "Small nudges are acceptable, but reliance on the AI for every step indicates a lack of mastery."
*   **BKT Effect**: Each hint incrementally raises the Guess Parameter ($P(G)$), reducing the final mastery update.

### B. The "Cost of Failure" (Wrong Test Cases)
*   **Mechanism**: Deduction for trial-and-error submissions.
*   **Penalty**: **-1 Point per Failed Test Case**.
*   **Logic**: "Brute-forcing the solution is discouraged. Efficiency matters."
*   **BKT Effect**: Reduces the confidence of the success signal.

---

## 5. Negative Scoring (AgentTutor Specific)
To prevent "guess spamming" in Multiple Choice Quizzes, we apply:

### A. The "Wrong Answer" Penalty
*   **Mechanism**: Standard negative marking.
*   **Penalty**: **-0.25 Points** (for a 1-point question).
*   **Logic**: Discourages random guessing. "If you don't know, skip it (or review concepts) rather than guessing."
*   **Impact**: A student who guesses blindly on 4 questions will likely end up with a score of 0 or negative, rather than the expected +1 from pure probability.

### B. The "Rapid Guessing" Penalty
*   **Mechanism**: Time-based heuristic.
*   **Trigger**: Answering in $< 2$ seconds.
*   **Penalty**: **-0.5 Points** (Severe).
*   **Logic**: "You cannot read and process a complex question in 2 seconds. This is treated as spam/gaming."


---

## 4. Negative Scoring & Penalties (AgentCode Specific)
The system uses a **Deduction-Based Continuous Scoring** model. A student cannot "fail" in a binary sense; instead, their **Quality of Success** is degraded by inefficiencies.

### The Granular Formula
$$ Score_{Final} = Score_{Base} - P_{Attempts} - P_{Hints} $$

Where:
1.  **$Score_{Base}$**: Ratio of Passed Test Cases (e.g., $1.0$ for all passed).
2.  **$P_{Attempts}$**: **-0.01** per failed attempt (Max Deduction: **-0.1**).
3.  **$P_{Hints}$**: **-0.02** per hint used (Max Deduction: **-0.2**).

### Example Scenario
*   Student passes all tests ($1.0$).
*   But took 5 tries ($5 \times 0.01 = -0.05$).
*   And used 3 hints ($3 \times 0.02 = -0.06$).
*   **Final Score**: $1.0 - 0.05 - 0.06 = \mathbf{0.89}$.

### BKT Impact
This scalar score ($0.89$) is passed to the BKT Engine as **Soft Evidence** (or Probability of Mastery), rather than a hard `1` or `0`.
*   High Score ($0.9$) $\rightarrow$ Strong Mastery Increase.
*   Low Score ($0.3$) $\rightarrow$ Weak/Negligible Increase.

---

## 5. Composite Mastery Logic (The "Stratified" Model)
Unlike traditional BKT which tracks a single probability ($0 \to 1$), MGKT treats Mastery as the **Sum of Three Components**. A student cannot achieve $100\%$ mastery using only one signal type.

### The "Full Proficiency" Formula
$$ Mastery_{Total} = (S_{Tutor} \times 0.25) + (S_{Code} \times 0.35) + (S_{Debug} \times 0.40) $$

### The Stratification Limits
1.  **Layer 1: Understanding (Tutor)**
    *   **Max Contribution**: **0.25**.
    *   *Constraint*: You can solve 100 quizzes, but your mastery for "Loops" will never exceed 0.25.
2.  **Layer 2: Application (Code)**
    *   **Max Contribution**: **0.35**.
    *   *Constraint*: Writing perfect code adds +0.35, pushing Total Mastery to **0.60** (0.25 + 0.35).
3.  **Layer 3: Analysis (Debug)**
    *   **Max Contribution**: **0.40**.
    *   *Constraint*: Debugging is the final "Proof of Depth", unlocking the final 40% to reach **1.0**.

### Why?
This ensures a student is **Multimodal**. They *must* talk, code, and debug to be considered a Master.


