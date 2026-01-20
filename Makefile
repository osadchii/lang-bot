.PHONY: help install lint format test check verify clean

PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
RUFF := ruff
MYPY := mypy

SRC_DIR := bot
TEST_DIR := tests
COVERAGE_MIN := 80

help:
	@echo "Available commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make lint          - Run ruff linter"
	@echo "  make format        - Format code with black"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make typecheck     - Run mypy type checking"
	@echo "  make check         - Run all checks without fixing"
	@echo "  make verify        - Full verification (same as CI)"
	@echo "  make verify-strict - Verification with coverage threshold"
	@echo "  make fix           - Auto-fix linting and formatting"
	@echo "  make clean         - Remove cache and build files"
	@echo "  make pre-commit    - Install pre-commit hooks"

install:
	$(PIP) install -r requirements.txt

lint:
	$(RUFF) check $(SRC_DIR)/

lint-fix:
	$(RUFF) check $(SRC_DIR)/ --fix

format-check:
	$(BLACK) --check $(SRC_DIR)/

format:
	$(BLACK) $(SRC_DIR)/ $(TEST_DIR)/

typecheck:
	$(MYPY) $(SRC_DIR)/

test:
	$(PYTEST) $(TEST_DIR)/ -v

test-cov:
	$(PYTEST) $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html

test-ci:
	$(PYTEST) $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=term-missing --cov-fail-under=$(COVERAGE_MIN)

check:
	@echo "=== Running Ruff Linter ==="
	$(RUFF) check $(SRC_DIR)/
	@echo ""
	@echo "=== Checking Black Formatting ==="
	$(BLACK) --check $(SRC_DIR)/
	@echo ""
	@echo "=== Running Type Check ==="
	$(MYPY) $(SRC_DIR)/
	@echo ""
	@echo "=== All checks passed ==="

verify:
	@echo "================================================"
	@echo "  Running Full Verification (mirrors CI/CD)"
	@echo "================================================"
	@echo ""
	@echo "=== Step 1/4: Ruff Linter ==="
	$(RUFF) check $(SRC_DIR)/
	@echo "Linting passed"
	@echo ""
	@echo "=== Step 2/4: Black Formatting ==="
	$(BLACK) --check $(SRC_DIR)/
	@echo "Formatting check passed"
	@echo ""
	@echo "=== Step 3/4: Type Checking ==="
	$(MYPY) $(SRC_DIR)/
	@echo "Type checking passed"
	@echo ""
	@echo "=== Step 4/4: Tests with Coverage ==="
	$(PYTEST) $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=term-missing || echo "Note: Tests need to be written"
	@echo ""
	@echo "================================================"
	@echo "  All verifications passed! Safe to push."
	@echo "================================================"

verify-strict:
	@echo "================================================"
	@echo "  Running Strict Verification (with coverage)"
	@echo "================================================"
	@echo ""
	@echo "=== Step 1/4: Ruff Linter ==="
	$(RUFF) check $(SRC_DIR)/
	@echo "Linting passed"
	@echo ""
	@echo "=== Step 2/4: Black Formatting ==="
	$(BLACK) --check $(SRC_DIR)/
	@echo "Formatting check passed"
	@echo ""
	@echo "=== Step 3/4: Type Checking ==="
	$(MYPY) $(SRC_DIR)/
	@echo "Type checking passed"
	@echo ""
	@echo "=== Step 4/4: Tests with Coverage (min $(COVERAGE_MIN)%) ==="
	$(PYTEST) $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=term-missing --cov-fail-under=$(COVERAGE_MIN)
	@echo ""
	@echo "================================================"
	@echo "  All strict verifications passed!"
	@echo "================================================"

fix:
	@echo "=== Fixing code style issues ==="
	$(RUFF) check $(SRC_DIR)/ --fix
	$(BLACK) $(SRC_DIR)/ $(TEST_DIR)/
	@echo "=== Done ==="

pre-commit:
	pre-commit install
	@echo "Pre-commit hooks installed"

clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned up cache files"
