.PHONY: main api frontend frontend-install frontend-build frontend-lint frontend-format dev setup-db test test-unit test-integration pre-commit format lint install clean clean-frontend help

main:
	@echo "Running main..."
	uv run python -m agentlab.main

api:
	@echo "Starting FastAPI server..."
	uv run uvicorn agentlab.api.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

frontend-install:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

frontend-build:
	@echo "Building frontend for production..."
	cd frontend && npm run build

frontend-lint:
	@echo "Linting frontend code..."
	cd frontend && npm run lint

frontend-format:
	@echo "Formatting frontend code..."
	cd frontend && npm run format

dev:
	@echo "Starting both backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@make -j2 api frontend

setup-db:
	@echo "Setting up database..."
	uv run python -m agentlab.database

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

clean-frontend:
	@echo "Cleaning frontend build and cache..."
	cd frontend && rm -rf node_modules dist .vite 2>/dev/null || true

help:
	@echo "Available targets:"
	@echo ""
	@echo "Backend:"
	@echo "  make main           - Run the main application"
	@echo "  make api            - Start the FastAPI server"
	@echo "  make setup-db       - Initialize the database"
	@echo "  make install        - Install/sync dependencies"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend       - Start frontend development server"
	@echo "  make frontend-install - Install frontend dependencies"
	@echo "  make frontend-build - Build frontend for production"
	@echo "  make frontend-lint  - Lint frontend code"
	@echo "  make frontend-format - Format frontend code"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start both backend and frontend"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make pre-commit     - Run pre-commit checks"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format         - Format backend code with Ruff"
	@echo "  make lint           - Lint backend code with Ruff"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Clean backend cache files"
	@echo "  make clean-frontend - Clean frontend build and cache"
	@echo ""
	@echo "  make help           - Show this help message"
