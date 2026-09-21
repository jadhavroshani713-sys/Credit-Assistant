# CREDIT ASSISTANT

> **AI-Powered Credit Health Analytics & Financial Counseling Platform**

An end-to-end full-stack web application designed to evaluate credit-health metrics, calculate financial indicators (Credit Utilization, Debt-to-Income ratio, score trajectories), and deliver personalized, actionable credit improvement recommendations powered by **Google Gemini AI**.

---

## Architecture & Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | **FastAPI** `v0.141.1` | High-performance asynchronous REST API with auto-generated OpenAPI docs |
| **Database & ORM** | **SQLAlchemy** `v2.0.54` + **SQLite** | Declarative ORM models, cascade constraints, and active foreign key pragmas |
| **Data Validation** | **Pydantic** `v2.13.5` + **email-validator** | Strict type-safety, schema validation, and serialization |
| **Security & Hashing** | **bcrypt** `v5.0.0` | 12-round salt hashing; zero plaintext password exposure |
| **AI Engine** | **Google GenAI SDK** `v2.24.0` | Structured credit counseling with resilient rule-based fallback |
| **Frontend Framework** | **React** `v19` + **Vite** `v8` | Modern Single Page Application with fast HMR and client-side routing |
| **Routing** | **React Router** `v7` | Declarative route structure with `ProtectedRoute` session guards |
| **Visualizations** | **Recharts** `v3` | Responsive doughnut charts (Credit Usage) & line charts (Score Trend) |
| **Testing** | **pytest** `v9.1.1` + **httpx** | Isolated in-memory `StaticPool` database test suite (21/21 tests passing) |

---

## Project Structure

```
CREDIT_ASSISTANT/
├── backend/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py             # Isolated in-memory SQLite fixtures (StaticPool)
│   │   ├── test_api.py             # 16 core API & calculation tests
│   │   └── test_recommendations.py # 5 Gemini AI & fallback recovery tests
│   ├── .env                        # Environment variables (gitignored)
│   ├── .env.example                # Template for environment configuration
│   ├── ai.py                       # Gemini AI prompt engine & contextual fallback
│   ├── credit_assistant.db         # Local SQLite database (gitignored)
│   ├── database.py                 # Engine, session factory & Base configuration
│   ├── main.py                     # FastAPI application & route declarations
│   ├── models.py                   # User, CreditProfile & ScoreHistory ORM models
│   ├── requirements.txt            # Python dependencies with pinned versions
│   ├── schemas.py                  # Pydantic v2 request and response schemas
│   ├── security.py                 # Bcrypt password hashing & verification helpers
│   └── verify_db.py                # Database connection and integrity verification
│
├── frontend/
│   ├── public/                     # Static icons and assets
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js           # Centralized API service layer
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx     # Landing hero & feature showcase
│   │   │   ├── RegisterPage.jsx    # User account creation form
│   │   │   ├── LoginPage.jsx       # User authentication form
│   │   │   ├── OnboardingPage.jsx  # Financial metrics ingestion form
│   │   │   └── DashboardPage.jsx   # Metrics, charts & AI recommendation UI
│   │   ├── App.jsx                 # Route definitions and authentication guard
│   │   ├── index.css               # Global responsive dark theme styling
│   │   └── main.jsx                # React application entry point
│   ├── .env                        # Frontend environment variables (VITE_API_URL)
│   ├── package.json                # Frontend dependencies and npm scripts
│   └── vite.config.js              # Vite bundler configuration & React deduplication
│
├── .gitignore                      # Git exclusion rules
└── README.md                       # Project documentation
```

---

## Project Roadmap & Implementation Status

| Phase | Phase Title | Status | Description |
|---|---|:---:|---|
| **Phase 1** | **Project Initialization & Environment Setup** | ✅ Completed | Project scaffolded, virtual environment created, Vite React app configured. |
| **Phase 2** | **Database Schema & SQLAlchemy Models** | ✅ Completed | `User`, `CreditProfile`, `ScoreHistory` models built with cascade relationships. |
| **Phase 3** | **API Architecture, Authentication & Core Routes** | ✅ Completed | `/register`, `/login`, `/financial-data`, `/dashboard/{id}` implemented. |
| **Phase 4** | **Backend API Logic & Automated Testing** | ✅ Completed | Server-side calculations (DTI, utilization), Pytest suite with isolated test DB. |
| **Phase 5** | **Gemini AI Integration & Full Frontend** | ✅ Completed | `GET /recommendations`, complete React UI, Recharts, E2E validation. |
| **Phase 6** | **Advanced AI Prompts & Multi-Turn Advisor** | ⏳ Planned | Multi-turn AI chat dialog, CIBIL simulator, custom debt-payoff strategies. |
| **Phase 7** | **Interactive Visualizations & Goal Simulators** | ⏳ Planned | What-If simulator, EMI calculators, interactive credit score milestone charts. |
| **Phase 8** | **Comprehensive E2E Automation** | ⏳ Planned | Playwright/Cypress end-to-end browser testing suite across multiple devices. |
| **Phase 9** | **Security Hardening & Production Auditing** | ⏳ Planned | JWT tokens with refresh cycles, Redis rate-limiting, CORS origin restrictions. |
| **Phase 10** | **Containerization & Cloud Deployment** | ⏳ Planned | Docker Compose, Google Cloud Run deployment, PostgreSQL migration. |

