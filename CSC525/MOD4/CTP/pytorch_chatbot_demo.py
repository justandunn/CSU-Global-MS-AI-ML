"""
CSC525 Module 4 Option #2: PyTorch Chatbot Demo

Reduced classroom demo inspired by the official PyTorch Chatbot Tutorial:
https://pytorch.org/tutorials/beginner/chatbot_tutorial.html

This is NOT a production chatbot. Training is intentionally short, the model is
small, and the dataset is filtered so the script can run on a typical Windows CPU.
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
import pathlib

import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# ---------------------------------------------------------------------------
# Paths (run from CSC525 course root)
# ---------------------------------------------------------------------------
COURSE_ROOT = pathlib.Path.cwd()
CORPUS_DIR = COURSE_ROOT / "MOD4" / "CTP" / "movie_dialogs_extracted" / "movie-corpus"
UTTERANCES_PATH = CORPUS_DIR / "utterances.jsonl"
CONVERSATIONS_PATH = CORPUS_DIR / "conversations.json"
OUTPUT_PATH = COURSE_ROOT / "MOD4" / "CTP" / "pytorch_chatbot_demo_output.txt"

# ---------------------------------------------------------------------------
# Demo hyperparameters (kept small for local CPU training)
# ---------------------------------------------------------------------------
MAX_LENGTH = 10
MIN_COUNT = 3
HIDDEN_SIZE = 256
N_LAYERS = 1
LEARNING_RATE = 0.001
N_ITERS = 300
PRINT_EVERY = 50
TEACHER_FORCING_RATIO = 0.5
MAX_TRAIN_PAIRS = 12000  # subsample so training finishes quickly on CPU

PAD_token = 0
SOS_token = 1
EOS_token = 2


class Logger:
    """Write the same message to the console and an output log file."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text("", encoding="utf-8")

    def log(self, message: str = "") -> None:
        print(message)
        with self.log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")


