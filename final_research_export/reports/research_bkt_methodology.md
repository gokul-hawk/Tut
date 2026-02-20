# Methodology: Multisignal Bayesian Knowledge Tracing

To accurately model student proficiency across diverse learning modalities, we implemented a **Multisignal Bayesian Knowledge Tracing (BKT)** algorithm. Unlike traditional BKT, which typically treats all student interactions as homogeneous binary signals (correct/incorrect), our model dynamically adjusts the probabilistic graphical model parameters—specifically **Guess** ($P(G)$), **Slip** ($P(S)$), and **Transition** ($P(T)$)—based on the semantic context of the interaction.

We categorize student interactions into three distinct heuristic signal types: **Understanding (Tutor)**, **Applying (Code)**, and **Analysis (Debug)**. The probability parameters for each signal were initialized based on the varying cognitive load and reliability associated with each activity type.

## 1. Parameter Initialization & Weighting Rationale

The BKT model updates the posterior mastery probability $P(L_n)$ using the standard Bayesian update rule, but with context-dependent parameters:

$$P(L_n|Observation) \propto P(Observation|L_{n-1}) \cdot P(L_{n-1})$$

Where the observation likelihood is governed by the specific activity parameters defined below.

### A. Understanding Signal (Tutor Interaction)
This signal corresponds to standard Socratic dialogue or multiple-choice assessments.
*   **Guess Probability ($P(G) = 0.25$):** We assign a higher guess probability to reflect the inherent "noise" in multiple-choice or short-answer formats, where students may correctly guess the answer without true mastery.
*   **Slip Probability ($P(S) = 0.15$):** A standard slip rate is maintained, accounting for minor misunderstandings or textual ambiguities.
*   **Transition Probability ($P(T) = 0.10$):** Reflects a baseline learning curve expected from passive or semi-active conversational engagement.

### B. Applying Signal (Code Generation)
This signal is generated when a student writes functional code to solve a problem.
*   **Guess Probability ($P(G) = 0.05$):** The probability of "guessing" syntactically and logically correct code is significantly lower than selecting a multiple-choice option. This low $P(G)$ makes a success event a strong positive predictor of mastery.
*   **Slip Probability ($P(S) = 0.10$):** We slightly reduce the slip probability, as failure to write correct code is often a genuine indicator of a lack of syntax or logic mastery rather than an accidental slip.
*   **Transition Probability ($P(T) = 0.30$):** Active construction of knowledge (writing code) is weighted with a higher transition probability, determining that successful coding implies a larger step-change in learning than answering a quiz.

### C. Analysis Signal (Debugging)
This signal is derived from the student's ability to identify and fix logical errors in identifying faulty code.
*   **Guess Probability ($P(G) = 0.01$):** We assign a near-zero guess probability. Successfully identifying a subtle logic bug and correcting it is almost impossible to achieve by chance.
*   **Slip Probability ($P(S) = 0.05$):** The slip rate is minimized. If a student understands the concept well enough to debug it, they effectively never "slip"; failure to debug is a strong indicator of a knowledge gap.
*   **Transition Probability ($P(T) = 0.40$):** Debugging acts as the highest-weighted learning event. It represents the "Analysis" level of Bloom's Taxonomy, suggesting that a student who can debug a concept has achieved a deeper, more robust mastery than one who can simply reproduce it.

## 2. Mathematical Definition (The BKT Theorem)

Bayesian Knowledge Tracing (BKT) is a **Hidden Markov Model (HMM)** that models learner knowledge as a latent binary variable ($L_n \in \{0, 1\}$).

### The Theorem (Update Rules)
For any concept $K$, the probability of mastery at step $n$ is updated in two stages:

#### Stage 1: The Bayesian Update (Posterior Calculation)
We calculate the posterior probability of mastery $P(L_n | Observation)$ using **Bayes' Theorem**.

**Case A: Student Answers Correctly ($Obs = 1$)**
The student either knew it ($1-P(S)$) or guessed it ($P(G)$):
$$ P(L_n | Obs=1) = \frac{P(L_{n-1}) \cdot (1 - P(S))}{P(L_{n-1}) \cdot (1 - P(S)) + (1 - P(L_{n-1})) \cdot P(G)} $$

**Case B: Student Answers Incorrectly ($Obs = 0$)**
The student either mastered but slipped ($P(S)$) or didn't know it ($1-P(G)$):
$$ P(L_n | Obs=0) = \frac{P(L_{n-1}) \cdot P(S)}{P(L_{n-1}) \cdot P(S) + (1 - P(L_{n-1})) \cdot (1 - P(G))} $$

#### Stage 2: The Learning Transition (Markov Step)
Even after the observation, the student might reflect and learn. We account for the probability of transitioning from "Unlearned" to "Learned" ($P(T)$) *between* steps:
$$ P(L_{n+1}) = P(L_n | Obs) + (1 - P(L_n | Obs)) \cdot P(T) $$
