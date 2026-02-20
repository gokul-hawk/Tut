# Architecture FAQ: BKT vs. GAT & Recommendation Logic

This document answers the core questions:
1.  **Why do we need GAT?** (The "Cold Start" Problem)
2.  **What is the difference between BKT and GAT?** (Depth vs. Breadth)
3.  **How is "Readiness" calculated?** (The Math)
4.  **How is the next topic recommended?** (The Algorithm)

---

## 1. Why do we include GAT (Graph Attention)?
**The Problem:** Traditional models (like BKT/DKT) treat every topic as an **Isolated Island**.
*   If a student masters "Addition", BKT for "Multiplication" still starts at zero knowledge (0.5 prior).
*   The model "doesn't know" that Addition is required for Multiplication. It waits for the student to fail 5 times before realizing they aren't ready.

**The GAT Solution:** We use the Knowledge Graph structure to **propagate knowledge**.
*   **Mechanism:** When you master "Addition", the GAT sends a signal to "Multiplication" saying, *"Hey, the prerequisites are met! Increase the Readiness Score!"*
*   **Benefit:** This solves the **Cold Start Problem**. The model knows you are ready for advanced topics *before you even attempt them*.

---

## 2. The Distinct Purposes: BKT vs. GAT

| Component | Focus Dimension | Key Question It Answers | Metaphor |
| :--- | :--- | :--- | :--- |
| **BKT (Bayesian)** | **Depth (Time)** | *"Based on the last 5 attempts at **Loops**, do you understand **Loops**?"* | The **Microscope**. Looks deep at one specific skill over time. |
| **GAT (Graph)** | **Breadth (Structure)** | *"Since you know **Variables**, are you ready to learn **Loops**?"* | The **Map**. Looks wide at how skills connect to each other. |

**Synthesis:**
*   **BKT** updates the **Mastery Probability** ($P(L)$) of a single node based on performance (Debug/Code/Quiz).
*   **GAT** updates the **Readiness Score** ($R$) of *neighboring* nodes based on the graph topology.

---

## 3. How is "Readiness" Calculated?

**Target Concept ($C_i$)**: The topic we want to check (e.g., "Loops").
**Prerequisites ($P_i$)**: The parent nodes in the graph (e.g., "Variables", "Conditionals").

**The Formula:**
$$ Readiness(C_i) = \frac{1}{|P_i|} \sum_{j \in P_i} Mastery(Node_j) $$

**In Plain English:**
> "The Readiness Score of a topic is simply the **average mastery of all its prerequisites**."

*   **Example:**
    *   To learn "Loops", you need "Variables" (Score 0.9) and "Booleans" (Score 0.1).
    *   $Readiness("Loops") = (0.9 + 0.1) / 2 = 0.5$
    *   **Verdict:** You are **NOT** ready. (You need to master Booleans first).

---

## 4. How is the "Next Topic" Recommended?

The Recommendation Engine scans all potential topics to find the **Zone of Proximal Development (ZPD)**.

**Selection Logic (The 3 Filters):**