---

## API Documentation

All endpoints are self-documented via Swagger UI at **`http://localhost:8000/docs`**.

### Available Endpoints

| Method | Endpoint | Description | Request Payload | Response Status |
|---|---|---|---|:---:|
| `GET` | `/` | Root information & active phase | None | `200 OK` |
| `GET` | `/health` | System health check | None | `200 OK` |
| `POST` | `/register` | Create account (hashes password) | `RegisterRequest` | `201 Created` |
| `POST` | `/login` | Authenticate user credentials | `LoginRequest` | `200 OK` |
| `POST` | `/financial-data` | Ingest financial metrics & compute indicators | `FinancialDataRequest` | `201 Created` |
| `GET` | `/dashboard/{user_id}` | Retrieve profile, metrics & score history | None | `200 OK` |
| `GET` | `/recommendations/{user_id}` | Generate AI credit-health recommendations | None | `200 OK` |

### Server-Side Financial Formulas

The server never trusts frontend computations. Key metrics are computed server-side:

$$\text{Credit Utilization (\%)} = \text{round}\left(\frac{\text{credit\_used}}{\text{credit\_limit}} \times 100, 2\right)$$
*(Safe against division-by-zero: defaults to $0.0\%$ if $\text{credit\_limit} = 0$)*

$$\text{Debt-to-Income (\%)} = \text{round}\left(\frac{\text{monthly\_expenses}}{\text{monthly\_salary}} \times 100, 2\right)$$
*(Safe against division-by-zero: defaults to $0.0\%$ if $\text{monthly\_salary} = 0$)*

$$\text{Score Improvement} = \text{new\_score} - \text{old\_score}$$
*(First financial submission defaults to `null`)*

---

## Quick Start Guide

### Prerequisites
- **Python 3.11+** (Python 3.14 compatible)
- **Node.js 18+** & **npm**

---

### 1. Backend Setup

Open a terminal and navigate to the backend directory:

```powershell
# Navigate to backend
cd backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env and add your Gemini API key (optional)
copy .env.example .env

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

- **Backend API**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`

---

### 2. Frontend Setup

Open a second terminal and navigate to the frontend directory:

```powershell
# Navigate to frontend
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```

- **Frontend Application**: `http://localhost:5173`

---

## Environment Configuration

### Backend (`backend/.env`)
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
DATABASE_URL=sqlite:///./credit_assistant.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
```
> **Note**: If `GEMINI_API_KEY` is not set or left as placeholder, the system automatically uses an intelligent, context-aware fallback counselor so features never crash.

### Frontend (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8000
```

---

## Running the Automated Test Suite

### Backend Unit & Integration Tests (Pytest)
```powershell
cd backend
.\venv\Scripts\activate
python -m pytest tests -v
```
All **21 test cases** execute in an isolated in-memory SQLite database (`:memory:` with `StaticPool`), ensuring the development database is never modified.

### Frontend Linting & Build Verification
```powershell
cd frontend
npm run lint    # Oxlint verification (0 errors, 0 warnings)
npm run build   # Production asset compilation
```

---

## Security & Data Privacy

1. **No Plaintext Passwords**: Passwords are encrypted using `bcrypt` with a work factor of 12 before database storage.
2. **Sanitized Responses**: Neither `password` nor `password_hash` is ever returned in any API response or logged.
3. **Environment Security**: All sensitive keys remain in `.env` files which are excluded from Git version control.
4. **Input Sanitization**: Pydantic v2 enforces schema boundaries and validates ranges (e.g., credit scores between 300 and 900).
5. **Session Safety**: Frontend uses protected client-side routes; session data is managed securely via browser storage.
