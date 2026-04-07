# Tareas: Sistema de API para Gestión de Documentos

**Entrada**: Documentos de diseño en `/specs/001-api-gestion-documentos/`
**Prerrequisitos**: plan.md, spec.md, research.md

**Pruebas**: TDD es obligatorio según la constitución - todas las tareas de prueba son REQUERIDAS y deben escribirse ANTES de la implementación.

**Organización**: Las tareas están agrupadas por historia de usuario para permitir la implementación y prueba independiente de cada historia.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos diferentes, sin dependencias)
- **[Historia]**: A qué historia de usuario pertenece la tarea (ej: US1, US2, US3)
- Incluir rutas exactas de archivos en las descripciones

## Convenciones de Rutas

Todas las rutas son relativas a la raíz del repositorio (`/Users/josejoaquincaparros/Documents/Proyectos-Facultad/NotebookUm/`)

---

## Fase 1: Configuración (Infraestructura Compartida)

**Propósito**: Inicialización del proyecto y estructura básica

- [ ] T001 [#291](https://github.com/JoaquinCaparros711/NotebookUm/issues/291) Actualizar pyproject.toml con todas las dependencias (Flask, SQLAlchemy, Flask-SQLAlchemy, mysql-connector-python, alembic, openai, docling, granian, celery, redis, python-dotenv, black, flake8, pylint, pytest, pytest-flask, pytest-cov, pytest-mock)
- [x] T002 [#292](https://github.com/JoaquinCaparros711/NotebookUm/issues/292) Ejecutar `uv sync` para instalar todas las dependencias
- [ ] T003 [#293](https://github.com/JoaquinCaparros711/NotebookUm/issues/293) [P] Crear .env.example con todas las variables de entorno requeridas (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, OPENAI_API_KEY, CELERY_BROKER_URL, SECRET_KEY, MAX_UPLOAD_SIZE)
- [x] T004 [#294](https://github.com/JoaquinCaparros711/NotebookUm/issues/294) [P] Configurar formateador black en pyproject.toml (line-length=100, cumplimiento PEP 8)
- [ ] T005 [#295](https://github.com/JoaquinCaparros711/NotebookUm/issues/295) [P] Configurar linter flake8 en archivo .flake8
- [ ] T006 [#296](https://github.com/JoaquinCaparros711/NotebookUm/issues/296) [P] Configurar pytest en pyproject.toml (testpaths, configuración de cobertura)
- [x] T007 [#297](https://github.com/JoaquinCaparros711/NotebookUm/issues/297) Crear estructura de directorios: app/models/, app/routes/, app/services/, app/utils/, tests/unit/, tests/integration/, tests/contract/, migrations/

---

## Fase 2: Base (Prerrequisitos Bloqueantes)

**Propósito**: Infraestructura central que DEBE completarse antes de que CUALQUIER historia de usuario pueda implementarse

**⚠️ CRÍTICO**: No se puede comenzar trabajo de historias de usuario hasta que esta fase esté completa

- [x] T008 [#299](https://github.com/JoaquinCaparros711/NotebookUm/issues/299) Crear app/config.py con clases BaseConfig, DevelopmentConfig, ProductionConfig, TestingConfig usando dataclasses para DatabaseConfig y OpenAIConfig
- [x] T009 [#300](https://github.com/JoaquinCaparros711/NotebookUm/issues/300) [P] Crear app/database.py con inicialización de SQLAlchemy (objeto db, clase Base)
- [ ] T010 [#301](https://github.com/JoaquinCaparros711/NotebookUm/issues/301) [P] Crear app/utils/errors.py con utilidades de respuesta de error RFC 9457 (función problem_details para errores 400/404/500)
- [x] T011 [#302](https://github.com/JoaquinCaparros711/NotebookUm/issues/302) Actualizar app/__init__.py con fábrica de aplicación Flask (función create_app) que inicializa db, registra blueprints y configura cliente OpenAI
- [ ] T012 [#303](https://github.com/JoaquinCaparros711/NotebookUm/issues/303) [P] Crear app/utils/db.py con utilidades de gestión de sesión de base de datos
- [ ] T013 [#304](https://github.com/JoaquinCaparros711/NotebookUm/issues/304) Inicializar migraciones Alembic en directorio migrations/
- [ ] T014 [#305](https://github.com/JoaquinCaparros711/NotebookUm/issues/305) Crear main.py con punto de entrada del servidor Granian
- [x] T015 [#306](https://github.com/JoaquinCaparros711/NotebookUm/issues/306) [P] Escribir pruebas unitarias para app/config.py en tests/unit/test_config.py (probar carga de variables de entorno)
- [x] T016 [#307](https://github.com/JoaquinCaparros711/NotebookUm/issues/307) [P] Escribir pruebas unitarias para app/utils/errors.py en tests/unit/test_errors.py (probar formato RFC 9457)

**Punto de control**: Base lista - la implementación de historias de usuario puede comenzar en paralelo

---

## Fase 3: Historia de Usuario 1 - Creación de Cuenta de Usuario (Prioridad: P1) 🎯 MVP

**Objetivo**: Permitir a nuevos usuarios crear cuentas y consultar su información de perfil

**Prueba Independiente**:
- Crear usuario vía POST /api/v1/users
- Consultar usuario vía GET /api/v1/users/{id}
- Validar que datos inválidos devuelven error descriptivo

### Pruebas para Historia de Usuario 1 (TDD - ESCRIBIR PRIMERO, ASEGURAR QUE FALLEN)

- [ ] T017 [#309](https://github.com/JoaquinCaparros711/NotebookUm/issues/309) [P] [US1] Escribir prueba de contrato para POST /api/v1/users en tests/contract/test_users_api.py (probar creación exitosa, probar errores de validación, probar email duplicado)
- [ ] T018 [#310](https://github.com/JoaquinCaparros711/NotebookUm/issues/310) [P] [US1] Escribir prueba de contrato para GET /api/v1/users/{id} en tests/contract/test_users_api.py (probar recuperación exitosa, probar 404 para usuario inexistente)
- [ ] T019 [#311](https://github.com/JoaquinCaparros711/NotebookUm/issues/311) [P] [US1] Escribir prueba unitaria para modelo Usuario en tests/unit/test_models.py (probar creación del modelo, probar restricción de unicidad de email, probar timestamps)

### Implementación para Historia de Usuario 1

- [ ] T020 [#312](https://github.com/JoaquinCaparros711/NotebookUm/issues/312) [US1] Crear modelo Usuario en app/models/user.py (id, email, nombre, created_at, updated_at con relaciones a documentos y preguntas)
- [ ] T021 [#313](https://github.com/JoaquinCaparros711/NotebookUm/issues/313) [US1] Crear migración Alembic para tabla usuarios
- [ ] T022 [#314](https://github.com/JoaquinCaparros711/NotebookUm/issues/314) [US1] Ejecutar migración: `uv run alembic upgrade head`
- [ ] T023 [#315](https://github.com/JoaquinCaparros711/NotebookUm/issues/315) [US1] Crear UserService en app/services/user_service.py (métodos create_user, get_user_by_id, validate_user_data)
- [ ] T024 [#316](https://github.com/JoaquinCaparros711/NotebookUm/issues/316) [US1] Escribir pruebas unitarias para UserService en tests/unit/test_services.py (probar create_user, probar get_user_by_id con db mockeada)
- [ ] T025 [#317](https://github.com/JoaquinCaparros711/NotebookUm/issues/317) [US1] Crear blueprint de usuarios en app/routes/users.py con endpoint POST /api/v1/users (validar entrada, llamar UserService, retornar JSON con ID de usuario)
- [ ] T026 [#318](https://github.com/JoaquinCaparros711/NotebookUm/issues/318) [US1] Agregar endpoint GET /api/v1/users/{id} a app/routes/users.py (llamar UserService, retornar datos de usuario o 404)
- [ ] T027 [#319](https://github.com/JoaquinCaparros711/NotebookUm/issues/319) [US1] Registrar blueprint de usuarios en app/__init__.py
- [ ] T028 [#320](https://github.com/JoaquinCaparros711/NotebookUm/issues/320) [US1] Agregar validación de entrada para creación de usuario (formato de email, campos requeridos) en app/routes/users.py
- [ ] T029 [#321](https://github.com/JoaquinCaparros711/NotebookUm/issues/321) [US1] Agregar manejo de errores con formato RFC 9457 para endpoints de usuario
- [ ] T030 [#322](https://github.com/JoaquinCaparros711/NotebookUm/issues/322) [US1] Ejecutar todas las pruebas de Historia de Usuario 1: `uv run pytest tests/contract/test_users_api.py tests/unit/test_models.py -v`

**Punto de control**: En este punto, la Historia de Usuario 1 debería ser completamente funcional - los usuarios pueden crear cuentas y recuperar su información

---

## Fase 4: Historia de Usuario 2 - Carga y Procesamiento de Documentos PDF (Prioridad: P1)

**Objetivo**: Permitir a usuarios cargar PDFs, extraer texto automáticamente, generar resúmenes vía IA, y consultar estado de procesamiento

**Prueba Independiente**:
- Cargar PDF válido <25MB vía POST /api/v1/documento/upload
- Rechazar archivos no-PDF con error 400
- Rechazar archivos >25MB con error 400 RFC 9457
- Verificar procesamiento asíncrono (respuesta inmediata)
- Consultar estado de procesamiento

### Pruebas para Historia de Usuario 2 (TDD - ESCRIBIR PRIMERO, ASEGURAR QUE FALLEN)

- [ ] T031 [#324](https://github.com/JoaquinCaparros711/NotebookUm/issues/324) [P] [US2] Escribir prueba de contrato para POST /api/v1/documento/upload en tests/contract/test_documents_api.py (probar carga de PDF válido, probar rechazo de no-PDF, probar rechazo >25MB, probar confirmación asíncrona)
- [ ] T032 [#325](https://github.com/JoaquinCaparros711/NotebookUm/issues/325) [P] [US2] Escribir prueba de integración para extracción de PDF en tests/integration/test_pdf_extraction.py (probar que Docling extrae texto de PDF de muestra, probar manejo de errores para PDF corrupto)
- [ ] T033 [#326](https://github.com/JoaquinCaparros711/NotebookUm/issues/326) [P] [US2] Escribir prueba de integración para generación de resumen en tests/integration/test_summary_generation.py (probar que OpenAI genera resumen del texto, probar resumen jerárquico para texto largo, probar soporte español/inglés)
- [ ] T034 [#327](https://github.com/JoaquinCaparros711/NotebookUm/issues/327) [P] [US2] Escribir prueba de integración para procesamiento asíncrono en tests/integration/test_async_processing.py (probar ejecución de tarea Celery, probar actualizaciones de estado en base de datos)
- [ ] T035 [#328](https://github.com/JoaquinCaparros711/NotebookUm/issues/328) [P] [US2] Escribir prueba unitaria para validación de archivos en tests/unit/test_validation.py (probar verificación de content-type PDF, probar verificación de tamaño, probar mensajes de error)

### Implementación para Historia de Usuario 2

- [ ] T036 [#329](https://github.com/JoaquinCaparros711/NotebookUm/issues/329) [P] [US2] Crear modelo HistorialDocumento en app/models/document.py (id, usuario_id, nombre_archivo, extracto_texto, tamanio_bytes, estado, created_at con relaciones a usuario y resúmenes)
- [ ] T037 [#330](https://github.com/JoaquinCaparros711/NotebookUm/issues/330) [P] [US2] Crear modelo Resumen en app/models/summary.py (id, documento_id, contenido, modelo_utilizado, created_at con relación a documento)
- [ ] T038 [#331](https://github.com/JoaquinCaparros711/NotebookUm/issues/331) [US2] Crear migración Alembic para tablas historial_documentos y resumenes
- [ ] T039 [#332](https://github.com/JoaquinCaparros711/NotebookUm/issues/332) [US2] Ejecutar migración: `uv run alembic upgrade head`
- [ ] T040 [#333](https://github.com/JoaquinCaparros711/NotebookUm/issues/333) [US2] Crear app/services/validation.py con funciones de validación de archivos (validate_pdf_content_type, validate_file_size, create_rfc9457_error)
- [ ] T041 [#334](https://github.com/JoaquinCaparros711/NotebookUm/issues/334) [US2] Crear app/services/pdf_service.py con integración Docling (función extract_text_from_pdf con manejo de errores para archivos corruptos)
- [ ] T042 [#335](https://github.com/JoaquinCaparros711/NotebookUm/issues/335) [US2] Crear app/services/summary_service.py con integración OpenAI (initialize_openai_client, detect_language, summarize_text, hierarchical_summarize para textos largos con lógica de reintento)
- [ ] T043 [#336](https://github.com/JoaquinCaparros711/NotebookUm/issues/336) [US2] Configurar Celery en app/services/async_tasks.py (configurar broker, crear process_document_task que llama a pdf_service y summary_service)
- [ ] T044 [#337](https://github.com/JoaquinCaparros711/NotebookUm/issues/337) [US2] Crear blueprint de documentos en app/routes/documents.py con endpoint POST /api/v1/documento/upload (validar archivo, guardar metadata, encolar tarea asíncrona, retornar estado de procesamiento)
- [ ] T045 [#338](https://github.com/JoaquinCaparros711/NotebookUm/issues/338) [US2] Agregar endpoint GET /api/v1/documento/{document_id}/status para consultar estado de procesamiento
- [ ] T046 [#339](https://github.com/JoaquinCaparros711/NotebookUm/issues/339) [US2] Registrar blueprint de documentos en app/__init__.py
- [ ] T047 [#340](https://github.com/JoaquinCaparros711/NotebookUm/issues/340) [US2] Agregar manejo integral de errores para endpoint de carga (error no-PDF, error de límite de tamaño con RFC 9457, errores de procesamiento)
- [ ] T048 [#341](https://github.com/JoaquinCaparros711/NotebookUm/issues/341) [US2] Actualizar modelo HistorialDocumento con campo estado (pending, processing, completed, failed)
- [ ] T049 [#342](https://github.com/JoaquinCaparros711/NotebookUm/issues/342) [US2] Actualizar tarea asíncrona para actualizar campo estado durante el ciclo de vida del procesamiento
- [ ] T050 [#343](https://github.com/JoaquinCaparros711/NotebookUm/issues/343) [US2] Ejecutar todas las pruebas de Historia de Usuario 2: `uv run pytest tests/contract/test_documents_api.py tests/integration/ -v`

**Punto de control**: En este punto, la Historia de Usuario 2 debería ser completamente funcional - los usuarios pueden cargar PDFs y el sistema los procesa asincrónicamente

---

## Fase 5: Historia de Usuario 3 - Consulta de Resúmenes Generados (Prioridad: P2)

**Objetivo**: Permitir a usuarios consultar resúmenes de documentos previamente procesados

**Prueba Independiente**:
- Consultar resumen vía GET /api/v1/summaries/document/{document_id}
- Verificar 404 para documento inexistente
- Verificar mensaje apropiado para documento en procesamiento
- Validar que solo el dueño puede acceder al resumen

### Pruebas para Historia de Usuario 3 (TDD - ESCRIBIR PRIMERO, ASEGURAR QUE FALLEN)

- [ ] T051 [#345](https://github.com/JoaquinCaparros711/NotebookUm/issues/345) [P] [US3] Escribir prueba de contrato para GET /api/v1/summaries/document/{document_id} en tests/contract/test_summaries_api.py (probar recuperación exitosa, probar 404 para documento inexistente, probar 403 para acceso no autorizado, probar estado pendiente para documento en procesamiento)
- [ ] T052 [#346](https://github.com/JoaquinCaparros711/NotebookUm/issues/346) [P] [US3] Escribir prueba de integración para recuperación de resumen en tests/integration/test_summary_retrieval.py (probar flujo completo: cargar → procesar → recuperar resumen)

### Implementación para Historia de Usuario 3

- [ ] T053 [#347](https://github.com/JoaquinCaparros711/NotebookUm/issues/347) [US3] Crear SummaryService en app/services/summary_service.py (métodos get_summary_by_document_id, check_user_ownership)
- [ ] T054 [#348](https://github.com/JoaquinCaparros711/NotebookUm/issues/348) [US3] Escribir pruebas unitarias para SummaryService en tests/unit/test_services.py (probar validación de propiedad, probar recuperación con db mockeada)
- [ ] T055 [#349](https://github.com/JoaquinCaparros711/NotebookUm/issues/349) [US3] Crear blueprint de resúmenes en app/routes/summaries.py con endpoint GET /api/v1/summaries/document/{document_id} (validar propiedad, retornar resumen o error apropiado)
- [ ] T056 [#350](https://github.com/JoaquinCaparros711/NotebookUm/issues/350) [US3] Registrar blueprint de resúmenes en app/__init__.py
- [ ] T057 [#351](https://github.com/JoaquinCaparros711/NotebookUm/issues/351) [US3] Agregar verificación de autorización para confirmar que el usuario es dueño del documento antes de retornar el resumen
- [ ] T058 [#352](https://github.com/JoaquinCaparros711/NotebookUm/issues/352) [US3] Agregar respuesta consciente del estado (retornar mensaje "en procesamiento" si estado no es "completed")
- [ ] T059 [#353](https://github.com/JoaquinCaparros711/NotebookUm/issues/353) [US3] Agregar manejo integral de errores (404 para no encontrado, 403 para no autorizado, mensajes claros para estado de procesamiento)
- [ ] T060 [#354](https://github.com/JoaquinCaparros711/NotebookUm/issues/354) [US3] Ejecutar todas las pruebas de Historia de Usuario 3: `uv run pytest tests/contract/test_summaries_api.py tests/integration/test_summary_retrieval.py -v`

**Punto de control**: En este punto, la Historia de Usuario 3 debería ser completamente funcional - los usuarios pueden recuperar resúmenes de sus documentos procesados

---

## Fase 6: Historia de Usuario 4 - Gestión del Historial de Documentos (Prioridad: P3)

**Objetivo**: Permitir CRUD completo sobre historial de documentos (listar, actualizar metadata, eliminar)

**Prueba Independiente**:
- GET /api/v1/documentos - listar todos los documentos del usuario
- PATCH /api/v1/documento/{id} - actualizar metadata
- DELETE /api/v1/documento/{id} - eliminar documento y sus resúmenes

### Pruebas para Historia de Usuario 4 (TDD - ESCRIBIR PRIMERO, ASEGURAR QUE FALLEN)

- [ ] T061 [#356](https://github.com/JoaquinCaparros711/NotebookUm/issues/356) [P] [US4] Escribir prueba de contrato para GET /api/v1/documentos en tests/contract/test_documents_api.py (probar listar todos los documentos del usuario, probar paginación si está implementada, probar lista vacía para usuario nuevo)
- [ ] T062 [#357](https://github.com/JoaquinCaparros711/NotebookUm/issues/357) [P] [US4] Escribir prueba de contrato para PATCH /api/v1/documento/{id} en tests/contract/test_documents_api.py (probar actualización de metadata, probar 404 para inexistente, probar 403 para no autorizado)
- [ ] T063 [#358](https://github.com/JoaquinCaparros711/NotebookUm/issues/358) [P] [US4] Escribir prueba de contrato para DELETE /api/v1/documento/{id} en tests/contract/test_documents_api.py (probar eliminación exitosa, probar eliminación en cascada de resúmenes, probar 404 para inexistente)

### Implementación para Historia de Usuario 4

- [ ] T064 [#359](https://github.com/JoaquinCaparros711/NotebookUm/issues/359) [US4] Agregar endpoint GET /api/v1/documentos a app/routes/documents.py (retornar todos los documentos del usuario autenticado con soporte de paginación)
- [ ] T065 [#360](https://github.com/JoaquinCaparros711/NotebookUm/issues/360) [US4] Agregar endpoint PATCH /api/v1/documento/{id} a app/routes/documents.py (actualizar metadata del documento, validar propiedad)
- [ ] T066 [#361](https://github.com/JoaquinCaparros711/NotebookUm/issues/361) [US4] Agregar endpoint DELETE /api/v1/documento/{id} a app/routes/documents.py (eliminar documento y cascadear a resúmenes, validar propiedad)
- [ ] T067 [#362](https://github.com/JoaquinCaparros711/NotebookUm/issues/362) [US4] Agregar métodos a DocumentService en app/services/document_service.py (list_user_documents, update_document, delete_document)
- [ ] T068 [#363](https://github.com/JoaquinCaparros711/NotebookUm/issues/363) [US4] Escribir pruebas unitarias para DocumentService en tests/unit/test_services.py
- [ ] T069 [#364](https://github.com/JoaquinCaparros711/NotebookUm/issues/364) [US4] Actualizar modelo Resumen para asegurar eliminación en cascada cuando se elimina un documento
- [ ] T070 [#365](https://github.com/JoaquinCaparros711/NotebookUm/issues/365) [US4] Agregar verificaciones de autorización para todas las operaciones CRUD
- [ ] T071 [#366](https://github.com/JoaquinCaparros711/NotebookUm/issues/366) [US4] Ejecutar todas las pruebas de Historia de Usuario 4: `uv run pytest tests/contract/test_documents_api.py -k "US4" -v`

**Punto de control**: En este punto, la Historia de Usuario 4 debería ser completamente funcional - los usuarios tienen control total sobre su historial de documentos

---

## Fase 7: Historia de Usuario 5 - Gestión del Historial de Preguntas (Prioridad: P3)

**Objetivo**: Permitir CRUD completo sobre historial de preguntas

**Prueba Independiente**:
- POST /api/v1/preguntas - crear nueva pregunta
- GET /api/v1/preguntas - listar preguntas del usuario
- PATCH /api/v1/pregunta/{id} - actualizar pregunta
- DELETE /api/v1/pregunta/{id} - eliminar pregunta

### Pruebas para Historia de Usuario 5 (TDD - ESCRIBIR PRIMERO, ASEGURAR QUE FALLEN)

- [ ] T072 [#368](https://github.com/JoaquinCaparros711/NotebookUm/issues/368) [P] [US5] Escribir prueba de contrato para POST /api/v1/preguntas en tests/contract/test_questions_api.py (probar creación de pregunta, probar validación)
- [ ] T073 [#369](https://github.com/JoaquinCaparros711/NotebookUm/issues/369) [P] [US5] Escribir prueba de contrato para GET /api/v1/preguntas en tests/contract/test_questions_api.py (probar listar preguntas del usuario, probar filtrado por document_id)
- [ ] T074 [#370](https://github.com/JoaquinCaparros711/NotebookUm/issues/370) [P] [US5] Escribir prueba de contrato para PATCH /api/v1/pregunta/{id} en tests/contract/test_questions_api.py (probar actualización de pregunta/respuesta)
- [ ] T075 [#371](https://github.com/JoaquinCaparros711/NotebookUm/issues/371) [P] [US5] Escribir prueba de contrato para DELETE /api/v1/pregunta/{id} en tests/contract/test_questions_api.py (probar eliminación de pregunta)
- [ ] T076 [#372](https://github.com/JoaquinCaparros711/NotebookUm/issues/372) [P] [US5] Escribir prueba unitaria para modelo HistorialPregunta en tests/unit/test_models.py

### Implementación para Historia de Usuario 5

- [ ] T077 [#373](https://github.com/JoaquinCaparros711/NotebookUm/issues/373) [US5] Crear modelo HistorialPregunta en app/models/question.py (id, usuario_id, documento_id, pregunta, respuesta, created_at con relaciones)
- [ ] T078 [#374](https://github.com/JoaquinCaparros711/NotebookUm/issues/374) [US5] Crear migración Alembic para tabla historial_preguntas
- [ ] T079 [#375](https://github.com/JoaquinCaparros711/NotebookUm/issues/375) [US5] Ejecutar migración: `uv run alembic upgrade head`
- [ ] T080 [#376](https://github.com/JoaquinCaparros711/NotebookUm/issues/376) [US5] Crear QuestionService en app/services/question_service.py (métodos crear, listar, actualizar, eliminar)
- [ ] T081 [#377](https://github.com/JoaquinCaparros711/NotebookUm/issues/377) [US5] Escribir pruebas unitarias para QuestionService en tests/unit/test_services.py
- [ ] T082 [#378](https://github.com/JoaquinCaparros711/NotebookUm/issues/378) [US5] Crear blueprint de preguntas en app/routes/questions.py con todos los endpoints CRUD
- [ ] T083 [#379](https://github.com/JoaquinCaparros711/NotebookUm/issues/379) [US5] Registrar blueprint de preguntas en app/__init__.py
- [ ] T084 [#380](https://github.com/JoaquinCaparros711/NotebookUm/issues/380) [US5] Agregar verificaciones de autorización para todas las operaciones de preguntas
- [ ] T085 [#381](https://github.com/JoaquinCaparros711/NotebookUm/issues/381) [US5] Agregar validación para creación de preguntas (campos requeridos)
- [ ] T086 [#382](https://github.com/JoaquinCaparros711/NotebookUm/issues/382) [US5] Ejecutar todas las pruebas de Historia de Usuario 5: `uv run pytest tests/contract/test_questions_api.py -v`

**Punto de control**: En este punto, la Historia de Usuario 5 debería ser completamente funcional - los usuarios pueden gestionar su historial de preguntas

---

## Fase 8: Mejoras y Aspectos Transversales

**Propósito**: Mejoras que afectan a múltiples historias de usuario

- [ ] T087 [#384](https://github.com/JoaquinCaparros711/NotebookUm/issues/384) [P] Agregar logging integral en todos los servicios (app/services/*.py) usando el módulo logging de Python
- [ ] T088 [#385](https://github.com/JoaquinCaparros711/NotebookUm/issues/385) [P] Crear README.md con instrucciones de configuración, documentación de API y ejemplos
- [ ] T089 [#386](https://github.com/JoaquinCaparros711/NotebookUm/issues/386) [P] Crear documentación de API con descripciones de endpoints, ejemplos de request/response
- [ ] T090 [#387](https://github.com/JoaquinCaparros711/NotebookUm/issues/387) Agregar middleware de limitación de tasa para prevenir abuso (Flask-Limiter)
- [ ] T091 [#388](https://github.com/JoaquinCaparros711/NotebookUm/issues/388) Agregar middleware de logging de request/response
- [ ] T092 [#389](https://github.com/JoaquinCaparros711/NotebookUm/issues/389) [P] Ejecutar verificación de cumplimiento PEP 8: `uv run black --check app/ tests/`
- [ ] T093 [#390](https://github.com/JoaquinCaparros711/NotebookUm/issues/390) [P] Ejecutar linting: `uv run flake8 app/ tests/`
- [ ] T094 [#391](https://github.com/JoaquinCaparros711/NotebookUm/issues/391) [P] Ejecutar análisis estático: `uv run pylint app/`
- [ ] T095 [#392](https://github.com/JoaquinCaparros711/NotebookUm/issues/392) Corregir todas las violaciones de PEP 8, flake8 y pylint
- [ ] T096 [#393](https://github.com/JoaquinCaparros711/NotebookUm/issues/393) Ejecutar suite completa de pruebas con cobertura: `uv run pytest --cov=app --cov-report=term-missing`
- [ ] T097 [#394](https://github.com/JoaquinCaparros711/NotebookUm/issues/394) Asegurar cobertura de pruebas >80% para todos los módulos
- [ ] T098 [#395](https://github.com/JoaquinCaparros711/NotebookUm/issues/395) Pruebas de rendimiento: Verificar que 100 cargas concurrentes se manejan sin degradación
- [ ] T099 [#396](https://github.com/JoaquinCaparros711/NotebookUm/issues/396) Auditoría de seguridad: Verificar vulnerabilidades de inyección SQL, validar todas las entradas
- [ ] T100 [#397](https://github.com/JoaquinCaparros711/NotebookUm/issues/397) Crear configuración Docker para despliegue (Dockerfile, docker-compose.yml con MySQL, Redis, Granian)
- [ ] T101 [#398](https://github.com/JoaquinCaparros711/NotebookUm/issues/398) [P] Actualizar .env.example con todas las opciones de configuración finales
- [ ] T102 [#399](https://github.com/JoaquinCaparros711/NotebookUm/issues/399) Escribir documentación de despliegue en docs/deployment.md

---

## Dependencias y Orden de Ejecución

### Dependencias entre Fases

- **Configuración (Fase 1)**: Sin dependencias - puede comenzar inmediatamente
- **Base (Fase 2)**: Depende de completar Configuración - BLOQUEA todas las historias de usuario
- **Historia de Usuario 1 (Fase 3)**: Depende de Base - objetivo MVP
- **Historia de Usuario 2 (Fase 4)**: Depende de Base Y Historia de Usuario 1 (necesita modelo Usuario)
- **Historia de Usuario 3 (Fase 5)**: Depende de Historia de Usuario 2 (necesita que existan documentos y resúmenes)
- **Historia de Usuario 4 (Fase 6)**: Depende de Historia de Usuario 2 (extiende gestión de documentos)
- **Historia de Usuario 5 (Fase 7)**: Depende de Base (puede ejecutarse en paralelo con otras historias pero necesita Usuario y opcionalmente HistorialDocumento)
- **Mejoras (Fase 8)**: Depende de que todas las historias de usuario deseadas estén completas

### Dependencias entre Historias de Usuario

```
Fase 1: Configuración
    ↓
Fase 2: Base (BLOQUEANTE CRÍTICO)
    ↓
    ├─→ Fase 3: Historia de Usuario 1 (Usuarios) 🎯 MVP
    │       ↓
    │   Fase 4: Historia de Usuario 2 (Carga y Procesamiento de Documentos)
    │       ↓
    │       ├─→ Fase 5: Historia de Usuario 3 (Consulta de Resúmenes)
    │       └─→ Fase 6: Historia de Usuario 4 (CRUD de Documentos)
    │
    └─→ Fase 7: Historia de Usuario 5 (CRUD de Preguntas) - Puede ejecutarse en paralelo

    ↓
Fase 8: Mejoras
```

### Dentro de Cada Historia de Usuario

**Flujo TDD (OBLIGATORIO)**:
1. Escribir TODAS las pruebas primero (contrato, integración, unitarias)
2. Ejecutar pruebas - DEBEN FALLAR (rojo)
3. Implementar modelos
4. Implementar servicios
5. Implementar rutas/endpoints
6. Ejecutar pruebas de nuevo - DEBEN PASAR (verde)
7. Refactorizar para calidad (mantener verde)

### Oportunidades de Paralelismo

- **Fase 1 (Configuración)**: T003, T004, T005, T006 pueden ejecutarse en paralelo
- **Fase 2 (Base)**: T009, T010, T012, T015, T016 pueden ejecutarse en paralelo
- **Dentro de Historias de Usuario**: Todas las pruebas marcadas [P] pueden ejecutarse en paralelo, todos los modelos marcados [P] pueden ejecutarse en paralelo
- **Fase 8 (Mejoras)**: T087, T088, T089, T092, T093, T094, T101 pueden ejecutarse en paralelo

---

## Ejemplo de Paralelismo: Historia de Usuario 2

```bash
# Lanzar todas las pruebas de Historia de Usuario 2 juntas (TDD - fase roja):
Tarea T031: "Prueba de contrato para POST /api/v1/documento/upload"
Tarea T032: "Prueba de integración para extracción de PDF"
Tarea T033: "Prueba de integración para generación de resumen"
Tarea T034: "Prueba de integración para procesamiento asíncrono"
Tarea T035: "Prueba unitaria para validación de archivos"

# Lanzar modelos en paralelo (fase verde):
Tarea T036: "Crear modelo HistorialDocumento"
Tarea T037: "Crear modelo Resumen"

# Servicios secuenciales (dependencias):
Tarea T040 → T041 → T042 → T043 (validación → pdf → resumen → asíncrono)
```

---

## Estrategia de Implementación

### MVP Primero (Solo Fases 1-3)

1. Completar Fase 1: Configuración (7 tareas)
2. Completar Fase 2: Base (9 tareas) - BLOQUEANTE CRÍTICO
3. Completar Fase 3: Historia de Usuario 1 (14 tareas) - Los usuarios pueden registrarse y recuperar perfiles
4. **PARAR Y VALIDAR**: Ejecutar todas las pruebas, desplegar localmente, verificar extremo a extremo
5. **DEMO**: Mostrar sistema funcional de registro/recuperación de usuarios

**Entregable MVP**: Sistema básico de gestión de usuarios listo para funcionalidades de procesamiento de documentos

### Entrega Incremental (Recomendada)

1. **Sprint 1**: Configuración + Base + HU1 → Gestión de usuarios funcionando
2. **Sprint 2**: HU2 → Carga y procesamiento de documentos funcionando (¡valor central!)
3. **Sprint 3**: HU3 → Consulta de resúmenes funcionando (flujo central completo)
4. **Sprint 4**: HU4 + HU5 → CRUD completo de documentos y preguntas
5. **Sprint 5**: Mejoras → Sistema listo para producción

### Estrategia de Equipo en Paralelo

Con 3 desarrolladores después de la fase Base:

1. **El equipo completa Fase 1 + 2 juntos** (trabajo de base)
2. Una vez completada la Base:
   - **Desarrollador A**: Historia de Usuario 1 (14 tareas)
   - **Desarrollador B**: Preparar Historia de Usuario 2 (investigar integración Docling/OpenAI)
   - **Desarrollador C**: Historia de Usuario 5 (10 tareas - independiente de HU2-4)
3. Después de completar HU1:
   - **Desarrollador A + B**: Historia de Usuario 2 (20 tareas - historia más grande)
   - **Desarrollador C**: Continuar HU5 o comenzar HU4
4. Secuencial: HU3 → HU4 (ambas dependen de HU2)
5. Paralelo: Tareas de mejoras al final

---

## Comandos de Ejecución de Pruebas

```bash
# Ejecutar todas las pruebas
uv run pytest

# Ejecutar pruebas de historia de usuario específica
uv run pytest tests/contract/test_users_api.py -v          # HU1
uv run pytest tests/contract/test_documents_api.py -v      # HU2, HU4
uv run pytest tests/contract/test_summaries_api.py -v      # HU3
uv run pytest tests/contract/test_questions_api.py -v      # HU5

# Ejecutar con cobertura
uv run pytest --cov=app --cov-report=html --cov-report=term-missing

# Ejecutar solo pruebas de integración
uv run pytest tests/integration/ -v

# Flujo TDD para una funcionalidad
uv run pytest tests/contract/test_users_api.py -v  # Debería FALLAR inicialmente
# ... implementar funcionalidad ...
uv run pytest tests/contract/test_users_api.py -v  # Debería PASAR después de la implementación
```

---

## Notas

- **Tareas [P]** = archivos diferentes, sin dependencias, pueden ejecutarse en paralelo
- **Etiqueta [Historia]** mapea tarea a historia de usuario específica para trazabilidad
- **TDD es OBLIGATORIO**: Las pruebas deben escribirse ANTES de la implementación (requisito de la constitución)
- Cada historia de usuario debe ser completable y testeable de forma independiente
- **Rojo-Verde-Refactorizar**: Verificar que las pruebas fallen → implementar → verificar que las pruebas pasen → refactorizar
- Hacer commit después de cada tarea o grupo lógico
- Detenerse en cualquier punto de control para validar la historia de forma independiente
- Todo el código debe pasar black, flake8 y pylint antes de fusionar
- Objetivo >80% de cobertura de pruebas para todos los módulos

---

## Conteo Total de Tareas

- **Fase 1 (Configuración)**: 7 tareas
- **Fase 2 (Base)**: 9 tareas
- **Fase 3 (Historia de Usuario 1)**: 14 tareas
- **Fase 4 (Historia de Usuario 2)**: 20 tareas
- **Fase 5 (Historia de Usuario 3)**: 10 tareas
- **Fase 6 (Historia de Usuario 4)**: 11 tareas
- **Fase 7 (Historia de Usuario 5)**: 15 tareas
- **Fase 8 (Mejoras)**: 16 tareas

**Total: 102 tareas**

**Alcance MVP**: 30 tareas (Fases 1-3)
**Valor Central**: 60 tareas (Fases 1-5 = MVP + procesamiento de documentos + consulta de resúmenes)
