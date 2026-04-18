# Prompt Optimizer API

A FastAPI service that improves user prompts with OpenAI and stores optimization results in PostgreSQL.

## Features

- Optimize prompts for a specific goal using OpenAI chat completions.
- Enforce structured JSON responses from the LLM.
- Persist optimization history in PostgreSQL.
- Health endpoint for quick service checks.
- Docker and Docker Compose support.

## Tech Stack

- Python 3.12
- FastAPI + Uvicorn
- OpenAI Python SDK
- PostgreSQL + psycopg2
- Docker / Docker Compose

## Project Structure

- `main.py` - FastAPI app and API endpoints.
- `service.py` - Prompt optimization logic and OpenAI call.
- `database.py` - DB connection, schema initialization, logging.
- `requirements.txt` - Python dependencies.
- `Dockerfile` - Multi-stage image build.
- `compose.yaml` - App + PostgreSQL local stack.

## API Endpoints

### GET `/health`

Returns service status.

Response:

```json
{
  "status": "ok"
}
```

### POST `/optimize`

Optimizes a prompt for a specific goal.

Request body:

```json
{
  "prompt": "Write a social media post about our new product",
  "goal": "Make it concise, engaging, and conversion-focused"
}
```

Response body:

```json
{
  "original_prompt": "Write a social media post about our new product",
  "optimized_prompt": "...",
  "changes": "..."
}
```

## Environment Variables

Copy `.env.example` to `.env` and fill in values.

Required values:

- `OPENAI_API_KEY` - API key for OpenAI.
- `POSTGRES_USER` - PostgreSQL username.
- `POSTGRES_PASSWORD` - PostgreSQL password.
- `POSTGRES_DB` - PostgreSQL database name.
- `DB_HOST` - Database host (`db` when running with Compose).

Optional values:

- `DB_PORT` (default: `5432`)
- `PORT` (default: `8000`)

## Run Locally (without Docker)

1. Create and activate a virtual environment.
2. Install dependencies.
3. Ensure PostgreSQL is running and env vars are configured.
4. Start the API.

Example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Run with Docker Compose

1. Create `.env` from `.env.example` and set real values.
2. Build and start services.

```bash
docker compose up --build
```

This starts:

- API at `http://localhost:8000`
- PostgreSQL at `localhost:5432`

Stop services:

```bash
docker compose down
```

## Quick Test

```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain our app features",
    "goal": "Make it clearer for non-technical users"
  }'
```

## Notes

- The service creates `optimization_logs` table on startup.
- If database logging fails, optimization still returns a response.
- If the upstream LLM returns invalid JSON, the API responds with HTTP 502.
