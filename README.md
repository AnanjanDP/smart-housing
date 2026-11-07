# StayMatch

StayMatch is a microservice-based housing platform that connects tenants with verified property listings and computes roommate compatibility scores.

## Quick start

You can run the full stack locally using Docker Compose. Make sure you have Docker and Docker Desktop installed.

Copy the environment variable template first:

```bash
cp .env.example .env
```

Start all microservices and the Nginx reverse proxy:

```bash
docker compose up -d --build
```

Seed the database with sample property listings and roommate profiles:

```bash
python scripts/seed_database.py
```

Once the containers start up, open your browser and head to `http://localhost:8000`.

### Service endpoints

- Frontend SPA: http://localhost:8000
- Core API (Django): http://localhost:8000/api/v1/
- Search service (FastAPI): http://localhost:8001/docs
- Recommendation service (FastAPI): http://localhost:8002/docs
- Prometheus metrics: http://localhost:9090

## Architecture

StayMatch separates concerns across four backend services, a React frontend, and an event pipeline driven by Apache Kafka. Nginx acts as the primary gateway routing traffic to downstream containers.

```
                  +-------------------+
                  |   React Frontend  |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |    Nginx Proxy    |
                  +---------+---------+
                            |
     +----------------------+----------------------+
     |                      |                      |
     v                      v                      v
+------------------+  +------------------+  +-------------------+
|  Core API        |  | Search Service   |  | Recommendation    |
| (Auth, Listings, |  | (Vector Search)  |  | Service (Matching)|
|  Roommates, DB)  |  | (FastAPI)        |  | (FastAPI)         |
+--------+---------+  +--------+---------+  +---------+---------+
         |                     |                      |
         +---------------------+----------------------+
                               |
                   +-----------+-----------+
                   |  Apache Kafka Event   |
                   |       Broker          |
                   +-----------+-----------+
                               |
                               v
                    +--------------------+
                    | Notification Worker|
                    +--------------------+
```

## Service overview

- **Core API (`services/core-api`)**: Built with Django 5.0 and Django REST Framework. Manages tenant and landlord authentication, user profiles, housing applications, and property listings backed by PostgreSQL.
- **Search service (`services/search-service`)**: Built with FastAPI. Embeds property listings with sentence-transformers, serves semantic search from an in-memory FAISS index kept in sync with PostgreSQL, and fuses it with keyword matching using Reciprocal Rank Fusion. See `services/search-service/README.md`.
- **Recommendation service (`services/recommendation-service`)**: Built with FastAPI. Computes compatibility percentages between roommate candidates based on budget, lifestyle choices, and dealbreaker filters.
- **Notification service (`services/notification-service`)**: Event-driven worker that consumes Kafka topics to trigger email notifications when users submit rental applications or message potential roommates.
- **Frontend (`frontend`)**: React 18 single-page application built with Vite and Lucide icons. Includes dual light/dark theme modes, property upload modals, and real-time roommate chat dialogs.

## Environment variables

The application reads system configuration from `.env`. The key variables required for local development include:

| Variable | Description | Default |
| --- | --- | --- |
| `DEBUG` | Enables Django debug mode | `True` |
| `SECRET_KEY` | Secret key for JWT signing | `django-insecure-...` |
| `POSTGRES_DB` | Main database name | `postgres` |
| `POSTGRES_USER` | Main database user | `postgres` |
| `POSTGRES_PASSWORD` | Main database password | `the_password` |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker host and port | `kafka:9092` |
| `VITE_SUPABASE_URL` | Supabase auth endpoint | Optional for OAuth |
| `VITE_SUPABASE_ANON_KEY` | Supabase public key | Optional for OAuth |

## Running locally without Docker

If you prefer to run services individually for development, start PostgreSQL, Redis, and Kafka first.

### Backend setup

Install dependencies inside virtual environments for each service:

```bash
# Core API
cd services/core-api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

```bash
# Search service
cd services/search-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8001 --reload
```

```bash
# Recommendation service
cd services/recommendation-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8002 --reload
```

### Frontend setup

Install dependencies and start the Vite dev server:

```bash
cd frontend
npm install
npm run dev
```

The dev server starts on `http://localhost:5173`.

## Database seeding

To populate your database with sample listings and roommate profiles:

```bash
python scripts/seed_database.py
```

This populates sample properties with image URLs, pricing tiers, and pre-configured roommate profiles so you can test search and matching right away.

## Running tests

Pytest handles backend test suites across the services:

```bash
# Core API tests
cd services/core-api
pytest

# Search service tests
cd ../search-service
pytest

# Recommendation service tests
cd ../recommendation-service
pytest
```
