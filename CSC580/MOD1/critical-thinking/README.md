# Module 1 Critical Thinking Assignment — Option 2

This program asks for four through eight linear-equation coefficients, generates deterministic synthetic training observations, fits a scikit-learn `LinearRegression` model, and compares its prediction with the equation's exact output.

## Windows setup

From the `CSC580` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\MOD1\critical-thinking\requirements.txt
```

## Reproducible assignment run

```powershell
.\.venv\Scripts\python.exe .\MOD1\critical-thinking\src\csc580_cta_1_option_2.py `
  --coefficients "1,2,3,4" `
  --inputs "10,20,30,40" `
  --seed 580
```

Run without `--coefficients` and `--inputs` to use the required interactive prompts.

## Automated tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover `
  -s .\MOD1\critical-thinking\tests `
  -p "test_*.py" `
  -v
```

## Submission checklist

- [ ] Run the interactive workflow successfully.
- [ ] Capture a legible screenshot showing supplied coefficients, learned coefficients, prediction, actual value, and error.
- [ ] Confirm the code contains four-to-eight-variable validation.
- [ ] Run all automated tests.
- [ ] Place only the required Python solution in `CSC580_CTA_1_2_Dunn_Justan.zip` unless the instructor requests supporting evidence.
- [ ] Open the zip and verify its contents before upload.

