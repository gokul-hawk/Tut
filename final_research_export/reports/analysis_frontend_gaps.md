# Analysis: Frontend Signal Gaps

We inspected `frontend/src/components/AgentTutor.jsx`.

## 1. Findings
*   **Quiz Panel**: Uses local state (`answers`, `showResult`).
*   **API Call**: `generateQuiz` calls `/chat/generate_quiz/` with `messages`.
*   **Completion**: When `data.is_complete` is true, it calls:
    ```javascript
    axios.post(".../report_success/", { source: "tutor" }, ...)
    ```

## 2. The Gap
The frontend **does not send any quiz performance data** to the `report_success` endpoint.
*   **Missing**: `correct_count`, `total_questions`, `hints_used`, `time_taken`.
*   **Result**: The backend receives `{ source: "tutor" }` and has to *guess* the score (or fetch from `TutorSession` which is also incomplete).

## 3. Required Changes
1.  **Quiz State Tracking**: We need to track:
    *   `startTime` per question.
    *   `hintCount` (if we add a hint button).
    *   `correctAttempts`.
2.  **Report Payload**: Update `report_success` call to include:
    ```json
    {
      "source": "tutor",
      "quiz_stats": {
        "correct": 3,
        "total": 5,
        "avg_time_sec": 12,
        "hints": 0
      }
    }
    ```
