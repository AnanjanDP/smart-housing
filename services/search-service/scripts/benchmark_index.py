"""Measure FAISS search latency at different catalogue sizes.

    python scripts/benchmark_index.py                  # synthetic vectors, no model needed
    python scripts/benchmark_index.py --embed 1000     # also time real embedding of 1000 listings

Numbers depend on your hardware; run it on the machine you care about.
"""
import argparse
import os
import statistics
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import vector_index  # noqa: E402


def percentile(values, q):
    return float(np.percentile(values, q))


def bench(n, dim, queries):
    rng = np.random.default_rng(0)
    vectors = rng.standard_normal((n, dim)).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    ids = [f"id{i}" for i in range(n)]
    snapshot = vector_index.build_snapshot(
        ids, {i: {} for i in ids}, {i: "v" for i in ids}, vectors, "bench", dim
    )
    qs = rng.standard_normal((queries, dim)).astype(np.float32)
    qs /= np.linalg.norm(qs, axis=1, keepdims=True)
    allowed = set(ids[: max(1, n // 10)])

    def timed(**kwargs):
        samples = []
        for q in qs:
            started = time.perf_counter()
            vector_index.search(snapshot, q, 20, **kwargs)
            samples.append((time.perf_counter() - started) * 1000)
        return samples

    plain, filtered = timed(), timed(allowed_ids=allowed)
    return plain, filtered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dim", type=int, default=384)
    parser.add_argument("--queries", type=int, default=200)
    parser.add_argument("--sizes", type=int, nargs="+", default=[1_000, 10_000, 100_000])
    parser.add_argument("--embed", type=int, default=0, help="also time embedding this many listings")
    args = parser.parse_args()

    print(f"{'listings':>10} {'p50 ms':>8} {'p95 ms':>8} | {'filtered p50':>12} {'filtered p95':>12}")
    for n in args.sizes:
        plain, filtered = bench(n, args.dim, args.queries)
        print(f"{n:>10} {statistics.median(plain):>8.2f} {percentile(plain, 95):>8.2f} | "
              f"{statistics.median(filtered):>12.2f} {percentile(filtered, 95):>12.2f}")

    if args.embed:
        from app.services.embedding import SentenceTransformerEmbedder

        embedder = SentenceTransformerEmbedder()
        embedder.encode(["warm up"])
        texts = [f"Listing {i}. Bright {i % 4 + 1} bedroom flat near the metro in area {i % 50}." for i in range(args.embed)]
        started = time.perf_counter()
        embedder.encode(texts)
        elapsed = time.perf_counter() - started
        print(f"\nembedding {args.embed} listings: {elapsed:.2f}s ({args.embed / elapsed:.0f} listings/s)")
        started = time.perf_counter()
        embedder.encode(["quiet flat near the metro"])
        print(f"embedding one query: {(time.perf_counter() - started) * 1000:.1f} ms")


if __name__ == "__main__":
    main()
