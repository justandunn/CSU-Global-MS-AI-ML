# CSC580 Module 2 Critical Thinking Assignment

This directory contains Option 2, **Predicting Future Sales**.

## Run

From the `CSC580` directory in PowerShell:

```powershell
.\.venv\Scripts\python.exe .\MOD2\critical-thinking\train_sales_model.py 2>&1 |
    Tee-Object .\MOD2\critical-thinking\output\run_output.txt
```

The program validates the supplied datasets, fits feature and target scalers on
the training data only, trains the required dense Keras network for 50 epochs,
evaluates the held-out test set, saves and reloads the trained model, and makes
the proposed-product earnings prediction.

## Submission contents

- APA-formatted Word report
- `train_sales_model.py`
- Source CSV files
- Training and evaluation screenshots
- `trained_model.h5`
- Reproducibility files and detailed outputs

