# MGKT Problem Formulation Inputs

Here are the specific inputs used in your research simulation, ready for your report.

## 1️⃣ Concept Space ($\mathcal{C}$)
*   **Count**: **50 Concepts** (Standard curriculum size for Introductory Python).
*   **Structure**: **Hierarchical** (e.g., `Variables` → `Control Flow` → `Loops` → `Functions`).

## 2️⃣ Knowledge Graph ($\mathcal{G}$)
*   **Graph Type**: **Directed Acyclic Graph (DAG)**.
*   **Edge Meaning**: **Prerequisite Only** ($A \to B$ means A is required for B).
    *   *Note*: While the graph edges are binary (exists/doesn't exist), the *GAT Attention Weights* ($W$) learn the *strength* of these dependencies during training.
*   **Multiple Parents**: **Yes**. (e.g., `Recursion` might depend on both `Functions` and `Conditionals`).

## 3️⃣ Interaction Types (Signals $\mathcal{S}$)
The exact list supported by MGKT:
*   [x] **Tutor conceptual Q&A** (Quiz/Chat)
*   [x] **Code writing** (Full program/Function)
*   [x] **Debugging** (Identify & Fix faulty line)

## 4️⃣ Outcome Representation
*   [x] **Binary correct / incorrect** ($Y \in \{0, 1\}$)
    *   *Crucial Detail*: While the *outcome* is binary, the *impact* is weighted by the signal type (e.g., specific Guess/Slip params).

## 5️⃣ Penalty Signals (Negative Evidence)
*   [x] **Repeated wrong compilation** (Counted as "Code Failure").
*   [x] **Guessing behavior** ( Implicitly handled: "Tutor Success" has high Guess Probability, minimizing mastery gain).
*   [x] **Timeout / skipping** (Treated as "Failure" in simulation).

## 6️⃣ Mastery State
*   **Representation**: **Continuous Probability** $[0, 1]$.
*   **Initial Mastery**: **Graph-based Prior** (Readiness Score). usage.
    *   *New Learners start at*: $R(Node) = Avg(Prerequisites)$.

## 7️⃣ Update Style
*   **Non-monotonic**: Mastery **can decrease** if a student fails a high-fidelity task (like Debugging), reflecting the discovery of a "hidden gap".

## 8️⃣ Cold-Start Handling
*   **Initialize using graph prerequisites**: A student who knows "Variables" is automatically initialized with non-zero readiness for "Loops".

## 9️⃣ Time Modeling
*   **Ignore time (sequence order only)**: The model uses discrete time steps $t$ ($t=1, t=2...$), not wall-clock timestamps.

## 🔟 Evaluation Context
*   **Is this simulation-based?**: **Yes**.
*   **No supervised training?**: **Mixed**.
    *   **BKT Component**: Unsupervised (Fixed Expert Parameters).
    *   **GAT Component**: **Supervised**. We trained the Graph Attention Weights ($W$) using the synthetic dataset to learn optimal propagation.
