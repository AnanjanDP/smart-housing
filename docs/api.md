# API Documentation & Endpoints

## Core API (`/api/v1/`)

### Auth Endpoints
- `POST /api/v1/users/register/` - Register new user
- `POST /api/v1/users/login/` - Login & retrieve JWT tokens (`access`, `refresh`)
- `GET  /api/v1/users/me/` - Retrieve current user profile

### Listing Endpoints
- `GET  /api/v1/listings/` - List & filter housing listings
- `POST /api/v1/listings/` - Create a listing (Landlord role required)
- `GET  /api/v1/listings/{id}/` - Retrieve listing details
- `PUT  /api/v1/listings/{id}/` - Update listing details

### Roommate Profiles
- `GET  /api/v1/roommates/profiles/` - List roommate profiles
- `POST /api/v1/roommates/profiles/` - Create / update current roommate profile
- `GET  /api/v1/roommates/compatibility/{profile_id}/` - Calculate compatibility score with a roommate

## Search Microservice (`/api/v1/search/`)
- `POST /api/v1/search/query` - Search listings. Body: `query`, `mode` (`hybrid` | `semantic` | `keyword`), `city`, `min_price`, `max_price`, `bedrooms`, `limit` (1-100). Semantic results come from a FAISS index of sentence embeddings; hybrid fuses them with keyword results using Reciprocal Rank Fusion. A blank query lists the filtered listings, newest first.
- `GET  /api/v1/search/index/stats` - Index model, size, version and last refresh result
- `POST /api/v1/search/index/refresh?force=` - Re-sync the index with the database (requires the `X-Admin-Token` header)
- `GET  /ready` - Readiness: 200 once the vector index is loaded or built, 503 while warming up

See `services/search-service/README.md` for how the index is built and kept current.

## Recommendation Microservice (`/api/v1/recommendations/`)
- `GET  /api/v1/recommendations/listings/{user_id}/` - Recommended listings for tenant
- `GET  /api/v1/recommendations/roommates/{user_id}/` - Top roommate matches ordered by score
