.PHONY: setup lint format test test-cov mutation docker-up docker-down tf-validate
setup:
	python -m pip install --require-hashes -r backend/requirements-dev.lock
	python -m pip install --require-hashes -r frontend/requirements-dev.lock
	python -m pip install --no-deps -e backend -e frontend
lint:
	python -m ruff check backend frontend scripts tests/e2e
	python -m ruff format --check backend frontend scripts tests/e2e
	python -m mypy --config-file backend/pyproject.toml backend/app
	python -m mypy --config-file frontend/pyproject.toml frontend/proyecto_climatico frontend/rxconfig.py frontend/serve.py
format:
	python -m ruff format backend frontend scripts tests/e2e
test:
	python -m pytest backend/tests
	python -m pytest frontend/tests
test-cov:
	python -m pytest backend/tests --cov=app --cov-report=term-missing --cov-fail-under=85
	python -m pytest frontend/tests --cov=proyecto_climatico.state --cov=proyecto_climatico.services --cov-fail-under=80
mutation:
	python scripts/mutation_smoke.py
docker-up:
	docker compose up --build --wait
docker-down:
	docker compose down
tf-validate:
	terraform fmt -check -recursive infra/terraform
	terraform -chdir=infra/terraform/envs/dev init -backend=false -lockfile=readonly
	terraform -chdir=infra/terraform/envs/dev validate
	terraform -chdir=infra/terraform/envs/prod init -backend=false -lockfile=readonly
	terraform -chdir=infra/terraform/envs/prod validate
