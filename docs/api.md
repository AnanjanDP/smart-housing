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
- `GET  /api/v1/search/listings/` - Hybrid & semantic keyword query search
- `POST /api/v1/search/semantic/` - Vector embedding similarity query

## Recommendation Microservice (`/api/v1/recommendations/`)
- `GET  /api/v1/recommendations/listings/{user_id}/` - Recommended listings for tenant
- `GET  /api/v1/recommendations/roommates/{user_id}/` - Top roommate matches ordered by score
