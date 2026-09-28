"""Run the Module 6 alpha chatbot over the custom FAQ/SOP corpus.

The alpha is intentionally simple: it uses the same TF-IDF cosine-similarity
retrieval logic from the Module 5 portfolio milestone and returns an approved
FAQ/SOP answer when confidence clears a draft threshold.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "data" / "custom_enterprise_faq_sop_corpus.csv"
DEFAULT_TRANSCRIPT = BASE_DIR / "outputs" / "alpha_demo_transcript.txt"
DEFAULT_PREDICTIONS = BASE_DIR / "outputs" / "alpha_demo_predictions.csv"
TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_']+")

DEMO_MESSAGES = [
    "I cannot get into my online account after changing my password.",
    "Can I get a copy of the invoice for my last order?",
    "The product has a technical error and freezes after setup.",
    "I need to reschedule my service appointment for next week.",
    "Can this purchase be returned or exchanged?",
    "Where is the current user guide for this workflow?",
    "I need a manager to call me about an unresolved complaint.",
    "What is your stock ticker price today?",
]


@dataclass(frozen=True)
class KnowledgeEntry:
    record_id: str
    route_label: str
    source_category: str
    text: str
    sample_question: str
    approved_answer: str


@dataclass(frozen=True)
class ChatbotResponse:
    user_message: str
    displayed_route: str
    matched_route: str
    matched_record_id: str
    matched_question: str
    response_text: str
    similarity: float
    above_threshold: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Module 6 alpha customer-service retrieval chatbot."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--threshold", type=float, default=0.35)
    parser.add_argument("--ngram-min", type=int, default=1)
    parser.add_argument("--ngram-max", type=int, default=1)
    parser.add_argument("--max-features", type=int, default=2500)
    parser.add_argument(
        "--message",
        action="append",
        help="Message to route. Repeat for multiple messages.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the built-in alpha demonstration messages.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start an interactive local chat loop.",
    )
    parser.add_argument("--transcript", type=Path, default=DEFAULT_TRANSCRIPT)
    parser.add_argument("--predictions-csv", type=Path, default=DEFAULT_PREDICTIONS)
    return parser.parse_args()


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]


def make_ngrams(tokens: list[str], ngram_min: int, ngram_max: int) -> list[str]:
    terms: list[str] = []
    for size in range(ngram_min, ngram_max + 1):
        if size <= 0 or len(tokens) < size:
            continue
        for index in range(len(tokens) - size + 1):
            terms.append(" ".join(tokens[index : index + size]))
    return terms


def load_entries(path: Path) -> list[KnowledgeEntry]:
    required = {
        "record_id",
        "route_label",
        "source_category",
        "combined_text",
        "sample_question",
        "approved_answer",
    }
    entries: list[KnowledgeEntry] = []
    with path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        if not reader.fieldnames:
            raise ValueError("Input CSV does not contain headers.")
        missing = sorted(required.difference(reader.fieldnames))
        if missing:
            raise ValueError(f"Missing required corpus columns: {missing}")
        for row in reader:
            text = (row.get("combined_text") or "").strip()
            route_label = (row.get("route_label") or "").strip()
            if not text or not route_label:
                continue
            entries.append(
                KnowledgeEntry(
                    record_id=(row.get("record_id") or "").strip(),
                    route_label=route_label,
                    source_category=(row.get("source_category") or "").strip(),
                    text=text,
                    sample_question=(row.get("sample_question") or "").strip(),
                    approved_answer=(row.get("approved_answer") or "").strip(),
                )
            )
    if not entries:
        raise ValueError("No usable FAQ/SOP entries were loaded.")
    return entries


def entry_terms(entry: KnowledgeEntry, ngram_min: int, ngram_max: int) -> list[str]:
    return make_ngrams(tokenize(entry.text), ngram_min, ngram_max)


def build_vocabulary(
    entries: list[KnowledgeEntry],
    ngram_min: int,
    ngram_max: int,
    max_features: int,
) -> list[str]:
    term_frequency: Counter[str] = Counter()
    document_frequency: Counter[str] = Counter()
    for entry in entries:
        terms = entry_terms(entry, ngram_min, ngram_max)
        term_frequency.update(terms)
        document_frequency.update(set(terms))

    ranked = sorted(
        term_frequency,
        key=lambda term: (-document_frequency[term], -term_frequency[term], term),
    )
    return ranked[:max_features] if max_features > 0 else ranked


class TfidfRetriever:
    def __init__(self, vocabulary: list[str], ngram_min: int, ngram_max: int) -> None:
        self.vocabulary = vocabulary
        self.vocabulary_set = set(vocabulary)
        self.ngram_min = ngram_min
        self.ngram_max = ngram_max
        self.idf: dict[str, float] = {}
        self.entries: list[KnowledgeEntry] = []
        self.entry_vectors: list[dict[str, float]] = []

    def fit(self, entries: list[KnowledgeEntry]) -> None:
        self.entries = entries
        documents = [
            [
                term
                for term in entry_terms(entry, self.ngram_min, self.ngram_max)
                if term in self.vocabulary_set
            ]
            for entry in entries
        ]
        document_frequency: Counter[str] = Counter()
        for document in documents:
            document_frequency.update(set(document))

        total_documents = len(documents)
        self.idf = {
            term: math.log((total_documents + 1) / (document_frequency[term] + 1)) + 1
            for term in self.vocabulary
        }
        self.entry_vectors = [self.vectorize_terms(document) for document in documents]

    def vectorize_terms(self, terms: list[str]) -> dict[str, float]:
        counts = Counter(term for term in terms if term in self.vocabulary_set)
        vector = {
            term: count * self.idf.get(term, 0.0)
            for term, count in counts.items()
            if term in self.idf
        }
        norm = math.sqrt(sum(value * value for value in vector.values()))
        if not norm:
            return vector
        return {term: value / norm for term, value in vector.items()}

    def vectorize_text(self, text: str) -> dict[str, float]:
        return self.vectorize_terms(
            make_ngrams(tokenize(text), self.ngram_min, self.ngram_max)
        )

    @staticmethod
    def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(term, 0.0) for term, value in left.items())

    def best_match(self, message: str) -> tuple[KnowledgeEntry, float]:
        query_vector = self.vectorize_text(message)
        scored = [
            (entry, self.cosine_similarity(query_vector, vector))
            for entry, vector in zip(self.entries, self.entry_vectors)
        ]
        scored.sort(key=lambda item: (-item[1], item[0].route_label, item[0].record_id))
        return scored[0]


def build_response(
    retriever: TfidfRetriever,
    message: str,
    threshold: float,
) -> ChatbotResponse:
    match, similarity = retriever.best_match(message)
    above_threshold = similarity >= threshold
    if above_threshold:
        route = match.route_label
        response = match.approved_answer
    else:
        route = "clarification_or_human_escalation"
        response = (
            "I am not confident that this message matches the approved support "
            "topics. Please rephrase the request or send it to a human agent."
        )

    return ChatbotResponse(
        user_message=message,
        displayed_route=route,
        matched_route=match.route_label,
        matched_record_id=match.record_id,
        matched_question=match.sample_question,
        response_text=response,
        similarity=similarity,
        above_threshold=above_threshold,
    )


def format_exchange(response: ChatbotResponse) -> str:
    status = "accepted" if response.above_threshold else "fallback"
    return "\n".join(
        [
            f"User: {response.user_message}",
            (
                "Alpha chatbot: "
                f"route={response.displayed_route}; "
                f"confidence={response.similarity:.4f}; "
                f"status={status}"
            ),
            f"Alpha chatbot response: {response.response_text}",
        ]
    )


def write_transcript(path: Path, responses: list[ChatbotResponse]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Module 6 Portfolio Milestone Alpha Chatbot Demo Transcript",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    for index, response in enumerate(responses, start=1):
        lines.append(f"Exchange {index}")
        lines.append(format_exchange(response))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_predictions(path: Path, responses: list[ChatbotResponse]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        fieldnames = [
            "user_message",
            "displayed_route",
            "matched_route",
            "matched_record_id",
            "matched_question",
            "similarity",
            "above_threshold",
            "response_text",
        ]
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        for response in responses:
            writer.writerow(
                {
                    "user_message": response.user_message,
                    "displayed_route": response.displayed_route,
                    "matched_route": response.matched_route,
                    "matched_record_id": response.matched_record_id,
                    "matched_question": response.matched_question,
                    "similarity": f"{response.similarity:.4f}",
                    "above_threshold": response.above_threshold,
                    "response_text": response.response_text,
                }
            )


def run_messages(
    entries: list[KnowledgeEntry],
    messages: list[str],
    args: argparse.Namespace,
) -> list[ChatbotResponse]:
    vocabulary = build_vocabulary(
        entries=entries,
        ngram_min=args.ngram_min,
        ngram_max=args.ngram_max,
        max_features=args.max_features,
    )
    retriever = TfidfRetriever(
        vocabulary=vocabulary,
        ngram_min=args.ngram_min,
        ngram_max=args.ngram_max,
    )
    retriever.fit(entries)
    return [
        build_response(retriever, message=message, threshold=args.threshold)
        for message in messages
    ]


def run_interactive(entries: list[KnowledgeEntry], args: argparse.Namespace) -> None:
    print("Module 6 alpha chatbot. Type 'exit' to stop.")
    while True:
        message = input("User: ").strip()
        if message.lower() in {"exit", "quit"}:
            break
        response = run_messages(entries, [message], args)[0]
        print(format_exchange(response))


def main() -> int:
    args = parse_args()
    entries = load_entries(args.input)

    if args.interactive:
        run_interactive(entries, args)
        return 0

    messages = list(args.message or [])
    if args.demo or not messages:
        messages.extend(DEMO_MESSAGES)

    responses = run_messages(entries, messages, args)
    write_transcript(args.transcript, responses)
    write_predictions(args.predictions_csv, responses)

    print(f"Loaded corpus rows: {len(entries)}")
    print(f"Demo exchanges: {len(responses)}")
    print(f"Accepted responses: {sum(item.above_threshold for item in responses)}")
    print(f"Fallback responses: {sum(not item.above_threshold for item in responses)}")
    print(f"Transcript: {args.transcript.resolve()}")
    print(f"Predictions CSV: {args.predictions_csv.resolve()}")
    print()
    for response in responses:
        print(format_exchange(response))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