1.  **Filter Out Mastered**: Ignore any topic where Mastery > 0.85. (Don't teach what is already known).
2.  **Filter Out Frustration**: Ignore any topic where Readiness < 0.60. (Don't teach what is impossible).
3.  **Select the "Gap"**: From the remaining candidates, pick the one with the **Highest Readiness**.

**The Priority Algorithm:**
$$ Score = \langle Readiness \uparrow, CurrentMastery \downarrow \rangle $$
1.  **Priority 1: High Readiness.** (The "Capacity" Filter).
    *   We ALWAYS pick the topic you are most prepared for.
    *   If Topic A has Readiness 0.9 and Topic B has Readiness 0.6, **Topic A wins**.
2.  **Priority 2: Low Mastery.** (The "Necessity" Filter).
    *   If Topic A and Topic B *both* have Readiness 0.9...
    *   We pick the one where your Mastery is **Lower** (e.g., 0.1 vs 0.5).
    *   **Logic**: "Fill the biggest gap first."

---

## 5. How is the GAT Trained?

The Graph Attention Network (GAT) weights ($W$) are learned through a **Supervised Training Process** on our synthetic dataset.

**The Training Loop (Step-by-Step):**
1.  **Input:** A student's current mastery state ($H_t$) and the Graph Adjacency Matrix ($A$).
2.  **Forward Pass (Prediction):** The model predicts the student's success on the *next* attempted concept based on their neighbor's influence.
    $$ \hat{y}_{next} = H_{current} + (A \cdot H_{current} \cdot W) $$
3.  **Loss Function:** We compare the prediction $\hat{y}$ against the actual outcome $y$ (Pass/Fail) using **Mean Squared Error (MSE)**.
    $$ Loss = (\hat{y} - y)^2 $$
4.  **Optimization:** We use **Gradient Descent** to adjust the weight $W$. If the model over-predicted, we lower $W$; if it under-predicted, we raise it.
4.  **Optimization:** We use **Gradient Descent** to adjust the weight $W$. If the model over-predicted, we lower $W$; if it under-predicted, we raise it.
5.  **Result:** Over 50 epochs, the model learns the optimal $W$ (approx. 0.3) that best explains how much "Prerequisite Mastery" influences "Future Success".

---

## 6. Critique: Homogeneous vs. Heterogeneous Graphs

**The Critique:** "Other GNN models (like HGKT) use multiple node types (Questions, Students, Skills). We only use Topic Nodes. Is our GAT too simple?"

**The Defense:**
1.  **Purpose-Driven Design**: Our goal is **Prerequisite Propagation**. We want to answer: *"If I know A, do I know B?"* This relationship exists *between concepts*, not between students or questions. Therefore, a **Homogeneous Concept Graph** is the mathematically correct tool for this specific job.
2.  **Data Efficiency**: Adding "Student Nodes" or "Question Nodes" explodes the graph size.
    *   *Our Graph*: 50 Nodes (Curriculum).
    *   *Heterogeneous Graph*: 50 Skills + 1000 Students + 5000 Questions = 6000+ Nodes.
    *   **Result**: They need 100x more data to train. We can train on small classrooms.
3.  **Interpretability**: When our GAT says "Readiness increased", we know exactly why (The Prerequisite Score went up). In complex Heterogeneous graphs, signals mix unpredictably between students and questions, becoming a "Black Box" again.

**Conclusion**: We prioritized **Efficiency & Explainability** over Complexity.

---

## 7. Critique: "Is this just Level Order Traversal?"

**The Critique:** "It looks like you are just doing a Breadth-First Search (BFS) or Level Order Traversal. Why do you call it **'Dynamic'**?"

**The Defense:**
A "Static" curriculum (Level Order) would be: *Variables -> Conditionals -> Loops*. Always. For everyone.
Our system is **Dynamic** because it reacts to the student's *actual performance*:

1.  **Backtracking (The Failure Loop):**
    *   *Static:* If you fail "Loops", the system says "Next is Functions".
    *   *Dynamic (Ours):* If you fail "Loops", your Mastery drops. The system **halts** forward progress and forces you to retry or review. It *traverses backwards* to fill the gap.
2.  **Skipping (The Mastery Shortcut):**
    *   *Static:* You must do "Variables" even if you are an expert.
    *   *Dynamic (Ours):* If your initial assessment shows Mastery > 0.85, the system **deletes** it from the queue and immediately unlocks "Loops".
3.  **Parallel Choice (The Fork):**
    *   *Static:* Variables -> Conditionals -> Loops (One Path).
    *   *Dynamic (Ours):* If "Variables" unlocks *both* "Conditionals" (Readiness 0.9) and "Data Types" (Readiness 0.9), the system calculates which one you are *more* likely to succeed at based on your unique history, choosing the **Optimal Next Step** rather than a fixed one.

**Summary:** Level Order Traversal is the *Happy Path* for a perfect student. **Dynamic Recommendation** is how we handle the *messy reality* of real students who fail, skip, and fork.

---

## 8. Dynamic Recommendation: A Concrete Scenario (The "Alice vs. Bob" Example)

Imagine the curriculum structure:
`Variables (A)` -> `Loops (B)` -> `Functions (C)`

### Scene 1: The "Failure Loop" (Dynamic Backtracking)
*   **Student**: Alice
*   **Action**: Alice masters `Variables` (Score 0.9) and attempts `Loops`.
*   **Result**: She FAILS `Loops` completely (Score drops to 0.1).
*   **Static System (Level Order)**: "Okay, next topic is `Functions`." (Ignoring the failure).
*   **Dynamic System (Ours)**:
    1.  `Loops` Mastery drops to 0.1.
    2.  Recommendation Engine re-evaluates.
    3.  `Functions` Readiness drops (because it needs `Loops`).
    4.  **System Action**: It *stops* forward progress. It recommends `Loops` **AGAIN** (or a specific remediation sub-topic). It effectively says: *"You cannot pass until you fix this."*

### Scene 2: The "Fast Track" (Dynamic Skipping)
*   **Student**: Bob
*   **Action**: Bob takes a pre-test or demonstrates advanced knowledge in Chat.
*   **Result**: System detects `Variables` mastery = 0.95 and `Loops` mastery = 0.92.
*   **Static System (Level Order)**: "Welcome Bob. Let's start with `Variables`." (Boring!)
*   **Dynamic System (Ours)**:
    1.  Filters out `Variables` (Mastered).
    2.  Filters out `Loops` (Mastered).
    3.  **System Action**: Immediately recommends `Functions`.
    4.  **Result**: Bob saves 2 hours of boring work. **That is Dynamic.**

---

## 9. Critique: "What makes it Multi-Granular?"

**The Critique:** "You call it MGKT (Multisignal Graph KT). Is 'Multisignal' the same as 'Multi-Granular'?"

**The Defense:**
Yes, "Multi-Granular" refers to the system's ability to measure knowledge at **Different Resolutions**. We are not just checking "Pass/Fail" (Binary Granularity). We measure:

1.  **Coarse Granularity (The "What")**:
    *   **Signal**: *AgentTutor* (Quiz).
    *   **Resolution**: Low (Binary Concept Check).
    *   **Meaning**: "Does the student know the *definition*?"

2.  **Medium Granularity (The "How")**:
    *   **Signal**: *AgentCode* (Writing Code).
    *   **Resolution**: Medium (Syntax & Logic).
    *   **Meaning**: "Can the student *construct* the solution?"

3.  **Fine Granularity (The "Why")**:
    *   **Signal**: *AgentDebug* (Fixing Bugs).
    *   **Resolution**: High (Deep Semantic Understanding).
    *   **Meaning**: "Can the student *analyze* a subtle error?"

**Conclusion**: Most systems (DKT) only see the world in Black & White (Correct/Incorrect). Our system sees in **High Definition** (Definitional, Constructive, Analytical).

---

## 10. Critique: "Is it even possible to fail?"

**The Critique:** "In many AI tutors, if I get it wrong, it just gives me the answer and moves on. Can I actually *fail* a topic in your system?"

**The Defense:**
**Yes, absolutely.** In fact, our system is stricter than a human tutor.

1.  **The Mastery Threshold**: You only "Pass" a topic if your Mastery Probability > **0.85**.
    *   If you get 0.80, you fail.
    *   If you get 0.40, you fail hard.

2.  **The Blocking Mechanism (GAT)**:
    *   If you fail "Variables" ($L=0.2$), the graph propagates this low score to "Loops" ($R \approx 0.2$).
    *   The Recommendation Engine demands $R > 0.6$ for new topics.
    *   **Result**: "Loops" is **LOCKED**. You literally cannot proceed to the next chapter.

3.  **The Only Way Out**:
    *   The system will keep recommending "Variables" (or its prerequisites) until you demonstrate mastery > 0.85.
    *   There is no "Skip" button. You *must* learn it.

---

## 11. Critique: "So Depth is preferred over Breadth?"

**The Critique:** "Since you prioritize Low Mastery, does that mean the system forces me to go Deep (fix mistakes) before I can go Wide (learn new things)?"

**The Defense:**
**Yes, exactly.** This is a feature, not a bug.

1.  **The Persistence Rule**:
    *   If you have two "Ready" topics:
        *   Topic A: You failed it yesterday (Mastery 0.1).
        *   Topic B: You never tried it (Mastery 0.5 - Default).
    *   The system picks **Topic A**.
    *   **Why?** Because a "hole" in your foundation is more dangerous than an "unopened door".

2.  **The Pedagogical Philosophy**:
    *   **Breadth-First** (Standard LMS): "Just finish the checklist." (Promotes superficial skimming).
    *   **Depth-First** (MGKT): "Fix your knowledge gaps before you build on top of them." (Promotes Mastery).

**In short**: we prioritize **Repairing** over **Exploring**.







