# CSC525 Module 8 Portfolio Project

Student: Justan Dunn  
Assignment: Option #2 - NLP Chatbot Final Version

## Project Summary

This submission contains a closed-domain customer-service routing and retrieval
chatbot. It uses character n-gram TF-IDF features and a supervised route-centroid
classifier to interpret a customer message. High-confidence messages receive an
approved route-specific response. Uncertain or unrelated messages receive a safe
fallback that requests clarification or human escalation.

The chatbot does not generate company policies or invent open-domain answers.
Its ten supported routes are:

- Account Access
- Billing and Invoice
- Escalation
- Onboarding
- Order Status
- Policy Lookup
- Returns and Refunds
- Service Scheduling
- Technical Support
- Training Materials

## Fastest Way to Run

On Windows, double-click:

`run_chatbot.bat`

The launcher opens the interactive chatbot. Enter a customer-service message at
the `You:` prompt. Enter `/topics` to list supported topics, `/help` for commands,
or `/quit` to exit.

## PowerShell Commands

From this folder:

```powershell
python chatbot.py --interactive
```

Run the prepared demonstration:

```powershell
python chatbot.py --demo
```

Run one message:

```powershell
python chatbot.py --message "I reset my password and cannot access the portal"
```

Return machine-readable output:

```powershell
python chatbot.py --message "Where is my shipment?" --json
```

Python 3.10 or newer is recommended. No third-party packages are required.

## Model and Evaluation

The final model was selected using an independent 52-message calibration set.
The final test set contains 62 raw messages: 50 in-domain messages and 12
out-of-domain messages. Unlike the Module 5 `combined_text` evaluation, no route
labels or curated keyword banks are appended to calibration or test inputs.

Final test results:

- Raw route accuracy: 0.9200
- In-domain coverage after fallback: 0.9000
- Accuracy among accepted in-domain messages: 0.9333
- Out-of-domain rejection rate: 0.7500
- Overall decision accuracy: 0.8226

The results are intentionally reported with the remaining errors. This is a
coursework prototype, not a production customer-service system.

## Rebuild the Project

The generated training data and model are included, so rebuilding is optional.
To reproduce all model artifacts:

```powershell
python build_final_datasets.py
python train_final_chatbot.py
python chatbot.py --demo
python validate_submission.py
```

## Important Files

- `chatbot.py`: final interactive chatbot entry point.
- `chatbot_model.py`: portable TF-IDF feature and centroid-classifier logic.
- `model/chatbot_model.json`: trained model and calibrated thresholds.
- `data/training_corpus.csv`: sanitized 80-message FAQ/SOP training corpus.
- `data/calibration_messages.csv`: independent threshold-selection data.
- `data/test_messages.csv`: independent final evaluation data.
- `outputs/final_metrics.json`: calibration and final test metrics.
- `outputs/test_predictions.csv`: row-level final-test results.
- `outputs/final_demo_transcript.txt`: prepared chatbot demonstration.
- `report/CSC525_Module8PP_Dunn_Justan.docx`: APA final report.
- `report/CSC525_Module8PP_Dunn_Justan.pdf`: PDF copy of the report.

## Privacy and Scope

The corpus contains synthetic, sanitized coursework examples. It contains no
private company, employee, or customer data. A real deployment would require
approved source content, security review, monitoring, and evaluation using the
organization's actual support language.
