# OSPF Demo - Development Commands
# Usage: make <command>

.PHONY: help dev up down logs backend frontend db-reset shell-backend shell-frontend

# Default target
help:
	@echo "OSPF Demo - Available Commands"
	@echo ""
	@echo "  make dev          - Start all services (recommended)"
	@echo "  make up           - Start all services in background"
	@echo "  make down         - Stop all services"
	@echo "  make logs         - View logs from all services"
	@echo ""
	@echo "  make backend      - Start only backend"
	@echo "  make frontend     - Start only frontend"
	@echo ""
	@echo "  make db-reset     - Reset database (WARNING: destroys data)"
	@echo "  make shell-backend  - Shell into backend container"
	@echo "  make shell-frontend - Shell into frontend container"
	@echo ""
	@echo "First time setup:"
	@echo "  1. cp env.example .env"
	@echo "  2. Add your GOOGLE_API_KEY to .env"
	@echo "  3. make dev"
	@echo ""

# Start all services with logs
dev:
	docker compose up --build

# Start all services in background
up:
	docker compose up -d --build

# Stop all services
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Start only backend
backend:
	docker compose up --build backend postgres redis

# Start only frontend (requires backend running)
frontend:
	docker compose up --build frontend

# Reset database (destroys all data)
db-reset:
	docker compose down -v
	docker compose up -d postgres
	@echo "Database reset. Run 'make dev' to start all services."

# Shell into backend container
shell-backend:
	docker compose exec backend /bin/sh

# Shell into frontend container  
shell-frontend:
	docker compose exec frontend /bin/sh

# Run backend tests
test:
	docker compose exec backend pytest

# Format code
format:
	docker compose exec backend ruff format src/
	docker compose exec backend ruff check --fix src/

# Check types
typecheck:
	docker compose exec backend mypy src/
