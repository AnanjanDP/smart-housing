.PHONY: help build up down restart logs migrate seed test health-check clean

help:
	@echo "StayMatch Platform Makefile Commands:"
	@echo "  make build         - Build all docker services"
	@echo "  make up            - Start all docker containers in background"
	@echo "  make down          - Stop and remove all containers"
	@echo "  make restart       - Restart containers"
	@echo "  make logs          - View aggregated docker logs"
	@echo "  make migrate       - Run Django database migrations"
	@echo "  make seed          - Run database seed script"
	@echo "  make test          - Execute all backend unit test suites"
	@echo "  make health-check  - Run platform health check script"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

migrate:
	docker-compose exec core-api python manage.py migrate

seed:
	docker-compose exec core-api python scripts/seed_database.py

test:
	docker-compose exec core-api python manage.py test
	docker-compose exec search-service pytest
	docker-compose exec recommendation-service pytest
	docker-compose exec notification-service pytest

health-check:
	bash scripts/health_check.sh

clean:
	docker-compose down -v --remove-orphans
