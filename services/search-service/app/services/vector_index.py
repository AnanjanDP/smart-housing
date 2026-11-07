from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import faiss
import numpy as np


@dataclass(frozen=True)
class IndexSnapshot:
    """An immutable view of the searchable listings.

    Searches read one snapshot from start to finish. Refreshing builds a new snapshot and swaps the
    reference, so a request never sees a half-updated index.
    """

    index: "faiss.Index"
    ids: Tuple[str, ...]
    positions: Dict[str, int]
    docs: Dict[str, dict]
    fingerprints: Dict[str, str]
    model: str
    dim: int
    version: int
    built_at: float

    @property
    def size(self) -> int:
        return len(self.ids)


def build_snapshot(
    ids: Sequence[str],
    docs: Dict[str, dict],
    fingerprints: Dict[str, str],
    vectors: np.ndarray,
    model: str,
    dim: int,
    version: int = 1,
) -> IndexSnapshot:
    ids = tuple(ids)
    if len(set(ids)) != len(ids):
        raise ValueError("Listing ids must be unique")
    vectors = np.ascontiguousarray(vectors, dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape[0] != len(ids):
        raise ValueError("vectors must have shape (len(ids), dim)")
    if len(ids) and vectors.shape[1] != dim:
        raise ValueError(f"vectors have dimension {vectors.shape[1]}, expected {dim}")

    index = faiss.IndexFlatIP(dim)
    if len(ids):
        index.add(vectors)

    return IndexSnapshot(
        index=index,
        ids=ids,
        positions={listing_id: pos for pos, listing_id in enumerate(ids)},
        docs={listing_id: docs[listing_id] for listing_id in ids},
        fingerprints={listing_id: fingerprints[listing_id] for listing_id in ids},
        model=model,
        dim=dim,
        version=version,
        built_at=time.time(),
    )


def empty_snapshot(model: str, dim: int, version: int = 0) -> IndexSnapshot:
    return build_snapshot([], {}, {}, np.zeros((0, dim), dtype=np.float32), model, dim, version)


def snapshot_vectors(snapshot: IndexSnapshot) -> np.ndarray:
    """All stored vectors in id order, read back from the FAISS index."""
    if snapshot.size == 0:
        return np.zeros((0, snapshot.dim), dtype=np.float32)
    return snapshot.index.reconstruct_n(0, snapshot.size)


def search(
    snapshot: IndexSnapshot,
    query_vector: np.ndarray,
    k: int,
    allowed_ids: Optional[Iterable[str]] = None,
) -> List[Tuple[str, float]]:
    """Exact nearest-neighbour search, optionally restricted to a set of listing ids.

    The restriction is applied inside FAISS with an id selector (a pre-filter), so you always get up
    to k results from the allowed set. Filtering after the search would return fewer than k results
    whenever disallowed listings crowd the top of the ranking.
    """
    if k <= 0 or snapshot.size == 0:
        return []

    query = np.ascontiguousarray(query_vector, dtype=np.float32).reshape(1, -1)
    if query.shape[1] != snapshot.dim:
        raise ValueError(f"query has dimension {query.shape[1]}, index expects {snapshot.dim}")

    params = None
    candidate_count = snapshot.size
    if allowed_ids is not None:
        allowed_positions = sorted(
            snapshot.positions[i] for i in set(allowed_ids) if i in snapshot.positions
        )
        if not allowed_positions:
            return []
        candidate_count = len(allowed_positions)
        if candidate_count < snapshot.size:
            selector = faiss.IDSelectorBatch(np.asarray(allowed_positions, dtype=np.int64))
            params = faiss.SearchParameters()
            params.sel = selector

    k = min(k, candidate_count)
    if params is not None:
        scores, positions = snapshot.index.search(query, k, params=params)
    else:
        scores, positions = snapshot.index.search(query, k)

    return [
        (snapshot.ids[pos], float(score))
        for score, pos in zip(scores[0], positions[0])
        if pos >= 0
    ]
