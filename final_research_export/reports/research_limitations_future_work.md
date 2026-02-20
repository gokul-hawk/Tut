# Limitations & Future Work

Every research project has boundaries. This document prepares you to answer the "What didn't work?" and "What's next?" questions during your defense.

---

## 1. Limitations (The "Honesty" Section)

### 1.1 Scalability & Latency
*   **The Issue**: Our Graph Attention Network (GAT) propagates updates to *every* neighbor. In a small graph (50 nodes), this is instant ($<10ms$).
*   **The Bottleneck**: In a real-world curriculum with 10,000 concepts (e.g., K-12 Math), updating the entire graph after every quiz question would introduce noticeable latency.
*   **Defense**: "For this prototype, exact propagation was prioritized. In production, we would use **Subgraph Sampling** to only update the local neighborhood."

### 1.2 Dependency on Synthetic Data
*   **The Issue**: We used a "Graph-Constrained Random Walk" to generate student data because real-world dataset (like ASSISTments) valid for *multimodal* interactions (Code/Debug/Quiz) do not exist publicly.
*   **The Risk**: The model might be overfitting to our own "perfect logic" rather than messy human behavior.
*   **Defense**: "The synthetic data was rigorously constrained by causal rules. It serves as a Proof of Concept (PoC) for the *architecture*, not a claim of deployment-readiness."

### 1.3 Static Graph Structure
*   **The Issue**: We manually defined the prerequisites (Variables $\rightarrow$ Loops).
*   **The Risk**: If the teacher is wrong, the model is wrong. It cannot "discover" that *Recursion* actually requires *Stack Memory* if we didn't explicitly link them.
*   **Defense**: "Automated Graph Discovery was out of scope, but is our primary item for Future Work."

---

## 2. Future Work (The "Vision" Section)

### 2.1 Causal Graph Discovery (PC-Algorithm)
Instead of manually drawing arrows, we propose using **Causal Discovery Algorithms** (like PC or FCI) on the interaction logs to *learn* the prerequisite structure.
*   *Hypothesis*: The system might discover hidden dependencies (e.g., "Students who fail *Boolean Logic* almost always fail *While Loops*").

### 2.2 Latency-Aware Scoring
Currently, we only track *Correctness* and *Modality*. We plan to add **Response Time** as a signal.
*   *Idea*: A correct answer in 5 seconds is "Mastery". A correct answer in 5 minutes is "Struggle".

### 2.3 Cross-Domain Transfer
Can mastering *Physics* (Vectors) boost readiness in *Computer Science* (Arrays)?
*   We propose a **Heterogeneous Graph** linking concepts across different subjects to enable cross-disciplinary recommendation.

---

## Summary for Slides
| Limitation | Proposed Solution (Future Work) |
| :--- | :--- |
| **High Latency (Large Graphs)** | Subgraph Sampling / localized updates |
| **Manual Graph Definition** | Automated Causal Discovery (PC-Algorithm) |
| **Synthetic Data Bias** | Deployment in a live classroom (Pilot Study) |
