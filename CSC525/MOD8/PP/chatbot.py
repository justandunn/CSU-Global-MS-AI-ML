"""Run the final CSC525 closed-domain customer-service chatbot."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from chatbot_model import Prediction, TfidfCentroidModel


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = BASE_DIR / "model" / "chatbot_model.json"
DEFAULT_TRANSCRIPT = BASE_DIR / "outputs" / "final_demo_transcript.txt"
DEMO_MESSAGES = [
    "I reset my password and now the portal will not accept my login.",
    "There is a fee on my latest bill that I do not recognize.",
    "I am really frustrated because my shipment has not arrived.",
    "Can we move the technician appointment to Friday morning?",
    "The application freezes when I open the reporting screen.",
    "Please send me the current training guide for this process.",
    "The automated steps did not work, so I need a live representative.",
    "Play some relaxing music.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the final closed-domain customer-service routing and retrieval chatbot."
        )
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument(
        "--message",
        action="append",
        help="Customer message to process. Repeat for multiple messages.",
    )
    parser.add_argument("--demo", action="store_true", help="Run eight demo messages.")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Open the interactive chat loop.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON for non-interactive messages.",
    )
    parser.add_argument("--transcript", type=Path, default=DEFAULT_TRANSCRIPT)
    return parser.parse_args()


def load_model(path: Path) -> TfidfCentroidModel:
    if not path.exists():
        raise FileNotFoundError(
            f"Model file not found: {path}. Run train_final_chatbot.py first."
        )
    return TfidfCentroidModel.from_dict(
        json.loads(path.read_text(encoding="utf-8"))
    )


def confidence_label(prediction: Prediction, model: TfidfCentroidModel) -> str:
    if not prediction.accepted:
        return "low"
    if (
        prediction.score >= model.minimum_score + 0.10
        and prediction.margin >= model.minimum_margin + 0.05
    ):
        return "high"
    return "moderate"


def response_payload(
    message: str,
    prediction: Prediction,
    model: TfidfCentroidModel,
) -> dict[str, object]:
    return {
        "user_message": message,
        "status": "answered" if prediction.accepted else "fallback",
        "route": prediction.displayed_route,
        "predicted_route": prediction.predicted_route,
        "confidence": confidence_label(prediction, model),
        "similarity_score": round(prediction.score, 4),
        "decision_margin": round(prediction.margin, 4),
        "response": prediction.response_text,
        "top_routes": [
            {"route": route, "score": round(score, 4)}
            for route, score in prediction.ranking
        ],
    }


def format_exchange(payload: dict[str, object]) -> str:
    return "\n".join(
        [
            f"User: {payload['user_message']}",
            f"Support bot: {payload['response']}",
            (
                "Decision: "
                f"{payload['route']} | confidence={payload['confidence']} | "
                f"similarity={float(payload['similarity_score']):.4f} | "
                f"margin={float(payload['decision_margin']):.4f}"
            ),
        ]
    )


def run_messages(
    model: TfidfCentroidModel,
    messages: list[str],
) -> list[dict[str, object]]:
    return [
        response_payload(message, model.predict(message), model)
        for message in messages
        if message.strip()
    ]


def write_transcript(path: Path, payloads: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "CSC525 Module 8 Final Chatbot Demonstration",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    for index, payload in enumerate(payloads, start=1):
        lines.append(f"Exchange {index}")
        lines.append(format_exchange(payload))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def print_topics(model: TfidfCentroidModel) -> None:
    print("Supported topics:")
    for route in sorted(model.route_display_names):
        print(f"  - {model.route_display_names[route]}")


def run_interactive(model: TfidfCentroidModel) -> None:
    print("=" * 72)
    print("Enterprise Customer-Service Routing Chatbot")
    print("Closed-domain NLP demonstration | Type /help for commands")
    print("=" * 72)
    print_topics(model)
    print()
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break
        if not message:
            continue
        command = message.lower()
        if command in {"/quit", "/exit", "quit", "exit"}:
            print("Session ended.")
            break
        if command == "/help":
            print("Commands: /topics, /help, /quit")
            continue
        if command == "/topics":
            print_topics(model)
            continue
        payload = response_payload(message, model.predict(message), model)
        print(f"Bot: {payload['response']}")
        print(
            f"     Route: {payload['route']} | "
            f"Confidence: {payload['confidence']} | "
            f"Score: {float(payload['similarity_score']):.4f}"
        )
        print()


def main() -> int:
    args = parse_args()
    model = load_model(args.model)
    messages = list(args.message or [])
    if args.demo:
        messages.extend(DEMO_MESSAGES)

    if messages:
        payloads = run_messages(model, messages)
        if args.json:
            print(json.dumps(payloads, indent=2))
        else:
            for payload in payloads:
                print(format_exchange(payload))
                print()
        if args.demo:
            write_transcript(args.transcript, payloads)
            print(f"Transcript: {args.transcript.resolve()}")

    if args.interactive or not messages:
        run_interactive(model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
