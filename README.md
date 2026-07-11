# 🎓 LMS / School Management System — with AI-Powered RAG Search

A **production-grade, multi-app Learning & School Management System (LMS)** built with **Django REST Framework** and **PostgreSQL**, covering the full academic lifecycle — admissions, attendance, exams, fees, timetable, transport, communication, and certification — plus a **Retrieval-Augmented Generation (RAG) search engine** that lets staff query student and academic data using natural language.

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![Django](https://img.shields.io/badge/django-5+-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-15+-336791.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)
![RAG](https://img.shields.io/badge/AI%20Search-RAG%20powered-purple.svg)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Tech Stack](#tech-stack)
4. [Applications / Modules](#applications--modules)
5. [AI-Powered Search (RAG)](#ai-powered-search-rag)
6. [Folder Structure](#folder-structure)
7. [Getting Started](#getting-started)
8. [Environment Variables](#environment-variables)
9. [Docker Setup](#docker-setup)
10. [Running Locally (Without Docker)](#running-locally-without-docker)
11. [API Documentation](#api-documentation)
12. [User Roles & Permissions](#user-roles--permissions)
13. [Standard API Response Format](#standard-api-response-format)
14. [Testing](#testing)
15. [Code Quality](#code-quality)
16. [Deployment](#deployment)
17. [Future Improvements](#future-improvements)
18. [Contributing](#contributing)
19. [License](#license)

---

## Overview

This platform digitizes end-to-end school/institution operations across **16 Django apps**, with a unified custom `User` model backing role-specific profiles (`Student`, `Teacher`, `Parent`, `Employee`). It covers:

- Student & staff identity, roles, and permission management
- Academic structure: academic years, departments, classes, sections, subjects
- Daily & monthly attendance tracking with configurable rules
- Fee structures, invoicing, payments, and discounts/scholarships
- Examinations, grading, and auto-generated report cards
- Homework/assignments with submission and grading workflows
- Online learning: courses, lessons, quizzes, and progress tracking
- Leave management with multi-level approval workflows and audit history
- Certificates and student document management
- School-wide communication: announcements, events, internal messaging, notifications
- Transport route, vehicle, and allocation management
- Timetable/period scheduling
- Centralized media library and system configuration/audit logging
- **A RAG-based natural language search layer** for instantly finding student and academic records without writing filters or SQL

Engineering principles applied throughout:

- Clean Architecture with **service / selector** layers separating business logic from views
- SOLID, DRY, and reusable generic API mixins (pagination, filtering, search, ordering)
- Consistent `TimeStamps` / `TimeUserStamps` base models (audit fields: `created_at`, `updated_at`, `created_by`, `updated_by`, soft delete)
- Auto-generated, collision-safe identifiers (`employee_id`, `invoice_number`, `payment_id`, `application_number`, `certificate_number`, route `code`, etc.)

---

## Architecture Diagram

```
                         ┌─────────────────────┐
                         │   Web / Mobile App    │
                         │ (Admin, Teacher,      │
                         │  Student, Parent UI)   │
                         └──────────┬───────────┘
                                    │ HTTPS
                         ┌──────────▼───────────┐
                         │        Nginx           │
                         │  Reverse Proxy / TLS    │
                         └─────┬─────────────┬────┘
                               │             │
                 ┌─────────────▼──┐    ┌─────▼───────────────┐
                 │  Django + DRF    │    │   RAG Search Service  │
                 │  (Gunicorn)      │    │  (Embedding + LLM      │
                 │  REST API        │    │   query orchestration) │
                 └───┬──────────┬──┘    └─────┬──────────────┘
                     │          │             │
        ┌────────────▼──┐  ┌────▼───────┐ ┌───▼─────────────┐
        │  PostgreSQL     │  │   Redis     │ │  Vector Store     │
        │ (System of       │  │ (Cache /    │ │ (pgvector /        │
        │  Record)         │  │  Celery      │ │  Chroma / Pinecone) │
        │                  │  │  Broker)     │ │                    │
        └──────────────────┘  └────┬───────┘ └────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │  Celery Worker /    │
                          │  Celery Beat         │
                          │ (Notifications,       │
                          │  report generation,    │
                          │  embedding sync jobs)   │
                          └───────────────────────┘
```

---

## Tech Stack

### Backend
Python 3.13+ · Django 5+ · Django REST Framework · PostgreSQL · Redis · Celery · JWT Authentication · DRF Spectacular (Swagger/OpenAPI) · Gunicorn · Nginx · Pillow · django-filter · Pytest

### AI / RAG Search Layer
- **Embedding model** for converting student/academic records into vector representations
- **Vector database** (`pgvector` extension on PostgreSQL, or a dedicated store such as Chroma/Pinecone) for similarity search
- **LLM orchestration layer** that turns a natural-language query into a retrieval + answer-generation pipeline
- **Celery-scheduled sync jobs** that keep embeddings up to date as records change

### Frontend
Next.js / React (or your admin panel of choice) · TypeScript · Tailwind CSS · Redux Toolkit / TanStack Query · Axios

### Database
PostgreSQL with composite indexes, unique constraints, and foreign keys across all 16 apps.

---

## Applications / Modules

| App | Responsibility | Key Models |
|---|---|---|
| **users** | Identity, auth, roles, permissions, staff/student/parent profiles | `User`, `Role`, `Permission`, `UserToken`, `Employee`, `Student`, `Teacher`, `Parent` |
| **academic** | Academic structure | `AcademicYear`, `Department`, `Class`, `Section`, `Subject`, `ClassSubject` |
| **attendance** | Daily/monthly attendance tracking & reporting | `DailyAttendance`, `MonthlyAttendanceReport`, `AttendanceConfiguration`, `AttendanceSummary` |
| **fee** | Fee structures, invoicing, payments, discounts | `FeeType`, `FeeStructure`, `FeeInvoice`, `FeeInvoiceItem`, `FeePayment`, `FeeDiscount`, `StudentDiscount` |
| **leave** | Leave applications, balances, multi-level approvals, audit trail | `LeaveType`, `LeaveApplication`, `LeaveBalance`, `LeaveConfiguration`, `LeaveApprovalWorkflow`, `LeaveHistory` |
| **online_learning** | Courses, lessons, quizzes, and progress | `Course`, `Lesson`, `CourseEnrollment`, `LessonProgress`, `Quiz`, `Question`, `QuestionOption`, `QuizAttempt`, `QuizAnswer` |
| **exams** | Exam scheduling, results, and grading | `ExamType`, `Exam`, `ExamSchedule`, `ExamResult`, `GradeSystem` |
| **report** | Report cards and student conduct records | `ReportCard`, `StudentBehavior` |
| **homework_assignments** | Homework creation and submission workflow | `Assignment`, `AssignmentSubmission` |
| **certificates** | Certificate templates, issuance, and student documents | `CertificateTemplate`, `Certificate`, `Document` |
| **communication** | Announcements, events, internal messaging, notifications | `Announcement`, `Event`, `Message`, `Notification` |
| **timetable** | Period definitions and class schedules | `TimeSlot`, `Timetable` |
| **transport** | Routes, vehicles, and student transport allocation | `Route`, `Vehicle`, `TransportAllocation` |
| **images** | Centralized media/image library | `Categories`, `Images` |
| **notifications** | Reusable transactional email templates | `EmailTemplate` |
| **configuration** | School settings, communication templates, system audit log | `SchoolSettings`, `EmailTemplate`, `SMSTemplate`, `AuditLog` |

---

## AI-Powered Search (RAG)

Beyond standard filtering and search endpoints, the platform includes a **Retrieval-Augmented Generation (RAG) search service** so staff can ask plain-language questions instead of building filters manually.

**Example queries:**
- *"Show me all Grade 10 students with attendance below 75% this month"*
- *"List students with overdue fee invoices in Section B"*
- *"Which students submitted assignment 'Algebra Worksheet 3' late?"*
- *"Find all pending leave applications for teachers this week"*

### How it works

1. **Indexing** — Celery jobs periodically (or on model `post_save` signals) convert relevant records — student profiles, attendance summaries, fee invoices, exam results, assignments, leave applications — into text chunks and generate embeddings.
2. **Vector storage** — Embeddings are stored in a vector index (`pgvector` on the same PostgreSQL instance, or an external vector database) alongside metadata (`student_id`, `class`, `academic_year`, record type) for filtered retrieval.
3. **Query pipeline** — A user's natural-language query is embedded, the vector store returns the top-k most relevant records, and those records are passed as grounded context to an LLM.
4. **Answer generation** — The LLM composes a concise, cited answer (or structured table) strictly from the retrieved records — it does not fabricate data outside what was retrieved.
5. **Access control** — Retrieval is always scoped by the requesting user's role/permissions (e.g., a teacher only retrieves students in their assigned classes; a parent only retrieves their own children's records).

### API

| Endpoint | Description |
|---|---|
| `POST /api/v1/search/ask/` | Accepts a natural-language query, returns an LLM-generated answer plus the source records used |
| `POST /api/v1/search/semantic/` | Returns raw top-k matching records for a query (no LLM generation — for building custom UI) |
| `POST /api/v1/search/reindex/` | Admin-only: triggers a manual re-embedding of a given app/model |

### Environment variables

```env
# RAG / LLM Search
LLM_PROVIDER=anthropic          # or openai, etc.
LLM_API_KEY=change-me
LLM_MODEL=claude-sonnet-5
EMBEDDING_MODEL=text-embedding-3-large
VECTOR_STORE=pgvector           # or chroma, pinecone
VECTOR_STORE_URL=postgresql://...
RAG_TOP_K=8
RAG_REINDEX_SCHEDULE_CRON="0 * * * *"   # hourly embedding sync
```

> Retrieved context is always scoped to what the querying user is authorized to see — the RAG layer sits behind the same role/permission checks as the rest of the API, never bypassing them.

---

## Folder Structure

```
backend/
├── apps/
│   ├── users/
│   ├── academic/
│   ├── attendance/
│   ├── fee/
│   ├── leave/
│   ├── online_learning/
│   ├── exams/
│   ├── report/
│   ├── homework_assignments/
│   ├── certificates/
│   ├── communication/
│   ├── timetable/
│   ├── transport/
│   ├── images/
│   ├── notifications/
│   ├── configuration/
│   └── search/              # RAG indexing, retrieval, and query endpoints
├── utils/
│   ├── reusable_classes.py    # TimeStamps, TimeUserStamps base models
│   ├── validators.py
│   └── enums.py
├── requirements/
├── Dockerfile
└── manage.py
```

---

## Getting Started

### Prerequisites
- Docker & Docker Compose (recommended), or
- Python 3.13+, PostgreSQL 15+ (with `pgvector` extension if using it), Redis 7+

```bash
git clone <your-repo-url>
cd lms-school-management-system
```

---

## Environment Variables

### Backend (`.env`)
```env
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=core.settings.local

POSTGRES_DB=lms_db
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1

ACCESS_TOKEN_LIFETIME_MINUTES=15
REFRESH_TOKEN_LIFETIME_DAYS=7

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=change-me
DEFAULT_FROM_EMAIL=no-reply@example.com

CORS_ALLOWED_ORIGINS=http://localhost:3000

# RAG / LLM Search (see AI-Powered Search section above)
LLM_PROVIDER=anthropic
LLM_API_KEY=change-me
LLM_MODEL=claude-sonnet-5
EMBEDDING_MODEL=text-embedding-3-large
VECTOR_STORE=pgvector
RAG_TOP_K=8
```

---

## Docker Setup

```bash
docker compose up --build
```

| Service | Description | Port |
|---|---|---|
| `backend` | Django + Gunicorn | 8000 |
| `db` | PostgreSQL (+ pgvector) | 5432 |
| `redis` | Redis | 6379 |
| `celery_worker` | Background jobs (notifications, reports, embedding sync) | — |
| `celery_beat` | Scheduled tasks (attendance reports, RAG reindex) | — |
| `nginx` | Reverse proxy | 80 |

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py reindex_search   # initial RAG embedding build
```

---

## Running Locally (Without Docker)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements/local.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

```bash
celery -A core worker -l info
celery -A core beat -l info
```

API base: `http://localhost:8000/api/v1` · Swagger: `http://localhost:8000/api/docs`

---

## API Documentation

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/`

All list endpoints support `?page=`, `?search=`, `?ordering=`, and model-specific filters. The RAG search endpoints (`/api/v1/search/*`) are documented separately in [AI-Powered Search (RAG)](#ai-powered-search-rag).

---

## User Roles & Permissions

| Role | Description |
|---|---|
| Super Admin | Full system access |
| Admin | Manage users, academics, fees, and settings |
| Teacher | Manage own classes: attendance, assignments, exam results, leave requests |
| Student | View own academic record, assignments, results, timetable |
| Parent | View linked children's academic, attendance, and fee records |
| Employee | Non-teaching staff access scoped by assigned role/permissions |

All roles and fine-grained permissions are data-driven via the `Role` and `Permission` models, not hardcoded — new roles can be composed from existing permissions.

---

## Standard API Response Format

```json
{
  "success": true,
  "message": "Attendance marked successfully",
  "data": {},
  "errors": []
}
```

---

## Testing

```bash
pytest --cov=apps
```

Covers model tests, serializer tests, API/view tests, permission tests, and RAG retrieval-accuracy tests (verifying retrieved records match expected ground truth for sample queries).

---

## Code Quality

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Enforced via **Black**, **isort**, **flake8**, and **Pytest coverage**.

---

## Deployment

1. Set `DEBUG=False`, configure `ALLOWED_HOSTS`
2. Use `requirements/production.txt` and `docker-compose.prod.yml`
3. `python manage.py collectstatic --noinput`
4. `python manage.py migrate`
5. Serve via Gunicorn behind Nginx with TLS
6. Ensure Celery worker/beat are running for notifications, report generation, and RAG embedding sync
7. Provision the vector store (enable `pgvector` extension or connect to your external vector DB) before running the initial reindex
8. Store secrets (JWT, DB, SMTP, LLM API keys) in your host's secret manager — never commit `.env`

---

## Future Improvements

- Voice-based query interface for the RAG search assistant
- Predictive analytics: at-risk student identification from attendance + grades trends
- Parent/student mobile app with push notifications
- Biometric/RFID attendance integration
- Multi-language (i18n) support for communication templates
- Fine-grained audit diffing UI built on top of `AuditLog`

---

## Contributing

```bash
git checkout -b feature/your-feature
# follow the service/selector pattern per app
pre-commit run --all-files
git commit -m "feat(attendance): add configurable half-day threshold"
git push origin feature/your-feature
```

**Commit message convention:** [Conventional Commits](https://www.conventionalcommits.org/) — `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

---

## License

MIT — free to use as a portfolio project or as a foundation for institutional deployments. Update this section with your organization's actual license terms if different.