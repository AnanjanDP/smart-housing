# StayMatch - Smart Housing & Roommate Matching Platform

StayMatch is an enterprise-grade, microservice-powered smart housing platform. It connects prospective tenants with verified housing listings and calculates AI-powered roommate compatibility scores.

## System Architecture Overview

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
|  Core Django API |  | Search Service   |  | Recommendation    |
| (Auth, Listings, |  | (Vector & Hybrid |  | Service (Matching |
|  Roommates, DB)  |  |  FastAPI)        |  |  ML Engine)       |
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
                    | Notification Event |
                    | Worker (Kafka Consumer)
                    +--------------------+
```

## Services & Tech Stack

1. **Core API (`services/core-api`)**: Python 3.11, Django 5.0, Django REST Framework, PostgreSQL, Celery, Redis.
2. **Search Microservice (`services/search-service`)**: FastAPI, Python 3.11, Vector Search, Trigram & Hybrid RRF ranking.
3. **Recommendation Microservice (`services/recommendation-service`)**: FastAPI, Cosine Similarity matching algorithms, Roommate compatibility engine.
4. **Notification Service (`services/notification-service`)**: Python Kafka event consumer for automated email & push alerts.
5. **Frontend (`frontend`)**: React 18, Axios, Lucide Icons, Modern CSS Design System.
6. **Infrastructure**: Docker Compose, Nginx, PostgreSQL, Redis, Apache Kafka, Prometheus & Grafana.

## Quickstart

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ & npm

### Running with Docker Compose
```bash
# 1. Clone & copy environment template
cp .env.example .env

# 2. Start all services
make up

# 3. Provision Kafka topics & seed database
make seed
```

### Accessing Services
- **Frontend SPA**: [http://localhost:3000](http://localhost:3000)
- **Nginx Gateway**: [http://localhost:8000](http://localhost:8000)
- **Django Core API**: [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
- **Search API Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Recommendation API Docs**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **Prometheus**: [http://localhost:9090](http://localhost:9090)
- **Grafana**: [http://localhost:3000](http://localhost:3000) (admin / admin)
