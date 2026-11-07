import os
import threading
import time

import numpy as np
import pytest

from app.repositories.listing_repository import ListingRepositoryError
from app.services import vector_index
from app.services.embedding import HashingEmbedder
from app.services.index_manager import IndexManager, SearchFilters, allowed_ids


class CountingEmbedder(HashingEmbedder):
    def __init__(self, dim=128):
        super().__init__(dim)
        self.encoded_texts = 0

    def encode(self, texts):
        self.encoded_texts += len(texts)
        return super().encode(texts)


class FakeRepo:
    def __init__(self, listings):
        self.listings = {l["id"]: dict(l) for l in listings}
        self.fail = False
        self.vanish = set()

    def set(self, listing):
        self.listings[listing["id"]] = dict(listing)

    def fetch_listing_versions(self):
        if self.fail:
            raise ListingRepositoryError("database is down")
        return {i: l["updated_at"] for i, l in self.listings.items()}

    def fetch_listings_by_ids(self, ids):
        if self.fail:
            raise ListingRepositoryError("database is down")
        return [dict(self.listings[i]) for i in ids if i in self.listings and i not in self.vanish]


def listing(listing_id, title, description, city="Pune", price=10000.0, bedrooms=1, updated="2025-01-01T00:00:00"):
    return {"id": listing_id, "title": title, "description": description, "city": city, "state": "MH",
            "price": price, "bedrooms": bedrooms, "is_available": True, "updated_at": updated}


@pytest.fixture
def catalogue():
    return [
        listing("a", "Sunny studio near metro", "Bright studio apartment close to the metro station"),
        listing("b", "Spacious family home", "Three bedroom house with garden and parking", price=25000.0, bedrooms=3),
        listing("c", "Budget single room", "Cheap single room for students", city="Mumbai", price=5000.0),
        listing("d", "Luxury penthouse", "Penthouse with sea view and rooftop pool", city="Mumbai", price=90000.0, bedrooms=4),
    ]


def make_manager(repo, embedder=None, index_dir=None, interval=0.0):
    return IndexManager(repo, embedder or CountingEmbedder(), index_dir=index_dir, refresh_interval=interval)


def top_ids(manager, query, k=3, filters=None):
    return [i for i, _ in manager.semantic_search(query, k, filters)]


# ---------------------------------------------------------------- building and refreshing
def test_first_refresh_indexes_every_listing(catalogue):
    manager = make_manager(FakeRepo(catalogue))
    result = manager.refresh()

    assert (result.added, result.updated, result.removed, result.total) == (4, 0, 0, 4)
    assert manager.snapshot.size == 4
    assert top_ids(manager, "studio near the metro")[0] == "a"


def test_refresh_without_changes_does_no_work(catalogue):
    embedder = CountingEmbedder()
    manager = make_manager(FakeRepo(catalogue), embedder)
    manager.refresh()
    version, encoded = manager.snapshot.version, embedder.encoded_texts

    result = manager.refresh()

    assert result.changed is False
    assert result.unchanged == 4
    assert manager.snapshot.version == version
    assert embedder.encoded_texts == encoded


def test_only_changed_listings_are_re_embedded(catalogue):
    repo = FakeRepo(catalogue)
    embedder = CountingEmbedder()
    manager = make_manager(repo, embedder)
    manager.refresh()
    before = embedder.encoded_texts

    repo.set(listing("c", "Lakeside cottage", "Quiet cottage beside the lake", city="Mumbai", updated="2025-02-01T00:00:00"))
    result = manager.refresh()

    assert (result.added, result.updated, result.removed, result.unchanged) == (0, 1, 0, 3)
    assert embedder.encoded_texts - before == 1
    assert top_ids(manager, "cottage beside the lake", k=1) == ["c"]


def test_unchanged_vectors_are_reused_exactly(catalogue):
    repo = FakeRepo(catalogue)
    manager = make_manager(repo)
    manager.refresh()
    before = vector_index.snapshot_vectors(manager.snapshot)
    ids_before = manager.snapshot.ids

    repo.set(listing("e", "New listing", "Brand new flat near the park"))
    manager.refresh()
    after = vector_index.snapshot_vectors(manager.snapshot)

    for listing_id in ids_before:
        assert np.allclose(before[ids_before.index(listing_id)], after[manager.snapshot.positions[listing_id]])


def test_removed_listings_disappear_and_added_listings_appear(catalogue):
    repo = FakeRepo(catalogue)
    manager = make_manager(repo)
    manager.refresh()

    del repo.listings["a"]
    repo.set(listing("z", "Hillside villa", "Large villa on the hillside with a view"))
    result = manager.refresh()

    assert (result.added, result.removed) == (1, 1)
    assert "a" not in manager.snapshot.positions
    assert top_ids(manager, "villa on the hillside", k=1) == ["z"]


