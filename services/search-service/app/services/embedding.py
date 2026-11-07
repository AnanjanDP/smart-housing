from __future__ import annotations

import hashlib
import logging
import re
import threading
from typing import Optional, Protocol, Sequence

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Embedder(Protocol):
    """Turns text into L2-normalised float32 vectors, so inner product equals cosine similarity."""

    name: str
    dim: int

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        ...


def l2_normalize(matrix: np.ndarray) -> np.ndarray:
    matrix = np.ascontiguousarray(matrix, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return matrix / norms


class HashingEmbedder:
    """Deterministic, dependency-free embedder based on signed feature hashing.

    It captures lexical overlap (words and character trigrams), not meaning. It exists so the
    index, the API and the tests run offline and quickly; production uses SentenceTransformerEmbedder.
    """

    def __init__(self, dim: int = 256):
        self.name = f"hashing-v1-{dim}"
        self.dim = dim

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def _features(self, text: str) -> list[str]:
        features = []
        for token in self._tokens(text):
            features.append(f"w:{token}")
            padded = f"^{token}$"
            for i in range(len(padded) - 2):
                features.append(f"c:{padded[i:i + 3]}")
        return features

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for feature in self._features(text):
                digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
                value = int.from_bytes(digest, "big")
                sign = 1.0 if (value >> 63) & 1 else -1.0
                out[row, value % self.dim] += sign
        return l2_normalize(out)


class SentenceTransformerEmbedder:
    """Sentence embeddings from a sentence-transformers model, loaded lazily on first use."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, batch_size: int = 64, device: Optional[str] = None):
        self.name = model_name
        self.batch_size = batch_size
        self.device = device
        self._model = None
        self._dim: Optional[int] = None
        self._lock = threading.Lock()

    def _load(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    from sentence_transformers import SentenceTransformer

                    logger.info("Loading embedding model %s", self.name)
                    model = SentenceTransformer(self.name, device=self.device)
                    self._dim = int(model.get_sentence_embedding_dimension())
                    self._model = model
        return self._model

    @property
    def dim(self) -> int:
        self._load()
        return self._dim

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        if len(texts) == 0:
            return np.zeros((0, self.dim), dtype=np.float32)
        model = self._load()
        vectors = model.encode(
            list(texts),
            batch_size=self.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return l2_normalize(vectors)


def get_embedder(backend: Optional[str] = None, model_name: Optional[str] = None) -> Embedder:
    backend = (backend or "sentence-transformers").lower()
    if backend in ("hash", "hashing"):
        return HashingEmbedder()
    if backend in ("sentence-transformers", "sentence_transformers", "st"):
        return SentenceTransformerEmbedder(model_name or DEFAULT_MODEL_NAME)
    raise ValueError(f"Unknown embedding backend: {backend!r}")


def listing_text(listing: dict) -> str:
    """The text that represents a listing in embedding space."""
    parts = [
        str(listing.get("title") or ""),
        str(listing.get("description") or ""),
        ", ".join(p for p in (listing.get("city"), listing.get("state")) if p),
    ]
    bedrooms = listing.get("bedrooms")
    if bedrooms is not None:
        parts.append(f"{bedrooms} bedroom")
    return ". ".join(p.strip() for p in parts if p and p.strip())
