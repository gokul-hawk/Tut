# Mathematical Formulations of the MGKT Framework

This document consolidates every mathematical equation used in the project for your thesis.

---

## 1. Local Knowledge Tracing (Multisignal BKT)

We model student mastery $L_t$ as a Hidden Markov Model.

### 1.1 The Variables
*   $L_t$: Latent Mastery State at time $t$ ($1=$ Known, $0=$ Unknown).
*   $Obs_t$: Observable Outcome at time $t$ ($1=$ Correct, $0=$ Incorrect).
*   $S_{type}$: Semantic Signal (Quiz, Code, Debug).

### 1.2 The Parameters (Context-Dependent)
Instead of fixed $P(G), P(S)$, we use a **Signal Mapping Function** $\phi(S_{type})$:

$$
\begin{align*}
P(G)_{quiz} &= 0.25, & P(S)_{quiz} &= 0.15 \\
P(G)_{code} &= 0.05, & P(S)_{code} &= 0.10 \\
P(G)_{debug} &= 0.01, & P(S)_{debug} &= 0.05
\end{align*}
$$

### 1.3 The Update Rule (Bayes Theorem)
**Step 1: Posterior Calculation**
If Observed Correct ($Obs_t = 1$):
$$ P(L_t | Obs=1) = \frac{P(L_{t-1}) \cdot (1 - P(S))}{P(L_{t-1}) \cdot (1 - P(S)) + (1 - P(L_{t-1})) \cdot P(G)} $$

If Observed Incorrect ($Obs_t = 0$):
$$ P(L_t | Obs=0) = \frac{P(L_{t-1}) \cdot P(S)}{P(L_{t-1}) \cdot P(S) + (1 - P(L_{t-1})) \cdot (1 - P(G))} $$

**Step 2: Transition (Learning)**
$$ P(L_{t+1}) = P(L_t | Obs) + (1 - P(L_t | Obs)) \cdot P(T) $$
where $P(T)$ is the Transition probability (Learning Rate), also weighted by signal type ($P(T)_{debug} > P(T)_{quiz}$).

---

## 2. Global Knowledge Propagation (Graph Attention)

We model the curriculum as a Directed Acyclic Graph $G=(V,E)$.

### 2.1 Readiness Score ($R_t$)
For a concept node $j$, the **Readiness Score** is computed by aggregating the mastery of its prerequisite set $\mathcal{P}_j$:

$$ R_t^{(j)} = \sigma \left( \sum_{k \in \mathcal{P}_j} \alpha_{kj} \cdot L_t^{(k)} \right) $$

where:
*   $L_t^{(k)}$ is the current mastery of prerequisite $k$.
*   $\alpha_{kj}$ is the attention weight (importance of $k$ for $j$).
*   $\sigma$ is the Sigmoid activation function (or Identity in simplified version).

### 2.2 Objective Function (GNN Training)
We learn the weights $\alpha$ by minimizing the prediction error on future success.
**Loss Function (MSE):**
$$ \mathcal{L} = \frac{1}{N} \sum_{i=1}^{N} (\hat{y}_i - y_i)^2 $$
where $y_i$ is the actual binary outcome (0/1) of the student's next attempt.

---

## 3. Recommendation Engine (The ZPD Algorithm)

We select the optimal next concept $c^*$ by maximizing a utility function.

### 3.1 The Utility Function
$$ U(c) = \lambda_1 \cdot R_t^{(c)} - \lambda_2 \cdot L_t^{(c)} $$
where:
*   $\lambda_1, \lambda_2$ are hyperparameters balancing Readiness vs. Mastery.
*   Assumption: We want High Readiness ($R \to 1$) but Low Mastery ($L \to 0$).

### 3.2 Constraints (The Filter)
$$
\begin{align*}
Subject \ to: \quad & L_t^{(c)} < 0.85 \quad (\text{Not Mastered}) \\
& R_t^{(c)} > 0.60 \quad (\text{Ready})
\end{align*}
$$

---

## 4. Dataset Generation (The Simulation Math)

We simulate student performance using a probabilistic Item Response Theory (IRT) model extended with Graph Constraints.

### 4.1 Probability of Success
The probability that student $u$ solves concept $i$ correctly:

$$ P(Correct_{u,i}) = w_1 \cdot \theta_u + w_2 \cdot \left( \frac{1}{|\mathcal{P}_i|} \sum_{k \in \mathcal{P}_i} L_{u,k} \right) - \delta_i + \epsilon $$

where:
*   $\theta_u$: **Student Ability** (Latent Trait, $\sim \mathcal{N}(0.5, 0.2)$).
*   $\sum L_{u,k}$: **Prerequisite Mastery** (Graph constraint).
*   $\delta_i$: **Concept Difficulty**.
*   $\epsilon$: Random Gaussian Noise.
