# FCP CLI Makefile (Food Context Protocol)

# ============================================
# Self-documentation
# ============================================
.PHONY: help
help: ## Show this help message
	@echo "FCP CLI - Development Commands"
	@echo "==============================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================
# Default
# ============================================
.DEFAULT_GOAL := help

# ============================================
# Setup
# ============================================
install: ## Install all dependencies
	uv sync --dev

# ============================================
# Testing
# ============================================
test: ## Run all tests
	uv run pytest tests/ -v

test-quick: ## Run tests without coverage for speed
	uv run pytest tests/ -x -q

coverage: ## Run tests with 100% coverage enforcement
	uv run pytest tests/ --cov=src/fcp_cli --cov-report=html --cov-report=term-missing --cov-branch --cov-fail-under=100.0

test-coverage: coverage ## Alias for coverage

coverage-html: coverage ## Open coverage HTML report
	open htmlcov/index.html

# ============================================
# Linting & Formatting
# ============================================
lint: ## Lint code with ruff
	uv run ruff check src/ tests/

lint-fix: ## Auto-fix lint errors with ruff
	uv run ruff check --fix src/ tests/

format: ## Format code with ruff
	uv run ruff format src/ tests/

format-check: ## Check code formatting without modifying files
	uv run ruff format --check src/ tests/

typecheck: ## Type check with ty (source code only)
	uv run ty check src/

prek: ## Run prek hooks on all files
	prek run --all-files

check: format-check lint typecheck coverage ## Run all checks (format, lint, typecheck, 100% coverage)

# ============================================
# CLI Testing
# ============================================
cli-help: ## Show FCP CLI help
	uv run fcp --help

cli-log: ## Test log command (add a test meal)
	uv run fcp log add "Test Pizza" --meal-type lunch

cli-profile: ## Show user profile
	uv run fcp profile show

cli-search: ## Search for meals
	uv run fcp search query "pizza" --limit 5

cli-recipes: ## List recipes
	uv run fcp recipes list

# ============================================
# Development
# ============================================
install-hooks: ## Install prek git hooks
	prek install

uninstall-hooks: ## Uninstall prek git hooks
	prek uninstall

# ============================================
# Cleaning
# ============================================
clean: ## Remove temporary files and caches
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f coverage.xml
	find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean ## Remove all generated files including .venv
	rm -rf .venv
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

# ============================================
# Documentation
# ============================================
docs: ## Open documentation directory
	@echo "Opening docs directory..."
	@ls -l docs/

# ============================================
# Build & Release
# ============================================
build: ## Build distribution packages
	uv build

publish-test: build ## Publish to TestPyPI
	uv publish --repository testpypi

publish: build ## Publish to PyPI (production)
	uv publish

# ============================================
# CI/CD Simulation
# ============================================
ci: clean check ## Simulate CI pipeline locally
	@echo "✅ CI checks passed!"
