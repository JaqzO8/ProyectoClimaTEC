#!/usr/bin/env bash
set -eo pipefail

echo "=================================================="
echo "    PROYECTOCLIMATICO - VALIDACIÓN QUALITY GATE   "
echo "=================================================="

# 1. Backend Validations
echo "--> [1/4] Validando Backend (Lint, Tipos, Tests, Cobertura)..."
cd backend
python -m ruff check .
python -m ruff format --check .
python -m mypy app
pytest --cov=app --cov-report=term-missing --cov-report=xml --cov-fail-under=80
cd ..

# 2. Frontend Validations
echo "--> [2/4] Validando Frontend (Lint, Tipos, Tests, Cobertura)..."
cd frontend
python -m ruff check .
python -m ruff format --check .
python -m mypy proyecto_climatico rxconfig.py serve.py
pytest --cov=proyecto_climatico.state --cov=proyecto_climatico.services --cov-report=term-missing --cov-fail-under=80
cd ..

# 3. Terraform Validations
echo "--> [3/4] Validando Terraform..."
terraform fmt -check -recursive infra/terraform
for env in dev prod prueba; do
  if [ -d "infra/terraform/envs/$env" ]; then
    terraform -chdir="infra/terraform/envs/$env" init -backend=false > /dev/null 2>&1 || true
    terraform -chdir="infra/terraform/envs/$env" validate
  fi
done

# 4. Security & Repository checks
echo "--> [4/4] Validando Seguridad y Repository Checks..."
python scripts/check_repository.py

echo ""
echo "=================================================="
echo "    QUALITY GATE: TODOS LOS CHECKS PASARON (>= 80%)"
echo "=================================================="
