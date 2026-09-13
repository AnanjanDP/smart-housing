# System Architecture Documentation

## Overview
StayMatch is an AI-enhanced smart housing & roommate finding platform designed using event-driven microservices architecture.

## Component Breakdown

1. **API Gateway / Reverse Proxy (Nginx)**
   - Routes ingress HTTP requests to downstream services based on URL path rules (`/api/v1/`, `/api/v1/search/`, `/api/v1/recommendations/`).
   - Handles SSL termination and CORS headers.

2. **Core API (`services/core-api`)**
   - Built with Django 5.0 and Django REST Framework.
   - Primary domain models: `User`, `Listing`, `RoommateProfile`, `Application`, `Review`, `Interaction`, `Notification`.
   - Emits Kafka events when major domain changes occur (e.g., listing published, application submitted).

3. **Search Service (`services/search-service`)**
   - Built with FastAPI.
   - Executes trigram fuzzy keyword matching and vector semantic similarity queries.
   - Combines scores using Reciprocal Rank Fusion (RRF).

4. **Recommendation Service (`services/recommendation-service`)**
   - Built with FastAPI.
   - Computes multi-factor roommate compatibility scores (budget match, lifestyle vectors, schedule overlap).
   - Generates personalized listing feeds for active users.

5. **Notification Service (`services/notification-service`)**
   - Asynchronous Python worker running Kafka consumers.
   - Formats notification messages and dispatches transactional emails or push notifications.

6. **Kafka Event Bus & Zookeeper**
   - Manages asynchronous event streams: `listing-events`, `application-events`, `review-events`, `notification-events`.

7. **Storage & Caching**
   - **PostgreSQL 15**: Primary relational data store with `pg_trgm` and `uuid-ossp` extensions.
   - **Redis 7**: Cache store for API responses and broker for Celery async background tasks.
