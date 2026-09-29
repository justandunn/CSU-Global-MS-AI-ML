"""Validate the Module 6 Portfolio Milestone package."""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "report"
VALIDATION_PATH = OUTPUT_DIR / "validation_check.txt"

REQUIRED_FILES = [
    BASE_DIR / "README.md",
    BASE_DIR / "chatbot_alpha.py",
    BASE_DIR / "build_module6_pm.py",
    BASE_DIR / "validate_module6_pm.py",
    BASE_DIR / "data" / "custom_enterprise_faq_sop_corpus.csv",
    OUTPUT_DIR / "alpha_demo_transcript.txt",
    OUTPUT_DIR / "alpha_demo_predictions.csv",
    OUTPUT_DIR / "alpha_demo_run_output.txt",
    OUTPUT_DIR / "training_metrics_snapshot.json",
    REPORT_DIR / "CSC525_Module6PM_Dunn_Justan.docx",
    REPORT_DIR / "CSC525_Module6PM_Dunn_Justan.pdf",
    REPORT_DIR / "report_validation.txt",
]

REQUIRED_PHRASES = [
    "Option #2: NLP Chatbot Project Alpha",
    "closed-domain",
    "TF-IDF",
    "RSiCS",
    "WikiQA",
    "human escalation",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml_text = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml_text)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    return " ".join(node.text or "" for node in root.findall(".//w:t", namespace))


def pdf_text_and_pages(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text, len(reader.pages)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["Module 6 PM validation"]

    missing = [str(path.relative_to(BASE_DIR)) for path in REQUIRED_FILES if not path.exists()]
    lines.append(f"Missing required files: {missing}")

    corpus_rows = read_csv(BASE_DIR / "data" / "custom_enterprise_faq_sop_corpus.csv")
    route_labels = sorted({row["route_label"] for row in corpus_rows})
    lines.append(f"Corpus rows: {len(corpus_rows)}")
    lines.append(f"Distinct routes: {len(route_labels)}")

    predictions = read_csv(OUTPUT_DIR / "alpha_demo_predictions.csv")
    accepted = [
        row
        for row in predictions
        if str(row.get("above_threshold", "")).lower() == "true"
    ]
    fallback = len(predictions) - len(accepted)
    lines.append(f"Alpha demo exchanges: {len(predictions)}")
    lines.append(f"Accepted responses: {len(accepted)}")
    lines.append(f"Fallback responses: {fallback}")

    metrics = json.loads(
        (OUTPUT_DIR / "training_metrics_snapshot.json").read_text(encoding="utf-8")
    )
    lines.append(f"Training snapshot train rows: {metrics['train_rows']}")
    lines.append(f"Training snapshot test rows: {metrics['test_rows']}")
    lines.append(f"Training snapshot accuracy: {metrics['metrics']['accuracy']}")
    lines.append(f"Training snapshot macro F1: {metrics['metrics']['macro_f1']}")

    report_docx = REPORT_DIR / "CSC525_Module6PM_Dunn_Justan.docx"
    report_pdf = REPORT_DIR / "CSC525_Module6PM_Dunn_Justan.pdf"
    docx_body = docx_text(report_docx)
    pdf_body, page_count = pdf_text_and_pages(report_pdf)
    lines.append(f"PDF page count: {page_count}")

    for phrase in REQUIRED_PHRASES:
        in_docx = phrase in docx_body
        in_pdf = phrase in pdf_body
        lines.append(f"Phrase '{phrase}' in DOCX: {in_docx}")
        lines.append(f"Phrase '{phrase}' in PDF: {in_pdf}")

    passed = (
        not missing
        and len(corpus_rows) == 80
        and len(route_labels) == 10
        and len(predictions) == 8
        and len(accepted) >= 6
        and fallback >= 1
        and page_count >= 4
        and all(phrase in docx_body and phrase in pdf_body for phrase in REQUIRED_PHRASES)
    )
    lines.append(f"Validation passed: {passed}")

    VALIDATION_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(VALIDATION_PATH)
    print("\n".join(lines))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
