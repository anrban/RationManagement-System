# 🏛️ Digital Ration Management System

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Government-grade welfare tracking system to eliminate leakages and duplication in public distribution.**

---

## 📋 Description

The **Digital Ration Management System** is a production-ready Python (FastAPI) application designed to modernise welfare distribution for government programmes (PDS, AAY, BPL schemes). It eliminates ghost beneficiaries, duplicate registrations, and fraudulent distributions through strong identity verification, immutable audit trails, and role-based access control.

---

## ✨ Features

- 🔐 **JWT Authentication** — Secure token-based auth for all API endpoints
- 👥 **Role-Based Access Control (RBAC)** — Four-tier role hierarchy (Super Admin, District Officer, Field Agent, Auditor)
- 🧬 **Deduplication Engine** — RapidFuzz fuzzy matching to detect duplicate beneficiary registrations
- 📦 **Distribution Logging** — End-to-end record of every ration distribution with GPS coordinates and QR acknowledgement
- 📊 **Analytics Dashboard API** — Real-time summary stats, distribution trends, and fraud flag reporting
- 🚩 **Fraud Flagging** — Flag and track suspected duplicate or fraudulent beneficiaries
- 🗒️ **Immutable Audit Logs** — Every action is logged with timestamp, IP address, and actor
- 📱 **SMS OTP Notifications** — Twilio-backed stub for beneficiary verification via mobile
- 🔲 **QR Code Generation** — QR codes for distribution acknowledgement (qrcode library)
- ⚙️ **Background Tasks** — Celery + Redis for async fraud alerts and daily report generation
- 🗄️ **PostGIS Support** — GPS-aware distribution log entries using GeoAlchemy2
- 🐳 **Docker Compose** — One-command full-stack setup (API + PostgreSQL/PostGIS + Redis + Celery)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **API Framework** | FastAPI 0.111 |
| **Database** | PostgreSQL 15 + PostGIS 3.3 |
| **ORM + Migrations** | SQLAlchemy 2.0 + Alembic |
| **Auth** | JWT (python-jose) + passlib bcrypt |
| **Cache / Broker** | Redis 7 |
| **Background Jobs** | Celery 5.4 |
| **Deduplication** | RapidFuzz |
| **QR Codes** | qrcode[pil] |
| **SMS Notifications** | Twilio (stub) |
| **Containerisation** | Docker + Docker Compose |
| **Testing** | pytest + httpx |

---

## 🚀 Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development without Docker)

### 1. Clone the repository

```bash
git clone https://github.com/anrban/RationManagement-System.git
cd RationManagement-System
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Start with Docker Compose

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 4. Run database migrations

```bash
docker-compose exec api alembic upgrade head
```

### 5. Local development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Set DATABASE_URL to a local SQLite or PostgreSQL instance in .env
uvicorn main:app --reload
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth Required | Role |
|---|---|---|---|
| `GET` | `/health` | No | — |
| `POST` | `/auth/register` | No | — |
| `POST` | `/auth/login` | No | — |
| `POST` | `/beneficiaries/register` | Yes | `district_officer`, `super_admin` |
| `GET` | `/beneficiaries/` | Yes | All authenticated |
| `POST` | `/beneficiaries/{id}/verify` | Yes | `district_officer`, `super_admin` |
| `GET` | `/beneficiaries/{id}/history` | Yes | All authenticated |
| `POST` | `/distributions/record` | Yes | `field_agent`, `super_admin` |
| `GET` | `/distributions/logs` | Yes | All authenticated |
| `GET` | `/distributions/{id}` | Yes | All authenticated |
| `GET` | `/analytics/summary` | Yes | Roles with `view_analytics` |
| `GET` | `/analytics/distribution-trends` | Yes | Roles with `view_analytics` |
| `GET` | `/analytics/fraud-flags` | Yes | Roles with `view_analytics` |
| `POST` | `/admin/flag-duplicate` | Yes | `super_admin` |
| `GET` | `/admin/audit-logs` | Yes | All authenticated |
| `GET` | `/admin/users` | Yes | `super_admin` |

---

## 🔐 Role Permissions

| Role | `read` | `write` | `delete` | `manage_users` | `view_analytics` | `write_distribution` |
|---|---|---|---|---|---|---|
| `super_admin` | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| `district_officer` | ✅ | ✅ | — | — | ✅ | — |
| `field_agent` | ✅ | — | — | — | — | ✅ |
| `auditor` | ✅ | — | — | — | ✅ | — |

---

## 📁 Project Structure

```
RationManagement-System/
├── main.py                     # FastAPI application entry point
├── database.py                 # SQLAlchemy engine, session, Base
├── models.py                   # ORM models (User, Beneficiary, DistributionLog, AuditLog, FraudFlag)
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── alembic/
│   └── env.py
├── auth/
│   ├── __init__.py
│   ├── jwt.py                  # JWT creation & verification
│   └── rbac.py                 # Role-based access control
├── routers/
│   ├── __init__.py
│   ├── auth.py                 # /auth/register, /auth/login
│   ├── beneficiaries.py        # Beneficiary CRUD & verification
│   ├── distributions.py        # Distribution log endpoints
│   ├── analytics.py            # Analytics & reporting
│   └── admin.py                # Admin operations
├── services/
│   ├── __init__.py
│   ├── deduplication.py        # RapidFuzz duplicate detection
│   ├── notifications.py        # Twilio SMS OTP stub
│   └── qr_generator.py         # QR code generation
├── schemas/
│   ├── __init__.py
│   ├── beneficiary.py          # Pydantic v2 beneficiary schemas
│   ├── distribution.py         # Pydantic v2 distribution schemas
│   ├── user.py                 # Pydantic v2 user/auth schemas
│   └── analytics.py            # Pydantic v2 analytics schemas
├── tasks/
│   ├── __init__.py
│   ├── alerts.py               # Celery fraud alert task
│   └── reports.py              # Celery daily report task
└── tests/
    ├── __init__.py
    ├── test_beneficiaries.py
    ├── test_distributions.py
    └── test_analytics.py
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feat/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.  
See [LICENSE](LICENSE) for details.
