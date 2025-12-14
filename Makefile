main:
	@echo "Running main..."
	uv run python -m agentlab.main

api:
	@echo "Starting FastAPI server..."
	uv run uvicorn agentlab.api.main:app --reload --host 0.0.0.0 --port 8000

setup-db:
	@echo "Setting up database..."
	uv run python -m agentlab.database.setup

test: test-unit test-integration
	@echo "All tests completed successfully"

pre-commit: test-unit format lint

test-unit:
	@echo "Running unit tests..."
	uv run pytest -s tests/unit

test-integration:
	@echo "Running integration tests..."
	uv run pytest -s tests/integration

format:
	@echo "Formatting code..."
	uv run ruff format

lint:
	@echo "Running linter..."
	uv run ruff check

install:
	@echo "Installing dependencies..."
	uv sync

clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

help:
	@echo "Available targets:"
	@echo "  make main           - Run the main application"
	@echo "  make api            - Start the FastAPI server"
	@echo "  make setup-db       - Initialize the database"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make format         - Format code with Ruff"
	@echo "  make lint           - Lint code with Ruff"
	@echo "  make pre-commit     - Run pre-commit checks"
	@echo "  make install        - Install/sync dependencies"
	@echo "  make clean          - Clean cache files"
	@echo "  make help           - Show this help message"
