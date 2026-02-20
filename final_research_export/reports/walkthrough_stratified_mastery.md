# Stratified Mastery Implementation Walkthrough

We have successfully implemented the **Stratified Mastery Model** across the full Agent stack. This ensures that every interaction (Tutor, Code, Debug) contributes a specific, weighted signal to the student's mastery profile.

## 1. The New Workflows

### Phase 1: Agent Tutor (Understanding)
*   **Old Behavior**: Chat completed -> Backend guessed score.
*   **New Behavior**:
    1.  Chat completes topic explanation.
    2.  System **Auto-Triggers** the `QuizPanel`.
    3.  Student must take the quiz.
    4.  Frontend sends `quiz_stats` (e.g., `{ correct: 4, total: 5 }`).
    5.  Backend calculates **Tutor Score** (Weight: 0.25).

### Phase 2: Agent Code (Applying)
*   **Old Behavior**: Passing tests sent generic success.
*   **New Behavior**:
    1.  Student writes code and runs tests.
    2.  On Success, Frontend calculates metrics:
        *   `ai_usage`: Number of hints/messages used.
        *   `total_tests`: Complexity proxy.
    3.  Frontend sends `code_stats`.
    4.  Backend calculates **Code Score** (Weight: 0.35) using `ScoringEngine`.

### Phase 3: Agent Debugger (Analysis)
*   **Old Behavior**: Fixed bug -> Generic success.
*   **New Behavior**:
    1.  Student submits diagnosis/fix.
    2.  Frontend tracks **Attempts** (retries).
    3.  Frontend sends `debug_stats` (`attempts`, `explanation_len`).
    4.  Backend calculates **Debug Score** (Weight: 0.40).
        *   1 Attempt = 100%
        *   2-3 Attempts = 75%
        *   >3 Attempts = 50%

## 2. Backend Logic Update (`views.py`)
We patched the BKT signal logic to ensure fairness:
*   **The Issue**: Comparing `Weighted Final Score` (e.g., 25.0) vs `Threshold` (80.0) caused false failures.
*   **The Fix**: BKT now updates based on the **Component Score**:
    *   If Source is **Tutor**, it checks `tutor_score >= 80`.
    *   If Source is **Code**, it checks `code_score >= 80`.

## 3. Verification
*   **Frontend**: All 3 Agents now send rich payloads (`quiz_stats`, `code_stats`, `debug_stats`).
*   **Scoring Engine**: Methods added/updated to parse these payloads.
*   **BKT Integration**: Validated `source_type` routing in `GKTModel`.

The system is now fully compliant with the **Multi-Signal Graph Knowledge Tracing** research specification.
