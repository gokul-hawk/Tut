# Ablation Study Implementation Plan

## Goal
Scientifically validate the contribution of each component in the MGKT framework by systematically removing them and measuring performance drop.

## 1. Model Variants (The "Ablations")

| Variant | Description | Hypothesis regarding Impact |
| :--- | :--- | :--- |
| **Full MGKT** | Graph + Weights + Prereqs | Best Performance (Baseline) |
| **No-Graph MGKT** | Disconnect neighbors (Isolation) | Fails "Cold Start" (No propagation) |
| **No-Weights MGKT** | Equal weights ($0.33$ each) | Fails "Sensitivity" (Can't distinguish Debug vs Quiz) |
| **No-Prereqs MGKT** | Random order learning | Fails "Realistic Trajectory" (Masters advanced topics too early) |

## 2. Simulation Logic `simulate_ablation_study.py`

### Class: `AblationSuite`
*   Initializes all 4 models.
*   Runs a shared scenario: **"The Comprehensive Student"**
    *   Sequence:
        1.  **Cold Start**: Learns a Prereq (does it propagate to Dependent?) -> Test No-Graph.
        2.  **Mixed Signals**: Fails Quiz, Passes Debug -> Test No-Weights.
        3.  **Sequence Violation**: Tries Advanced Topic -> Test No-Prereqs.

### Metrics
*   **Propagation Gain**: $\Delta Mastery(Dependent)$ after mastering Prereq.
*   **Resolution Score**: Final mastery after conflicting signals (Fail Quiz + Pass Debug).
*   **Validity Score**: Ability to reject mastery if prerequisites are missing.

## 3. Output
*   **Console Table**: Comparisons of metrics across all 4 models.
*   **Report**: `analysis_ablation_report.md` summarizing the "Component value".
