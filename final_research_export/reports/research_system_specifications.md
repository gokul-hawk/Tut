# MGKT System Specifications: Technical Blueprint

This document defines the exact technical configuration of your Multisignal Graph Knowledge Tracing (MGKT) system.

---

## 1. INPUT REPRESENTATION (Very Important)

👉 **What signals are you using for each student interaction?**

We use a **Multisignal Tuple** for every interaction event $E_t$:

$$ S = \{ R, T, C \} $$

*   **$R$ (Response Accuracy)**: Binary Correctness ($0$ or $1$).
    *   *We do not use continuous scores (0.7) to avoid ambiguity.*
*   **$T$ (Interaction Type)**: The pedagogical modality ($T \in \{ \text{Quiz}, \text{Code}, \text{Debug} \}$).
    *   *This is the core differentiator.*
*   **$C$ (Context)**: The specific Concept Node ID being attempted.

---

## 2. CONCEPT MAPPING

👉 **Does each question map to single or multiple concepts?**

*   **Mapping Strategy**: **Single Concept Dominance**.
    *   Each question $q$ is mapped to **one primary concept** $c_{primary}$.
*   **Reasoning**: To maintain graph differentiability. If a question maps to $\{c1, c2, c3\}$, failure is ambiguous (which one did they fail?).
*   **Example**:
    *   $q_{101}$ ("Fix the loop index") $\rightarrow$ `For_Loops`
    *   $q_{102}$ ("Declare an integer") $\rightarrow$ `Variables`

---

## 3. GRAPH STRUCTURE (CORE OF MGKT)

👉 **Do you have a concept graph?**

*   **Structure**: **Homogeneous Directed Acyclic Graph (DAG)**.
    *   **Nodes ($V$)**: Concepts (e.g., "Recursion").
    *   **Edges ($E$)**: Prerequisite Relationships ($A \rightarrow B$ means "A is required for B").
*   **Construction Method**: **Hybrid Construction**.
    *   **Level 1**: Manually defined "Skeleton" (Domain Expert / Syllabus).
    *   **Level 2**: Refined by **Causal Discovery** (PC-Algorithm) on student data (Future Work).

---

## 4. MASTERY REPRESENTATION

👉 **How are you representing student knowledge?**

*   **Representation**: **Probabilistic Scalar per Node**.
    *   Start State: $L_0 = 0.5$ (Uncertain) or Graph Prior (0.1 if deep in graph).
    *   Current State: $L_t \in [0.0, 1.0]$.
*   **Why not Vector Embeddings?**
    *   We need **Explainability**. A probability of $0.95$ clearly means "Mastered". An embedding vector `[-0.2, 0.4, ...]` is opaque to teachers.

---

## 5. BASE MODEL — BKT OR NOT?

👉 **Are you using Bayesian Knowledge Tracing (BKT) as base?**

*   **Architecture**: **Neuro-Symbolic Hybrid**.
*   **Local Update (Symbolic)**: We use **Standard BKT** parameters ($P(L_0), P(T), P(S), P(G)$) for the *local* node update.
*   **Global Update (Neural)**: We use **GAT (Graph Attention)** to *modify* the priors of neighboring nodes.

---

## 6. MULTISIGNAL ADAPTATION (Your Novelty 🔥)

👉 **How do signals affect learning?**

We **Dynamically Swap BKT Parameters** based on the signal type $T$:

| Signal Type ($T$) | Guess Probability $P(G)$ | Slip Probability $P(S)$ | Learning Rate $P(T)$ |
| :--- | :--- | :--- | :--- |
| **Quiz** (Tutor) | **High (0.25)** | High (0.15) | Low (0.10) |
| **Code** (Apply) | Medium (0.10) | Medium (0.10) | Medium (0.30) |
| **Debug** (Analyze) | **Low (0.01)** | **Low (0.05)** | **High (0.50)** |

*   **Logic**:
    *   If $T = \text{Debug}$ and Result = Correct: **Massive Mastery Gain**. (Because $P(G) \approx 0$).
    *   If $T = \text{Quiz}$ and Result = Correct: **Small Mastery Gain**. (Because they might have guessed).

---

## 7. GRAPH PROPAGATION

👉 **How should knowledge flow?**

*   **Mechanism**: **Weighted Graph Propagation (GAT-light)**.
*   **Formula**:
    $$ \text{Readiness}(B) = \sigma \left( \sum_{A \in Prereqs(B)} W_{AB} \cdot \text{Mastery}(A) \right) $$
*   **Direction**:
    *   **Forward Propagation**: Mastery of *Prerequisite* increases Readiness of *dependent*.
    *   **Backward Blocking**: Failure of *Prerequisite* locks the *dependent*.

---

## 8. LEARNING PROCESS

👉 **How does the system update over time?**

*   **Type**: **Online Learning** (Real-time).
*   **Sequence**:
    1.  **Interaction**: Student receives response $S = \{1, \text{Debug}, \text{Loops}\}$.
    2.  **Local Update**: $L_{loops} = BKT\_Update(L_{loops}, S)$.
    3.  **Global Propagate**: Neighbors (e.g., `Nested_Loops`) update their Readiness scores.
    4.  **Recommend**: System re-ranks the queue based on new scores.

---

## 9. OBJECTIVE FUNCTION

👉 **What are you optimizing?**

*   **Metric**: **Predictive Accuracy (RMSE)**.
*   **Goal**: Minimize the error between *Predicted Mastery* and *Actual Future Performance*.
    $$ \mathcal{L} = \sum ( \hat{y}_{t+1} - y_{t+1} )^2 $$
*   *Note: In the recommendation engine, we essentially optimize for "Zone of Proximal Development" (Readiness $\approx$ 1, Mastery $\approx$ 0).*

---

## 10. OUTPUT

👉 **What does MGKT produce?**

1.  **Student Model**: A dynamic Knowledge Graph where every node has a $(Mastery, Readiness)$ tuple.
2.  **Actionable Output**: A singe **Next Best Action** (Recommendation).
3.  **Alerts**: "Stuck" detection (if Mastery drops below threshold on a prerequisite).