def normalize_text(text: str) -> str:
    """Lowercase, keep basic punctuation, and collapse extra whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s\.\?\!,']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_count(sentence: str) -> int:
    sentence = sentence.strip()
    if not sentence:
        return 0
    return len(sentence.split())


def order_utterance_ids(utterance_rows: list[dict]) -> list[str]:
    """
    Order utterances in one conversation using reply-to links.

    The JSON corpus stores conversation structure on each utterance instead of
    inside conversations.json, so we rebuild the chronological chain here.
    """
    if not utterance_rows:
        return []

    by_id = {row["id"]: row for row in utterance_rows}
    child_map: dict[str, str] = {}

    for row in utterance_rows:
        parent_id = row.get("reply-to") or row.get("reply_to")
        if parent_id:
            child_map[parent_id] = row["id"]

    roots = [
        row
        for row in utterance_rows
        if (row.get("reply-to") in (None, "")) and (row.get("reply_to") in (None, ""))
    ]
    if not roots:
        roots = [row for row in utterance_rows if row["id"] == row.get("conversation_id")]

    if not roots:
        return [row["id"] for row in sorted(utterance_rows, key=lambda item: item["id"])]

    ordered_ids: list[str] = []
    current_id: str | None = roots[0]["id"]
    seen: set[str] = set()

    while current_id and current_id not in seen:
        seen.add(current_id)
        ordered_ids.append(current_id)
        current_id = child_map.get(current_id)

    return ordered_ids


def extract_utterance_ids(conversation_obj: dict) -> list[str] | None:
    """Support both utterance_ids and utterances fields when present."""
    if not isinstance(conversation_obj, dict):
        return None

    if "utterance_ids" in conversation_obj:
        raw_ids = conversation_obj["utterance_ids"]
        if isinstance(raw_ids, list):
            return [str(item) for item in raw_ids]

    if "utterances" in conversation_obj:
        raw_utterances = conversation_obj["utterances"]
        if not isinstance(raw_utterances, list):
            return None

        utterance_ids: list[str] = []
        for item in raw_utterances:
            if isinstance(item, str):
                utterance_ids.append(item)
            elif isinstance(item, dict):
                utterance_id = item.get("id") or item.get("utterance_id")
                if utterance_id:
                    utterance_ids.append(str(utterance_id))
        if utterance_ids:
            return utterance_ids

    return None


def load_utterances(path: Path) -> tuple[pd.DataFrame, dict[str, str]]:
    """Load utterances.jsonl and build an id-to-text lookup."""
    if not path.exists():
        raise FileNotFoundError(f"Utterances file not found: {path}")

    utterances_df = pd.read_json(path, lines=True)
    if utterances_df.empty:
        raise ValueError("utterances.jsonl did not contain any rows.")

    id_column = "id" if "id" in utterances_df.columns else "utterance_id"
    text_column = "text" if "text" in utterances_df.columns else "utterance_text"

    if id_column not in utterances_df.columns or text_column not in utterances_df.columns:
        raise ValueError(
            "Could not find utterance id/text columns. "
            f"Available columns: {list(utterances_df.columns)}"
        )

    utterances_df = utterances_df.rename(columns={id_column: "id", text_column: "text"})
    utterances_df["id"] = utterances_df["id"].astype(str)
    utterances_df["text"] = utterances_df["text"].astype(str)

    id_to_text = dict(zip(utterances_df["id"], utterances_df["text"]))
    return utterances_df, id_to_text


def load_conversations(path: Path) -> dict:
    """Load conversations.json."""
    if not path.exists():
        raise FileNotFoundError(f"Conversations file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        conversations = json.load(file)

    if isinstance(conversations, list):
        conversations = {
            str(item.get("id", index)): item
            for index, item in enumerate(conversations)
            if isinstance(item, dict)
        }
    elif not isinstance(conversations, dict):
        raise ValueError("conversations.json must be a JSON object or list of objects.")

    return conversations


def build_pairs(
    conversations: dict,
    utterances_df: pd.DataFrame,
    id_to_text: dict[str, str],
) -> list[tuple[str, str]]:
    """Create cleaned input-response pairs from adjacent utterances."""
    grouped_rows: dict[str, list[dict]] = defaultdict(list)
    for row in utterances_df.to_dict(orient="records"):
        conversation_id = str(row.get("conversation_id", row.get("id", "")))
        grouped_rows[conversation_id].append(
            {
                "id": str(row["id"]),
                "conversation_id": conversation_id,
                "reply-to": row.get("reply-to"),
                "reply_to": row.get("reply_to"),
            }
        )

    pairs: list[tuple[str, str]] = []

    for conversation_id, conversation_obj in conversations.items():
        utterance_ids = extract_utterance_ids(conversation_obj)
        if utterance_ids is None:
            utterance_ids = order_utterance_ids(grouped_rows.get(str(conversation_id), []))

        for index in range(len(utterance_ids) - 1):
            input_text = normalize_text(id_to_text.get(utterance_ids[index], ""))
            response_text = normalize_text(id_to_text.get(utterance_ids[index + 1], ""))

            if not input_text or not response_text:
                continue
            if word_count(input_text) > MAX_LENGTH or word_count(response_text) > MAX_LENGTH:
                continue

            pairs.append((input_text, response_text))

    return pairs


def trim_rare_words(
    pairs: list[tuple[str, str]], min_count: int
) -> tuple[dict[str, int], dict[int, str], list[tuple[str, str]]]:
    """Build vocabulary and drop rare words, following the tutorial pattern."""
    word_counts: Counter[str] = Counter()
    for input_text, response_text in pairs:
        for sentence in (input_text, response_text):
            word_counts.update(sentence.split())

    word2index: dict[str, int] = {"PAD": PAD_token, "SOS": SOS_token, "EOS": EOS_token}
    next_index = 3
    for word, count in word_counts.items():
        if count >= min_count:
            word2index[word] = next_index
            next_index += 1

    trimmed_pairs: list[tuple[str, str]] = []
    for input_text, response_text in pairs:
        input_words = [word for word in input_text.split() if word in word2index]
        response_words = [word for word in response_text.split() if word in word2index]
        if input_words and response_words:
            trimmed_pairs.append((" ".join(input_words), " ".join(response_words)))

    index2word = {index: word for word, index in word2index.items()}
    return word2index, index2word, trimmed_pairs


def sentence_to_indexes(sentence: str, word2index: dict[str, int]) -> list[int]:
    return [SOS_token] + [word2index[word] for word in sentence.split()] + [EOS_token]


def pairs_to_tensors(
    pairs: list[tuple[str, str]],
    word2index: dict[str, int],
) -> list[tuple[torch.Tensor, torch.Tensor]]:
    tensor_pairs: list[tuple[torch.Tensor, torch.Tensor]] = []
    for input_text, response_text in pairs:
        input_indexes = sentence_to_indexes(input_text, word2index)
        target_indexes = sentence_to_indexes(response_text, word2index)
        tensor_pairs.append(
            (
                torch.tensor(input_indexes, dtype=torch.long),
                torch.tensor(target_indexes, dtype=torch.long),
            )
        )
    return tensor_pairs


class EncoderRNN(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, n_layers: int = 1) -> None:
        super().__init__()
        self.hidden_size = hidden_size
        self.n_layers = n_layers
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, n_layers)

    def forward(self, input_tensor: torch.Tensor, hidden: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        embedded = self.embedding(input_tensor)
        output, hidden = self.gru(embedded, hidden)
        return output, hidden

    def init_hidden(self, device: torch.device) -> torch.Tensor:
        return torch.zeros(self.n_layers, 1, self.hidden_size, device=device)


class DecoderRNN(nn.Module):
    def __init__(self, output_size: int, hidden_size: int, n_layers: int = 1) -> None:
        super().__init__()
        self.hidden_size = hidden_size
        self.n_layers = n_layers
        self.embedding = nn.Embedding(output_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, n_layers)
        self.out = nn.Linear(hidden_size, output_size)

    def forward(
        self,
        input_tensor: torch.Tensor,
        hidden: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        embedded = self.embedding(input_tensor)
        output, hidden = self.gru(embedded, hidden)
        output = self.out(output)
        output = F.log_softmax(output, dim=2)
        return output, hidden, embedded


def train_step(
    input_tensor: torch.Tensor,
    target_tensor: torch.Tensor,
    encoder: EncoderRNN,
    decoder: DecoderRNN,
    encoder_optimizer: optim.Optimizer,
    decoder_optimizer: optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    max_length: int,
    teacher_forcing_ratio: float = 0.5,
) -> float:
    encoder_hidden = encoder.init_hidden(device)

    encoder_optimizer.zero_grad()
    decoder_optimizer.zero_grad()

    target_length = target_tensor.size(0)
    losses: list[torch.Tensor] = []

    encoder_output, encoder_hidden = encoder(input_tensor, encoder_hidden)
    decoder_input = torch.tensor([[SOS_token]], device=device)
    decoder_hidden = encoder_hidden

    use_teacher_forcing = random.random() < teacher_forcing_ratio

    if use_teacher_forcing:
        for decoder_index in range(target_length):
            decoder_output, decoder_hidden, _ = decoder(decoder_input, decoder_hidden)
            losses.append(
                criterion(
                    decoder_output.squeeze(0),
                    target_tensor[decoder_index].view(1),
                )
            )
            decoder_input = target_tensor[decoder_index].view(1, 1)
    else:
        for decoder_index in range(target_length):
            decoder_output, decoder_hidden, _ = decoder(decoder_input, decoder_hidden)
            topv, topi = decoder_output.topk(1)
            decoder_input = topi.squeeze(-1).detach()

            losses.append(
                criterion(
                    decoder_output.squeeze(0),
                    target_tensor[decoder_index].view(1),
                )
            )
            if decoder_input.item() == EOS_token:
                break

    if not losses:
        return 0.0

    loss = sum(losses) / len(losses)
    loss.backward()
    encoder_optimizer.step()
    decoder_optimizer.step()

    return loss.item()


def train_model(
    tensor_pairs: list[tuple[torch.Tensor, torch.Tensor]],
    encoder: EncoderRNN,
    decoder: DecoderRNN,
    logger: Logger,
    device: torch.device,
    n_iters: int = N_ITERS,
    print_every: int = PRINT_EVERY,
) -> None:
    encoder_optimizer = optim.Adam(encoder.parameters(), lr=LEARNING_RATE)
    decoder_optimizer = optim.Adam(decoder.parameters(), lr=LEARNING_RATE)
    criterion = nn.NLLLoss()

    for iteration in range(1, n_iters + 1):
        input_tensor, target_tensor = random.choice(tensor_pairs)
        input_tensor = input_tensor.to(device).view(-1, 1)
        target_tensor = target_tensor.to(device)

        loss = train_step(
            input_tensor,
            target_tensor,
            encoder,
            decoder,
            encoder_optimizer,
            decoder_optimizer,
            criterion,
            device,
            MAX_LENGTH,
            TEACHER_FORCING_RATIO,
        )

        if iteration % print_every == 0 or iteration == 1:
            logger.log(f"Iteration {iteration}/{n_iters} | average loss: {loss:.4f}")


def evaluate_greedy(
    input_sentence: str,
    encoder: EncoderRNN,
    decoder: DecoderRNN,
    word2index: dict[str, int],
    index2word: dict[int, str],
    device: torch.device,
    max_length: int = MAX_LENGTH,
) -> str:
    cleaned = normalize_text(input_sentence)
    words = [word for word in cleaned.split() if word in word2index]
    if not words:
        return "(no known words in prompt)"

    indexes = [SOS_token] + [word2index[word] for word in words] + [EOS_token]
    input_tensor = torch.tensor(indexes, dtype=torch.long, device=device).view(-1, 1)

    with torch.no_grad():
        encoder_hidden = encoder.init_hidden(device)
        encoder_output, encoder_hidden = encoder(input_tensor, encoder_hidden)
        decoder_input = torch.tensor([[SOS_token]], device=device)
        decoder_hidden = encoder_hidden

        decoded_words: list[str] = []
        for _ in range(max_length):
            decoder_output, decoder_hidden, _ = decoder(decoder_input, decoder_hidden)
            topv, topi = decoder_output.topk(1)
            next_index = topi.item()

            if next_index == EOS_token:
                break
            if next_index not in (PAD_token, SOS_token):
                decoded_words.append(index2word.get(next_index, "<UNK>"))
            decoder_input = topi.detach().view(1, 1)

    if not decoded_words:
        return "(model did not produce a response)"
    return " ".join(decoded_words)


def main() -> int:
    logger = Logger(OUTPUT_PATH)

    logger.log("CSC525 Module 4 - Reduced PyTorch Chatbot Demo")
    logger.log("Based on the PyTorch Chatbot Tutorial, adapted for classroom use.")
    logger.log(f"PyTorch version: {torch.__version__}")
    logger.log(f"CUDA available: {torch.cuda.is_available()}")
    logger.log(f"Course root: {COURSE_ROOT}")
    logger.log(f"Corpus directory: {CORPUS_DIR}")
    logger.log("")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.log(f"Using device: {device}")
    logger.log("")

    utterances_df, id_to_text = load_utterances(UTTERANCES_PATH)
    conversations = load_conversations(CONVERSATIONS_PATH)
    logger.log(f"Utterances loaded: {len(utterances_df):,}")
    logger.log(f"Conversations loaded: {len(conversations):,}")

    raw_pairs = build_pairs(conversations, utterances_df, id_to_text)
    logger.log(f"Filtered sentence pairs (max {MAX_LENGTH} words): {len(raw_pairs):,}")

    word2index, index2word, trimmed_pairs = trim_rare_words(raw_pairs, MIN_COUNT)
    logger.log(f"Pairs after rare-word trimming (min_count={MIN_COUNT}): {len(trimmed_pairs):,}")
    logger.log(f"Vocabulary size (including PAD/SOS/EOS): {len(word2index):,}")

    if len(trimmed_pairs) < 100:
        logger.log("Not enough training pairs after filtering. Check corpus paths and cleaning rules.")
        return 1

    if len(trimmed_pairs) > MAX_TRAIN_PAIRS:
        random.seed(42)
        trimmed_pairs = random.sample(trimmed_pairs, MAX_TRAIN_PAIRS)
        logger.log(f"Subsampled to {MAX_TRAIN_PAIRS:,} pairs for faster CPU training.")

    tensor_pairs = pairs_to_tensors(trimmed_pairs, word2index)
    logger.log(f"Training tensor pairs: {len(tensor_pairs):,}")
    logger.log("")

    vocab_size = len(word2index)
    encoder = EncoderRNN(vocab_size, HIDDEN_SIZE, N_LAYERS).to(device)
    decoder = DecoderRNN(vocab_size, HIDDEN_SIZE, N_LAYERS).to(device)

    logger.log(
        f"Training for {N_ITERS} iterations "
        f"(hidden_size={HIDDEN_SIZE}, teacher_forcing={TEACHER_FORCING_RATIO})..."
    )
    train_model(tensor_pairs, encoder, decoder, logger, device)
    logger.log("")

    sample_prompts = [
        "hello",
        "how are you",
        "what is your name",
        "i love you",
        "goodbye",
    ]
    logger.log("Sample greedy-decoding responses:")
    for prompt in sample_prompts:
        response = evaluate_greedy(prompt, encoder, decoder, word2index, index2word, device)
        logger.log(f"Human: {prompt}")
        logger.log(f"Bot: {response}")
        logger.log("")

    logger.log(f"Output log saved to: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
