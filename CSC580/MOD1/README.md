# Module 1: Introduction to Deep Learning

## Due pattern

- Initial discussion post: Thursday, July 23, 2026, 11:59 p.m. MT.
- Two or more substantive replies: Sunday, July 26, 2026, 11:59 p.m. MT.
- Critical Thinking Assignment: Sunday, July 26, 2026, 11:59 p.m. MT.

Canvas currently displays no item-level due date, but the instructor announcement states the weekly Thursday/Sunday schedule above.

## Discussion Forum (25 points)

Explain useful deep-learning applications beyond computer vision, identify the architectures used (such as CNN or RNN), and analyze likely industry impacts. Support the post with at least two credible sources from the CSU Global Library.

The instructor additionally encourages original screenshots, charts, graphs, or figures as evidence. The initial post must be unique and substantive; submit at least two substantive replies that add analysis or ask/answer a thoughtful question.

### Discussion workflow

- [x] Select two non-computer-vision applications from different industries.
- [x] Map each application to a specific architecture and explain why it fits.
- [ ] Verify the two selected scholarly articles through the CSU Global Library; APA metadata is recorded in the draft.
- [x] Draft claim-evidence-analysis paragraphs with matching citations.
- [ ] Add an original architecture comparison table or figure if useful.
- [ ] Post by Thursday and save a local copy.
- [ ] Write two distinct peer replies by Sunday.

## Critical Thinking Assignment (70 points)

Complete one option only and identify the option in the submission title.

### Option 1: Face detection

Complete the supplied Python starter using `face_recognition` and Pillow. Supply an image containing one or more faces, detect each face, print its pixel coordinates, and draw red boxes around faces. Submit the input image and Python source as `CSC580_CTA_1_1_Dunn_Justan.zip`.

### Option 2: Configurable linear-equation learner

Create a Python program that accepts coefficients for a linear equation containing four to eight variables, generates conforming training data, fits a scikit-learn linear regression model, prompts for test inputs, and prints predicted and actual values. Submit the Python solution as `CSC580_CTA_1_2_Dunn_Justan.zip`.

### Recommendation

Choose Option 2. It builds the reusable validation, model-training, prediction, and expected-versus-actual reporting pattern needed for either capstone track. It is also more portable on Windows than the native dependencies commonly required by `face_recognition`.

### Implementation checklist for Option 2

- [x] Validate that the variable count is between four and eight.
- [x] Validate coefficient and test-input counts and numeric types.
- [x] Use a reproducible random-number generator seed.
- [x] Keep data generation, fitting, prediction, and console interaction in separate functions.
- [x] Print learned coefficients, predicted value, actual value, and absolute error.
- [x] Add automated tests for calculation, validation, reproducibility, and model accuracy.
- [x] Run from the isolated workspace environment and save text evidence.
- [ ] Inspect the zip contents and filename before submission.

## Portfolio reminder

Review both Module 8 options now. The Module 4 milestone is available after BioSig-ID validation. Its recommended Option 2 extends Module 3's Auto MPG regression assignment with early stopping, held-out evaluation, prediction plots, and error-distribution analysis.