def test_listing_that_changes_then_becomes_unavailable_is_dropped(catalogue):
    repo = FakeRepo(catalogue)
    manager = make_manager(repo)
    manager.refresh()

    repo.set(listing("a", "Changed", "Changed text", updated="2025-03-01T00:00:00"))
    repo.vanish.add("a")
    result = manager.refresh()

    assert "a" not in manager.snapshot.positions
    assert result.removed == 1


def test_forced_refresh_re_embeds_everything(catalogue):
    embedder = CountingEmbedder()
    manager = make_manager(FakeRepo(catalogue), embedder)
    manager.refresh()
    before = embedder.encoded_texts

    result = manager.refresh(force=True)

    assert result.forced is True
    assert embedder.encoded_texts - before == 4


def test_changing_the_embedding_model_rebuilds_the_whole_index(catalogue):
    repo = FakeRepo(catalogue)
    manager = make_manager(repo, CountingEmbedder(dim=64))
    manager.refresh()
    manager._embedder = CountingEmbedder(dim=128)

    result = manager.refresh()

    assert result.forced is True
    assert manager.snapshot.dim == 128
    assert manager._embedder.encoded_texts == 4


def test_database_failure_keeps_serving_the_previous_index(catalogue):
    repo = FakeRepo(catalogue)
    manager = make_manager(repo)
    manager.refresh()

    repo.fail = True
    with pytest.raises(ListingRepositoryError):
        manager.refresh()

    assert manager.snapshot.size == 4
    assert top_ids(manager, "studio near the metro")[0] == "a"
    assert "database is down" in manager.stats()["last_error"]

    repo.fail = False
    manager.refresh()
    assert manager.stats()["last_error"] is None


def test_empty_catalogue_yields_an_empty_working_index():
    manager = make_manager(FakeRepo([]))
    manager.refresh()
    assert manager.snapshot.size == 0
    assert manager.semantic_search("anything", 5) == []


# ---------------------------------------------------------------- search and filters
def test_blank_query_returns_nothing(catalogue):
    manager = make_manager(FakeRepo(catalogue))
    manager.refresh()
    assert manager.semantic_search("   ", 5) == []


def test_filters_are_applied_inside_the_search(catalogue):
    manager = make_manager(FakeRepo(catalogue))
    manager.refresh()

    assert set(top_ids(manager, "room", k=10, filters=SearchFilters(city="mumbai"))) == {"c", "d"}
    assert set(top_ids(manager, "room", k=10, filters=SearchFilters(max_price=10000))) == {"a", "c"}
    assert set(top_ids(manager, "room", k=10, filters=SearchFilters(min_price=20000))) == {"b", "d"}
    assert top_ids(manager, "room", k=10, filters=SearchFilters(bedrooms=3)) == ["b"]
    assert top_ids(manager, "room", k=10, filters=SearchFilters(city="Delhi")) == []


def test_allowed_ids_is_none_without_filters(catalogue):
    manager = make_manager(FakeRepo(catalogue))
    manager.refresh()
    assert allowed_ids(manager.snapshot, None) is None
    assert allowed_ids(manager.snapshot, SearchFilters()) is None


def test_stats_describe_the_index(catalogue):
    manager = make_manager(FakeRepo(catalogue))
    manager.refresh()
    stats = manager.stats()
    assert stats["listings"] == 4
    assert stats["version"] == 1
    assert stats["last_refresh"]["added"] == 4


# ---------------------------------------------------------------- persistence
def test_index_survives_a_restart_without_re_embedding(tmp_path, catalogue):
    repo = FakeRepo(catalogue)
    first = make_manager(repo, CountingEmbedder(), index_dir=str(tmp_path))
    first.start()
    assert os.path.exists(tmp_path / "index.faiss") and os.path.exists(tmp_path / "meta.json")

    embedder = CountingEmbedder()
    second = make_manager(repo, embedder, index_dir=str(tmp_path))
    second.start()

    assert second.snapshot.size == 4
    assert embedder.encoded_texts == 0
    assert top_ids(second, "studio near the metro")[0] == "a"


