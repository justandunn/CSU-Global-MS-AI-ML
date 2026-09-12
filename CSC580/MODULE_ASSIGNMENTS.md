# CSC580 Weekly Assignment Map

This map records the assignment choices visible in Canvas after BioSig-ID validation was cleared. Always re-check Canvas for instructor announcements, revised dates, and filename formatting before submission.

## Module 1

- Option 1: detect faces in an image with `face_recognition` and Pillow.
- Option 2: fit a configurable four-to-eight-variable linear equation with scikit-learn regression.
- Recommended: Option 2 for validation and regression workflow reuse.

## Module 2

- Option 1: classify MNIST digits with a multilayer perceptron; vary neurons, learning rates, hidden layers, and batch sizes.
- Option 2: predict video-game sales with Keras; scale train/test CSVs, train for 50 epochs, report test MSE, save/reload the model, and predict a proposed product.
- Recommended: Option 2 for scaling, model persistence, and regression continuity.

## Module 3

- Option 1: implement linear regression with TensorFlow on generated data.
- Option 2: predict fuel efficiency with the Auto MPG dataset; normalize inputs, train two dense regression models, compare MAE and MSE variants, and document plots and screenshots.
- Recommended: Option 2 because Module 4 Portfolio Milestone Option 2 explicitly extends it.

## Module 4

### Critical Thinking

- Option 1: predict Tox21 toxicity with a neural network, dropout, accuracy analysis, and TensorBoard evidence.
- Option 2: synthetic logistic regression with TensorFlow and plotted predictions.
- Choice can be made independently of the milestone. Prefer the option with the cleanest modern TensorFlow compatibility after a short environment spike.

### Portfolio Milestone

- Option 1: extend Module 1 face detection into identity recognition within a group.
- Option 2: improve the Module 3 Auto MPG model with `EarlyStopping`, evaluate held-out MAE/MSE, plot true versus predicted MPG, plot prediction errors, and analyze every screenshot in Word.
- Recommended: Option 2.
- Required archive name shown by Canvas: `CSC580_MidTermPortfolio _Option_2_last_name_first_name.zip`. Verify the apparent extra space before final packaging.

## Module 5

- Option 1: tune the Module 4 Tox21 network across hyperparameters and repeated random seeds, then identify the best model.
- Option 2: build an Iris random-forest classifier, report probabilities, compare predictions with actual classes, and supply a confusion matrix.
- Recommendation depends on Module 4 CT choice: choose Option 1 only if Module 4 CT Option 1 was completed; otherwise use Option 2.

## Module 6

- Option 1: classify CIFAR-10 images with a TensorFlow CNN and explain model veracity using the supplied flowchart.
- Option 2: classify Kaggle dog/cat images, compare one- and two-convolution-layer models, measure correlation/accuracy, save the model, and build a simple prediction interface.
- Recommended: Option 1 because CIFAR-10 and CNN utilities directly prepare for final Portfolio Option 1 if we switch to the GAN.

## Module 7

- No Critical Thinking assignment is listed.
- Use the available development time for the final encoder-decoder LSTM spike: sequence generator, one-hot encoding, training/inference models, exact-match evaluation, and flowchart draft.

## Module 8

- Submit one final Portfolio option only: CIFAR-10 GAN or encoder-decoder LSTM.
- Current recommendation: encoder-decoder LSTM.
- Complete the four-use-case research paper, implementation, evidence, analysis, APA QA, and archive verification.

## Reusable QA contract

Every programming assignment should capture:

- Python and package versions.
- Deterministic seeds where supported.
- Input schema, shapes, and sample counts.
- Explicit train/validation/test boundaries.
- Model configuration and hyperparameters.
- Runtime command and console output.
- Required metrics and plots.
- Screenshot-to-analysis traceability.
- Rubric and archive-content verification.
