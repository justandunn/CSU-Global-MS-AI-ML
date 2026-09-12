"""QA-only DOCX to PDF conversion through the installed Microsoft Word engine."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QA_DEPS = ROOT / "qa_dependencies"
sys.path[:0] = [str(QA_DEPS), str(QA_DEPS / "win32"), str(QA_DEPS / "win32" / "lib")]
os.add_dll_directory(str(QA_DEPS / "pywin32_system32"))

import win32com.client  # type: ignore  # noqa: E402


def main() -> None:
    source = (ROOT / "CSC580_FinalPortfolio_Option_2_Dunn_Justan.docx").resolve()
    target = (ROOT / "docx_render" / "CSC580_FinalPortfolio_Option_2_Dunn_Justan.pdf").resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    document = None
    try:
        document = word.Documents.Open(str(source), ReadOnly=True)
        document.ExportAsFixedFormat(str(target), 17)
    finally:
        if document is not None:
            document.Close(False)
        word.Quit()
    print(target)


if __name__ == "__main__":
    main()
