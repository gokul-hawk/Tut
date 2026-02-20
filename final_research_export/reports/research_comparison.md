# Comparative Analysis: Advantages of the Neuro-Symbolic Architecture

Our proposed **Multisignal Graph Knowledge Tracing (MGKT)** model addresses critical limitations in existing Knowledge Tracing literature by synthesizing symbolic provenance (BKT) with diverse evidence signals.

## 1. Baseline Models for Comparison

To validate the efficacy of our approach, we benchmark against three established paradigms in Knowledge Tracing:

### A. Standard BKT (Corbett & Anderson, 1995)
*   **Architecture:** Hidden Markov Model (HMM) per concept.
*   **Limitation:** **Uni-modal & Independent.** It treats all concepts as statistically independent (no transfer of learning) and all correct answers as identical signals. It cannot distinguish between a "lucky guess" on a quiz and a "perfectly written algorithm."

### B. Deep Knowledge Tracing (DKT) (Piech et al., 2015)
*   **Architecture:** Long Short-Term Memory (LSTM) / RNNs.
*   **Limitation:** **Data Inefficiency & Opacity.** While it captures sequential dependencies better than BKT, it functions as a "Black Box." It requires massive datasets (10k+ trajectories) to learn simple prerequisite rules (e.g., *Variables -> Loops*) that our model knows *a priori* via the Graph. It also fails to provide interpretable reasons for its predictions.

### C. Graph-Based Knowledge Tracing (GKT) (Nakagawa et al., 2019)
*   **Architecture:** Graph Neural Networks (GNN) on a concept graph.
*   **Limitation:** **Signal Homogeneity.** Existing GKT implementations improve on DKT by acting on a graph structure, but they typically still rely on binary correctness logs ($0/1$). They lack the **Multisignal semantic weighting** (Code vs. Debug vs. Tutor) that is central to our contribution.

---

## 2. Our Contribution: The Hybrid Advantage

| Feature | Standard BKT | DKT (LSTM) | GKT (Graph) | **Ours (MGKT)** |
| :--- | :--- | :--- | :--- | :--- |
| **Input Fidelity** | Binary ($0/1$) | Binary ($0/1$) | Binary ($0/1$) | **Multi-Modal (Quiz/Code/Debug)** |
| **Dependency Awareness** | None | Implicit (Learned) | Explicit (Graph) | **Explicit + Attention Weighted** |
| **Interpretability** | High | Low | Medium | **High (Neuro-Symbolic)** |
| **Data Requirement** | Low | Very High | Medium | **Low (Graph Priors)** |

### Key Improvements
1.  **Signal Differentiation:** Unlike BKT/DKT/GKT, which treat a multiple-choice guess the same as code synthesis, our model mathematically weights **Debugging > Coding > Chat**. This prevents "guessing" your way to mastery.
2.  **Instant Warm-Start:** By injecting the Knowledge Graph structure as a prior, our model is effective from *Student #1*, whereas DKT and GKT often struggle with the "Cold Start" problem until thousands of students have been observed.

## 3. Differentiation from Recent SOTA (2024-2025)

### vs. SQKT (Student Question-based KT)
While SQKT utilizes LLMs to parse student inquiry intent, it remains dependent on the student's self-awareness of their knowledge gaps. MGKT operates on **demonstrated capability** (Debugging/Coding performance), providing a more objective measure of mastery that mitigates the Dunning-Kruger effect inherent in self-reported confusion.

### vs. DPKT (Difficulty-aware Programming KT)
DPKT leverages Transformer models (CodeBERT) for semantic difficulty analysis. While powerful, this introduces significant computational latency and lack of interpretability. MGKT achieves competitive difficulty-awareness through **Graph Topology** (Prerequisite density) rather than embedding-space distance, offering a lightweight ($O(1)$) and explainable alternative suitable for real-time tutoring.

### vs. Multimodal systems (Behavior/Gaze Tracking)
Behavioral systems require invasive client-side instrumentation (mouse tracking, gaze detection). MGKT achieves high-fidelity signals purely through **Pedagogical Interaction Types** (Debug vs Code), ensuring compatibility with standard LMS privacy standards and log formats while extracting deeper cognitive signals than simple correctness.

