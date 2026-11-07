# Search service

FastAPI service that answers listing searches. It combines **semantic search** (sentence embeddings in a FAISS index) with **keyword matching**, and fuses the two rankings with Reciprocal Rank Fusion (RRF).

## How a search works

```
query ──► embed (all-MiniLM-L6-v2, 384-d, L2-normalised)
            │
            ├─► FAISS IndexFlatIP, filters applied inside the search ──► ranked ids (cosine similarity)
            │
            └─► keyword matcher over the same in-memory snapshot ───────► ranked ids (share of matching terms)

                         RRF:  score(d) = sum over rankings of 1 / (60 + rank)
```

- **Embeddings.** Each available listing is turned into text (title, description, city and state, bedrooms) and embedded once. Vectors are unit length, so the inner product FAISS computes is cosine similarity.
- **Exact search.** `IndexFlatIP` scans every vector. That is exact and fast enough for this catalogue size (about 8 ms per query at 100,000 listings on a laptop CPU; run `scripts/benchmark_index.py` on your own hardware).
- **Filters run inside FAISS.** City, price and bedroom filters become an id selector, so a query always returns up to `k` listings that satisfy the filters. Filtering after the search would return too few results whenever filtered-out listings crowd the top of the ranking.
- **Fusion.** RRF uses ranks, not scores, so cosine similarities and keyword scores (which are not comparable) combine without normalisation.

## Keeping the index in step with the database

`IndexManager` owns the live index.

1. On startup it loads the last saved index (if the embedding model matches), then runs a refresh.
2. A refresh reads `(id, updated_at)` for every available listing, fetches **only the listings that are new or changed**, embeds just those, reuses the stored vectors for everything else, and builds a new snapshot.
3. The new snapshot is swapped in atomically. A search takes one snapshot and uses it from start to finish, so it never sees a half-updated index and a refresh never blocks a search.
4. The index and its metadata are written to disk (`VECTOR_INDEX_DIR`) with atomic renames, so a restart does not re-embed the catalogue.
5. If the database is unreachable, the refresh fails and the previous index keeps serving. A database outage is never mistaken for an empty catalogue.
6. A background thread repeats the refresh every `INDEX_REFRESH_INTERVAL_SECONDS`. `POST /index/refresh` triggers one on demand.

Changing `EMBEDDING_MODEL_NAME` rebuilds the whole index automatically (vectors from different models are not comparable).

## API

All routes are under `/api/v1/search`.

| Route | Purpose |
|---|---|
| `POST /query` | Search. Body: `query`, `mode` (`hybrid` default, `semantic`, `keyword`), `city`, `min_price`, `max_price`, `bedrooms`, `limit` (1-100). A blank query lists the filtered listings, newest first (`mode: "browse"`). |
| `GET /index/stats` | Model, dimension, listing count, index version, last refresh result and error |
| `POST /index/refresh?force=` | Refresh now (`force=true` re-embeds everything). Needs the `X-Admin-Token` header; disabled while `SEARCH_ADMIN_TOKEN` is empty |

Service-level: `GET /health` (process is up) and `GET /ready` (an index is loaded or built; 503 while warming up).

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `EMBEDDING_BACKEND` | `sentence-transformers` | `hash` uses a deterministic offline embedder (tests, development without a model) |
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Any sentence-transformers model |
| `VECTOR_INDEX_DIR` | empty (no persistence) | Where the index is saved; compose mounts a volume at `/data/vector_index` |
| `INDEX_REFRESH_INTERVAL_SECONDS` | `60` | `0` disables the background refresh |
| `SEARCH_ADMIN_TOKEN` | empty | Enables `POST /index/refresh` |

## Running and testing

```bash
pip install -r requirements.txt          # service + FAISS (enough to run the tests)
pip install -r requirements-ml.txt       # sentence-transformers, needed to serve real embeddings
pytest                                   # offline: uses the hashing embedder
RUN_MODEL_TESTS=1 pytest tests/test_real_embeddings.py   # downloads the model, checks semantic quality
python scripts/benchmark_index.py --embed 1000           # latency and embedding throughput
```

The Docker image installs CPU-only PyTorch and bakes the model into the image, so the container starts without network access.

## Limits and what comes next

- **Single process.** Each process holds its own model and index and writes the index files. Run one worker per container and scale with replicas (each replica builds its own copy from the database, or from a shared read-only volume). The production compose file therefore uses `--workers 1`.
- **Exact (flat) index.** Fine to a few hundred thousand listings. Beyond that, move to an IVF or HNSW index (or pgvector / a vector database); the search function is the only place that changes.
- **Change detection uses `updated_at`.** Bulk SQL updates that bypass Django's `auto_now` are missed until `POST /index/refresh?force=true`.
- **Keyword matching is term overlap on the in-memory snapshot**, not fuzzy matching. Typo-tolerant text search (PostgreSQL `pg_trgm`) and location-radius search are not implemented.

## Chat WebSocket

`/api/v1/search/ws/chat/{room_id}` is private and authenticated.

1. Open the socket (browser origin must be in `CORS_ALLOWED_ORIGINS`).
2. Within 5 seconds send `{"type": "auth", "token": "<core-api access token>"}`. The token is verified with
   `JWT_SIGNING_KEY` (the core-api `SECRET_KEY`), HS256 only, and must be an unexpired access token.
3. Rooms are `dm.<userA>.<userB>` (the two user ids, lower-case, sorted) or `listing.<listingId>.<tenantId>`
   (joinable only by that tenant and the listing's owner). Anyone else is closed with 4403.
4. Send `{"id": <client id>, "text": "...", "sender_name": "..."}`. The server sets `sender_id` from the token and
   broadcasts `{"type": "chat_message", "id", "client_id", "sender_id", "sender_name", "text", "timestamp"}`.

Close codes: 4401 not authenticated, 4403 forbidden, 4429 room full / flooding, 1009 frame too large, 1011 server error.
Limits: 8 KB per frame, 2000 characters per message, 10 messages per 10 seconds, 10 connections per room.

## Typo-tolerant search (pg_trgm)

`mode: "fuzzy"` ranks listings by PostgreSQL trigram similarity (`word_similarity`) of each query term against the
title, city, state and address, so "banglore" finds Bangalore. In `hybrid` mode it is a third ranking fused with the
keyword and semantic ones; if the database query fails that leg is skipped. The GIN indexes come from core-api
migration `listings.0002_trigram_indexes`. `tests/test_fuzzy_postgres.py` runs the query against a real PostgreSQL
(see the file header; CI starts one).
