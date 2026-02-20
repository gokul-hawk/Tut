# MGKT Mathematical Breakdown: The "Stratified" Logic

This document provides the **explicit mathematical proof** of how the system builds "Total Mastery" using three capped components.

### The Input Signal
The BKT Engine receives a **Binary Classification** derived from the continuous Score ($y_t$):
*   **Input**: $\{ \text{Success}, \text{Failure} \}$
*   **Derivation**: $y_t \ge \text{Threshold}(0.8) \rightarrow \text{Success}$.
    *(Note: The "Softness" comes from the Parameters $P(G), P(S)$ acting as confidence weights, not the raw input value itself)*.

### The Formula
$$ Mastery_{Total} = (S_{Tutor} \times 0.25) + (S_{Code} \times 0.35) + (S_{Debug} \times 0.40) $$

---

## Case 1: AgentTutor (The "Base" Layer)
*   **Signal ($y_t$)**: 1.0 (Correct Quiz).
*   **BKT Update**:
    *   Parameters: $P(G)=0.25, P(S)=0.15, P(T)=0.1$.
    *   Prior ($0.40$) $\xrightarrow{\text{Update}}$ **Posterior ($0.72$)**.
*   **Contribution**: $0.72 \times 0.25 = \mathbf{0.18}$.

## Case 2: AgentCode (The "Application" Layer)
*   **Signal ($y_t$)**: 0.95 (Code with penalties).
*   **BKT Update**:
    *   Parameters: $P(G)=0.05, P(S)=0.10, P(T)=0.3$.
    *   Prior ($0.40$) $\xrightarrow{\text{Update}}$ **Posterior ($0.946$)**.
*   **Contribution**: $0.946 \times 0.35 = \mathbf{0.331}$.

## Case 3: AgentDebug (The "Depth" Layer)
*   **Signal ($y_t$)**: 0.90 (Fixed bug, 1 retry).
*   **BKT Update**:
    *   Parameters: $P(G)=0.01, P(S)=0.05, P(T)=0.4$.
    *   Prior ($0.40$) $\xrightarrow{\text{Update}}$ **Posterior ($0.984$)**.
*   **Contribution**: $0.984 \times 0.40 = \mathbf{0.393}$.

### Final Composite Mastery
$$ M_{Total} = 0.18 + 0.331 + 0.393 = \mathbf{0.904} $$

---

## 4. The Impact of Negative Scoring (The "Efficiency Threshold")
"How does a penalty (-0.1) affect the BKT if BKT only sees binary?"

Answer: **The Threshold Mechanism**.
The system converts the **Continuous Score ($y_t$)** into a **Binary Decision** using a strict threshold (e.g., $0.8$).

### Scenario: The "Messy" Coder
*   **Performance**: Passes all tests ($1.0$), but uses 10 Attempts ($10 \times 0.01$) and 6 Hints ($6 \times 0.02$).
*   **Score ($y_t$)**: $1.0 - 0.1 - 0.12 = \mathbf{0.78}$.
*   **Threshold Check**: $0.78 < 0.80 \rightarrow$ **Failure**.
*   **BKT Consequence**:
    *   Instead of increasing Mastery (Success), the system treats this as a **Failure**.
    *   **Result**: Mastery *decreases* (e.g., $0.40 \to 0.35$) because the student relied too heavily on trial-and-error.

---

## 5. The Readiness Score (Recommendation Logic)
"How does the system decide what to teach next?"

Answer: **The Arithmetic Mean of Prerequisites**.
For any concept $C$, the readiness $R(C)$ is the average mastery of its parents ($P$).

$$ R(C) = \frac{1}{|P|} \sum_{i \in P} M_{Total}(i) $$

### Example: "Functions"
*   **Prerequisites**: `Loops` ($0.90$), `Variables` ($0.98$).
*   **Calculation**:
    $$ R(\text{Func}) = \frac{0.90 + 0.98}{2} = \mathbf{0.94} $$
*   **Decision**: Since $0.94 > \text{Threshold}(0.60)$, "Functions" is **Ready** to be recommended.
