"""Rasterize the Word-exported QA PDF to page PNGs for visual inspection."""

from pathlib import Path

import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "docx_render" / "CSC580_FinalPortfolio_Option_2_Dunn_Justan.pdf"


def main() -> None:
    document = pdfium.PdfDocument(PDF)
    for index, page in enumerate(document):
        bitmap = page.render(scale=2.0)
        image = bitmap.to_pil()
        image.save(ROOT / "docx_render" / f"page-{index + 1}.png")
    print(f"Rendered {len(document)} pages")


if __name__ == "__main__":
    main()
