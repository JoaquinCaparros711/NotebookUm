# Implementation Plan: Sistema de API para Gestión de Documentos

**Branch**: `001-api-gestion-documentos` | **Date**: 2026-04-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-api-gestion-documentos/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Construir una API RESTful para gestión y procesamiento de documentos PDF que permita a los usuarios cargar documentos, extraer texto automáticamente, generar resúmenes mediante IA, y consultar el historial de documentos procesados. El sistema utilizará Flask como framework web, Docling para extracción de texto, OpenAI para generación de resúmenes, MySQL para persistencia, y Granian como servidor de aplicaciones ASGI de alto rendimiento. Todo el procesamiento de documentos será asíncrono para no bloquear al usuario.

## Technical Context

**Language/Version**: Python 3.12 (PEP 8 compliance mandatory)  
**Primary Dependencies**: 
  - Flask 3.1+ (web framework)
  - OpenAI 2.29.0+ (AI text summarization)
  - Docling (PDF text extraction)
  - MySQL connector/driver (NEEDS CLARIFICATION - specific library choice)
  - Granian (ASGI server)
**Storage**: MySQL (relational database for users, documents, summaries, and question history)  
**Testing**: pytest 8.0+, pytest-flask 1.3+ (TDD mandatory per constitution)  
**Target Platform**: Linux/Unix server environments (cloud deployment ready)
**Project Type**: Web service / REST API  
**Performance Goals**: 
  - Accept PDF upload and respond within 5 seconds (async processing initiation)
  - Handle 100 concurrent document uploads without degradation
  - Query summaries in <2 seconds
  - User creation/retrieval in <30 seconds
**Constraints**: 
  - PDF files only (application/pdf content-type)
  - Maximum file size: 25MB
  - Do NOT store original PDF files (only extracted text and summaries)
  - Async document processing (non-blocking)
  - RFC 9457 compliant error responses
  - All API endpoints must start with `/api/v1/`
**Scale/Scope**: 
  - Multi-user system with user isolation
  - Spanish and English document support
  - 4 main database tables (usuarios, historial_documentos, resumenes, historial_preguntas)
  - Full CRUD operations for all entities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. KISS (Keep It Simple, Stupid)
- **Status**: PASS
- **Rationale**: REST API with straightforward CRUD operations. Flask is lightweight and appropriate for the scope. Async processing via background tasks keeps architecture simple.

### ✅ II. DRY (Don't Repeat Yourself)
- **Status**: PASS
- **Rationale**: Design will use shared base models, common error handlers, and reusable validation utilities. Database schema normalizes data to avoid duplication.

### ✅ III. YAGNI (You Aren't Gonna Need It)
- **Status**: PASS
- **Rationale**: Building only specified features. No premature optimization or speculative abstractions. CRUD operations are required, not over-engineered.

### ✅ IV. SOLID Principles
- **Status**: PASS
- **Rationale**: 
  - Single Responsibility: Separate models, routes, services, and utilities
  - Open/Closed: Services can be extended without modifying core logic
  - Dependency Inversion: Will use dependency injection for services (database, OpenAI client)

### ✅ V. TDD (Test-Driven Development - NON-NEGOTIABLE)
- **Status**: PASS
- **Commitment**: All code will follow red-green-refactor cycle. pytest and pytest-flask already configured. Tests will be written BEFORE implementation code.

### ✅ VI. SDD (Specification-Driven Development)
- **Status**: PASS
- **Evidence**: spec.md exists with detailed user stories, acceptance criteria, and success metrics. Implementation cannot proceed without approved specification.

### ✅ VII. PEP 8 Compliance
- **Status**: PASS
- **Tooling**: Will use black (formatter), flake8 (linter), and pylint (static analysis) to enforce PEP 8 compliance automatically.

### ⚠️ VIII. 12-Factor App (First Six Factors)
- **Status**: NEEDS CLARIFICATION → Research required
- **Factors to validate**:
  - I. Codebase: ✅ Git repository already established
  - II. Dependencies: ✅ UV is being used for dependency management
  - III. Config: ⚠️ NEEDS CLARIFICATION - Environment variable strategy for MySQL credentials, OpenAI API keys, file size limits
  - IV. Backing Services: ⚠️ NEEDS CLARIFICATION - MySQL connection pooling strategy, OpenAI client initialization
  - V. Build/Release/Run: ⚠️ NEEDS CLARIFICATION - Deployment pipeline with Granian server
  - VI. Processes: ⚠️ NEEDS CLARIFICATION - Stateless design with async task handling (background workers architecture)

**Overall Gate Status**: ⚠️ **CONDITIONAL PASS** - Proceed to Phase 0 research to resolve 12-Factor App clarifications

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── __init__.py              # Flask app factory
├── config.py                # Configuration management (12-Factor: env vars)
├── models/                  # Database models (SQLAlchemy/MySQL)
│   ├── __init__.py
│   ├── user.py             # Usuario model
│   ├── document.py         # Historial_documentos model
│   ├── summary.py          # Resumenes model
│   └── question.py         # Historial_preguntas model
├── routes/                  # API endpoints
│   ├── __init__.py
│   ├── users.py            # /api/v1/users endpoints
│   ├── documents.py        # /api/v1/documento endpoints
│   ├── summaries.py        # /api/v1/summaries endpoints
│   └── questions.py        # /api/v1/questions endpoints (future CRUD)
├── services/                # Business logic layer
│   ├── __init__.py
│   ├── pdf_service.py      # Docling integration for text extraction
│   ├── summary_service.py  # OpenAI integration for summarization
│   ├── async_tasks.py      # Background task management
│   └── validation.py       # File validation (PDF type, size limits)
└── utils/                   # Shared utilities
    ├── __init__.py
    ├── errors.py           # RFC 9457 error responses
    └── db.py               # Database connection/session management

tests/
├── unit/                    # Unit tests (isolated, mocked dependencies)
│   ├── test_models.py
│   ├── test_services.py
│   └── test_validation.py
├── integration/             # Integration tests (database, external services)
│   ├── test_pdf_extraction.py
│   ├── test_summary_generation.py
│   └── test_async_processing.py
└── contract/                # API contract tests (endpoint behavior)
    ├── test_users_api.py
    ├── test_documents_api.py
    └── test_summaries_api.py

main.py                      # Application entry point (Granian server setup)
pyproject.toml              # UV dependency configuration
.env.example                # Environment variable template
migrations/                  # Database migrations (Alembic)
```

**Structure Decision**: Single project structure selected. This is a REST API backend service with clear separation of concerns: models (data layer), routes (presentation layer), services (business logic), and utilities (cross-cutting concerns). The structure follows Flask best practices and supports TDD with comprehensive test coverage across unit, integration, and contract levels.

## Complexity Tracking

> No violations detected. All constitution principles can be satisfied with straightforward implementation.
