# Tasks: Sistema de API para Gestión de Documentos

**Input**: Design documents from `/specs/001-api-gestion-documentos/`
**Prerequisites**: plan.md, spec.md, research.md

**Tests**: TDD is mandatory per constitution - all test tasks are REQUIRED and must be written BEFORE implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

All paths are relative to repository root (`/Users/josejoaquincaparros/Documents/Proyectos-Facultad/NotebookUm/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Update pyproject.toml with all dependencies (Flask, SQLAlchemy, Flask-SQLAlchemy, mysql-connector-python, alembic, openai, docling, granian, celery, redis, python-dotenv, black, flake8, pylint, pytest, pytest-flask, pytest-cov, pytest-mock)
- [ ] T002 Run `uv sync` to install all dependencies
- [ ] T003 [P] Create .env.example with all required environment variables (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, OPENAI_API_KEY, CELERY_BROKER_URL, SECRET_KEY, MAX_UPLOAD_SIZE)
- [ ] T004 [P] Configure black formatter in pyproject.toml (line-length=100, PEP 8 compliance)
- [ ] T005 [P] Configure flake8 linter in .flake8 file
- [ ] T006 [P] Configure pytest in pyproject.toml (testpaths, coverage settings)
- [ ] T007 Create directory structure: app/models/, app/routes/, app/services/, app/utils/, tests/unit/, tests/integration/, tests/contract/, migrations/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create app/config.py with BaseConfig, DevelopmentConfig, ProductionConfig, TestingConfig classes using dataclasses for DatabaseConfig and OpenAIConfig
- [ ] T009 [P] Create app/database.py with SQLAlchemy initialization (db object, Base class)
- [ ] T010 [P] Create app/utils/errors.py with RFC 9457 error response utilities (problem_details function for 400/404/500 errors)
- [ ] T011 Update app/__init__.py with Flask app factory (create_app function) that initializes db, registers blueprints, and configures OpenAI client
- [ ] T012 [P] Create app/utils/db.py with database session management utilities
- [ ] T013 Initialize Alembic migrations in migrations/ directory
- [ ] T014 Create main.py with Granian server entry point
- [ ] T015 [P] Write unit tests for app/config.py in tests/unit/test_config.py (test environment variable loading)
- [ ] T016 [P] Write unit tests for app/utils/errors.py in tests/unit/test_errors.py (test RFC 9457 format)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Creación de Cuenta de Usuario (Priority: P1) 🎯 MVP

**Goal**: Permitir a nuevos usuarios crear cuentas y consultar su información de perfil

**Independent Test**: 
- Crear usuario vía POST /api/v1/users
- Consultar usuario vía GET /api/v1/users/{id}
- Validar que datos inválidos devuelven error descriptivo

### Tests for User Story 1 (TDD - WRITE FIRST, ENSURE THEY FAIL)

- [ ] T017 [P] [US1] Write contract test for POST /api/v1/users in tests/contract/test_users_api.py (test successful creation, test validation errors, test duplicate email)
- [ ] T018 [P] [US1] Write contract test for GET /api/v1/users/{id} in tests/contract/test_users_api.py (test successful retrieval, test 404 for non-existent user)
- [ ] T019 [P] [US1] Write unit test for Usuario model in tests/unit/test_models.py (test model creation, test email uniqueness constraint, test timestamps)

### Implementation for User Story 1

- [ ] T020 [US1] Create Usuario model in app/models/user.py (id, email, nombre, created_at, updated_at with relationships to documentos and preguntas)
- [ ] T021 [US1] Create Alembic migration for usuarios table
- [ ] T022 [US1] Run migration: `uv run alembic upgrade head`
- [ ] T023 [US1] Create UserService in app/services/user_service.py (create_user, get_user_by_id, validate_user_data methods)
- [ ] T024 [US1] Write unit tests for UserService in tests/unit/test_services.py (test create_user, test get_user_by_id with mocked db)
- [ ] T025 [US1] Create users blueprint in app/routes/users.py with POST /api/v1/users endpoint (validate input, call UserService, return JSON with user ID)
- [ ] T026 [US1] Add GET /api/v1/users/{id} endpoint to app/routes/users.py (call UserService, return user data or 404)
- [ ] T027 [US1] Register users blueprint in app/__init__.py
- [ ] T028 [US1] Add input validation for user creation (email format, required fields) in app/routes/users.py
- [ ] T029 [US1] Add error handling with RFC 9457 format for user endpoints
- [ ] T030 [US1] Run all User Story 1 tests: `uv run pytest tests/contract/test_users_api.py tests/unit/test_models.py -v`

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create accounts and retrieve their information

---

## Phase 4: User Story 2 - Carga y Procesamiento de Documentos PDF (Priority: P1)

**Goal**: Permitir a usuarios cargar PDFs, extraer texto automáticamente, generar resúmenes vía IA, y consultar estado de procesamiento

**Independent Test**:
- Cargar PDF válido <25MB vía POST /api/v1/documento/upload
- Rechazar archivos no-PDF con error 400
- Rechazar archivos >25MB con error 400 RFC 9457
- Verificar procesamiento asíncrono (respuesta inmediata)
- Consultar estado de procesamiento

### Tests for User Story 2 (TDD - WRITE FIRST, ENSURE THEY FAIL)

- [ ] T031 [P] [US2] Write contract test for POST /api/v1/documento/upload in tests/contract/test_documents_api.py (test valid PDF upload, test non-PDF rejection, test >25MB rejection, test async confirmation)
- [ ] T032 [P] [US2] Write integration test for PDF extraction in tests/integration/test_pdf_extraction.py (test Docling extracts text from sample PDF, test error handling for corrupted PDF)
- [ ] T033 [P] [US2] Write integration test for summary generation in tests/integration/test_summary_generation.py (test OpenAI generates summary from text, test hierarchical summarization for long text, test Spanish/English support)
- [ ] T034 [P] [US2] Write integration test for async processing in tests/integration/test_async_processing.py (test Celery task execution, test status updates in database)
- [ ] T035 [P] [US2] Write unit test for file validation in tests/unit/test_validation.py (test PDF content-type check, test file size check, test error messages)

### Implementation for User Story 2

- [ ] T036 [P] [US2] Create HistorialDocumento model in app/models/document.py (id, usuario_id, nombre_archivo, extracto_texto, tamanio_bytes, estado, created_at with relationships to usuario and resumenes)
- [ ] T037 [P] [US2] Create Resumen model in app/models/summary.py (id, documento_id, contenido, modelo_utilizado, created_at with relationship to documento)
- [ ] T038 [US2] Create Alembic migration for historial_documentos and resumenes tables
- [ ] T039 [US2] Run migration: `uv run alembic upgrade head`
- [ ] T040 [US2] Create app/services/validation.py with file validation functions (validate_pdf_content_type, validate_file_size, create_rfc9457_error)
- [ ] T041 [US2] Create app/services/pdf_service.py with Docling integration (extract_text_from_pdf function with error handling for corrupted files)
- [ ] T042 [US2] Create app/services/summary_service.py with OpenAI integration (initialize_openai_client, detect_language, summarize_text, hierarchical_summarize for long texts with retry logic)
- [ ] T043 [US2] Setup Celery in app/services/async_tasks.py (configure broker, create process_document_task that calls pdf_service and summary_service)
- [ ] T044 [US2] Create documents blueprint in app/routes/documents.py with POST /api/v1/documento/upload endpoint (validate file, save metadata, enqueue async task, return processing status)
- [ ] T045 [US2] Add GET /api/v1/documento/{document_id}/status endpoint to check processing status
- [ ] T046 [US2] Register documents blueprint in app/__init__.py
- [ ] T047 [US2] Add comprehensive error handling for upload endpoint (non-PDF error, size limit error with RFC 9457, processing errors)
- [ ] T048 [US2] Update HistorialDocumento model with estado field (pending, processing, completed, failed)
- [ ] T049 [US2] Update async task to update estado field throughout processing lifecycle
- [ ] T050 [US2] Run all User Story 2 tests: `uv run pytest tests/contract/test_documents_api.py tests/integration/ -v`

**Checkpoint**: At this point, User Story 2 should be fully functional - users can upload PDFs and system processes them asynchronously

---

## Phase 5: User Story 3 - Consulta de Resúmenes Generados (Priority: P2)

**Goal**: Permitir a usuarios consultar resúmenes de documentos previamente procesados

**Independent Test**:
- Consultar resumen vía GET /api/v1/summaries/document/{document_id}
- Verificar 404 para documento inexistente
- Verificar mensaje apropiado para documento en procesamiento
- Validar que solo el dueño puede acceder al resumen

### Tests for User Story 3 (TDD - WRITE FIRST, ENSURE THEY FAIL)

- [ ] T051 [P] [US3] Write contract test for GET /api/v1/summaries/document/{document_id} in tests/contract/test_summaries_api.py (test successful retrieval, test 404 for non-existent document, test 403 for unauthorized access, test pending status for processing document)
- [ ] T052 [P] [US3] Write integration test for summary retrieval in tests/integration/test_summary_retrieval.py (test complete flow: upload → process → retrieve summary)

### Implementation for User Story 3

- [ ] T053 [US3] Create SummaryService in app/services/summary_service.py (get_summary_by_document_id, check_user_ownership methods)
- [ ] T054 [US3] Write unit tests for SummaryService in tests/unit/test_services.py (test ownership validation, test retrieval with mocked db)
- [ ] T055 [US3] Create summaries blueprint in app/routes/summaries.py with GET /api/v1/summaries/document/{document_id} endpoint (validate ownership, return summary or appropriate error)
- [ ] T056 [US3] Register summaries blueprint in app/__init__.py
- [ ] T057 [US3] Add authorization check to verify user owns the document before returning summary
- [ ] T058 [US3] Add status-aware response (return "processing" message if estado is not "completed")
- [ ] T059 [US3] Add comprehensive error handling (404 for not found, 403 for unauthorized, clear messaging for processing state)
- [ ] T060 [US3] Run all User Story 3 tests: `uv run pytest tests/contract/test_summaries_api.py tests/integration/test_summary_retrieval.py -v`

**Checkpoint**: At this point, User Story 3 should be fully functional - users can retrieve summaries of their processed documents

---

## Phase 6: User Story 4 - Gestión del Historial de Documentos (Priority: P3)

**Goal**: Permitir CRUD completo sobre historial de documentos (listar, actualizar metadata, eliminar)

**Independent Test**:
- GET /api/v1/documentos - listar todos los documentos del usuario
- PATCH /api/v1/documento/{id} - actualizar metadata
- DELETE /api/v1/documento/{id} - eliminar documento y sus resúmenes

### Tests for User Story 4 (TDD - WRITE FIRST, ENSURE THEY FAIL)

- [ ] T061 [P] [US4] Write contract test for GET /api/v1/documentos in tests/contract/test_documents_api.py (test list all user documents, test pagination if implemented, test empty list for new user)
- [ ] T062 [P] [US4] Write contract test for PATCH /api/v1/documento/{id} in tests/contract/test_documents_api.py (test update metadata, test 404 for non-existent, test 403 for unauthorized)
- [ ] T063 [P] [US4] Write contract test for DELETE /api/v1/documento/{id} in tests/contract/test_documents_api.py (test successful deletion, test cascade delete of summaries, test 404 for non-existent)

### Implementation for User Story 4

- [ ] T064 [US4] Add GET /api/v1/documentos endpoint to app/routes/documents.py (return all documents for authenticated user with pagination support)
- [ ] T065 [US4] Add PATCH /api/v1/documento/{id} endpoint to app/routes/documents.py (update document metadata, validate ownership)
- [ ] T066 [US4] Add DELETE /api/v1/documento/{id} endpoint to app/routes/documents.py (delete document and cascade to summaries, validate ownership)
- [ ] T067 [US4] Add DocumentService methods in app/services/document_service.py (list_user_documents, update_document, delete_document)
- [ ] T068 [US4] Write unit tests for DocumentService in tests/unit/test_services.py
- [ ] T069 [US4] Update Resumen model to ensure cascade delete when documento is deleted
- [ ] T070 [US4] Add authorization checks for all CRUD operations
- [ ] T071 [US4] Run all User Story 4 tests: `uv run pytest tests/contract/test_documents_api.py -k "US4" -v`

**Checkpoint**: At this point, User Story 4 should be fully functional - users have full control over their document history

---

## Phase 7: User Story 5 - Gestión del Historial de Preguntas (Priority: P3)

**Goal**: Permitir CRUD completo sobre historial de preguntas

**Independent Test**:
- POST /api/v1/preguntas - crear nueva pregunta
- GET /api/v1/preguntas - listar preguntas del usuario
- PATCH /api/v1/pregunta/{id} - actualizar pregunta
- DELETE /api/v1/pregunta/{id} - eliminar pregunta

### Tests for User Story 5 (TDD - WRITE FIRST, ENSURE THEY FAIL)

- [ ] T072 [P] [US5] Write contract test for POST /api/v1/preguntas in tests/contract/test_questions_api.py (test create question, test validation)
- [ ] T073 [P] [US5] Write contract test for GET /api/v1/preguntas in tests/contract/test_questions_api.py (test list user questions, test filtering by document_id)
- [ ] T074 [P] [US5] Write contract test for PATCH /api/v1/pregunta/{id} in tests/contract/test_questions_api.py (test update question/answer)
- [ ] T075 [P] [US5] Write contract test for DELETE /api/v1/pregunta/{id} in tests/contract/test_questions_api.py (test delete question)
- [ ] T076 [P] [US5] Write unit test for HistorialPregunta model in tests/unit/test_models.py

### Implementation for User Story 5

- [ ] T077 [US5] Create HistorialPregunta model in app/models/question.py (id, usuario_id, documento_id, pregunta, respuesta, created_at with relationships)
- [ ] T078 [US5] Create Alembic migration for historial_preguntas table
- [ ] T079 [US5] Run migration: `uv run alembic upgrade head`
- [ ] T080 [US5] Create QuestionService in app/services/question_service.py (create, list, update, delete methods)
- [ ] T081 [US5] Write unit tests for QuestionService in tests/unit/test_services.py
- [ ] T082 [US5] Create questions blueprint in app/routes/questions.py with all CRUD endpoints
- [ ] T083 [US5] Register questions blueprint in app/__init__.py
- [ ] T084 [US5] Add authorization checks for all question operations
- [ ] T085 [US5] Add validation for question creation (required fields)
- [ ] T086 [US5] Run all User Story 5 tests: `uv run pytest tests/contract/test_questions_api.py -v`

**Checkpoint**: At this point, User Story 5 should be fully functional - users can manage their question history

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T087 [P] Add comprehensive logging throughout all services (app/services/*.py) using Python logging module
- [ ] T088 [P] Create README.md with setup instructions, API documentation, and examples
- [ ] T089 [P] Create API documentation with endpoint descriptions, request/response examples
- [ ] T090 Add rate limiting middleware to prevent abuse (Flask-Limiter)
- [ ] T091 Add request/response logging middleware
- [ ] T092 [P] Run PEP 8 compliance check: `uv run black --check app/ tests/`
- [ ] T093 [P] Run linting: `uv run flake8 app/ tests/`
- [ ] T094 [P] Run static analysis: `uv run pylint app/`
- [ ] T095 Fix all PEP 8, flake8, and pylint violations
- [ ] T096 Run full test suite with coverage: `uv run pytest --cov=app --cov-report=term-missing`
- [ ] T097 Ensure test coverage is >80% for all modules
- [ ] T098 Performance testing: Verify 100 concurrent uploads handled without degradation
- [ ] T099 Security audit: Check for SQL injection vulnerabilities, validate all inputs
- [ ] T100 Create Docker configuration for deployment (Dockerfile, docker-compose.yml with MySQL, Redis, Granian)
- [ ] T101 [P] Update .env.example with all final configuration options
- [ ] T102 Write deployment documentation in docs/deployment.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP target
- **User Story 2 (Phase 4)**: Depends on Foundational AND User Story 1 (needs Usuario model)
- **User Story 3 (Phase 5)**: Depends on User Story 2 (needs documents and summaries to exist)
- **User Story 4 (Phase 6)**: Depends on User Story 2 (extends document management)
- **User Story 5 (Phase 7)**: Depends on Foundational (can run parallel to other stories but needs Usuario and optionally HistorialDocumento)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (CRITICAL BLOCKER)
    ↓
    ├─→ Phase 3: User Story 1 (Users) 🎯 MVP
    │       ↓
    │   Phase 4: User Story 2 (Document Upload & Processing)
    │       ↓
    │       ├─→ Phase 5: User Story 3 (Summary Retrieval)
    │       └─→ Phase 6: User Story 4 (Document CRUD)
    │
    └─→ Phase 7: User Story 5 (Questions CRUD) - Can run in parallel
    
    ↓
Phase 8: Polish
```

### Within Each User Story

**TDD Workflow (MANDATORY)**:
1. Write ALL tests first (contract, integration, unit)
2. Run tests - they MUST FAIL (red)
3. Implement models
4. Implement services
5. Implement routes/endpoints
6. Run tests again - they MUST PASS (green)
7. Refactor for quality (maintain green)

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005, T006 can run in parallel
- **Phase 2 (Foundational)**: T009, T010, T012, T015, T016 can run in parallel
- **Within User Stories**: All tests marked [P] can run in parallel, all models marked [P] can run in parallel
- **Phase 8 (Polish)**: T087, T088, T089, T092, T093, T094, T101 can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together (TDD - red phase):
Task T031: "Contract test for POST /api/v1/documento/upload"
Task T032: "Integration test for PDF extraction"
Task T033: "Integration test for summary generation"
Task T034: "Integration test for async processing"
Task T035: "Unit test for file validation"

# Launch models in parallel (green phase):
Task T036: "Create HistorialDocumento model"
Task T037: "Create Resumen model"

# Sequential services (dependencies):
Task T040 → T041 → T042 → T043 (validation → pdf → summary → async)
```

---

## Implementation Strategy

### MVP First (Phases 1-3 Only)

1. Complete Phase 1: Setup (7 tasks)
2. Complete Phase 2: Foundational (9 tasks) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 (14 tasks) - Users can register and retrieve profiles
4. **STOP and VALIDATE**: Run all tests, deploy locally, verify end-to-end
5. **DEMO**: Show working user registration/retrieval system

**MVP Deliverable**: Basic user management system ready for document processing features

### Incremental Delivery (Recommended)

1. **Sprint 1**: Setup + Foundational + US1 → User management working
2. **Sprint 2**: US2 → Document upload and processing working (core value!)
3. **Sprint 3**: US3 → Summary retrieval working (complete core workflow)
4. **Sprint 4**: US4 + US5 → Full CRUD on documents and questions
5. **Sprint 5**: Polish → Production-ready system

### Parallel Team Strategy

With 3 developers after Foundational phase:

1. **Team completes Phase 1 + 2 together** (foundational work)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (14 tasks)
   - **Developer B**: Prepare for User Story 2 (research Docling/OpenAI integration)
   - **Developer C**: User Story 5 (10 tasks - independent from US2-4)
3. After US1 complete:
   - **Developer A + B**: User Story 2 (20 tasks - largest story)
   - **Developer C**: Continue US5 or start US4
4. Sequential: US3 → US4 (both depend on US2)
5. Parallel: Polish tasks at the end

---

## Test Execution Commands

```bash
# Run all tests
uv run pytest

# Run specific user story tests
uv run pytest tests/contract/test_users_api.py -v          # US1
uv run pytest tests/contract/test_documents_api.py -v      # US2, US4
uv run pytest tests/contract/test_summaries_api.py -v      # US3
uv run pytest tests/contract/test_questions_api.py -v      # US5

# Run with coverage
uv run pytest --cov=app --cov-report=html --cov-report=term-missing

# Run integration tests only
uv run pytest tests/integration/ -v

# TDD workflow for a feature
uv run pytest tests/contract/test_users_api.py -v  # Should FAIL initially
# ... implement feature ...
uv run pytest tests/contract/test_users_api.py -v  # Should PASS after implementation
```

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- **TDD is MANDATORY**: Tests must be written BEFORE implementation (constitution requirement)
- Each user story should be independently completable and testable
- **Red-Green-Refactor**: Verify tests fail → implement → verify tests pass → refactor
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All code must pass black, flake8, and pylint before merging
- Target >80% test coverage for all modules

---

## Total Task Count

- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 9 tasks
- **Phase 3 (User Story 1)**: 14 tasks
- **Phase 4 (User Story 2)**: 20 tasks
- **Phase 5 (User Story 3)**: 10 tasks
- **Phase 6 (User Story 4)**: 11 tasks
- **Phase 7 (User Story 5)**: 15 tasks
- **Phase 8 (Polish)**: 16 tasks

**Total: 102 tasks**

**MVP Scope**: 30 tasks (Phases 1-3)
**Core Value**: 60 tasks (Phases 1-5 = MVP + document processing + summary retrieval)
