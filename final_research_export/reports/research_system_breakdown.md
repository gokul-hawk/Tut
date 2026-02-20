# Research System Breakdown: MGKT (10-Point Spec)

This document answers your "10-Point Questionnaire" exactly as implemented in the codebase.

---

## 1. Input Representation (The Signals)
*What signals are you using?*
$$ S = \{ Correctness, InteractionType, HintsUsed, ResponseTime, TestCasesPassed \} $$
*   **Correct (0/1)**: Did they pass?
*   **Type (Categorical)**: {Quiz, Code, Debug} $\rightarrow$ Determines Weight.
*   **Hints (Integer)**: Count of hints used (Penalty Factor).
*   **Time (Float)**: Seconds taken (Used for "Rapid Guessing" penalty).
*   **Tests (Ratio)**: For Code, $Passed/Total$.

## 2. Concept Mapping
*One-to-One or Many-to-Many?*
*   **Primary**: **One-to-One** (1 Question $\rightarrow$ 1 Main Topic).
    *   *Reason*: To isolate the signal for BKT.
*   **Secondary (Implicit)**: Coding questions implicitly test prerequisites, but we attribute the score to the *target* node.

## 3. Graph Structure
*Do you have a concept graph?*
*   **Yes**.
*   **Nodes**: Concepts (Variables, Loops, Functions).
*   **Edges**: Prerequisite Relationships ($A \rightarrow B$).
*   **Source**: **Defined Manually** (Expert Knowledge).
    *   *Implementation*: Stored in `prerequisites.json` and loaded into Neo4j.

## 4. Mastery Representation
*How is knowledge represented?*
*   **Scalar Probability per Concept**.
$$ H_t = [P(Mastery_{Variables}), P(Mastery_{Loops}), \dots] $$
*   Each value is a float $\in [0.0, 1.0]$.
*   *Interpretation*: $0.2 = Unlearned$, $0.95 = Mastered$.

## 5. Base Model (Neuro-Symbolic)
*Are you using BKT?*
*   **Yes, as the Core Update Rule.**
*   **Neuro-Symbolic Twist**: We use the *structure* of BKT, but the *parameters* are dynamic.
*   **4 Parameters**:
    1.  **Prior $P(L_0)$**: Initial belief.
    2.  **Learn $P(T)$**: Transition probability.
    3.  **Guess $P(G)$**: Risk of false positive.
    4.  **Slip $P(S)$**: Risk of false negative.

## 6. Multisignal Adaptation (The Optimization)
*How do signals affect learning?*
We dynamically swap the BKT parameters based on the **Signal Source**:

| Signal Source | Action | BKT Modification |
| :--- | :--- | :--- |
| **Quiz (Tutor)** | Ambiguous | High Guess ($0.25$), Low Learn ($0.1$) |
| **Code (Apply)** | Standard | Low Guess ($0.05$), High Learn ($0.3$) |
| **Debug (Analyze)** | strong | **Zero Guess ($0.01$)**, Max Learn ($0.4$) |
| **Hint Usage** | **Penalty** | **Increase Guess ($P(G) \uparrow$)** (Massively reduces learning gain) |

## 7. Graph Propagation
*How does knowledge flow?*
*   **Technique**: **Heuristic Graph Attention (Inference-Only GAT)**.
*   **Logic**:
    1.  Compute Attention Score (Similarity) between Parent & Child.
    2.  If Parent improves, propagate a fraction of that gain to the Child.
    $$ Mastery_{Child} \leftarrow Mastery_{Child} + \alpha \cdot (Attention_{Score} \cdot Mastery_{Parent}) $$
*   *Result*: Mastering "Variables" boosts the readiness of "Loops".

## 8. Learning Process
*   **Online Learning** (Step-by-Step).
*   **Cycle**:
    1.  User acts (Answer/Code).
    2.  **BKT Update**: Update specific node $P(L)$.
    3.  **GAT Propagation**: Ripple effect to neighbors.
    4.  **Recommendation**: Re-sort candidates based on new state.

## 9. Objective Function
*What are we optimizing?*
*   **Maximize True Mastery Reliability**.
*   (We are not training a neural net with a loss function like `MSE`; we are optimizing the *decision boundaries* of the Expert System).

## 10. Output
*What does MGKT produce?*
1.  **Real-Time Mastery State**: The [0-1] vector for all concepts.
2.  **Readiness Score**: "Am I ready for $X$?" (Avg of ancestors).
3.  **Next Best Action**: The specific topic recommended next.

## 11. The "Concept Explorer" (Retroactive Decay Detection)
*How do you handle forgetting?*
*   **The Problem**: Standard BKT assumes a fixed "Forgetting Rate" ($P(F)$), which is often inaccurate.
*   **Our Solution**: Instead of *guessing* that a student forgot, we **Test It**.
*   **Mechanism**:
    1.  **Trigger**: If a student fails a "Child" topic (e.g., Loops), the system flags the "Parent" (Variables) as *At-Risk*.
    2.  **Action**: The "Concept Explorer" serves a Micro-Quiz on the Parent.
    3.  **Update**:
        *   If **Pass**: Parent Mastery is reinforced.
        *   If **Fail**: Parent Mastery is **Slashed** (e.g., $0.9 \rightarrow 0.4$).
*   **Result**: The graph self-corrects for "False Mastery" over time.

