# VillageVerse Backend

Multi-agent Indian village simulation API (FastAPI + LangGraph + Ollama).

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to the project root as `.env` and set `OLLAMA_MODEL` to your local Ollama model (e.g. `llama3.2:1b`).

For fast API verification without Ollama, set `MOCK_LLM=true` and run:

```bash
python tests/run_verify.py
```

## Run

```bash
cd backend
uvicorn main:app --reload --port 8000
```

## Frontend (Phase 5+)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (requires API on port 8000).

## Seed world

```bash
curl -X POST http://localhost:8000/admin/seed
```

## Simulation

```bash
curl -X POST http://localhost:8000/simulation/tick
curl -X POST http://localhost:8000/simulation/run -H "Content-Type: application/json" -d "{\"ticks\": 10}"
curl http://localhost:8000/simulation/status
```

## Migrations

```bash
cd backend
alembic upgrade head
```
