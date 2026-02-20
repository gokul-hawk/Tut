# Recommendation Engine Algorithm: Calculating the Zone of Proximal Development

The recommendation system utilizes the Knowledge Graph topology to dynamically calculate a **Readiness Score ($R$)** for every concept in the curriculum. This score quantifies the student's preparedness to learn a new topic based on their mastery of its dependencies.

## 1. Readiness Score Calculation

For a given target concept $C_i$, let $P_i$ be the set of its immediate prerequisite concepts defined in the Knowledge Graph adjacency matrix $A$. The Readiness Score $R(C_i)$ is computed as the arithmetic mean of the posterior mastery probabilities of all prerequisites:

$$
R(C_i) = 
\begin{cases} 
1.0 & \text{if } P_i = \emptyset \quad (\text{Root Node}) \\
\frac{1}{|P_i|} \sum_{j \in P_i} P(L_j) & \text{if } P_i \neq \emptyset 
\end{cases}
$$

Where:
*   $P(L_j)$ comes from the **BKT** service (posterior probability of mastering prerequisite $j$).
*   If a concept has no prerequisites ($P_i = \emptyset$), $R(C_i) = 1.0$, allowing foundations to be recommended immediately.

## 2. Recommendation Candidates Selection

The system generates a ranked list of recommendations $S_{rec}$ by filtering and sorting the entire concept space $C$:

1.  **Exclusion Filter:** Remove $C_i$ if $P(L_i) > \tau$ (where $\tau = 0.85$). We do not recommend concepts the student has already mastered.
2.  **Ranking Function:** Sort remaining candidates by descending Readiness, using current mastery as a low-priority tie-breaker:
    $$Score(C_i) = \langle R(C_i), -P(L_i) \rangle$$
    
    *   **Primary Sort:** High Readiness ($R \approx 1.0$) implies all prerequisites are known.
    *   **Secondary Sort:** Low Current Mastery ($P(L) \approx 0.0$) prioritizes completely new topics over ones partially learned.

## 3. Pedagogical Implication (ZPD)

This algorithm mathematically formalizes Vygotsky's **Zone of Proximal Development (ZPD)**. 
*   Concepts with $R(C_i) \ll 0.5$ are in the **"Zone of Frustration"** (Dependencies unknown).
*   Concepts with $R(C_i) \approx 1.0$ and $P(L_i) \approx 0.0$ are in the **"Zone of Proximal Development"** (Ready to learn).
*   Concepts with $P(L_i) > 0.85$ are in the **"Zone of Mastery"** (Already learned).
