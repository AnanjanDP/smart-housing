from __future__ import annotations

import json
import os
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

    query = np.array(query_vector, dtype=np.float32, copy=True).reshape(1, -1)
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


INDEX_FILE = "index.faiss"
META_FILE = "meta.json"
FORMAT_VERSION = 1


def save_snapshot(snapshot: IndexSnapshot, directory: str) -> None:
    """Write the snapshot so a restart does not have to re-embed every listing.

    Each file is written to a temporary name and renamed into place; the metadata file is renamed
    last, so a reader that finds metadata always finds the matching index (it also checks the count).
    """
    os.makedirs(directory, exist_ok=True)
    index_path = os.path.join(directory, INDEX_FILE)
    meta_path = os.path.join(directory, META_FILE)

    faiss.write_index(snapshot.index, index_path + ".tmp")
    meta = {
        "format": FORMAT_VERSION,
        "model": snapshot.model,
        "dim": snapshot.dim,
        "version": snapshot.version,
        "built_at": snapshot.built_at,
        "ids": list(snapshot.ids),
        "fingerprints": snapshot.fingerprints,
        "docs": snapshot.docs,
    }
    with open(meta_path + ".tmp", "w", encoding="utf-8") as handle:
        json.dump(meta, handle)

    os.replace(index_path + ".tmp", index_path)
    os.replace(meta_path + ".tmp", meta_path)


def load_snapshot(directory: str) -> Optional[IndexSnapshot]:
    """Read a saved snapshot, or return None if it is missing, unreadable or inconsistent."""
    index_path = os.path.join(directory, INDEX_FILE)
    meta_path = os.path.join(directory, META_FILE)
    if not (os.path.exists(index_path) and os.path.exists(meta_path)):
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as handle:
            meta = json.load(handle)
        if meta.get("format") != FORMAT_VERSION:
            return None
        index = faiss.read_index(index_path)
        ids = tuple(meta["ids"])
        if index.ntotal != len(ids) or index.d != meta["dim"]:
            return None
        return IndexSnapshot(
            index=index,
            ids=ids,
            positions={listing_id: pos for pos, listing_id in enumerate(ids)},
            docs={listing_id: meta["docs"][listing_id] for listing_id in ids},
            fingerprints={listing_id: meta["fingerprints"][listing_id] for listing_id in ids},
            model=meta["model"],
            dim=int(meta["dim"]),
            version=int(meta["version"]),
            built_at=float(meta["built_at"]),
        )
    except Exception:
        return None
