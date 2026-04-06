# Tasks: API de Procesamiento de Documentos

**Input**: Design documents from `/specs/001-api-gestion-documentos/`
**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: TDD es OBLIGATORIO según la constitución del proyecto. Los tests se escriben
ANTES de la implementación siguiendo el ciclo Red-Green-Refactor.

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `app/`, `tests/` at repository root
- Paths shown below follow plan.md structure

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan in app/ #84
- [ ] T002 Initialize Python project with uv and pyproject.toml dependencies #85
- [ ] T003 [P] Create .env.example with required environment variables #86
- [ ] T004 [P] Configure pytest and pytest-asyncio in pyproject.toml #87
- [ ] T005 [P] Create tests/conftest.py with base fixtures and mocks #88

**Checkpoint**: Project can run `uv sync` and `pytest` without errors

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Phase ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] Unit test for Settings config loading in tests/unit/test_config.py #89
- [ ] T007 [P] Unit test for database connection pool in tests/unit/test_db_connection.py #90
- [ ] T008 [P] Unit test for ProblemDetail schema in tests/unit/test_error_schema.py #91
- [ ] T009 [P] Unit test for global exception handler in tests/unit/test_error_handlers.py #92
- [ ] T010 [P] Unit test for JWT utilities in tests/unit/test_security.py #93

### Implementation for Foundational Phase

- [ ] T011 Implement Settings with pydantic-settings in app/config.py #94
- [ ] T012 Implement asyncpg connection pool in app/db/connection.py #95
- [ ] T013 [P] Create ProblemDetail RFC 9457 schema in app/schemas/error.py #96
- [ ] T014 [P] Create custom exceptions in app/core/exceptions.py #97
- [ ] T015 Implement global exception handler in app/core/error_handlers.py #98
- [ ] T016 Implement JWT utilities (create/verify token) in app/core/security.py #99
- [ ] T017 [P] Create base repository abstract class in app/repositories/base.py #100
- [ ] T018 Create FastAPI app factory with error handlers in app/main.py #101
- [ ] T019 [P] Create DDL script for usuarios table in docs/usuarios.sql #102
- [ ] T020 [P] Create DDL script for documentos table in docs/documentos.sql #103
- [ ] T021 [P] Create DDL script for resumenes table in docs/resumenes.sql #104

**Checkpoint**: Foundation ready - `pytest tests/unit/` passes, app starts with `granian`

---

## Phase 3: User Story 1 - Registro de Usuario (Priority: P1) 🎯 MVP

**Goal**: Permitir a usuarios crear cuenta y autenticarse para acceder al sistema

**Independent Test**: Crear usuario via POST /api/v1/users, obtener token via POST /api/v1/auth/login,
consultar perfil via GET /api/v1/users/{id}

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T022 [P] [US1] Unit test for Usuario model in tests/unit/test_models/test_usuario.py #105
- [ ] T023 [P] [US1] Unit test for UsuarioRepository in tests/unit/test_repositories/test_usuario_repository.py #106
- [ ] T024 [P] [US1] Unit test for AuthService in tests/unit/test_services/test_auth_service.py #107
- [ ] T025 [P] [US1] Contract test for POST /api/v1/users in tests/contract/test_users_create.py #108
- [ ] T026 [P] [US1] Contract test for GET /api/v1/users/{id} in tests/contract/test_users_get.py #109
- [ ] T027 [P] [US1] Contract test for POST /api/v1/auth/login in tests/contract/test_auth_login.py #110
- [ ] T028 [P] [US1] Integration test for user registration flow in tests/integration/test_api/test_user_flow.py #111

### Implementation for User Story 1

- [ ] T029 [P] [US1] Create Usuario model in app/models/usuario.py #112
- [ ] T030 [P] [US1] Create Usuario Pydantic schemas in app/schemas/usuario.py #113
- [ ] T031 [US1] Implement UsuarioRepository in app/repositories/usuario_repository.py #114
- [ ] T032 [US1] Implement AuthService (register, login, hash password) in app/services/auth_service.py #115
- [ ] T033 [P] [US1] Create authentication dependency in app/api/deps.py #116
- [ ] T034 [US1] Implement POST /api/v1/users endpoint in app/api/v1/users.py #117
- [ ] T035 [US1] Implement GET /api/v1/users/{id} endpoint in app/api/v1/users.py #118
- [ ] T036 [US1] Implement POST /api/v1/auth/login endpoint in app/api/v1/auth.py #119
- [ ] T037 [US1] Register user routes in app/api/v1/router.py #120

**Checkpoint**: User Story 1 complete - can register, login, and view profile

---

## Phase 4: User Story 2 - Subida y Procesamiento de Documentos (Priority: P1) 🎯 MVP

**Goal**: Permitir subir PDFs, extraer texto con Docling, generar resumen con Nemotron

**Independent Test**: Subir PDF via POST /api/v1/documento/upload, recibir 202 Accepted,
verificar que documento pasa a estado processing→completed, resumen se genera

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T038 [P] [US2] Unit test for Documento model in tests/unit/test_models/test_documento.py #121
- [ ] T039 [P] [US2] Unit test for DocumentoRepository in tests/unit/test_repositories/test_documento_repository.py #122
- [ ] T040 [P] [US2] Unit test for ExtractionService (mock Docling) in tests/unit/test_services/test_extraction_service.py #123
- [ ] T041 [P] [US2] Unit test for SummaryService (mock OpenAI) in tests/unit/test_services/test_summary_service.py #124
- [ ] T042 [P] [US2] Unit test for DocumentService (orchestration) in tests/unit/test_services/test_document_service.py #125
- [ ] T043 [P] [US2] Contract test for POST /api/v1/documento/upload in tests/contract/test_documento_upload.py #126
- [ ] T044 [P] [US2] Contract test for file validation (PDF, size) in tests/contract/test_documento_validation.py #127
- [ ] T045 [P] [US2] Integration test for upload flow in tests/integration/test_api/test_upload_flow.py #128

