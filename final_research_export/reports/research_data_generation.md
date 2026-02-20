# Dataset Generation Methodology: Graph-Constrained Student Simulation

To effectively train the Graph Attention Network (GAT) without compromising user privacy or waiting for large-scale pilot data, we implemented a **Graph-Constrained Monte Carlo Simulation** to generate high-fidelity synthetic student learning trajectories.

Unlike naive random generation, our methodology rigorously respects the causal dependencies defined in the Knowledge Graph. This ensures that the generated dataset reflects realistic learning patterns—specifically, that mastery of prerequisite concepts significantly increases the probability of mastering dependent concepts.

## 1. Simulation Protocol

We model the student's learning process as a probabilistic random walk through the Knowledge Graph $G = (V, E)$. For each simulated student $S_k$, we execute the following protocol:

### Step 1: Attribute Initialization
We assign each student a latent ability parameter $\theta_k$, sampled from a normal distribution:
$$\theta_k \sim \mathcal{N}(\mu=0.5, \sigma=0.2)$$
This parameter represents the student's intrinsic aptitude, influencing their baseline probability of success across all topics.

### Step 2: Trajectory Generation
The student attempts concepts in a semi-topological order. For each concept node $V_i$, the probability of success $P(Success|V_i)$ is conditional on:
1.  **Student Ability ($\theta_k$)**
2.  **Prerequisite Mastery State ($M_{parent}$)**: The average mastery status of all direct parent nodes in the graph.

The success probability is calculated as:
$$P(Success | V_i) = w_1 \cdot \theta_k + w_2 \cdot \left( \frac{1}{|P_i|} \sum_{j \in P_i} M_j \right) + \epsilon$$

Where:
*   $P_i$ is the set of prerequisite indices for node $V_i$.
*   $M_j \in \{0, 1\}$ is the binary mastery status of prerequisite $j$.
*   $w_1, w_2$ are weights balancing ability vs. prior knowledge (e.g., $0.4, 0.6$).
*   $\epsilon$ is Gaussian noise $\mathcal{N}(0, 0.05)$ to simulate variability.

## 2. Dataset Validity for GAT Training

This generation method guarantees that the dataset contains the **structural signals** required for the GAT to converge.
*   **Correlation preservation:** The simulation ensures $Corr(Mastery_{prereq}, Mastery_{dependent}) > 0$.
*   **Causal inference:** By enforcing $P(Success | \neg Prereq) \approx 0$, the dataset teaches the GAT that knowledge flows along the directed edges $E$, validating the attention mechanism's purpose.

The resulting dataset $D = \{ (X^{(k)}, Y^{(k)}) \}_{k=1}^N$ consists of $N=500$ distinct learning trajectories used for supervised training of the attention weights.

## 3. Comparison with Benchmark Datasets (e.g., ASSISTments 2009/2012)

A common question is: *"Why generate synthetic data instead of using the standard ASSISTments dataset?"*

### The "Missing Graph" Problem
*   **ASSISTments Data**: Provides thousands of student interactions (User, Problem, Correctness).
*   **The Gap**: It **does not provide an explicit Knowledge Graph**. It tells you *what* problems were solved, but not *how* the skills are structurally related (e.g., that "Pythagoras" is a prerequisite for "Trigonometry").
*   **Impact on GAT**: A Graph Attention Network (GAT) requires an adjacency matrix ($A$) to propagate signals. To use ASSISTments, we would first need to *infer* or *hand-craft* this graph, introducing a source of error/bias.

### Our Strategy: Topological Ground Truth
By producing our own data via graph-constrained simulation, we ensure **perfect alignment** between the data generation process and the graph topology. This allows us to isolate and validate the GAT's performance mathematically, proving that the architecture *works* when the graph is correct.

**Future Work**: Applying MGKT to ASSISTments would involve a two-step process: (1) Statistical Graph Discovery (e.g., using transition probabilities to infer prerequisites), followed by (2) Training the GAT on this inferred structure.

## 4. Advanced Topic: Structure Learning (Graph Discovery)

To answer the question *"Could we use ASSISTments to GENERATE the graph?"* — **Yes, absolutely.**

This is a field called **Causal Discovery** or **Structure Learning**. Instead of hand-coding the graph, we could mathematically infer it from the data:

1.  **Dependency Analysis**: If students who fail Concept A almost *always* fail Concept B (but not vice versa), we can infer a directed edge: $A \to B$.
2.  **Algorithm**: We would use the **PC-Algorithm** or **Bayesian Network Structure Learning** to discover the "hidden" prerequisite graph typically assumed by experts.
3.  **Benefit**: This would make our model fully autonomous—it would "discover" the curriculum structure just by watching students learn!


