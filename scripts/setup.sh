#!/usr/bin/env bash
set -e

echo "=== Initializing StayMatch Platform Environment ==="

if [ ! -f .env ]; then
  echo "Copying .env.example to .env..."
  cp .env.example .env
fi

echo "Building Docker Containers..."
docker-compose build

echo "Starting Docker Services..."
docker-compose up -d

echo "Waiting for Postgres to become healthy..."
until docker-compose exec postgres pg_isready -U staymatch_user -d staymatch_db; do
  echo "Waiting for database..."
  sleep 2
done

echo "Running Django Migrations..."
docker-compose exec core-api python manage.py migrate

echo "Seeding initial dataset..."
docker-compose exec core-api python scripts/seed_database.py

echo "=== StayMatch Setup Complete! ==="
