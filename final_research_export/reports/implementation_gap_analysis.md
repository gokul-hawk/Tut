# Implementation Gap Analysis: Research vs. Codebase

This document identifies the critical discrepancies between the **Research Specifications** (what we promised) and the **Current Codebase** (what is implemented).

---

## 1. Critical Logic Gaps (Must Fix)

### A. The "Dummy Signal" Bug (State Layer)
*   **Research Claim**: "Continuous Score is converted to Binary Observation via Threshold ($y_t \ge 0.8 \to 1$)."
*   **Current Code** (`main_agent/views.py`):
    ```python
    gkt.update(request.user.email, req_topic, is_correct=True, source_type=source)
    ```
*   **The Gap**: The system **Hardcodes `is_correct=True`**.
*   **Impact**: Even if a student gets a score of 10/100, the BKT engine treats it as a **Success**, increasing mastery. The "Efficiency Threshold" logic is **MISSING**.

### B. Stratified Mastery (Data Structure)
*   **Research Claim**: "Total Mastery = $Sum(Component \times Cap)$."
*   **Current Code** (`gkt_model.py`):
    *   State is a **1D Array** (`[0.1, 0.4, ...]`).
    *   Updates overwrite the scalar value directly.
*   **The Gap**: The system **cannot distinguish** between Tutor Mastery and Code Mastery. It treats all knowledge as a single bucket.
*   **Impact**: It is mathematically impossible to implement the "Capped Contribution" logic without storing 3 separate vectors.

---

## 2. Mathematical Mismatches

### A. Scoring Weights
*   **Research Claim**: Tutor (0.25) / Code (0.35) / Debug (0.40).
*   **Current Code** (`scoring_engine.py`): Tutor (0.25) / Code (**0.45**) / Debug (**0.30**).
*   **Action**: `scoring_engine.py` needs to be updated to match the report.

### B. Penalty Logic
*   **Research Claim**: $Score = \dots - (Attempts \times 0.01) - (Hints \times 0.02)$.
*   **Current Code** (`scoring_engine.py`):
    *   `ai_penalty = min(ai_usage * 5, 20)` (Scale 0-100).
    *   `test_penalty = min(failures * 1, 10)` (Scale 0-100).
*   **The Gap**: The logic exists but uses a **0-100 Scale**, whereas BKT expects **0.0-1.0**.
*   **Action**: Normalize the `scoring_engine` outputs before BKT processing.

---

## 3. Missing Modules

### A. The Concept Explorer (Retroactive Decay)
*   **Research Claim**: "Failure on Child Node triggers Probe on Parent Node."
*   **Status**: **Not Implemented**. No code exists to check parent status upon failure.

### B. Graph Discovery
*   **Research Claim**: (Optional Future Work) "Inferring structure from data."
*   **Status**: **Not Implemented** (Low Priority).

---

## 4. Summary of Work Required
1.  **Update `gkt_model.py`**: Change State Vector to support 3 channels (or simulate it).
2.  **Fix `main_agent/views.py`**: Implement the `Threshold Check` ($Score \ge 80 \to is\_correct=True$).
3.  **Align `scoring_engine.py`**: Update weights to `0.35/0.40`.
