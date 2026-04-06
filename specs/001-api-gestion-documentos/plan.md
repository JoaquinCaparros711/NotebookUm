# Implementation Plan: API de Gestión de Documentos

## Overview

Build a document processing API with user registration, PDF upload/processing, and summary retrieval capabilities. The system uses FastAPI for the API layer, PostgreSQL for persistence, and integrates with external services (Docling for text extraction, OpenAI/Nemotron for summarization).

## Architecture

- **API Layer**: FastAPI with OpenAPI documentation
- **Database**: PostgreSQL with asyncpg connection pool
- **Models**: SQLAlchemy ORM (usuarios, documentos, resumenes tables)
- **Services**: Business logic layer (auth, document processing, summarization)
- **Repositories**: Data access layer with abstract base class
- **Security**: JWT tokens for authentication, bcrypt for password hashing
- **Error Handling**: RFC 9457 Problem Details

## Implementation Phases

### Phase 1: Setup (Project Initialization)
- Create project structure
- Initialize Python with uv and pyproject.toml
- Configure environment variables
- Setup pytest and test fixtures

### Phase 2: Foundational (Core Infrastructure)
- Settings configuration with pydantic-settings
- Database connection pool with asyncpg
- Error schemas (RFC 9457) and exception handling
- JWT utilities for token management
- Base repository abstraction
- FastAPI app factory with middleware
- Database table DDL scripts

### Phase 3: User Story 1 (User Registration & Authentication)
- Usuario model and repository
- Authentication service (register, login, password hashing)
- User endpoints (POST /api/v1/users, GET /api/v1/users/{id})
- Login endpoint (POST /api/v1/auth/login)
- Authentication dependency for protected routes

### Phase 4: User Story 2 (Document Upload & Processing)
- Documento model and repository
- ExtractionService (Docling integration)
- SummaryService (OpenAI/Nemotron integration)
- DocumentService (orchestrates upload + background processing)
- Upload endpoint with async background tasks
- File validation (PDF type, 25MB limit)

### Phase 5: User Story 3 (Summary Retrieval)
- Resumen model and repository
- GET /api/v1/summaries/document/{id} endpoint
- Ownership authorization checks
- Status handling (pending, processing, completed, failed)

### Phase 6: Polish & Cross-Cutting Concerns
- Structured logging
- API documentation
- Health check endpoint
- Full test coverage validation
- Docker containerization

## Test Strategy (TDD)

All tests follow Red-Green-Refactor cycle:
- Write unit tests first, ensure they FAIL
- Write integration/contract tests first, ensure they FAIL
- Implement code to make tests PASS
- Refactor while maintaining green state

Test organization:
- `tests/unit/` - isolated unit tests with mocks
- `tests/contract/` - API contract tests
- `tests/integration/` - end-to-end flow tests

## Database Schema

### usuarios table
- id (UUID, PK)
- email (VARCHAR unique)
- password_hash (VARCHAR)
- nombre (VARCHAR)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### documentos table
- id (UUID, PK)
- usuario_id (UUID, FK)
- nombre (VARCHAR)
- status (ENUM: pending, processing, completed, failed)
- contenido_extraido (TEXT nullable)
- metadata (JSONB)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### resumenes table
- id (UUID, PK)
- documento_id (UUID, FK)
- resumen (TEXT)
- modelo (VARCHAR)
- generated_at (TIMESTAMP)
- created_at (TIMESTAMP)

## Dependencies & Constraints

### Hard Blockers
- Foundation phase MUST complete before any user story work
- Database schema must exist before repository implementations
- JWT utilities must exist before auth service

### Parallel Opportunities
- Setup phase: all [P] tasks run in parallel
- Foundational phase: all [P] tests and implementations run in parallel
- User Stories 1 & 2: can proceed in parallel after Foundation
- Within each story: all [P] test tasks run in parallel

### Sequential Requirements
- Within each story: Tests → Models → Repositories → Services → Endpoints
- User Story 3: depends on User Story 2 completion (needs documentos table)

## Success Criteria

Each phase completes when:
- **Phase 1**: `uv sync` and `pytest` run without errors
- **Phase 2**: `pytest tests/unit/` passes, app starts with `granian`
- **Phase 3**: User can register, login, retrieve profile
- **Phase 4**: User can upload PDF, processing runs async, status updates correctly
- **Phase 5**: User can retrieve summary with proper authorization
- **Phase 6**: Coverage >80%, health check responds, Docker build succeeds

## Notes

- All paths follow single-project structure: `app/`, `tests/` at repo root
- Use async/await throughout (FastAPI, asyncpg, services)
- Background tasks for document processing via BackgroundTask
- Error responses use RFC 9457 Problem Detail format
- Logging includes BackgroundTask lifecycle (start/success/failure)
- Commit after each task or logical group
- TDD is non-negotiable: verify tests fail before implementation
