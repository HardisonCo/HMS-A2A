.PHONY: build up down restart logs ps clean test lint format help dev-env

# Environment variables
ENV_FILE := .env
include $(ENV_FILE)
export

# Docker compose command
DOCKER_COMPOSE := docker-compose

# Default target
all: help

# Build the Docker images
build:
	$(DOCKER_COMPOSE) build

# Start all services in the background
up:
	$(DOCKER_COMPOSE) up -d

# Start all services in the foreground with logs
start:
	$(DOCKER_COMPOSE) up

# Stop all services
down:
	$(DOCKER_COMPOSE) down

# Restart all services
restart: down up

# View logs for all services
logs:
	$(DOCKER_COMPOSE) logs -f

# View running services
ps:
	$(DOCKER_COMPOSE) ps

# Clean up Docker resources
clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans
	rm -rf __pycache__ .pytest_cache

# Run tests
test:
	cd src && pytest -v

# Run linting
lint:
	find . -type f -name "*.py" | xargs pylint
	find . -type f -name "*.rs" | xargs rustfmt --check

# Format code
format:
	find . -type f -name "*.py" | xargs black
	find . -type f -name "*.rs" | xargs rustfmt

# Setup local development environment
dev-env:
	python -m venv venv
	venv/bin/pip install -r requirements.txt
	@echo "Virtual environment created. Activate with 'source venv/bin/activate'"

# Run the genetic engine with real Rust implementation
build-genetic-engine:
	cd src/coordination/genetic-engine && cargo build --release

# Run the genetic engine tests
test-genetic-engine:
	cd src/coordination/genetic-engine && cargo test

# Run integration tests
integration-test:
	./run_integration_test.sh

# Run the demo
run-demo:
	./start-demo.sh

# Setup the development environment
setup-dev:
	./start-dev.sh

# Display help information
help:
	@echo "Available commands:"
	@echo "  make build           Build Docker images"
	@echo "  make up              Start services in the background"
	@echo "  make start           Start services in the foreground with logs"
	@echo "  make down            Stop services"
	@echo "  make restart         Restart services"
	@echo "  make logs            View logs for all services"
	@echo "  make ps              View running services"
	@echo "  make clean           Clean up Docker resources"
	@echo "  make test            Run tests"
	@echo "  make lint            Run linting"
	@echo "  make format          Format code"
	@echo "  make dev-env         Setup local development environment"
	@echo "  make build-genetic-engine  Build the Rust genetic engine"
	@echo "  make test-genetic-engine   Run genetic engine tests"
	@echo "  make integration-test      Run integration tests"
	@echo "  make run-demo             Run the demo"
	@echo "  make setup-dev            Setup the development environment"