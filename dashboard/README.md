# Neural Lattice Dashboard

React + Vite front-end for the Neural Lattice Cognitive Architecture (NLCA). The UI surfaces zone summaries, document triage, Eisenhower matrix views, and session controls backed by the FastAPI service.

## Prerequisites
- Node 20+
- Running NLCA API (see repository root README for backend quick start)

## Setup
```bash
cd dashboard
cp .env.example .env   # optional: override API base URL
npm install
```

### API configuration
The dashboard targets `http://127.0.0.1:8000` by default. To point at another host/port, set `VITE_API_BASE` in `.env`:
```
VITE_API_BASE=http://localhost:8000
```

## Run the dashboard
```bash
npm run dev   # http://localhost:5173 with HMR
```

## Test, lint, and build
```bash
npm run test   # vitest
npm run lint   # eslint
npm run build  # production build
```
