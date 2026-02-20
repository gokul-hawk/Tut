# Research Problem Formulation: The Challenge of Accurate Knowledge Tracing in Tutoring Systems

**Title:** Beyond Correctness: Addressing Signal Ambiguity and Cold-Start Latency in Knowledge Tracing

---

## 1. Problem Statement

The fundamental problem of Knowledge Tracing (KT) is to estimate a student's latent mastery state $L_t$ for a set of concepts $C = \{c_1, c_2, ..., c_N\}$ based on their sequence of observable interactions $I = \{i_1, i_2, ..., i_t\}$.

Formally, we seek to learn the posterior probability distribution:
$$ P(L_t | I_{0...t}) $$

While this structure is well-defined, existing approaches fail to capture the complexity of real-world learning due to two critical limitations: **Signal Ambiguity** and **Topological Blindness**.

### 1.1 The Challenge of Signal Ambiguity (The "Guessing" Problem)
A correct answer is not always proof of mastery.
*   **Traditional View (BKT/DKT):** Treat all interactions as binary correctness tuples $(c_k, r_t \in \{0,1\})$.
*   **The Flaw:** A student who guesses "C" on a multiple-choice question ($r_t=1$) is mathematically indistinguishable from a student who writes a perfect algorithm ($r_t=1$).
*   **Consequence:** This leads to **False Positive Mastery**, where students "game the system" by guessing, and the model promotes them to advanced topics prematurely.

### 1.2 The Challenge of Topological Blindness (The "Cold Start" Problem)
Learning is not isolated; concepts are interconnected.
*   **Traditional View (BKT):** Treats each concept $c_k$ as an independent Hidden Markov Model. Learning $c_i$ provides zero information about $c_j$.
*   **Deep Learning View (DKT):** Attempts to learn dependencies implicitly from massive datasets ($N > 10,000$).
*   **The Flaw:** For a new student or a new curriculum (Cold Start), the model has no data to infer these relationships. It defaults to a non-informative prior ($P(L)=0.5$) until sufficient history is collected.
*   **Consequence:** High-performing students maximize their "frustration metric" by being forced to prove mastery on elementary topics (like Variables) even after demonstrating advanced skills (like Loops), simply because the model cannot infer the logical implication $Loops \implies Variables$.

---

## 2. Research Objectives

To address these limitations, this research proposes a **Multisignal Graph Knowledge Tracing (MGKT)** framework with the following objectives:

1.  **Objective 1: Signal Disambiguation**
    To replace binary correctness logs with **Semantic Interaction Types** (Quiz, Code, Debug), assigning distinct probabilistic weights to each. We hypothesize that weighting *Analysis* (Debugging) higher than *Recall* (Quiz) will reduce false discovery rates.

2.  **Objective 2: Topological Warm-Starting**
    To utilize a domain-expert **Knowledge Graph** as a structural prior. We aim to demonstrate that propagating mastery signals through the graph (via Graph Attention Networks) significantly reduces the number of interactions required to accurately model a student's state (Convergence Speed).

3.  **Objective 3: Dynamic ZPD Recommendation**
    To formulate a recommendation policy $\pi(L_t, G)$ that selects the optimal next concept $c_{t+1}$ by balancing **Readiness** (Prerequisite Mastery) and **Utility** (Learning Gap), rather than following a static linear order.

---

## 3. Scope & Constraints

*   **Domain:** Introductory Programming (Python). This domain is chosen because the distinction between *Syntax* (Coding) and *Semantics* (Debugging) is explicitly measurable.
*   **Data Constraint:** The model must be trainable on small-scale classroom data ($N < 100$), precluding the use of data-hungry Transformer experiments (e.g., GPT-4 based KT) as the primary baseline.
*   **Privacy Constraint:** The system must operate on standard Interaction Logs without requiring invasive biometrics (eye-tracking) or continuous screen recording.
