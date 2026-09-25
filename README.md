# CREDIT ASSISTANT

> **AI-Powered Credit Health Analytics & Financial Counseling Platform**

An end-to-end full-stack web application designed to evaluate credit-health metrics, calculate financial indicators (Credit Utilization, Debt-to-Income ratio, score trajectories), and deliver personalized, actionable credit improvement recommendations powered by **Groq**, **OpenAI**, or **Google Gemini AI**, with automated PDF report generation via **ReportLab**.

---

## Technical Architecture

```
                                 Send Financial Data & Queries
[User] --> [Web Frontend] -----------------------------------------> [FastAPI Backend] <---> [AI Engine (Groq / OpenAI / Gemini)]
             (React.js)   <-----------------------------------------       (Python)     <---  AI Analysis & Recommendations
                             JSON Responses / Display Report                 |   ^
                                                                             |   | Store & Retrieve User Data / Query Results
                                                                             v   v
                                                                   [Database (PostgreSQL / Supabase / SQLite)]
                                                                             |
                                                                             v
                                                            [Financial Health Report (JSON)]
                                                                             |
                                                                             +---> [PDF Generation Service (ReportLab)]
                                                                                   (Generates Official Credit PDF Report)
```

---

## Architecture & Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Web Frontend** | **React** `v19` + **Vite** `v8` | Single Page Application with fast HMR, interactive dashboard, and PDF report triggers |
| **Routing** | **React Router** `v7` | Declarative route structure with `ProtectedRoute` session guards |
| **Visualizations** | **Recharts** `v3` | Responsive doughnut charts (Credit Usage) & line charts (Score History Trend) |
| **Backend Framework** | **FastAPI** `v0.141.1` | Asynchronous REST API with auto-generated OpenAPI documentation |
| **AI Engine** | **Groq** / **OpenAI** / **Google Gemini** | Multi-provider AI counseling engine with resilient deterministic fallback |
| **PDF Generation Service** | **ReportLab** `v5.0.1` | High-quality branded Credit Health & Financial Advisory PDF generator |
| **Database & ORM** | **SQLAlchemy** `v2.0.54` | Flexible ORM supporting **PostgreSQL / Supabase** or local **SQLite** |
| **Data Validation** | **Pydantic** `v2.13.5` + **email-validator** | Strict type-safety, schema validation, and serialization |
| **Security & Hashing** | **bcrypt** `v5.0.0` | 12-round salt hashing; zero plaintext password exposure |
| **Testing** | **pytest** `v9.1.1` + **httpx** | Isolated in-memory `StaticPool` database test suite (**28/28 tests passing**) |

---

## Project Structure

```
CREDIT_ASSISTANT/
├── backend/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py             # Isolated in-memory SQLite fixtures (StaticPool)
│   │   ├── test_api.py             # 16 core API & calculation tests
│   │   ├── test_pdf_report.py      # 7 PDF generation & financial report tests
│   │   └── test_recommendations.py # 5 Multi-AI & fallback recovery tests
│   ├── .env                        # Environment variables (gitignored)
│   ├── .env.example                # Template for environment configuration
│   ├── ai.py                       # Multi-Provider AI Engine (Groq / OpenAI / Gemini)
│   ├── credit_assistant.db         # Local SQLite database (gitignored)
│   ├── database.py                 # Engine, session factory (PostgreSQL / Supabase / SQLite)
│   ├── main.py                     # FastAPI application & route declarations
│   ├── models.py                   # User, CreditProfile & ScoreHistory ORM models
│   ├── pdf_service.py              # ReportLab PDF Generation Service
│   ├── requirements.txt            # Python dependencies with pinned versions
│   ├── schemas.py                  # Pydantic v2 request, response & report schemas
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
│   │   │   └── DashboardPage.jsx   # Metrics, charts, AI insights & PDF report download
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

## API Documentation

All endpoints are self-documented via Swagger UI at **`http://localhost:8000/docs`**.

### Available Endpoints

| Method | Endpoint | Description | Request Payload | Response Status |
|---|---|---|---|:---:|
| `GET` | `/` | Root information & active phase | None | `200 OK` |
| `GET` | `/health` | System health check | None | `200 OK` |
| `POST` | `/register` | Create account (hashes password with bcrypt) | `RegisterRequest` | `201 Created` |
| `POST` | `/login` | Authenticate user credentials | `LoginRequest` | `200 OK` |
| `POST` | `/financial-data` | Ingest financial metrics & compute indicators | `FinancialDataRequest` | `201 Created` |
| `GET` | `/dashboard/{user_id}` | Retrieve profile, metrics & score history | None | `200 OK` |
| `GET` | `/recommendations/{user_id}` | Generate AI credit-health recommendations | None | `200 OK` |
| `GET` | `/report/{user_id}` | Financial Health Report (JSON Response) | None | `200 OK` |
| `GET` | `/report/pdf/{user_id}` | Download Generated PDF Credit Report (ReportLab) | None | `200 OK (PDF Stream)` |

### Server-Side Financial Formulas

$$\text{Credit Utilization (\%)} = \text{round}\left(\frac{\text{credit\_used}}{\text{credit\_limit}} \times 100, 2\right)$$
*(Defaults to $0.0\%$ if $\text{credit\_limit} = 0$)*

$$\text{Debt-to-Income (\%)} = \text{round}\left(\frac{\text{monthly\_expenses}}{\text{monthly\_salary}} \times 100, 2\right)$$
*(Defaults to $0.0\%$ if $\text{monthly\_salary} = 0$)*

$$\text{Score Improvement} = \text{new\_score} - \text{old\_score}$$
*(First financial submission defaults to `null`)*

---

## Quick Start Guide

### Prerequisites
- **Python 3.11+** (Python 3.14 compatible)
- **Node.js 18+** & **npm**

---

### 1. Backend Setup

```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # On Windows
# source venv/bin/activate # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

- **Backend API**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`

---

### 2. Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

- **Frontend Application**: `http://localhost:5173`

---

## Environment Configuration

### Backend (`backend/.env`)
```env
# AI Engine Provider (Groq / OpenAI / Gemini)
GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

# Database (PostgreSQL / Supabase or SQLite)
DATABASE_URL=sqlite:///./credit_assistant.db
# For PostgreSQL / Supabase, use:
# DATABASE_URL=postgresql://user:password@aws-0-region.pooler.supabase.com:6543/postgres

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
```
> **Resilient Fallback**: If no AI API key is configured, the system automatically uses an intelligent, context-aware rule-based counselor.

### Frontend (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8000
```

---

## Running the Automated Test Suite

```powershell
cd backend
.\venv\Scripts\activate
python -m pytest tests -v
```
All **28 test cases** pass with 100% success rate:
- 16 core API & calculation tests
- 7 PDF generation & financial report tests
- 5 multi-AI & fallback recovery tests