### Implementation for User Story 2

- [ ] T046 [P] [US2] Create Documento model in app/models/documento.py #129
- [ ] T047 [P] [US2] Create Documento Pydantic schemas in app/schemas/documento.py #130
- [ ] T048 [US2] Implement DocumentoRepository in app/repositories/documento_repository.py #131
- [ ] T049 [US2] Implement ExtractionService (Docling wrapper) in app/services/extraction_service.py #132
- [ ] T050 [US2] Implement SummaryService (OpenAI/Nemotron wrapper) in app/services/summary_service.py #133
- [ ] T051 [US2] Implement DocumentService (upload + BackgroundTask) in app/services/document_service.py #134
- [ ] T052 [US2] Implement POST /api/v1/documento/upload endpoint in app/api/v1/documents.py #135
- [ ] T053 [US2] Add file validation middleware (PDF, 25MB) in app/api/v1/documents.py #136
- [ ] T054 [US2] Register document routes in app/api/v1/router.py #137

**Checkpoint**: User Story 2 complete - can upload PDF, processing runs async

---

## Phase 5: User Story 3 - Consulta de Resúmenes (Priority: P2)

**Goal**: Permitir consultar resúmenes de documentos procesados

**Independent Test**: Consultar GET /api/v1/summaries/document/{id}, recibir resumen
si completed, estado si processing/pending, error si failed/not found

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T055 [P] [US3] Unit test for Resumen model in tests/unit/test_models/test_resumen.py #138
- [ ] T056 [P] [US3] Unit test for ResumenRepository in tests/unit/test_repositories/test_resumen_repository.py #139
- [ ] T057 [P] [US3] Contract test for GET /api/v1/summaries/document/{id} (completed) in tests/contract/test_summaries_completed.py #140
- [ ] T058 [P] [US3] Contract test for GET /api/v1/summaries/document/{id} (processing) in tests/contract/test_summaries_processing.py #141
- [ ] T059 [P] [US3] Contract test for authorization (own documents only) in tests/contract/test_summaries_auth.py #142
- [ ] T060 [P] [US3] Integration test for summary retrieval flow in tests/integration/test_api/test_summary_flow.py #143

### Implementation for User Story 3

- [ ] T061 [P] [US3] Create Resumen model in app/models/resumen.py #144
- [ ] T062 [P] [US3] Create Resumen Pydantic schemas in app/schemas/resumen.py #145
- [ ] T063 [US3] Implement ResumenRepository in app/repositories/resumen_repository.py #146
- [ ] T064 [US3] Implement GET /api/v1/summaries/document/{id} endpoint in app/api/v1/summaries.py #147
- [ ] T065 [US3] Add ownership authorization check in app/api/v1/summaries.py #148
- [ ] T066 [US3] Register summary routes in app/api/v1/router.py #149

**Checkpoint**: User Story 3 complete - can retrieve summaries with proper auth

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T067 [P] Add structured logging configuration in app/core/logging.py #150
- [ ] T068 [P] Add BackgroundTask logging (start/success/failure) in app/services/document_service.py #151
- [ ] T069 [P] Create API documentation in docs/api-guide.md #152
- [ ] T070 [P] Add health check endpoint in app/api/v1/health.py #153
- [ ] T071 Run full test suite and verify coverage >80% #154
- [ ] T072 Run quickstart.md validation manually #155
- [x] T073 [P] Add Dockerfile for containerized deployment #156

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 and US2 can proceed in parallel (if staffed)
  - US3 depends on US2 (needs documentos to query)
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Depends on US2 (needs documentos and resumenes to exist)

### Within Each User Story (TDD Flow)

1. Tests MUST be written and FAIL before implementation
2. Models before repositories
3. Repositories before services
4. Services before endpoints
5. Endpoints before route registration
6. Story complete when all story tests pass

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tests marked [P] can run in parallel
- All Foundational implementations marked [P] can run in parallel
- Once Foundational completes: US1 and US2 can start in parallel
- Within each story: All tests marked [P] can run in parallel
- Within each story: Models and schemas marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: T022 "Unit test for Usuario model"
Task: T023 "Unit test for UsuarioRepository"
Task: T024 "Unit test for AuthService"
Task: T025 "Contract test for POST /api/v1/users"
Task: T026 "Contract test for GET /api/v1/users/{id}"
Task: T027 "Contract test for POST /api/v1/auth/login"
Task: T028 "Integration test for user registration flow"

# Launch parallelizable implementations:
Task: T029 "Create Usuario model"
Task: T030 "Create Usuario Pydantic schemas"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Registration + Auth)
4. Complete Phase 4: User Story 2 (Document Upload + Processing)
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo if ready (minimal viable product)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Can demo registration
3. Add User Story 2 → Test independently → Can demo upload (MVP!)
4. Add User Story 3 → Test independently → Full feature complete
5. Polish phase → Production ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Registration)
   - Developer B: User Story 2 (Upload) - runs in parallel
3. Developer A moves to User Story 3 after US1 complete
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD is NON-NEGOTIABLE: Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
