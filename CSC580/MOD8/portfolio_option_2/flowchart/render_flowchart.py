"""Render a submission-ready PNG companion to the editable Excalidraw flowchart."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon


OUTPUT = Path(__file__).resolve().parent / "encoder_decoder_lstm_flowchart.png"


def box(ax, x, y, w, h, text, color, fontsize=9):
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
        facecolor=color, edgecolor="#25364a", linewidth=1.4
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize)
    return (x, y, w, h)


def diamond(ax, cx, cy, w, h, text, color="#fff3bf"):
    points = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(points, closed=True, facecolor=color, edgecolor="#25364a", linewidth=1.4))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=8.5)


def arrow(ax, start, end, text=None, dashed=False):
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops={"arrowstyle": "->", "color": "#36475b", "lw": 1.4,
                    "linestyle": "--" if dashed else "-"}
    )
    if text:
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, text,
                fontsize=7.5, color="#36475b", ha="center", va="center",
                bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})


def main():
    fig, ax = plt.subplots(figsize=(12, 15.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 16)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_title("Encoder Decoder LSTM Processing Workflow", fontsize=20, weight="bold", pad=18)

    box(ax, 4.5, 14.9, 3, 0.6, "Start reproducible run", "#a5d8ff", 10)
    box(ax, 4.2, 13.8, 3.6, 0.7, "Configure seed, 51 tokens,\n6 inputs, and 3 outputs", "#fff3bf")
    box(ax, 4.2, 12.6, 3.6, 0.7, "Generate source sequences\nwith integers 1 through 50", "#c3fae8")
    box(ax, 4.2, 11.35, 3.6, 0.78, "Reverse the first three values\nand prepend decoder start token 0", "#d0bfff")
    box(ax, 4.2, 10.1, 3.6, 0.78, "One hot encode and create isolated\ntraining, validation, and test sets", "#c3fae8")
    box(ax, 4.2, 8.75, 3.6, 0.88, "Build encoder and decoder LSTMs\nwith shared training and inference weights", "#d0bfff")

    for y1, y2 in [(14.9, 14.5), (13.8, 13.3), (12.6, 12.13), (11.35, 10.88), (10.1, 9.63)]:
        arrow(ax, (6, y1), (6, y2))

    ax.text(2.25, 8.45, "TRAINING", fontsize=11, weight="bold", ha="center", color="#315c85")
    ax.text(9.75, 8.45, "INFERENCE AND EVALUATION", fontsize=11, weight="bold", ha="center", color="#6b4b8a")

    box(ax, 0.6, 7.25, 3.3, 0.9, "Train with teacher forcing\nAdam and categorical cross entropy\nMonitor validation loss", "#a5d8ff")
    diamond(ax, 2.25, 5.9, 2.8, 1.25, "No validation\nimprovement for\n5 epochs?")
    box(ax, 0.7, 4.45, 3.1, 0.72, "Restore best model weights", "#b2f2bb")
    arrow(ax, (4.8, 8.75), (2.25, 8.15), "training path")
    arrow(ax, (2.25, 7.25), (2.25, 6.53))
    arrow(ax, (2.25, 5.27), (2.25, 5.17), "yes or max epochs")
    arrow(ax, (0.85, 5.9), (0.85, 7.7), "no continue", True)

    box(ax, 8.1, 7.25, 3.3, 0.9, "Encode one unseen source once\nto initialize decoder hidden\nand cell states", "#d0bfff")
    box(ax, 8.1, 6.05, 3.3, 0.7, "Send start token 0\nto the inference decoder", "#a5d8ff")
    box(ax, 8.1, 4.75, 3.3, 0.82, "Predict next token, update states,\nand feed prediction back", "#d0bfff")
    diamond(ax, 9.75, 3.5, 2.7, 1.15, "Three target\ntokens generated?")
    box(ax, 8.0, 2.05, 3.5, 0.82, "Decode integers and compare the\nfull prediction with expected target", "#eebefa")
    diamond(ax, 6.0, 1.15, 2.7, 1.05, "All 100 test\nsequences evaluated?")
    box(ax, 0.7, 0.72, 3.7, 0.86, "Report exact match accuracy and save\npredictions, metrics, and figures", "#b2f2bb")
    box(ax, 0.95, 0.05, 3.2, 0.45, "End verified run", "#b2f2bb", 10)

    arrow(ax, (3.8, 4.8), (8.1, 7.7), "best weights initialize inference")
    arrow(ax, (9.75, 7.25), (9.75, 6.75))
    arrow(ax, (9.75, 6.05), (9.75, 5.57))
    arrow(ax, (9.75, 4.75), (9.75, 4.08))
    arrow(ax, (8.4, 3.5), (7.55, 5.15), "no loop", True)
    arrow(ax, (9.75, 2.92), (9.75, 2.87), "yes")
    arrow(ax, (8.0, 2.46), (7.1, 1.5))
    arrow(ax, (6.0, 1.68), (8.35, 2.05), "no next sequence", True)
    arrow(ax, (4.65, 1.15), (4.4, 1.15), "yes")
    arrow(ax, (2.55, 0.72), (2.55, 0.5))

    plt.tight_layout()
    fig.savefig(OUTPUT, dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