def test_restart_picks_up_changes_made_while_the_service_was_down(tmp_path, catalogue):
    repo = FakeRepo(catalogue)
    make_manager(repo, index_dir=str(tmp_path)).start()

    del repo.listings["b"]
    repo.set(listing("n", "Garden flat", "Flat with a private garden"))
    embedder = CountingEmbedder()
    restarted = make_manager(repo, embedder, index_dir=str(tmp_path))
    restarted.start()

    assert "b" not in restarted.snapshot.positions
    assert "n" in restarted.snapshot.positions
    assert embedder.encoded_texts == 1


def test_saved_index_from_another_model_is_ignored(tmp_path, catalogue):
    repo = FakeRepo(catalogue)
    make_manager(repo, CountingEmbedder(dim=64), index_dir=str(tmp_path)).start()

    embedder = CountingEmbedder(dim=128)
    manager = make_manager(repo, embedder, index_dir=str(tmp_path))
    manager.start()

    assert manager.snapshot.dim == 128
    assert embedder.encoded_texts == 4


def test_corrupt_saved_index_is_ignored_and_rebuilt(tmp_path, catalogue):
    repo = FakeRepo(catalogue)
    make_manager(repo, index_dir=str(tmp_path)).start()
    (tmp_path / "meta.json").write_text("{not json")

    embedder = CountingEmbedder()
    manager = make_manager(repo, embedder, index_dir=str(tmp_path))
    manager.start()

    assert manager.snapshot.size == 4
    assert embedder.encoded_texts == 4


def test_mismatched_index_and_metadata_are_rejected(tmp_path, catalogue):
    repo = FakeRepo(catalogue)
    make_manager(repo, index_dir=str(tmp_path)).start()
    snapshot = vector_index.load_snapshot(str(tmp_path))
    smaller = vector_index.build_snapshot(
        snapshot.ids[:2], snapshot.docs, snapshot.fingerprints,
        vector_index.snapshot_vectors(snapshot)[:2], snapshot.model, snapshot.dim, snapshot.version,
    )
    # An index with 2 vectors next to metadata that lists 4 ids must not load.
    import faiss
    faiss.write_index(smaller.index, str(tmp_path / "index.faiss"))
    assert vector_index.load_snapshot(str(tmp_path)) is None


def test_missing_directory_loads_nothing(tmp_path):
    assert vector_index.load_snapshot(str(tmp_path / "nope")) is None


def test_a_failed_save_does_not_break_serving(catalogue, monkeypatch):
    def broken_save(snapshot, directory):
        raise OSError("disk full")

    monkeypatch.setattr(vector_index, "save_snapshot", broken_save)
    manager = make_manager(FakeRepo(catalogue), index_dir="/unwritable")
    manager.refresh()
    assert manager.snapshot.size == 4


# ---------------------------------------------------------------- background refresh and concurrency
def test_background_refresher_picks_up_new_listings(catalogue):
    repo = FakeRepo(catalogue)
    manager = make_manager(repo, interval=0.05)
    manager.start()
    try:
        repo.set(listing("late", "Late arrival", "Listing added after startup"))
        deadline = time.time() + 3
        while time.time() < deadline and "late" not in manager.snapshot.positions:
            time.sleep(0.02)
        assert "late" in manager.snapshot.positions
    finally:
        manager.stop()


def test_background_refresher_survives_database_errors(catalogue):
    repo = FakeRepo(catalogue)
    manager = make_manager(repo, interval=0.05)
    manager.start()
    try:
        repo.fail = True
        time.sleep(0.2)
        repo.fail = False
        repo.set(listing("back", "Recovered", "Added after the outage"))
        deadline = time.time() + 3
        while time.time() < deadline and "back" not in manager.snapshot.positions:
            time.sleep(0.02)
        assert "back" in manager.snapshot.positions
    finally:
        manager.stop()


def test_searches_during_refreshes_never_fail_or_see_partial_state(catalogue):
    repo = FakeRepo(catalogue)
    manager = make_manager(repo)
    manager.refresh()
    errors = []
    stop = threading.Event()

    def writer():
        n = 0
        while not stop.is_set():
            n += 1
            repo.set(listing(f"x{n % 5}", f"Listing {n}", f"Generated listing number {n}", updated=f"2025-01-{n % 28 + 1:02d}T00:00:{n % 60:02d}"))
            try:
                manager.refresh()
            except Exception as exc:
                errors.append(exc)

    thread = threading.Thread(target=writer)
    thread.start()
    try:
        for _ in range(300):
            snapshot = manager.snapshot
            hits = manager.semantic_search("studio near the metro", 5, snapshot=snapshot)
            assert all(listing_id in snapshot.docs for listing_id, _ in hits)
            assert snapshot.index.ntotal == snapshot.size == len(snapshot.docs)
    finally:
        stop.set()
        thread.join()
    assert errors == []
