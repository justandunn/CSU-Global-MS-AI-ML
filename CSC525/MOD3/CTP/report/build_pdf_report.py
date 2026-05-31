"""Build the Module 3 Critical Thinking Project PDF report."""

from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "report"
OUTPUTS_DIR = ROOT / "outputs"
PDF_PATH = REPORT_DIR / "module3_ctp_report.pdf"
CONSOLE_IMAGE = OUTPUTS_DIR / "console_output_screenshot.png"
CODE_IMAGE = OUTPUTS_DIR / "code_excerpt_screenshot.png"
PLOT_IMAGE = OUTPUTS_DIR / "polynomial_regression_fit.png"


def image_flowable(path: Path, max_width: float = 6.35 * inch, max_height: float = 7.0 * inch) -> Image:
    with PILImage.open(path) as image:
        width_px, height_px = image.size
    ratio = min(max_width / width_px, max_height / height_px)
    return Image(str(path), width=width_px * ratio, height=height_px * ratio)


def build_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "APA Title",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=12,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        "center": ParagraphStyle(
            "APA Center",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        "heading": ParagraphStyle(
            "APA Heading",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=12,
            leading=24,
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "body": ParagraphStyle(
            "APA Body",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            leading=24,
            alignment=TA_LEFT,
            firstLineIndent=0.5 * inch,
            spaceAfter=0,
        ),
        "figure_number": ParagraphStyle(
            "APA Figure Number",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=12,
            leading=24,
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=0,
        ),
        "figure_title": ParagraphStyle(
            "APA Figure Title",
            parent=styles["Normal"],
            fontName="Times-Italic",
            fontSize=12,
            leading=18,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "note": ParagraphStyle(
            "APA Note",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            leading=18,
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=6,
        ),
        "reference": ParagraphStyle(
            "APA Reference",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            leading=24,
            alignment=TA_LEFT,
            leftIndent=0.5 * inch,
            firstLineIndent=-0.5 * inch,
            spaceAfter=0,
        ),
    }


def add_page_number(canvas, _doc) -> None:
    canvas.saveState()
    canvas.setFont("Times-Roman", 12)
    canvas.drawRightString(7.5 * inch, 10.5 * inch, str(canvas.getPageNumber()))
    canvas.restoreState()


def add_figure(story: list, styles: dict[str, ParagraphStyle], number: int, title: str, path: Path, note: str) -> None:
    story.append(Paragraph(f"Figure {number}", styles["figure_number"]))
    story.append(Paragraph(title, styles["figure_title"]))
    story.append(image_flowable(path))
    story.append(Paragraph(f"<i>Note.</i> {note}", styles["note"]))


def build_pdf() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=LETTER,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
        title="Module 3 Critical Thinking Project Report",
        author="Student Name",
    )

    story: list = []
    story.extend([Spacer(1, 1.4 * inch)])
    story.append(Paragraph("Simple Polynomial Regression in Python:", styles["title"]))
    story.append(Paragraph("Predicting Salary From Years of Experience", styles["title"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("Student Name", styles["center"]))
    story.append(Paragraph("Colorado State University Global", styles["center"]))
    story.append(Paragraph("CSC525: Principles of Machine Learning", styles["center"]))
    story.append(Paragraph("Dong Nguyen", styles["center"]))
    story.append(Paragraph("May 30, 2026", styles["center"]))
    story.append(PageBreak())

    story.append(Paragraph("Simple Polynomial Regression in Python", styles["heading"]))
    story.append(
        Paragraph(
            "This project used polynomial regression to predict salary from years of experience. "
            "Polynomial regression extends a basic linear relationship by adding powered terms for the independent "
            "variable, which allows the fitted model to represent mild curvature in the data (W3Schools, n.d.). "
            "The dataset contained 30 observations with two fields: years of experience and salary (rohankayan, n.d.).",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "The Python script validates the local CSV file, separates the data into training and test sets, fits a "
            "second-degree polynomial using NumPy least squares, and reports performance on the held-out test set. "
            "NumPy was used for the polynomial fit and numerical evaluation because it provides efficient array "
            "operations for scientific computing (Harris et al., 2020).",
            styles["body"],
        )
    )
    story.append(Paragraph("Results", styles["heading"]))
    story.append(
        Paragraph(
            "The model produced an R-squared value of .9572 on the held-out test data, with a root mean squared error "
            "of $5,026.08 and a mean absolute error of $3,835.38. These results indicate that a simple degree-2 "
            "polynomial model captured most of the relationship between experience and salary in this small dataset. "
            "The output also demonstrates salary predictions for candidates with 2.5, 5.0, 7.5, and 10.0 years of experience.",
            styles["body"],
        )
    )
    story.append(PageBreak())
    add_figure(
        story,
        styles,
        1,
        "Console Output From the Polynomial Regression Script",
        CONSOLE_IMAGE,
        "The primary output screenshot shows the model equation, train/test split, evaluation metrics, and sample salary predictions.",
    )
    story.append(
        Paragraph(
            "The fitted curve visually follows the upward relationship in the observed data. However, the model is limited "
            "by the small number of records and by the fact that real salary outcomes depend on many additional variables, "
            "including role, location, education, industry, and market conditions.",
            styles["body"],
        )
    )
    story.append(PageBreak())
    add_figure(
        story,
        styles,
        2,
        "Observed Salary Values and Degree-2 Polynomial Fit",
        PLOT_IMAGE,
        "The blue points represent observed salaries, and the red curve represents the polynomial regression fit.",
    )
    story.append(Paragraph("Code Evidence", styles["heading"]))
    story.append(
        Paragraph(
            "The executable Python file is submitted separately. Figure 3 shows the main model training, evaluation, "
            "and prediction section of the script.",
            styles["body"],
        )
    )
    story.append(PageBreak())
    add_figure(
        story,
        styles,
        3,
        "Code Excerpt Showing Model Training and Output Generation",
        CODE_IMAGE,
        "The excerpt shows the main workflow used to load data, fit the polynomial model, evaluate it, and print predictions.",
    )
    story.append(PageBreak())
    story.append(Paragraph("References", styles["heading"]))
    story.append(
        Paragraph(
            "Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., "
            "Wieser, E., Taylor, J., Berg, S., Smith, N. J., Kern, R., Picus, M., Hoyer, S., van Kerkwijk, "
            "M. H., Brett, M., Haldane, A., Fernandez del Rio, J., Wiebe, M., Peterson, P., ... Oliphant, "
            "T. E. (2020). Array programming with NumPy. <i>Nature, 585</i>(7825), 357-362. "
            "https://doi.org/10.1038/s41586-020-2649-2",
            styles["reference"],
        )
    )
    story.append(
        Paragraph(
            "rohankayan. (n.d.). <i>Years of experience and salary dataset</i> [Data set]. Kaggle. "
            "https://www.kaggle.com/datasets/rohankayan/years-of-experience-and-salary-dataset",
            styles["reference"],
        )
    )
    story.append(
        Paragraph(
            "W3Schools. (n.d.). <i>Machine learning - Polynomial regression.</i> "
            "https://www.w3schools.com/python/python_ml_polynomial_regression.asp",
            styles["reference"],
        )
    )

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(PDF_PATH)


if __name__ == "__main__":
    build_pdf()
