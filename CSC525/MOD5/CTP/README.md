# CSC525 Module 5 Critical Thinking Project

Student: Justan Dunn  
Assignment choice: Option #1: Text Dataset Augmentation

## Dataset

This submission uses a sampled subset of the Bitext Customer Support LLM Chatbot Training Dataset. The original dataset contains customer-service instruction text, support categories, intent labels, and response text. The submitted raw file is a balanced sample of 135 rows, with five non-`Z` source rows selected for each of the 27 intents. Rows with `Z` in the Bitext `flags` field were excluded from the submitted seed sample to avoid typo/noise variants in the un-augmented file.

Source links:

- Hugging Face: https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset
- GitHub: https://github.com/bitext/customer-support-llm-chatbot-training-dataset

## Files

- `augment_text_dataset.py`: Python script that augments a CSV, TSV, or TXT text dataset.
- `data/raw/bitext_customer_support_seed.csv`: Un-augmented Bitext seed dataset sample.
- `data/augmented/bitext_customer_support_augmented.csv`: Augmented output dataset.
- `outputs/augmentation_summary.json`: Machine-readable run summary.
- `outputs/run_output.txt`: Console output from the successful script run.
- `outputs/validation_check.txt`: Validation results for row counts, metadata columns, labels, and intent balance.
- `dataset_candidates.md`: Dataset selection notes.

## What Was Augmented

The script augments the `instruction` field, which contains the customer support request text. It preserves the original `category`, `intent`, `response`, placeholder tokens such as `{{Order Number}}`, and source metadata. Each source row produces two augmented variants, and the output file also includes the original row for auditability.

The submitted run created:

- 135 original rows.
- 270 augmented rows.
- 405 total output rows.

The augmentation methods are:

- Phrase replacement: swaps common support phrases with intent-preserving alternatives, such as `can you` and `could you`.
- Polite request framing: adds a customer-service request frame.
- Customer-support context framing: adds a short support-chat context phrase.
- Next-step framing: adds wording that asks for support routing or the next action.

## How to Run

From the `CSC525` course folder:

```powershell
python MOD5\CTP\augment_text_dataset.py `
  --input MOD5\CTP\data\raw\bitext_customer_support_seed.csv `
  --text-column instruction `
  --output MOD5\CTP\data\augmented\bitext_customer_support_augmented.csv `
  --summary MOD5\CTP\outputs\augmentation_summary.json `
  --augmentations-per-row 2 `
  --seed 525
```

The script uses only the Python standard library. No package installation is required.

## AI-Use Note

AI assistance was used to help structure the Python script, organize the submission package, and draft this description. The dataset selection, script execution, output files, and validation checks were reviewed and run locally before submission.
