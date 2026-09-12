"""Create readable evidence images from the actual captured program output."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_PATH = OUTPUT_DIR / "run_output.txt"


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/cour.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def render_terminal(lines: list[str], output_name: str, title: str) -> None:
    font = load_font(22)
    title_font = load_font(24)
    width = 1500
    line_height = 34
    height = 80 + line_height * len(lines) + 35
    image = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 58), fill="#1f2937")
    draw.ellipse((22, 19, 38, 35), fill="#ef4444")
    draw.ellipse((48, 19, 64, 35), fill="#f59e0b")
    draw.ellipse((74, 19, 90, 35), fill="#10b981")
    draw.text((112, 13), title, font=title_font, fill="#f9fafb")
    y = 76
    for line in lines:
        draw.text((28, y), line, font=font, fill="#d1fae5")
        y += line_height
    image.save(OUTPUT_DIR / output_name)


def main() -> None:
    raw_lines = LOG_PATH.read_text(encoding="utf-16", errors="replace").splitlines()
    clean = [line.strip("\ufeff") for line in raw_lines if line.strip()]

    setup_lines = [
        line
        for line in clean
        if line.startswith("CSC580")
        or line.startswith("TensorFlow version")
        or line.startswith("Training rows")
        or line.startswith("Input features")
        or line.startswith("Random seed")
        or line.startswith(" Total params")
    ]
    epoch_lines = [line for line in clean if line.startswith("Epoch ") or "/32 -" in line]
    training_excerpt = setup_lines + [""] + epoch_lines[:6] + ["..."] + epoch_lines[-6:]

    results = [
        line
        for line in clean
        if line.startswith("Test MSE")
        or line.startswith("Test RMSE")
        or line.startswith("Test MAE")
        or line.startswith("Earnings Prediction")
        or line.startswith("Model saved")
    ]

    render_terminal(
        training_excerpt,
        "training_verbose_output.png",
        "Actual TensorFlow training output",
    )
    render_terminal(
        results,
        "evaluation_prediction_output.png",
        "Actual evaluation and prediction output",
    )


if __name__ == "__main__":
    main()

