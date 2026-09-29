"""Portable TF-IDF centroid model used by the final CSC525 chatbot."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable


WORD_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9']+")
NON_TEXT_PATTERN = re.compile(r"[^a-zA-Z0-9']+")


@dataclass(frozen=True)
class FeatureConfig:
    name: str
    word_ngram_min: int
    word_ngram_max: int
    char_ngram_min: int
    char_ngram_max: int
    max_features: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "word_ngram_min": self.word_ngram_min,
            "word_ngram_max": self.word_ngram_max,
            "char_ngram_min": self.char_ngram_min,
            "char_ngram_max": self.char_ngram_max,
            "max_features": self.max_features,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FeatureConfig":
        return cls(
            name=str(data["name"]),
            word_ngram_min=int(data["word_ngram_min"]),
            word_ngram_max=int(data["word_ngram_max"]),
            char_ngram_min=int(data["char_ngram_min"]),
            char_ngram_max=int(data["char_ngram_max"]),
            max_features=int(data["max_features"]),
        )


@dataclass(frozen=True)
class Prediction:
    predicted_route: str
    displayed_route: str
    response_text: str
    accepted: bool
    score: float
    margin: float
    ranking: tuple[tuple[str, float], ...]


def normalize_text(text: str) -> str:
    return " ".join(NON_TEXT_PATTERN.sub(" ", text.lower()).split())


def make_ngrams(items: list[str], minimum: int, maximum: int) -> list[str]:
    terms: list[str] = []
    if minimum <= 0 or maximum <= 0:
        return terms
    for size in range(minimum, maximum + 1):
        if len(items) < size:
            continue
        for index in range(len(items) - size + 1):
            terms.append(" ".join(items[index : index + size]))
    return terms


def extract_features(text: str, config: FeatureConfig) -> list[str]:
    normalized = normalize_text(text)
    features: list[str] = []
    if config.word_ngram_min > 0:
        words = [match.group(0) for match in WORD_PATTERN.finditer(normalized)]
        features.extend(
            f"w:{term}"
            for term in make_ngrams(
                words,
                config.word_ngram_min,
                config.word_ngram_max,
            )
        )
    if config.char_ngram_min > 0:
        padded = f" {normalized} "
        for size in range(config.char_ngram_min, config.char_ngram_max + 1):
            if len(padded) < size:
                continue
            features.extend(
                f"c:{padded[index:index + size]}"
                for index in range(len(padded) - size + 1)
            )
    return features


def normalize_vector(vector: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(value * value for value in vector.values()))
    if not norm:
        return {}
    return {term: value / norm for term, value in vector.items()}


def dot_product(left: dict[str, float], right: dict[str, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right.get(term, 0.0) for term, value in left.items())


class TfidfCentroidModel:
    def __init__(self, config: FeatureConfig) -> None:
        self.config = config
        self.vocabulary: list[str] = []
        self.vocabulary_set: set[str] = set()
        self.idf: dict[str, float] = {}
        self.centroids: dict[str, dict[str, float]] = {}
        self.route_responses: dict[str, str] = {}
        self.route_display_names: dict[str, str] = {}
        self.minimum_score = 0.0
        self.minimum_margin = 0.0
        self.fallback_response = (
            "I am not confident that this request matches an approved support topic. "
            "Please rephrase the question or send it to a human support agent."
        )
        self.metadata: dict[str, Any] = {}

    def fit(
        self,
        examples: Iterable[tuple[str, str]],
        route_responses: dict[str, str],
        route_display_names: dict[str, str],
    ) -> None:
        rows = list(examples)
        if not rows:
            raise ValueError("At least one training example is required.")

        feature_documents = [extract_features(text, self.config) for text, _ in rows]
        term_frequency: Counter[str] = Counter()
        document_frequency: Counter[str] = Counter()
        for document in feature_documents:
            term_frequency.update(document)
            document_frequency.update(set(document))

        ranked_terms = sorted(
            term_frequency,
            key=lambda term: (
                -document_frequency[term],
                -term_frequency[term],
                term,
            ),
        )
        self.vocabulary = ranked_terms[: self.config.max_features]
        self.vocabulary_set = set(self.vocabulary)

        document_count = len(feature_documents)
        self.idf = {
            term: math.log((document_count + 1) / (document_frequency[term] + 1)) + 1
            for term in self.vocabulary
        }

        route_vectors: dict[str, list[dict[str, float]]] = defaultdict(list)
        for (_, route), features in zip(rows, feature_documents):
            route_vectors[route].append(self.vectorize_features(features))

        self.centroids = {}
        for route, vectors in route_vectors.items():
            summed: dict[str, float] = defaultdict(float)
            for vector in vectors:
                for term, value in vector.items():
                    summed[term] += value
            averaged = {
                term: value / len(vectors)
                for term, value in summed.items()
            }
            self.centroids[route] = normalize_vector(averaged)

        self.route_responses = dict(route_responses)
        self.route_display_names = dict(route_display_names)

    def vectorize_features(self, features: list[str]) -> dict[str, float]:
        counts = Counter(
            feature for feature in features if feature in self.vocabulary_set
        )
        weighted = {
            term: count * self.idf[term]
            for term, count in counts.items()
            if term in self.idf
        }
        return normalize_vector(weighted)

    def vectorize_text(self, text: str) -> dict[str, float]:
        return self.vectorize_features(extract_features(text, self.config))

    def rank(self, text: str) -> list[tuple[str, float]]:
        vector = self.vectorize_text(text)
        ranking = [
            (route, dot_product(vector, centroid))
            for route, centroid in self.centroids.items()
        ]
        ranking.sort(key=lambda item: (-item[1], item[0]))
        return ranking

    def predict(self, text: str) -> Prediction:
        ranking = self.rank(text)
        if not ranking:
            raise ValueError("The model has no route centroids.")
        predicted_route, score = ranking[0]
        runner_up = ranking[1][1] if len(ranking) > 1 else 0.0
        margin = score - runner_up
        accepted = score >= self.minimum_score and margin >= self.minimum_margin
        if accepted:
            displayed_route = self.route_display_names.get(
                predicted_route, predicted_route.replace("_", " ").title()
            )
            response = self.route_responses[predicted_route]
        else:
            displayed_route = "Clarification or Human Escalation"
            response = self.fallback_response
        return Prediction(
            predicted_route=predicted_route,
            displayed_route=displayed_route,
            response_text=response,
            accepted=accepted,
            score=score,
            margin=margin,
            ranking=tuple(ranking[:3]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_type": "supervised TF-IDF route-centroid classifier",
            "config": self.config.to_dict(),
            "vocabulary": self.vocabulary,
            "idf": self.idf,
            "centroids": self.centroids,
            "route_responses": self.route_responses,
            "route_display_names": self.route_display_names,
            "minimum_score": self.minimum_score,
            "minimum_margin": self.minimum_margin,
            "fallback_response": self.fallback_response,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TfidfCentroidModel":
        model = cls(FeatureConfig.from_dict(data["config"]))
        model.vocabulary = [str(term) for term in data["vocabulary"]]
        model.vocabulary_set = set(model.vocabulary)
        model.idf = {str(k): float(v) for k, v in data["idf"].items()}
        model.centroids = {
            str(route): {str(k): float(v) for k, v in vector.items()}
            for route, vector in data["centroids"].items()
        }
        model.route_responses = {
            str(k): str(v) for k, v in data["route_responses"].items()
        }
        model.route_display_names = {
            str(k): str(v) for k, v in data["route_display_names"].items()
        }
        model.minimum_score = float(data["minimum_score"])
        model.minimum_margin = float(data["minimum_margin"])
        model.fallback_response = str(data["fallback_response"])
        model.metadata = dict(data.get("metadata", {}))
        return model
