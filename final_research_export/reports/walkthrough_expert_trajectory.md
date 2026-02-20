# Walkthrough: Expert Trajectory (Learning Curve)

## Visual Analysis
![Expert Trajectory Learning Curve](file:///c:/Users/gokul/.gemini/antigravity/brain/d17f1ba0-5ec9-4687-9332-b531226f81c8/learning_curve.png)

## Comparative Breakdown

### 1. BKT: The "Optimist"
*   **Behavior**: BKT shows very steep growth, reaching **certainty (1.0)** within 12 steps. 
*   **Verdict**: While it responds fast, it is prone to "Overconfidence," assuming the student knows everything after a short streak.

### 2. DKT: The "Steady State"
*   **Behavior**: DKT stabilizes around **0.92**. It recognizes the expert pattern but maintains a slight buffer.
*   **Verdict**: Reliable for prediction, but less sensitive to the specific *type* of signal (Tutor vs Code) in our simplified simulation.

### 3. MGKT-GAT: The "Strategic Skeptic"
*   **Behavior**: 
    *   **Phase 1 (Tutor)**: Grows cautiously. It refuses to believe the student is an expert based on quizzes alone.
    *   **Phase 2 (Code)**: Shows dynamic jumps as the student proves themselves in "Application" tasks.
    *   **Phase 3 (Debug)**: Reaches a **Saturation Ceiling of 0.95**.
*   **Verdict**: This is the most **Pedagogically Safe** model. By never hitting 1.0, it ensures the system remains alert to potential gaps, which is critical for long-term learning retention.

## Conclusion
The trajectory graph proves that the **GAT-enabled MGKT** is the most sophisticated learner. It understands the hierarchy of signals (Debug > Code > Tutor) and maintains a healthy safety margin, preventing the "Premature Mastery" common in simpler models.
