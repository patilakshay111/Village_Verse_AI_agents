# VillageVerse Frontend

React + Vite + TypeScript + Tailwind CSS UI for Anandgaon.

## Prerequisites

Backend running at http://127.0.0.1:8000

```bash
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

## Run

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Pages

- **Dashboard** — simulation controls, village status, latest events/stories
- **Story Feed** — filters, infinite scroll, full story modal
- **Villagers / Families / Locations** — browse and detail views
- **Search** — cross-entity keyword search

## Config

Copy `.env.example` to `.env` and set `VITE_API_URL` if the API is not on port 8000.
