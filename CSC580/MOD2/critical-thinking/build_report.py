"""Build the APA-style Word report for CSC580 Module 2 Option 2."""

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
REPORT_DIR = ROOT / "report"
REPORT_PATH = REPORT_DIR / "CSC580_CTA_2_2_Dunn_Justan.docx"


def set_font(run, size: float = 12, bold: bool = False, italic: bool = False) -> None:
    run.font.name = "Times New Roman"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Times New Roman")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = "PAGE"
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    value = OxmlElement("w:t")
    value.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, value, end])
    set_font(run)


def add_body_paragraph(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.first_line_indent = Inches(0.5)
    paragraph.paragraph_format.line_spacing = 2
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    set_font(paragraph.add_run(text))


def add_heading(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.style = doc.styles["Heading 1"]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.line_spacing = 2
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    run = paragraph.add_run(text)
    set_font(run, bold=True)


def add_figure(doc: Document, image_path: Path, number: int, title: str, alt: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.keep_with_next = True
    paragraph.paragraph_format.space_after = Pt(0)
    run = paragraph.add_run(f"Figure {number}")
    set_font(run, bold=True)

    title_paragraph = doc.add_paragraph()
    title_paragraph.paragraph_format.keep_with_next = True
    title_paragraph.paragraph_format.space_after = Pt(6)
    set_font(title_paragraph.add_run(title), italic=True)

    picture_paragraph = doc.add_paragraph()
    picture_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture_paragraph.paragraph_format.keep_together = True
    picture_run = picture_paragraph.add_run()
    shape = picture_run.add_picture(str(image_path), width=Inches(6.25))
    doc_pr = shape._inline.docPr
    doc_pr.set("descr", alt)
    doc_pr.set("title", title)

    note = doc.add_paragraph()
    note.paragraph_format.line_spacing = 2
    note.paragraph_format.space_after = Pt(0)
    label = note.add_run("Note. ")
    set_font(label, italic=True)
    set_font(note.add_run("Generated from the actual program run completed for this assignment."))


def configure_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 2
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)

    heading = doc.styles["Heading 1"]
    heading.font.name = "Times New Roman"
    heading._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    heading._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    heading.font.size = Pt(12)
    heading.font.bold = True
    heading.font.color.rgb = None


def build_report() -> Path:
    metrics = json.loads((OUTPUT_DIR / "metrics.json").read_text(encoding="utf-8"))
    doc = Document()
    configure_styles(doc)

    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.5)
    section.footer_distance = Inches(0.5)
    add_page_number(section.header.paragraphs[0])

    # APA student title page.
    for _ in range(4):
        doc.add_paragraph()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.line_spacing = 2
    set_font(
        title.add_run("Option 2: Predicting Future Sales With a TensorFlow Neural Network"),
        bold=True,
    )
    for line in [
        "Justan Dunn",
        "Colorado State University Global",
        "CSC580-1: Applying Machine Learning and Neural Networks",
        "Dong Nguyen",
        "August 2, 2026",
    ]:
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.line_spacing = 2
        paragraph.paragraph_format.space_after = Pt(0)
        set_font(paragraph.add_run(line))

    doc.add_page_break()
    add_heading(doc, "Option 2: Predicting Future Sales With a TensorFlow Neural Network")

    add_body_paragraph(
        doc,
        "The purpose of this assignment was to construct a TensorFlow neural network that predicts total earnings for a proposed video game. The supplied data describe previously sold games through critic rating, genre indicators, exclusivity, portability, suitability for children, sequel status, and unit price. These features create a supervised regression problem because the required output, total earnings, is a continuous dollar amount. The completed workflow validated the source files, scaled the features and target, trained and evaluated a dense neural network, saved and reloaded the model, and generated a final prediction for the proposed product. The implementation also preserved the separation between training and testing data so that reported performance represents observations not used to fit the network.",
    )

    add_heading(doc, "Data Preparation")
    add_body_paragraph(
        doc,
        f"The training dataset contained {metrics['training_rows']:,} records, and the independent test dataset contained {metrics['testing_rows']:,} records. Each supervised record contained nine model inputs and the total_earnings target. Before training, the program verified the expected column order, confirmed that all values were numeric, checked for missing values, and verified that the proposed-product file contained exactly one row. The program used separate MinMaxScaler objects for the features and target. Both scalers were fitted only on the training dataset and then applied to the test dataset. This approach prevents information from the test set from influencing the fitted scaling parameters. The proposed-product row supplied with the course files was already represented on the zero-to-one scale and was validated before prediction.",
    )
    add_body_paragraph(
        doc,
        "Scaling was important because the raw columns used substantially different ranges. Binary genre indicators were represented as zero or one, critic ratings used a small rating scale, unit prices were measured in dollars, and total earnings were much larger dollar values. Converting the variables to a common range allowed the optimizer to update the network weights without the earnings column numerically dominating the inputs. The fitted feature and target scalers were saved with the results so the preprocessing can be reproduced when the model is used again.",
    )

    add_heading(doc, "Neural Network Method")
    add_body_paragraph(
        doc,
        f"The TensorFlow {metrics['tensorflow_version']} implementation used a Keras Sequential model. The input layer accepted nine features. Three fully connected hidden layers contained 50, 100, and 50 neurons and used the rectified linear unit activation function. The single output neuron used a linear activation, which is appropriate for an unrestricted continuous prediction. The resulting model contained 10,701 trainable parameters. Mean squared error (MSE) served as the loss function, and the Adam optimizer adjusted the weights. The model trained for the required 50 epochs with shuffling enabled, a batch size of {metrics['batch_size']}, and verbose output. A fixed random seed of {metrics['seed']} was applied to Python, NumPy, and TensorFlow to improve reproducibility.",
    )
    add_body_paragraph(
        doc,
        "Figure 1 presents excerpts from the actual verbose output. Training loss decreased rapidly during the first several epochs and then remained low. The small increase near the final epochs indicates that additional training does not guarantee a better model. A stronger production workflow would reserve a validation set and use early stopping, but the present run retained the assignment’s required 50-epoch training procedure. Figure 2 shows the complete loss trajectory and makes the early convergence visible.",
    )

    add_figure(
        doc,
        OUTPUT_DIR / "training_verbose_output.png",
        1,
        "TensorFlow Training Output",
        "Terminal-style capture of the actual TensorFlow run showing dataset counts and selected epochs.",
    )
    add_figure(
        doc,
        OUTPUT_DIR / "training_loss.png",
        2,
        "Training Mean Squared Error Across 50 Epochs",
        "Line chart showing scaled training mean squared error decreasing across 50 epochs.",
    )

    add_heading(doc, "Results")
    add_body_paragraph(
        doc,
        f"On the held-out test dataset, scaled MSE was {metrics['scaled_test_mse']:.8f}. After converting predictions back into dollars, MSE was ${metrics['test_mse_dollars_squared']:,.2f} in squared-dollar units, root mean squared error (RMSE) was ${metrics['test_rmse_dollars']:,.2f}, and mean absolute error (MAE) was ${metrics['test_mae_dollars']:,.2f}. RMSE indicates the approximate scale of error while assigning greater influence to larger misses. MAE shows that the predictions differed from the actual earnings by approximately ${metrics['test_mae_dollars']:,.0f} on average. Reporting the dollar-based measures alongside scaled MSE makes the model’s accuracy easier to interpret than the assignment’s scaled loss alone.",
    )
    add_body_paragraph(
        doc,
        f"After evaluation, the trained model was saved as trained_model.h5 and reloaded from disk without retraining. The reloaded model predicted total earnings of ${metrics['proposed_product_prediction_dollars']:,.2f} for the proposed video game. This reload test demonstrated that the submitted model file contains a usable trained network rather than only an in-memory result. Figure 3 records the evaluation metrics, final prediction, and successful model reload reported by the actual program run.",
    )
    add_figure(
        doc,
        OUTPUT_DIR / "evaluation_prediction_output.png",
        3,
        "Test Evaluation and Proposed-Product Prediction",
        "Terminal-style capture of the actual test metrics, proposed-product prediction, and model reload confirmation.",
    )

    add_heading(doc, "Interpretation and Limitations")
    add_body_paragraph(
        doc,
        "The results demonstrate that a relatively small dense neural network can learn the relationship between the supplied game characteristics and historical earnings. However, the prediction should be interpreted within the boundaries of the dataset. The model does not include advertising expenditure, release timing, platform installed base, competition, geographic market, digital versus physical sales, or changing consumer preferences. It also produces a point estimate rather than a prediction interval. Consequently, the dollar output is a model-based estimate and should not be treated as a guaranteed revenue result.",
    )
    add_body_paragraph(
        doc,
        "Several improvements would strengthen a future version. A validation subset and early stopping could identify the epoch that best generalizes rather than automatically using the final epoch. Repeated runs with several random seeds would reveal how sensitive the result is to initialization. Alternative widths, learning rates, and regularization methods could be compared through a controlled experiment. Finally, the neural network should be evaluated against a simple linear-regression baseline. If the more complex model does not materially reduce held-out error, the simpler model may be easier to explain and maintain. These practices would extend the assignment from a successful demonstration into a more reliable forecasting workflow.",
    )

    add_heading(doc, "Conclusion")
    add_body_paragraph(
        doc,
        f"This project completed the full TensorFlow regression workflow required by Option 2. The program validated and scaled the supplied data, trained a nine-input dense network for 50 epochs, evaluated an untouched test set, saved and reloaded the trained model, and predicted ${metrics['proposed_product_prediction_dollars']:,.2f} in earnings for the proposed product. The test MAE of ${metrics['test_mae_dollars']:,.2f} provides an interpretable measure of typical error, while the saved artifacts make the result reproducible. The assignment also established reusable practices for later coursework: training-only preprocessing, explicit data validation, deterministic execution, held-out evaluation, model persistence, and evidence-based reporting.",
    )

    doc.add_page_break()
    add_heading(doc, "References")
    references = [
        "Geitgey, A. (n.d.). Building deep learning applications with Keras 2.0 [Data set and code repository]. GitHub. https://github.com/johannlilly/linkedin-learning-building-deep-learning-applications-with-keras-2-0",
        "TensorFlow. (n.d.). The Sequential model. Retrieved August 6, 2026, from https://www.tensorflow.org/guide/keras/sequential_model",
    ]
    for text in references:
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.left_indent = Inches(0.5)
        paragraph.paragraph_format.first_line_indent = Inches(-0.5)
        paragraph.paragraph_format.line_spacing = 2
        paragraph.paragraph_format.space_after = Pt(0)
        set_font(paragraph.add_run(text))

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    doc.core_properties.title = "Option 2: Predicting Future Sales With a TensorFlow Neural Network"
    doc.core_properties.subject = "CSC580 Module 2 Critical Thinking Assignment"
    doc.core_properties.author = "Justan Dunn"
    doc.core_properties.keywords = "TensorFlow, Keras, regression, video game sales"
    doc.save(REPORT_PATH)
    return REPORT_PATH


if __name__ == "__main__":
    print(build_report())

