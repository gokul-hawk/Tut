# State Layer: The Executive Summary (Flashcard)

**Role**: The "Brain" that evolves the Student Model in real-time.

---

### Step 1: Signal Processing (The Translator)
*   **Role**: Converts raw behavior (Code, Quiz, Hints) into a single probability ($0.0 - 1.0$).
*   **Action**: "You submitted messy code with 3 hints." $\rightarrow$ **Score: 0.78** (Binary Failure).
*   **Value**: Ensures the math (BKT) receives a clean, normalized input from complex interactions.

### Step 2: BKT Update (The "Local Learner")
*   **Role**: Updates the **Active Node** (e.g., "Loops").
*   **Action**: "We are now 95% sure you know Loops."
*   **Math**: Bayes' Theorem adjusts probability based on Evidence vs. Guess/Slip parameters.
    *   *Result*: Precision Learning for the specific topic practiced.

### Step 3: GAT Update (The "Graph Spreader")
*   **Role**: Updates **Dependent Nodes** (e.g., "Functions").
*   **Action**: "Since you mastered Loops, you are now 89% Ready for Functions."
*   **Logic**: Propagates gains downstream to unlock future curriculum.

---

### Phase 4: Storage Strategy (The "Hybrid Memory")
*   **Dynamic State (`user_state.json`)**: Stores probabilities as a simple array for **Zero-Latency access**.
*   **Static Graph (`Neo4j`)**: Stores structure (Edges/Nodes) for **Logical dependencies**.
*   **Why?**: Combines the speed of JSON with the relationship power of a Graph DB.
