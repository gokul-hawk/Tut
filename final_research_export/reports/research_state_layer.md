# The MGKT State Layer (The "Brain")

This document details the **State Management Architecture**, acting as the "Memory" of the system.

---

### 1. The Core Data Structures
The State Layer is composed of two primary data structures:

#### A. The Student Model ($H_t$)
*   **Format**: A dense vector of floating-point probabilities.
*   **Size**: $1 \times N$ (where $N = \text{Total Concepts}$).
*   **Value Range**: $[0.0, 1.0]$.
*   **Semantics**: $H_t[i]$ represents the probability that the student has mastered Concept $i$.
*   **Storage**: Low-latency JSON file (`user_state.json`) for $O(1)$ access.
    *   *Example*: `{"user@email": [0.95, 0.10, 0.40, ...]}`

#### B. The Knowledge Topology ($G$)
*   **Format**: A Directed Acyclic Graph (DAG) represented as an Adjacency Matrix $A$.
*   **Size**: $N \times N$.
*   **Semantics**: $A_{ij} = 1$ if Concept $j$ is a prerequisite for Concept $i$.
*   **Storage**: **Neo4j Graph Database** (Persistent).
    *   *Query*: `MATCH (d:Concept)-[:REQUIRES]->(p:Concept)`

---

### 2. The Update Engine (`GKTModel`)
The `GKTModel` class acts as the **State Facade**, coordinating all updates.

#### Step 1: Initialization (Cold Start)
*   **Action**: Loads Concepts from Neo4j $\rightarrow$ Sorts Alphabetically $\rightarrow$ Maps to Indices $0..N$.
*   **Matrix Build**: Queries Neo4j edges to construct the Adjacency Matrix $A$ in memory.
*   **User Check**: If user is new, initializes $H_0 = [0.1, 0.1, \dots]$.

#### Step 2: The Update Cycle (`update()`)
When a signal arrives, the State Layer executes a two-phase commit:

1.  **Phase 1: Local Update (BKT Service)**
    *   **Target**: Only the active concept index $i$.
    *   **Logic**: $H_t[i] \leftarrow BKT(H_{t-1}[i], \text{Signal}, \text{Params})$.
    *   *Result*: The mastery of the specific topic changes.

2.  **Phase 2: Global Propagation (GAT Service)**
    *   **Target**: All dependent nodes $j$ where $A_{ji} = 1$.
    *   **Logic**: $H_t[j] \leftarrow H_t[j] + \alpha(A_{ji} \cdot H_t[i])$.
    *   *Result*: Mastery flows downstream to unlock future topics.

---

### 3. Persistence & Serialization
*   **Frequency**: On every single interaction.
*   **Mechanism**:
    *   **Read**: Load `user_state.json` into RAM.
    *   **Modify**: Update NumPy array.
    *   **Write**: Dump back to `user_state.json` (Atomic Write).
*   **Why JSON?**: For this research prototype, file-based JSON offers zero-latency reads compared to querying a DB for every vector operation.

---

### Summary for Defense
*   **"What is the State?"**: A Probability Vector ($H_t$) mapped to a Graph ($G$).
*   **"Where does it live?"**: `user_state.json` (Dynamic) + `Neo4j` (Static).
*   **"How does it change?"**: Via the `GKTModel` Facade calling BKT (Local) and GAT (Global).
