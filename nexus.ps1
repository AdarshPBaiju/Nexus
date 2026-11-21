<#
.SYNOPSIS
    Project Nexus Windows CLI and Task Orchestrator.
.DESCRIPTION
    Provides native PowerShell execution parity for GNU Make targets across
    Python (uv), TypeScript (pnpm), Go, and Rust runtimes.
#>

param (
    [Parameter(Position = 0)]
    [string]$Command = "help",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host "Project Nexus Windows Orchestrator (nexus.ps1):" -ForegroundColor Cyan
    Write-Host "  install        Install dependencies across pnpm, uv, go, and cargo"
    Write-Host "  dev            Start development servers concurrently"
    Write-Host "  lint           Run static analysis (Ruff, ESLint, Go vet)"
    Write-Host "  lint-fix       Auto-fix safe lint violations"
    Write-Host "  format         Auto-format Python (Ruff) and TypeScript (Prettier)"
    Write-Host "  format-check   Verify formatting compliance in CI"
    Write-Host "  typecheck      Run static type assertions (mypy, tsc)"
    Write-Host "  test           Execute automated test suites"
    Write-Host "  db-up          Start local development container stack"
    Write-Host "  db-down        Stop local development container stack"
    Write-Host "  clean          Purge temporary caches and build artifacts"
}

switch ($Command.ToLower()) {
    "help" {
        Show-Help
    }
    "install" {
        Write-Host "==> Installing Node & TypeScript packages (pnpm)..." -ForegroundColor Green
        pnpm install
        Write-Host "==> Syncing Python virtual environment (uv)..." -ForegroundColor Green
        uv sync
        Write-Host "==> Dependencies successfully installed." -ForegroundColor Green
    }
    "dev" {
        Write-Host "==> Launching development servers..." -ForegroundColor Green
        pnpm turbo run dev
    }
    "lint" {
        Write-Host "==> Running Ruff lint check (Python)..." -ForegroundColor Green
        uv run ruff check .
        Write-Host "==> Running Turborepo lint (TypeScript)..." -ForegroundColor Green
        pnpm turbo run lint
    }
    "lint-fix" {
        Write-Host "==> Auto-fixing Python violations (Ruff)..." -ForegroundColor Green
        uv run ruff check --fix .
        Write-Host "==> Auto-fixing TypeScript / Web violations..." -ForegroundColor Green
        pnpm turbo run lint:fix
    }
    "format" {
        Write-Host "==> Formatting Python files (Ruff)..." -ForegroundColor Green
        uv run ruff format .
        Write-Host "==> Formatting TypeScript/JSON/YAML files (Prettier)..." -ForegroundColor Green
        pnpm run format
    }
    "format-check" {
        Write-Host "==> Checking Python formatting (Ruff)..." -ForegroundColor Green
        uv run ruff format --check .
        Write-Host "==> Checking TypeScript formatting (Prettier)..." -ForegroundColor Green
        pnpm run format:check
    }
    "typecheck" {
        Write-Host "==> Typechecking TypeScript packages..." -ForegroundColor Green
        pnpm turbo run typecheck
        Write-Host "==> Typechecking Python services (mypy)..." -ForegroundColor Green
        uv run mypy services/nexus-api
    }
    "test" {
        Write-Host "==> Running test suites..." -ForegroundColor Green
        pnpm turbo run test
        uv run pytest services/nexus-api/tests
    }
    "db-up" {
        Write-Host "==> Starting local infrastructure containers..." -ForegroundColor Green
        docker compose -f infra/docker/docker-compose.dev.yml up -d
    }
    "db-down" {
        Write-Host "==> Stopping local infrastructure containers..." -ForegroundColor Green
        docker compose -f infra/docker/docker-compose.dev.yml down
    }
    "clean" {
        Write-Host "==> Cleaning cache directories..." -ForegroundColor Yellow
        $dirs = @(".turbo", "node_modules", "target", "dist", ".mypy_cache", ".ruff_cache", "services\nexus-api\.venv")
        foreach ($d in $dirs) {
            if (Test-Path $d) {
                Remove-Item -Recurse -Force $d
            }
        }
        Write-Host "==> Clean complete." -ForegroundColor Green
    }
    default {
        Write-Error "Unknown command: $Command. Run '.\nexus.ps1 help' for usage."
    }
}
