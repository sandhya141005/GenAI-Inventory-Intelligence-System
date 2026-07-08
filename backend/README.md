# GenAI Inventory Intelligence Backend

FastAPI backend for PostgreSQL-backed inventory decision intelligence.

## Setup

```powershell
python -m venv .backend-venv
.\.backend-venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Docker

```powershell
docker compose up --build -d
```

The API runs at `http://localhost:8000` and PostgreSQL persists through the `postgres_data` volume.

The container database URL is:

```text
postgresql+psycopg2://inventory:inventory@postgres:5432/inventory_copilot
```

## Database

Run migrations for a local non-container API process:

```powershell
alembic upgrade head
```

Required analytics tables:

- `products`
- `stores`
- `sales`
- `warehouse_stock`
- `transfers`

## Analytics Endpoints

- `GET /api/analytics/overview`
- `GET /api/analytics/inventory`
- `GET /api/analytics/recommendations`
- `GET /api/analytics/reports`
- `GET /api/analytics/charts`
- `GET /api/analytics/transfers`
- `GET /api/analytics/inventory-aging`
- `GET /api/analytics/notices`

Open `http://localhost:8000/docs` to verify the routes.
