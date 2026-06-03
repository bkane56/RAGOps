.PHONY: db-up db-down backend frontend test test-backend test-frontend install

db-up:
	docker compose up -d db

db-down:
	docker compose down

install:
	cd backend && uv sync --extra dev
	cd frontend && yarn install

backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && yarn dev

test-backend:
	cd backend && uv run pytest app/tests -v --cov=app --cov-report=term-missing

test-frontend:
	cd frontend && yarn test:coverage

test: test-backend test-frontend
