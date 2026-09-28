# CSC525 Module 6 Portfolio Milestone

Student: Justan Dunn  
Assignment choice: Option #2: NLP Chatbot Project Alpha

## Purpose

This package keeps the Module 8 portfolio project aligned with the prior
Module 4 and Module 5 portfolio milestones. The selected project remains a
closed-domain customer-service routing and retrieval chatbot.

## Current Alpha

The alpha chatbot is implemented in:

`chatbot_alpha.py`

It uses the sanitized custom enterprise FAQ/SOP corpus selected in the Module 4
data plan and trained in the Module 5 milestone:

`data/custom_enterprise_faq_sop_corpus.csv`

The alpha uses a dependency-free TF-IDF cosine-similarity retriever. A user
message is transformed into the same feature space as the FAQ/SOP entries, the
closest approved entry is selected, and the chatbot returns the approved answer
when the similarity score is above the current alpha threshold.

## Alpha Demo Result

The included demo uses eight customer-service messages:

- 7 in-domain messages accepted.
- 1 out-of-domain message sent to fallback / human escalation.
- Runtime threshold: 0.35.

Outputs:

- `outputs/alpha_demo_transcript.txt`
- `outputs/alpha_demo_predictions.csv`
- `outputs/alpha_demo_run_output.txt`

## How to Reproduce

From the `CSC525` course folder:

```powershell
python MOD6\PM\chatbot_alpha.py --demo

python MOD6\PM\build_module6_pm.py

python MOD6\PM\validate_module6_pm.py
```

To run a custom message:

```powershell
python MOD6\PM\chatbot_alpha.py --message "I need help getting into my account"
```

To use the interactive local chat loop:

```powershell
python MOD6\PM\chatbot_alpha.py --interactive
```

## Deliverables

- `report/CSC525_Module6PM_Dunn_Justan.docx`
- `report/CSC525_Module6PM_Dunn_Justan.pdf`
- `chatbot_alpha.py`
- `data/custom_enterprise_faq_sop_corpus.csv`
- `outputs/alpha_demo_transcript.txt`
- `outputs/alpha_demo_predictions.csv`
- `outputs/training_metrics_snapshot.json`
- `outputs/validation_check.txt`

## Project Continuity

The final Module 8 chatbot should continue this path:

- Keep the chatbot closed-domain.
- Expand the FAQ/SOP corpus with more paraphrases and ambiguous cases.
- Use RSiCS to test realistic customer-service phrasing.
- Use WikiQA-style answer relevance testing to refine fallback behavior.
- Package the final chatbot with clear run instructions and a concise technical
  report.
