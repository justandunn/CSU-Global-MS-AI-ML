"""Create the instructor-ready Module 8 Portfolio Project archive."""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PACKAGE_NAME = "CSC525_Module8PP_Dunn_Justan"
ZIP_PATH = BASE_DIR / f"{PACKAGE_NAME}_submission_package.zip"
MANIFEST_PATH = BASE_DIR / "outputs" / "package_manifest.json"

PACKAGE_FILES = [
    Path("README.md"),
    Path("requirements.txt"),
    Path("run_chatbot.bat"),
    Path("chatbot.py"),
    Path("chatbot_model.py"),
    Path("build_final_datasets.py"),
    Path("train_final_chatbot.py"),
    Path("validate_submission.py"),
    Path("data/training_corpus.csv"),
    Path("data/calibration_messages.csv"),
    Path("data/test_messages.csv"),
    Path("model/chatbot_model.json"),
    Path("outputs/final_metrics.json"),
    Path("outputs/hyperparameter_sweep.csv"),
    Path("outputs/calibration_predictions.csv"),
    Path("outputs/test_predictions.csv"),
    Path("outputs/confusion_matrix.csv"),
    Path("outputs/final_demo_transcript.txt"),
    Path("outputs/validation_check.txt"),
    Path("outputs/docx_a11y_report.json"),
    Path("report/CSC525_Module8PP_Dunn_Justan.docx"),
    Path("report/CSC525_Module8PP_Dunn_Justan.pdf"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    missing = [str(path) for path in PACKAGE_FILES if not (BASE_DIR / path).exists()]
    if missing:
        raise FileNotFoundError("Missing package files: " + ", ".join(missing))

    entries = [
        {
            "path": str(path).replace("\\", "/"),
            "bytes": (BASE_DIR / path).stat().st_size,
            "sha256": sha256(BASE_DIR / path),
        }
        for path in PACKAGE_FILES
    ]
    manifest = {
        "package": PACKAGE_NAME,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(entries),
        "files": entries,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    archive_files = PACKAGE_FILES + [Path("outputs/package_manifest.json")]
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative_path in archive_files:
            archive_name = Path(PACKAGE_NAME) / relative_path
            archive.write(BASE_DIR / relative_path, archive_name.as_posix())

    with zipfile.ZipFile(ZIP_PATH) as archive:
        corrupt = archive.testzip()
        names = archive.namelist()
    if corrupt:
        raise RuntimeError(f"Archive CRC validation failed for {corrupt}")
    if len(names) != len(archive_files):
        raise RuntimeError("Archive file count does not match package manifest.")

    print(f"Package: {ZIP_PATH.resolve()}")
    print(f"Files: {len(names)}")
    print(f"Bytes: {ZIP_PATH.stat().st_size}")
    print("Archive CRC validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
