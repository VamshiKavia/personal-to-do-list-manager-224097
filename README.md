# Backend (FastAPI) - Todo List

This is a minimal FastAPI backend that exposes CRUD routes for a Todo list.

## Endpoints

- GET /api/todos
- POST /api/todos
- PUT /api/todos/{id}
- DELETE /api/todos/{id}
- GET / (health check)

OpenAPI docs: /docs

## Run locally

1. Create and activate a Python 3.10+ virtualenv
2. Install dependencies:

   pip install -r backend/requirements.txt

3. Start the server:

   uvicorn backend.main:app --host 0.0.0.0 --port 3001

The server listens on port 3001 by default per project notes.

## CORS

Set REACT_APP_FRONTEND_URL in environment to control allowed origins.

Example:

export REACT_APP_FRONTEND_URL=http://localhost:3000

## Notes

- Storage is in-memory for this scope.
- No secrets are hardcoded. Configuration via environment variables.
