from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from app.services import vector_index
from app.services.embedding import Embedder, listing_text
from app.services.vector_index import IndexSnapshot

logger = logging.getLogger(__name__)

FETCH_BATCH = 500


@dataclass
class RefreshResult:
    added: int = 0
    updated: int = 0
    removed: int = 0
    unchanged: int = 0
    total: int = 0
    changed: bool = False
    duration_seconds: float = 0.0
    forced: bool = False

    def as_dict(self) -> dict:
        return {
            "added": self.added,
            "updated": self.updated,
            "removed": self.removed,
            "unchanged": self.unchanged,
            "total": self.total,
            "changed": self.changed,
            "forced": self.forced,
            "duration_seconds": round(self.duration_seconds, 3),
        }


@dataclass
class SearchFilters:
    city: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None

    def is_empty(self) -> bool:
        return all(v is None for v in (self.city, self.min_price, self.max_price, self.bedrooms))

    def matches(self, listing: dict) -> bool:
        if self.city and self.city.lower() not in str(listing.get("city", "")).lower():
            return False
        if self.min_price is not None and listing.get("price", 0.0) < self.min_price:
            return False
        if self.max_price is not None and listing.get("price", 0.0) > self.max_price:
            return False
        if self.bedrooms is not None and listing.get("bedrooms") != self.bedrooms:
            return False
        return True


def allowed_ids(snapshot: IndexSnapshot, filters: Optional[SearchFilters]) -> Optional[Set[str]]:
    """Ids of listings that satisfy the filters, or None when there is nothing to filter."""
    if filters is None or filters.is_empty():
        return None
    return {listing_id for listing_id, doc in snapshot.docs.items() if filters.matches(doc)}


