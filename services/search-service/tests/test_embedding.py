import numpy as np
import pytest

from app.services.embedding import (
    HashingEmbedder,
    SentenceTransformerEmbedder,
    get_embedder,
    l2_normalize,
    listing_text,
)


def test_hashing_embedder_is_deterministic_and_normalised():
    embedder = HashingEmbedder(dim=128)
    a = embedder.encode(["sunny studio near the metro", "garden house"])
    b = embedder.encode(["sunny studio near the metro", "garden house"])

    assert a.shape == (2, 128)
    assert a.dtype == np.float32
    assert np.array_equal(a, b)
    assert np.allclose(np.linalg.norm(a, axis=1), 1.0, atol=1e-5)


def test_similar_text_scores_higher_than_unrelated_text():
    embedder = HashingEmbedder()
    query, close, far = embedder.encode(
        ["studio near metro", "bright studio close to the metro station", "three bedroom house with garden"]
    )
    assert float(query @ close) > float(query @ far)


def test_empty_text_gives_zero_vector_not_nan():
    vectors = HashingEmbedder(dim=64).encode([""])
    assert vectors.shape == (1, 64)
    assert not np.isnan(vectors).any()
    assert np.allclose(vectors, 0.0)


def test_l2_normalize_leaves_zero_rows_untouched():
    out = l2_normalize(np.array([[3.0, 4.0], [0.0, 0.0]]))
    assert np.allclose(out[0], [0.6, 0.8])
    assert np.allclose(out[1], [0.0, 0.0])


def test_get_embedder_selects_backend():
    assert isinstance(get_embedder("hash"), HashingEmbedder)
    assert isinstance(get_embedder("sentence-transformers", "some/model"), SentenceTransformerEmbedder)
    with pytest.raises(ValueError):
        get_embedder("does-not-exist")


def test_sentence_transformer_embedder_does_not_load_model_on_construction():
    embedder = SentenceTransformerEmbedder("some/model-that-is-never-downloaded")
    assert embedder.name == "some/model-that-is-never-downloaded"
    assert embedder._model is None


def test_listing_text_combines_the_searchable_fields():
    text = listing_text(
        {"title": "Sunny studio", "description": "Near the metro", "city": "Pune", "state": "MH", "bedrooms": 1}
    )
    assert "Sunny studio" in text
    assert "Near the metro" in text
    assert "Pune, MH" in text
    assert "1 bedroom" in text


def test_listing_text_tolerates_missing_fields():
    assert listing_text({"title": "Only a title"}) == "Only a title"
