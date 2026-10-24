# Real Estate AI Sales & Marketing Automation Platform

An autonomous, AI-powered real estate sales assistant and marketing intelligence platform. Receives customer enquiries through WhatsApp, engages in natural contextual conversations, collects customer preferences, qualifies leads into Hot, Warm, or Cold tiers, matches inquiries with verified property inventory, schedules on-site visits, and triggers automated follow-ups.

---

## 1. Technology Stack

- **AI Orchestration:** Python 3.12, Anthropic Claude API (`anthropic` SDK: Claude 3.7 Sonnet / Claude 3.5 Haiku)
- **Backend API:** FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings
- **Messaging Channel:** WhatsApp Business Platform Cloud API (Meta)
- **Persistence:** PostgreSQL 15+ (Supabase) via SQLAlchemy 2.0 & Alembic
- **Development Tunneling:** Cloudflare Quick Tunnels (`cloudflared`)
- **Hosting Targets:** Render (Backend), Supabase (Database), Vercel (Next.js Dashboard)
- **Testing:** Pytest, Pytest-Asyncio, HTTPX Async Transport

---

## 2. Project Directory Structure

```
Real Estate-Ai_Automation/
├── .gitignore
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Build configuration & pytest settings
├── README.md                 # Project documentation
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI entrypoint & middleware
│   ├── config/               # Settings & environment validation
│   ├── core/                 # Constants, logging, exceptions
│   ├── db/                   # Database session & models
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic data contracts
│   ├── repositories/         # Database access layer
│   ├── services/             # Business logic layer
│   ├── integrations/         # WhatsApp, Claude, Meta, Calendar clients
│   ├── agents/               # AI orchestrators & state machines
│   ├── jobs/                 # Application-owned follow-up schedulers
│   └── api/                  # REST API v1 routes & endpoints
├── docs/                     # Architectural specifications
│   ├── architecture.md
│   ├── database-schema.md
│   ├── api-design.md
│   ├── ai-agent-design.md
│   ├── security.md
│   ├── testing-strategy.md
│   ├── deployment.md
│   ├── roadmap.md
│   └── phase-reports/        # Formal review reports for each phase
└── tests/                    # Automated test harness
    ├── conftest.py           # Shared fixtures & test client
    ├── unit/                 # Unit tests
    └── integration/          # API & webhook integration tests
```

---

## 3. Quickstart & Local Setup

### 3.1 Prerequisites
- Python 3.11 or 3.12 installed
- Git installed
- Cloudflared installed (optional for local WhatsApp webhook testing)

### 3.2 Installation
```powershell
# 1. Clone repository & navigate to workspace
cd "E:\Real Estate-Ai_Automation"

# 2. Activate virtual environment (already initialized)
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
Copy-Item .env.example .env
```

### 3.3 Running Tests
```powershell
.\.venv\Scripts\pytest.exe
```

### 3.4 Running Local Development Server
```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```
Visit API Documentation: `http://localhost:8000/api/v1/docs`  
Health Check: `http://localhost:8000/health`

---

## 4. Current Status: Phase 1 Complete (Foundation & Architecture)

Phase 1 has established the repository architecture, foundational codebase, environment validation, security rules, and test harness.  
See [`docs/phase-reports/phase-01-report.md`](docs/phase-reports/phase-01-report.md) for the complete Phase 1 report.
