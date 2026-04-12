# Proyecto NotebookUm: Sistema de API para Gestión de Documentos

**A tener en cuenta:** Diseño del sistema, tareas y pruebas en Inglés técnico (por convención de código) y documentación principal en Español.

**NotebookUm** es una API RESTful corporativa diseñada para la gestión asíncrona de archivos PDF. Permite a los usuarios crear cuentas, extraer inteligentemente texto de PDFs, generar resúmenes mediante IA de última generación y almacenar historiales interactivos para posteriores consultas y Q&A.

## 🚀 Funcionalidades Principales

1. **Gestión de Cuentas**: Creación e individualización del historial de cada usuario (`/api/v1/users`).
2. **Extracción y Procesamiento**: Uso de la librería **Docling** para extracción precisa de texto en documentos PDF (hasta 25MB).
3. **Resúmenes con IA**: Generación de resúmenes asíncronos mediante modelos de lenguaje (OpenAI / Nemotron-3 nano 30B).
4. **Almacenamiento Histórico**: Historial de documentos cargados, sus resúmenes y preguntas de seguimiento (Q&A) guardados permanentemente.

## 🛠️ Stack Tecnológico

- **Metodología**: SCRUM, iterativo en sprints, focalizado en historias de usuario.
- **Lenguaje**: Python 3.12 (Apego obligatorio a PEP 8).
- **Framework Web**: Flask (API RESTful sincrónica para endpoints).
- **Servicio Asíncrono**: Celery y Redis (para no bloquear cargas y procesamiento pesado).
- **Base de Datos**: MySQL (Consultas estructuradas a través de SQLAlchemy y migraciones por Alembic).
- **Dependencias**: Gestor ultra-rápido `uv`.
- **Servidor ASGI**: Granian (para máximo rendimiento).

## 📜 Principios Arquitectónicos (`constitution.md`)

Todo avance propuesto en el código o arquitectura debe ampararse en estos pilares formales:

- **KISS (Keep It Simple, Stupid)**: Soluciones simples y directas; si la complejidad es necesaria, se documenta la alternativa simple como inválida.
- **DRY (Don't Repeat Yourself)**: Evitar duplicaciones en favor de una abstracción unificada y mantenible.
- **YAGNI (You Aren't Gonna Need It)**: Evitar infraestructura hipotética; implementación condicionada estrictamente al `spec.md`.
- **SOLID**: Diseño orientado a objetos robusto y extensible.

## 🔄 Metodologías Obligatorias

- **TDD (Test-Driven Development)**: *NO NEGOCIABLE*. Los desarrolladores y agentes escriben el test en `/tests` antes de tocar una sola línea de `/app`. El ciclo *Rojo-Verde-Refactor* rige cada tarea.
- **SDD (Specification-Driven Development)**: Todas las implementaciones provienen de las historias de usuario de `/specs`.
- **12-Factor App**: Se requiere cumplimiento estricto de primeros 6 factores:
  1. Un código base.
  2. Dependencias aisladas.
  3. Configuración en entorno (variables `.env`).
  4. Backing services conectados como recursos.
  5. Separación Build, release, run.
  6. Procesos sin estado.

## 🤖 Arquitectura Multimodelo de Agentes

El repositorio aprovecha un flujo jerárquico de IA (Definidos en `AGENTS.md`) aplicado para automatizar tareas, validar diseño y analizar impacto:
- **Sintetizador (Gemma3-4b)**: Síntesis de lógica.
- **Interrogador (Nemotron-3-nano-30b)**: Casos de QA y límites.
- **Investigador (GPT-OSS-20b)**: Análisis profundo y validación 12-factor, dependencias y refactors asíncronos.

**Nota:** Existen reglas de agente dedicadas para desarrollo en `/app/agents.md`, planificación en `/specs/agents.md`, y pruebas en `/tests/agents.md`.

## ⚙️ Estructura del Proxecto

```text
NotebookUm/
├── app/             # Lógica de negocio (Flask, modelos, servicios)
├── specs/           # Planificación de arquitectura e historias (SDD)
├── tests/           # Fixtures de pruebas, validaciones y contratos 
├── migrations/      # Historial de cambios de base de datos
└── main.py          # Entrypoint de Granian
```

Para instrucciones detalladas sobre las fases de implementación, pruebas en paralelo y estrategias MVP, consulte `specs/001-api-gestion-documentos/tasks.md` y `specs/001-api-gestion-documentos/plan.md`.

# 🤖 Instrucciones para IA (Commit Guidelines)

> **IMPORTANTE**: Antes de realizar cualquier commit, la IA debe validar los cambios contra la "Constitución de NotebookUM" y asegurarse de seguir este estándar de mensajes.

## Estándar de Mensajes (Conventional Commits)

Todos los commits deben seguir la estructura: `<type>(<scope>): <description>`

### Tipos Permitidos
* **feat**: (Nueva Función) Añade una nueva característica.
    * *Ejemplo*: `feat(api): add 25MB file size validation`
* **fix**: (Corrección) Resuelve un error o comportamiento inesperado.
    * *Ejemplo*: `fix(db): resolve users table migration error`
* **refactor**: (Estructura) Mejora el código sin cambiar su lógica externa.
    * *Ejemplo*: `refactor: extract docling parsing to service layer`
* **chore**: (Mantenimiento) Tareas rutinarias o de dependencias.
    * *Ejemplo*: `chore(deps): update flask via uv`
* **perf**: (Rendimiento) Optimización de velocidad o recursos.
    * *Ejemplo*: `perf(ai): optimize nemotron inference latency`
* **docs**: (Documentación) Cambios en README o manuales.
    * *Ejemplo*: `docs: update api endpoint reference`

## Reglas de Ejecución para la IA
1.  **Language**: El mensaje del commit DEBE ser en **Inglés**.
2.  **Mood**: Usar modo imperativo (ej. `add`, no `added` ni `adds`).
3.  **Scope**: El "scope" entre paréntesis es opcional pero recomendado (api, db, ai, auth).
4.  **No Markdown**: No usar formato markdown dentro del mensaje del commit (solo texto plano).