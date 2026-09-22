$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "    PROYECTOCLIMATICO - VALIDACIÓN QUALITY GATE   " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Backend Validations
Write-Host "--> [1/4] Validando Backend (Lint, Tipos, Tests, Cobertura)..." -ForegroundColor Yellow
Push-Location backend
try {
    python -m ruff check .
    python -m ruff format --check .
    python -m mypy app
    pytest --cov=app --cov-report=term-missing --cov-report=xml --cov-fail-under=80
} finally {
    Pop-Location
}

# 2. Frontend Validations
Write-Host "--> [2/4] Validando Frontend (Lint, Tipos, Tests, Cobertura)..." -ForegroundColor Yellow
Push-Location frontend
try {
    python -m ruff check .
    python -m ruff format --check .
    python -m mypy proyecto_climatico rxconfig.py serve.py
    pytest --cov=proyecto_climatico.state --cov=proyecto_climatico.services --cov-report=term-missing --cov-fail-under=80
} finally {
    Pop-Location
}

# 3. Terraform Validations
Write-Host "--> [3/4] Validando Terraform..." -ForegroundColor Yellow
terraform fmt -check -recursive infra/terraform
$envs = @("dev", "prod", "prueba")
foreach ($env in $envs) {
    if (Test-Path "infra/terraform/envs/$env") {
        terraform -chdir="infra/terraform/envs/$env" init -backend=false
        terraform -chdir="infra/terraform/envs/$env" validate
    }
}

# 4. Security & Repository checks
Write-Host "--> [4/4] Validando Seguridad y Repository Checks..." -ForegroundColor Yellow
python scripts/check_repository.py

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "    QUALITY GATE: TODOS LOS CHECKS PASARON (>= 80%)" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
