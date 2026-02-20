# MGKT: Framework & Mathematical Formulation

**Title:** Multisignal Graph Knowledge Tracing (MGKT) Framework

## 1. System Framework Overview (Diagram)

The MGKT architecture operates as a closed-loop control system where student interactions flow through a signal classifier, update a local probabilistic model (BKT), propagate through a global knowledge graph (GAT), and finally inform the recommendation engine.

```mermaid
graph TD
    User((Student)) -->|Interaction $I_t$| Classifier[Signal Classifier]
    
    subgraph "1. Multisignal Processing"
        Classifier -->|Quiz| S_Quiz[Signal: Understanding]
        Classifier -->|Code| S_Code[Signal: Application]
        Classifier -->|Debug| S_Debug[Signal: Analysis]
    end
    
    subgraph "2. Local Update (BKT Engine)"
        S_Quiz -->|Update $P(G,S)$| BKT[Bayesian Knowledge Tracing]
        S_Code -->|Update $P(G,S)$| BKT
        S_Debug -->|Update $P(G,S)$| BKT
        BKT -->|Posterior Mastery $L_t$| NodeState[Concept Node State]
    end
    
    subgraph "3. Global Propagation (GAT)"
        NodeState -->|Input Feature $H_t$| GAT[Graph Attention Network]
        GAT -->|Weighted Sum| Readiness[Readiness Score $R_t$]
    end
    
    subgraph "4. Recommendation Logic (ZPD)"
        Readiness -->|Filter: $R > 0.6$| Recommender[ZPD Selector]
        NodeState -->|Filter: $L < 0.85$| Recommender
        Recommender -->|Select Max $R$| NextTopic[Next Concept $C_{t+1}$]
    end
    
    NextTopic -->|Feedback Loop| User
```

---

## 2. Mathematical Formulation

We define the **MGKT Framework** as a 4-tuple $\mathcal{F} = (G, \mathcal{M}, \Psi, \Omega)$:

### A. The Knowledge Graph ($G$)
Let $G = (V, E)$ be a Directed Acyclic Graph (DAG) where:
*   $V = \{c_1, c_2, ..., c_N\}$ represents the set of $N$ pedagogical concepts.
*   $E \subseteq V \times V$ represents the prerequisite dependencies, where $(c_i, c_j) \in E$ implies $c_i$ is a prerequisite for $c_j$.

### B. The Multisignal Interaction Space ($\mathcal{M}$)
Let $I_t$ be an interaction at time $t$. We define a mapping function $\phi: I_t \to (S_type, \alpha, \beta)$ that categorizes the interaction into a semantic signal with specific probabilistic parameters:

$$
\phi(I_{type}) = 
\begin{cases} 
(\text{Quiz}, P(G)=0.25, P(S)=0.15) & \text{if type is Quiz} \\
(\text{Code}, P(G)=0.05, P(S)=0.10) & \text{if type is Code} \\
(\text{Debug}, P(G)=0.01, P(S)=0.05) & \text{if type is Debug}
\end{cases}
$$

### C. The Local Update Function ($\Psi$: BKT)
For a specific node $c_k$, the mastery state $L_t^{(k)}$ is updated using the Bayesian operator $\Psi$:
$$ L_t^{(k)} = \Psi(L_{t-1}^{(k)}, I_t, \phi(I_t)) $$
Where $\Psi$ applies the standard BKT update using the *dynamic* Guess/Slip parameters defined by $\phi$.

### D. The Global Propagation Function ($\Omega$: GAT)
The hidden state of the graph $H_t$ is updated by the Graph Attention function $\Omega$ to calculate the **Readiness Vector** $R_t$:
$$ R_t = \Omega(G, H_t) $$
For a specific node $c_j$ with prerequisites $\mathcal{P}_j$:
$$ R_t^{(j)} = \sigma \left( \sum_{k \in \mathcal{P}_j} \alpha_{kj} \cdot L_t^{(k)} \right) $$
Where $\alpha_{kj} = \frac{1}{|\mathcal{P}_j|}$ (Simple Averaging Attention) in our current implementation.

---

## 3. The Objective Function (Recommendation)

The goal of the framework is to select the optimal next concept $c^*$ that maximizes learning efficiency (ZPD).
$$ c^* = \text{argmax}_{c \in V} \left( \lambda_1 R_t^{(c)} - \lambda_2 L_t^{(c)} \right) $$
Subject to constraints:
1.  $L_t^{(c)} < \theta_{mastery}$ (Not already learned)
2.  $R_t^{(c)} > \theta_{readiness}$ (Prerequisites sufficient)

This formulation ensures the system always picks the "Most Ready, Least Mastered" topic.
