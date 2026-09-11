.PHONY: help setup lint format test test-cov docker-up docker-down tf-validate

help:
	@echo "Comandos disponibles:"
	@echo "  make setup        - Crear venv e instalar dependencias"
	@echo "  make lint         - Ejecutar linters (ruff, mypy)"
	@echo "  make format       - Dar formato al código (ruff format)"
	@echo "  make test         - Ejecutar pruebas automatizadas"
	@echo "  make test-cov     - Pruebas con informe de cobertura"
	@echo "  make docker-up    - Levantar contenedores Docker"
	@echo "  make docker-down  - Detener contenedores Docker"
	@echo "  make tf-validate  - Validar Terraform"

setup:
	python -m venv .venv
	.venv/bin/pip install -r backend/requirements.txt || .venv/Scripts/pip install -r backend/requirements.txt

lint:
	python -m ruff check backend frontend
	python -m mypy backend

format:
	python -m ruff format backend frontend

test:
	python -m pytest backend/tests

test-cov:
	python -m pytest backend/tests --cov=app --cov-report=term-missing

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

tf-validate:
	terraform -chdir=infra/terraform/envs/dev init -backend=false
	terraform -chdir=infra/terraform/envs/dev validate
