# CREDIT ASSISTANT

## Project

AI-powered Credit Assistant.

## Current Phase

Phase 1 — Project Initialization and Environment Setup

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite

## Frontend

- React
- Vite

## AI

- Google Gemini API

## Current Status

Environment initialized.

---

## Getting Started

### Backend

```bash
cd backend
# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start the server
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000

- `GET /` — Project info
- `GET /health` — Health check
- `GET /docs` — Swagger UI

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

---

## Development Roadmap

| Phase | Description |
|-------|-------------|
| ✅ Phase 1 | Environment Setup |
| ⬜ Phase 2 | Database Schema |
| ⬜ Phase 3 | Authentication |
| ⬜ Phase 4 | Financial Data API |
| ⬜ Phase 5 | Dashboard |
| ⬜ Phase 6 | Gemini AI Integration |
| ⬜ Phase 7 | Charts and Visualization |
| ⬜ Phase 8 | Testing |
| ⬜ Phase 9 | Security |
| ⬜ Phase 10 | Deployment |
