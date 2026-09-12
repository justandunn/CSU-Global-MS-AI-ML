# CSC580 Capstone-Oriented Course Workflow

## Capstone target

Module 8 requires one of two 300-point projects. Option 2 is selected:

1. A GAN trained on a selected CIFAR-10 class, with a four-use-case research paper, first/last-epoch images, screenshots, and performance analysis.
2. An encoder-decoder LSTM for sequence-to-sequence prediction, with a four-use-case research paper, flowchart, documented Python source, prediction output, screenshots, and analysis.

The formal 75-point Portfolio Milestone occurs in Module 4. Its two options are now available:

1. Extend Module 1 Critical Thinking Option 1 into facial recognition that determines whether a specific person appears in a group.
2. Extend Module 3 Critical Thinking Option 2 (Auto MPG regression) with early stopping, test-set evaluation, a true-versus-predicted plot, and prediction-error distribution analysis.

## Reusable weekly workflow

1. Capture the exact prompt, rubric, naming convention, and due dates.
2. Create a small, explainable implementation with a deterministic seed where supported.
3. Validate inputs, shapes, row/sample counts, train/test separation, and expected output type.
4. Record package versions and the exact run command.
5. Save console output, metrics, figures, and screenshots as evidence.
6. Write a short analysis covering method, results, limitations, and improvement opportunities.
7. Verify every rubric item and archive filename before submission.

## Module-to-capstone map

| Module | Course focus | Reusable capstone asset |
|---|---|---|
| 1 | ML review; FCNN, CNN, RNN, LSTM | Environment validation, reproducible run pattern, architecture comparison, evidence capture |
| 2 | Tensors and TensorFlow computations | Select sales regression to reuse scaling, train/test isolation, model persistence, and prediction reporting |
| 3 | Linear and logistic regression | Select Auto MPG to create the exact baseline required by the recommended Module 4 milestone |
| 4 | Fully connected deep networks | Add early stopping, held-out evaluation, prediction plots, residual analysis, and milestone report |
| 5 | Hyperparameter optimization | Use a structured experiment table, repeated seeds, best-model selection, and confusion-matrix QA |
| 6 | CNNs | Select CIFAR-10 CNN if leaning toward the GAN; reuse image loading, architecture, evaluation, and flowchart work |
| 7 | RNNs and recurrent cells | Direct preparation for encoder-decoder LSTM, sequence generation, decoding, accuracy checks |
| 8 | Reinforcement learning and final | Freeze dependencies, reproduce results, finish report, QA rubric, build final zip |

## Decision gates

- End of Module 1: select a provisional capstone option and begin the regression workflow.
- Module 3: confirm the selected option runs in the current Python environment.
- Module 4: submit the milestone and log instructor feedback.
- Module 5: lock evaluation metrics and experiment format.
- Module 6 or 7: complete the core implementation for Option 1 or Option 2 respectively.
- Module 8: perform only final analysis, evidence capture, documentation, and packaging.

## Selected capstone path

Final Portfolio Option 2 is locked. The sequence task has an objective exact-match accuracy measure, produces compact reproducible outputs, maps directly to Module 7, and avoids the long and visually subjective GAN training cycle.

For the Module 4 Portfolio Milestone, choose Option 2. This creates a coherent early-course path:

`M1 configurable regression -> M2 sales regression -> M3 Auto MPG -> M4 early stopping and residual analysis`

This code should not be forced directly into the LSTM implementation. Instead, reuse the engineering practices: deterministic seeds, explicit train/validation/test separation, normalization, model construction functions, early stopping, held-out metrics, prediction evidence, and documented conclusions.

Module 6 is the final capstone decision gate. Its CIFAR-10 CNN Option 1 is directly reusable if the GAN becomes preferable; otherwise, complete it as a focused CNN exercise and proceed to the encoder-decoder LSTM in Module 7.