class IndexManager:
    """Owns the live FAISS index: builds it, keeps it in step with the database, and serves searches.

    The current snapshot is replaced as a whole under a lock; readers take a reference and use it
    without locking, so a refresh never blocks or corrupts a search.
    """

    def __init__(
        self,
        repository,
        embedder: Embedder,
        index_dir: Optional[str] = None,
        refresh_interval: float = 0.0,
    ):
        self._repo = repository
        self._embedder = embedder
        self._index_dir = index_dir or None
        self._refresh_interval = refresh_interval

        self._snapshot: Optional[IndexSnapshot] = None
        self._swap_lock = threading.Lock()
        self._refresh_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self._last_result: Optional[RefreshResult] = None
        self._last_error: Optional[str] = None
        self._last_refresh_at: Optional[float] = None
        self._embed_query = lru_cache(maxsize=1024)(self._embed_query_uncached)

    # ------------------------------------------------------------------ lifecycle
    def start(self) -> None:
        """Load any saved index, bring it up to date, and start the background refresher."""
        self._load_persisted()
        try:
            self.refresh()
        except Exception as exc:
            logger.warning("Initial index refresh failed, serving the saved index if any: %s", exc)
        if self._refresh_interval > 0 and self._thread is None:
            self._stop.clear()
            self._thread = threading.Thread(target=self._loop, name="index-refresher", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None

    def _loop(self) -> None:
        while not self._stop.wait(self._refresh_interval):
            try:
                self.refresh()
            except Exception as exc:
                logger.warning("Background index refresh failed: %s", exc)

    def _load_persisted(self) -> None:
        if not self._index_dir or self._snapshot is not None:
            return
        saved = vector_index.load_snapshot(self._index_dir)
        if saved is None:
            return
        if saved.model != self._embedder.name:
            logger.info("Ignoring saved index built with %s (current model is %s)", saved.model, self._embedder.name)
            return
        with self._swap_lock:
            self._snapshot = saved
        logger.info("Loaded saved index: %d listings, version %d", saved.size, saved.version)

    @property
    def ready(self) -> bool:
        """True once an index has been loaded from disk or built from the database."""
        return self._snapshot is not None

    # ------------------------------------------------------------------ snapshot access
    @property
    def snapshot(self) -> IndexSnapshot:
        current = self._snapshot
        if current is None:
            with self._swap_lock:
                if self._snapshot is None:
                    self._snapshot = vector_index.empty_snapshot(self._embedder.name, self._embedder.dim)
                current = self._snapshot
        return current

    # ------------------------------------------------------------------ refresh
    def refresh(self, force: bool = False) -> RefreshResult:
        """Bring the index in line with the database, re-embedding only what changed.

        Raises if the database cannot be read; the previous index stays in service.
        """
        with self._refresh_lock:
            started = time.time()
            try:
                result = self._refresh_locked(force)
            except Exception as exc:
                self._last_error = str(exc)
                raise
            result.duration_seconds = time.time() - started
            self._last_result = result
            self._last_error = None
            self._last_refresh_at = time.time()
            return result

    def _refresh_locked(self, force: bool) -> RefreshResult:
        current = self._snapshot
        versions: Dict[str, str] = self._repo.fetch_listing_versions()

        model_changed = current is not None and current.model != self._embedder.name
        reusable: Dict[str, str] = {} if (current is None or force or model_changed) else current.fingerprints

        to_fetch = [i for i, version in versions.items() if reusable.get(i) != version]
        removed_ids = [] if current is None else [i for i in current.ids if i not in versions]
        result = RefreshResult(forced=force or model_changed)

        if current is not None and not to_fetch and not removed_ids and not result.forced:
            result.unchanged = current.size
            result.total = current.size
            return result

        fetched: Dict[str, dict] = {}
        for start in range(0, len(to_fetch), FETCH_BATCH):
            for doc in self._repo.fetch_listings_by_ids(to_fetch[start:start + FETCH_BATCH]):
                fetched[doc["id"]] = doc

        # Keep a listing if it was just fetched, or if its saved copy is still current. A listing that was
        # fetched-for but did not come back (it became unavailable in between) is dropped.
        kept_ids = sorted(
            i for i, version in versions.items()
            if i in fetched or (current is not None and i in current.docs and reusable.get(i) == version)
        )

        new_vectors = self._encode_documents([fetched[i] for i in kept_ids if i in fetched])
        new_by_id = {i: new_vectors[n] for n, i in enumerate(i for i in kept_ids if i in fetched)}

        old_vectors = vector_index.snapshot_vectors(current) if current is not None and current.size else None
        rows: List[np.ndarray] = []
        docs: Dict[str, dict] = {}
        fingerprints: Dict[str, str] = {}
        for listing_id in kept_ids:
            if listing_id in fetched:
                rows.append(new_by_id[listing_id])
                docs[listing_id] = fetched[listing_id]
                fingerprints[listing_id] = fetched[listing_id].get("updated_at") or versions[listing_id]
            else:
                rows.append(old_vectors[current.positions[listing_id]])
                docs[listing_id] = current.docs[listing_id]
                fingerprints[listing_id] = current.fingerprints[listing_id]

        dim = self._embedder.dim
        matrix = np.vstack(rows) if rows else np.zeros((0, dim), dtype=np.float32)
        version = (current.version if current is not None else 0) + 1
        snapshot = vector_index.build_snapshot(
            kept_ids, docs, fingerprints, matrix, self._embedder.name, dim, version
        )

        previous_ids = set(current.ids) if current is not None else set()
        result.added = sum(1 for i in fetched if i not in previous_ids)
        result.updated = sum(1 for i in fetched if i in previous_ids)
        result.removed = len([i for i in previous_ids if i not in docs])
        result.unchanged = snapshot.size - result.added - result.updated
        result.total = snapshot.size
        result.changed = True

        with self._swap_lock:
            self._snapshot = snapshot
        logger.info(
            "Index refreshed to version %d: +%d ~%d -%d (total %d)",
            version, result.added, result.updated, result.removed, result.total,
        )
        self._persist(snapshot)
        return result

    def _encode_documents(self, documents: List[dict]) -> np.ndarray:
        if not documents:
            return np.zeros((0, self._embedder.dim), dtype=np.float32)
        return self._embedder.encode([listing_text(d) for d in documents])

    def _persist(self, snapshot: IndexSnapshot) -> None:
        if not self._index_dir:
            return
        try:
            vector_index.save_snapshot(snapshot, self._index_dir)
        except Exception as exc:
            logger.warning("Could not save the index to %s: %s", self._index_dir, exc)

    # ------------------------------------------------------------------ search
    def _embed_query_uncached(self, query: str) -> np.ndarray:
        vector = self._embedder.encode([query])[0]
        vector.setflags(write=False)
        return vector

    def semantic_search(
        self,
        query: str,
        k: int,
        filters: Optional[SearchFilters] = None,
        snapshot: Optional[IndexSnapshot] = None,
    ) -> List[Tuple[str, float]]:
        snapshot = snapshot or self.snapshot
        if snapshot.size == 0 or not query.strip():
            return []
        return vector_index.search(
            snapshot, self._embed_query(query.strip()), k, allowed_ids(snapshot, filters)
        )

    # ------------------------------------------------------------------ introspection
    def stats(self) -> dict:
        snapshot = self.snapshot
        return {
            "model": snapshot.model,
            "dimension": snapshot.dim,
            "listings": snapshot.size,
            "version": snapshot.version,
            "built_at": snapshot.built_at,
            "persisted": bool(self._index_dir),
            "refresh_interval_seconds": self._refresh_interval,
            "last_refresh_at": self._last_refresh_at,
            "last_refresh": self._last_result.as_dict() if self._last_result else None,
            "last_error": self._last_error,
        }


_manager: Optional[IndexManager] = None
_manager_lock = threading.Lock()


def get_index_manager() -> IndexManager:
    """The process-wide manager, created on first use from the service settings."""
    global _manager
    with _manager_lock:
        if _manager is None:
            from app.core.config import settings
            from app.repositories.listing_repository import ListingRepository
            from app.services.embedding import get_embedder

            _manager = IndexManager(
                ListingRepository(),
                get_embedder(settings.EMBEDDING_BACKEND, settings.EMBEDDING_MODEL_NAME),
                index_dir=settings.VECTOR_INDEX_DIR or None,
                refresh_interval=settings.INDEX_REFRESH_INTERVAL_SECONDS,
            )
        return _manager


def set_index_manager(manager: Optional[IndexManager]) -> None:
    global _manager
    with _manager_lock:
        _manager = manager
