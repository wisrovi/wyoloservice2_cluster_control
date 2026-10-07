# Makefile for NeuralForge Cluster Admin (API + UI)

VERSION := $(shell sed -n 's/^__version__ = "\(.*\)"/\1/p' api/backend/__init__.py)
DOCKER_COMPOSE := CLUSTER_ADMIN_VERSION=$(VERSION) docker compose
API_IMAGE := wisrovi/train_service:cluster_admin_api_v$(VERSION)
UI_IMAGE := wisrovi/train_service:cluster_admin_ui_v$(VERSION)

.PHONY: help setup build up down restart logs ps shell-api shell-ui test pytest coverage push dev clean version

help:
	@echo "🧠 NeuralForge Cluster Admin v$(VERSION) - Management CLI"
	@echo ""
	@echo "  make setup      - Create control_host.env from the example template"
	@echo "  make build      - Build API and UI Docker images"
	@echo "  make up         - Build and start the stack in background"
	@echo "  make down       - Stop and remove the stack"
	@echo "  make restart    - Recreate the stack"
	@echo "  make logs       - Follow container logs"
	@echo "  make ps         - Show container status"
	@echo "  make shell-api  - Open a shell in the API container"
	@echo "  make shell-ui   - Open a shell in the UI container"
	@echo "  make test       - Run unit tests inside Docker"
	@echo "  make coverage   - Run coverage inside Docker"
	@echo "  make push       - Push both images to Docker Hub"
	@echo "  make dev        - Run API and UI locally without Docker (start.sh)"
	@echo "  make clean      - Remove Python caches"

version:
	@echo $(VERSION)

setup:
	@if [ ! -f control_host.env ]; then cp control_host.env.example control_host.env && echo "✅ control_host.env created. Edit it before 'make up'."; else echo "⚠️  control_host.env already exists."; fi

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d --build

down:
	$(DOCKER_COMPOSE) down

restart: down up

logs:
	$(DOCKER_COMPOSE) logs -f

ps:
	$(DOCKER_COMPOSE) ps

shell-api:
	$(DOCKER_COMPOSE) exec cluster_admin_api /bin/bash

shell-ui:
	$(DOCKER_COMPOSE) exec cluster_admin_ui /bin/bash

test pytest:
	./run_tests.sh

coverage:
	./coverage.sh

push:
	docker push $(API_IMAGE)
	docker push $(UI_IMAGE)

dev:
	./start.sh

clean:
	find . -path ./old -prune -o -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
