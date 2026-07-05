# GenAI Inventory Intelligence Backend

FastAPI backend for the Member 2 scope: auth, PostgreSQL schema, chat memory, LangGraph orchestration, and Groq/OpenAI LLM integration.

## Setup

```powershell
python -m venv .backend-venv
.\.backend-venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

Put API keys only in `backend/.env`. Groq is the default provider; OpenAI is available by setting `LLM_PROVIDER=openai`. For local demos without keys, keep `ALLOW_MOCK_LLM=true`.

## Database

Start PostgreSQL:

```powershell
cd backend
docker compose up -d postgres
```

Run migrations and seed mock business data:

```powershell
alembic upgrade head
python scripts/seed_mock_data.py
```

## Run API

```powershell
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs.

## Docker

```powershell
docker compose up --build
```

The API runs at http://localhost:8000 and PostgreSQL at localhost:5432.

## Main Endpoints

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/auth/me`
- `POST /api/copilot/chat`
- `GET /api/copilot/morning-brief`
- `GET /api/copilot/weekly-report`
- `POST /api/copilot/recommendations`
- `POST /api/copilot/nl-query`

All copilot endpoints require `Authorization: Bearer <access_token>` and route through the LangGraph workflow.
