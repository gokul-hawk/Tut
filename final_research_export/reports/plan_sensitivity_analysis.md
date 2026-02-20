# Sensitivity Analysis Implementation Plan

## Goal
Conduct a rigorous **Sensitivity Analysis** to quantify how the MGKT model responds to specific pedagogical signals compared to baselines (BKT, DKT).

## 1. Simulation Design
We will create `simulate_sensitivity_analysis.py` to run the following controlled experiments:

### Experiment A: Signal Weight Sensitivity
*   **Hypothesis**: MGKT mastery should increase non-linearly with "high-value" signals (Debug/Code) compared to "low-value" signals (Quiz).
*   **Procedure**:
    1.  Feed 5 consecutive "Quiz Correct" signals -> Measure Mastery Gain.
    2.  Feed 5 consecutive "Code Correct" signals -> Measure Mastery Gain.
    3.  Feed 5 consecutive "Debug Correct" signals -> Measure Mastery Gain.
*   **Expected Result**: Debug Slope > Code Slope > Quiz Slope. BKT should have equal slopes.

### Experiment B: Noise Resistance (The "Lucky Guess" Test)
*   **Hypothesis**: MGKT should dampen mastery growth when signals are "noisy" (e.g., fast guesses).
*   **Procedure**:
    1.  Simulate a sequence of "Correct" answers with "Low Confidence" metadata (simulating guessing).
    2.  Compare MGKT Final Mastery vs BKT Final Mastery.

### Experiment C: Breakthrough Detection (The "Eureka" Test)
*   **Hypothesis**: A single "Debug Success" after a string of failures should trigger a larger mastery jump in MGKT than BKT.
*   **Procedure**:
    1.  Sequence: 5 Failures -> 1 Debug Success.
    2.  Measure $\Delta Mastery$ at the final step.

## 2. Implementation Steps
1.  **Create Script**: `backend/simulate_sensitivity_analysis.py`
    *   Import Mock Models.
    *   Define the 3 Experiments.
    *   Run loops and collect data.
    *   Generate a Markdown Report.
2.  **Execute**: Run the script.
3.  **Analyze**: Present the "Sensitivity Metrics" (e.g., "Debug is 2.5x more impactful than Quiz").

## 3. Deliverable
*   **Console Output**: Detailed tables of mastery progression.
*   **Artifact**: `analysis_sensitivity_report.md` summarizing the findings.
