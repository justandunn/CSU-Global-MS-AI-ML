"""Validate the final Module 8 chatbot package and generated artifacts."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "report"
MODEL_PATH = BASE_DIR / "model" / "chatbot_model.json"
METRICS_PATH = OUTPUT_DIR / "final_metrics.json"
TEST_PREDICTIONS_PATH = OUTPUT_DIR / "test_predictions.csv"
TRANSCRIPT_PATH = OUTPUT_DIR / "final_demo_transcript.txt"
VALIDATION_PATH = OUTPUT_DIR / "validation_check.txt"
DOCX_PATH = REPORT_DIR / "CSC525_Module8PP_Dunn_Justan.docx"
PDF_PATH = REPORT_DIR / "CSC525_Module8PP_Dunn_Justan.pdf"
A11Y_PATH = OUTPUT_DIR / "docx_a11y_report.json"


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def pdf_page_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("rb") as file_obj:
        data = file_obj.read()
    return data.count(b"/Type /Page") - data.count(b"/Type /Pages")


def main() -> int:
    required = [
        BASE_DIR / "README.md",
        BASE_DIR / "requirements.txt",
        BASE_DIR / "run_chatbot.bat",
        BASE_DIR / "build_final_datasets.py",
        BASE_DIR / "chatbot_model.py",
        BASE_DIR / "train_final_chatbot.py",
        BASE_DIR / "chatbot.py",
        BASE_DIR / "data" / "training_corpus.csv",
        BASE_DIR / "data" / "calibration_messages.csv",
        BASE_DIR / "data" / "test_messages.csv",
        MODEL_PATH,
        METRICS_PATH,
        TEST_PREDICTIONS_PATH,
        TRANSCRIPT_PATH,
        DOCX_PATH,
        PDF_PATH,
    ]
    missing = [str(path.relative_to(BASE_DIR)) for path in required if not path.exists()]

    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else {}
    test_metrics = metrics.get("test_metrics", {})
    predictions = csv_rows(TEST_PREDICTIONS_PATH) if TEST_PREDICTIONS_PATH.exists() else []
    training = csv_rows(BASE_DIR / "data" / "training_corpus.csv")
    calibration = csv_rows(BASE_DIR / "data" / "calibration_messages.csv")
    tests = csv_rows(BASE_DIR / "data" / "test_messages.csv")

    training_questions = {row["sample_question"].strip().lower() for row in training}
    evaluation_messages = {
        row["message"].strip().lower() for row in calibration + tests
    }
    exact_overlap = training_questions.intersection(evaluation_messages)

    demo = subprocess.run(
        [sys.executable, str(BASE_DIR / "chatbot.py"), "--demo"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    transcript = TRANSCRIPT_PATH.read_text(encoding="utf-8") if TRANSCRIPT_PATH.exists() else ""
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8")) if MODEL_PATH.exists() else {}
    a11y = json.loads(A11Y_PATH.read_text(encoding="utf-8")) if A11Y_PATH.exists() else {}
    runtime_source = "\n".join(
        (BASE_DIR / filename).read_text(encoding="utf-8")
        for filename in ("chatbot.py", "chatbot_model.py")
    )

    checks = {
        "missing_required_files": missing,
        "training_rows": len(training),
        "calibration_rows": len(calibration),
        "test_rows": len(tests),
        "test_prediction_rows": len(predictions),
        "training_evaluation_exact_overlap": len(exact_overlap),
        "distinct_routes": int(metrics.get("distinct_routes", 0)),
        "selected_config": metrics.get("selected_config", {}).get("name"),
        "raw_route_accuracy": test_metrics.get("raw_route_accuracy"),
        "overall_decision_accuracy": test_metrics.get("overall_decision_accuracy"),
        "out_of_domain_rejection_rate": test_metrics.get("out_of_domain_rejection_rate"),
        "demo_exit_code": demo.returncode,
        "demo_exchange_count": transcript.count("Exchange "),
        "demo_has_fallback": "confidence=low" in transcript,
        "model_has_keyword_bank_in_runtime_input": (
            "combined_text" in runtime_source or "keywords" in runtime_source
        ),
        "docx_a11y_findings": sum(a11y.get("counts", {}).values()),
        "docx_bytes": DOCX_PATH.stat().st_size if DOCX_PATH.exists() else 0,
        "pdf_bytes": PDF_PATH.stat().st_size if PDF_PATH.exists() else 0,
        "pdf_page_count": pdf_page_count(PDF_PATH),
        "model_vocabulary_size": len(model.get("vocabulary", [])),
    }

    passed = (
        not missing
        and checks["training_rows"] == 80
        and checks["calibration_rows"] == 52
        and checks["test_rows"] == 62
        and checks["test_prediction_rows"] == 62
        and checks["training_evaluation_exact_overlap"] == 0
        and checks["distinct_routes"] == 10
        and float(checks["raw_route_accuracy"] or 0) >= 0.80
        and float(checks["overall_decision_accuracy"] or 0) >= 0.70
        and float(checks["out_of_domain_rejection_rate"] or 0) >= 0.60
        and checks["demo_exit_code"] == 0
        and checks["demo_exchange_count"] == 8
        and checks["demo_has_fallback"]
        and not checks["model_has_keyword_bank_in_runtime_input"]
        and checks["docx_a11y_findings"] == 0
        and checks["docx_bytes"] > 10_000
        and checks["pdf_bytes"] > 10_000
        and checks["pdf_page_count"] >= 5
        and checks["model_vocabulary_size"] > 100
    )

    lines = ["CSC525 Module 8 Portfolio Project Validation"]
    lines.extend(f"{key}: {value}" for key, value in checks.items())
    lines.append(f"Validation passed: {passed}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(VALIDATION_PATH.read_text(encoding="utf-8"))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
