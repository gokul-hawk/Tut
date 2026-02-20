# Mathematical Walkthrough: The "Under the Hood" Calculation

This document provides the **explicit manual calculation** for the "Alex & Loops" scenario to prove the system's math.

---

### Scenario Recap
*   **Concept**: `Loops`
*   **Prior Mastery ($P(L_{t-1})$)**: $0.40$ (Unlearned).
*   **Interaction**: Coding Task (Success).
*   **Score ($y_t$)**: $0.95$ (Treated as **Evidence = True**).
*   **Parameters (Code Mode)**:
    *   $P(G) = 0.05$ (Guess).
    *   $P(S) = 0.10$ (Slip).
    *   $P(T) = 0.30$ (Transit).

---

### Step 1: The Bayesian Update (Diagnosis)
We want to find the Posterior probability $P(L_t | Evidence)$.

**Formula**:
$$ P(L | E) = \frac{P(L) \cdot (1 - P(S))}{P(L) \cdot (1 - P(S)) + (1 - P(L)) \cdot P(G)} $$

**Substitution**:
*   $Numerator = 0.40 \times (1 - 0.10) = 0.40 \times 0.90 = \mathbf{0.36}$
*   $Denominator\_Term1 = 0.36$
*   $Denominator\_Term2 = (1 - 0.40) \times 0.05 = 0.60 \times 0.05 = \mathbf{0.03}$
*   $Total\_Denominator = 0.36 + 0.03 = \mathbf{0.39}$

**Calculation**:
$$ P(L | E) = \frac{0.36}{0.39} \approx \mathbf{0.923} $$

*Interpretation*: The evidence (correct code) makes us 92.3% sure he knew it at that moment.

---

### Step 2: The Transition Update (Learning)
Now we account for the possibility that he learned *during* the task.

**Formula**:
$$ P(L_{next}) = P(L | E) + (1 - P(L | E)) \cdot P(T) $$

**Substitution**:
*   $P(L | E) = 0.923$
*   $Chance\_To\_Learn = (1 - 0.923) = 0.077$
*   $Learning\_Gain = 0.077 \times 0.30 = \mathbf{0.0231}$

**Calculation**:
$$ P(L_{next}) = 0.923 + 0.0231 \approx \mathbf{0.946} $$

**Final Result**: The mastery of `Loops` jumps from **0.40** to **0.95**.

---

### Step 3: Graph Propagation (GAT)
Now we update the neighbor `Functions`.
*   **Assumption**: `Functions` depends on `Loops` with weight $A=1.0$.
*   **Propagation Weight ($\alpha$)**: $0.5$.
*   **Previous Readiness**: $0.40$ (based on old Loops mastery).

**Formula**:
$$ Readiness_{Func} = \alpha \cdot M_{Loops} + (1-\alpha) \cdot M_{OtherPrereqs} $$
*(Simplified: Readiness tracks Prerequisite Mastery)*

**New Readiness**:
$$ Readiness = 0.95 $$

**Result**: `Functions` is unlocked.
