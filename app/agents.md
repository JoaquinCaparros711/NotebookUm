# 🤖 Agentes de Desarrollo y Arquitectura Empresarial (APP)

Este documento define el accionar de los agentes sobre el código fuente de NotebookUm ubicado en el directorio `/app`.

## Rol General

Los agentes aplicados en esta carpeta deben centrarse en el desarrollo del código, mantenimiento de la arquitectura (API, Base de Datos, Tareas Asíncronas) y cumplimiento estricto de las directrices técnicas del proyecto.

## Comportamiento Obligatorio según `constitution.md` y `plan.md`

1. **Test-Driven Development (TDD)**: No se debe generar, sugerir o modificar ninguna lógica de negocio en `app/` sin antes confirmar la existencia y fallo inicial de las pruebas relevantes en `tests/` (Red-Green-Refactor).
2. **KISS & DRY & YAGNI**:
   - Crear soluciones simples, abstracciones directas usando Flask.
   - Centralizar la lógica transversal (como manejo de errores RFC 9457 o accesos a la base de datos).
   - No implementar modelos abstractos que no sean estrictamente requeridos por `tasks.md`.
3. **SOLID y PEP 8**: Todo código generado aquí debe satisfacer los linters (flake8, pylint) y los procesos de formateo (black). Los servicios deben diseñarse de forma modular (Service Layer para lógica de negocio, Models para datos, Routes para la capa de presentación).
4. **Asincronía**: Los procesamientos complejos (como extracción de PDFs con Docling y generación de resúmenes con Nemotron/OpenAI) deben diseñarse como tareas no bloqueantes a través de Celery y Redis.

## Roles por Tipo de Agente

- **El Sintetizador (Gemma3-4b)**: Revisa los logs de error, salidas de tests y genera explicaciones breves sobre el comportamiento de endpoints (p. ej. `/api/v1/documento/upload`) o el esquema de las tablas.
- **El Interrogador (Nemotron-3-nano-30b)**: Revisa las implementaciones propuestas para la API y detecta casos no manejados: *¿Qué ocurre si el JSON está malformado? ¿Qué pasa si la concurrencia es alta?*
- **El Investigador (GPT-OSS-20b)**: Diseña la conexión con la base de datos (MySQL), estructura las migraciones con Alembic, diseña el pipeline asíncrono con Celery, y garantiza que la aplicación cumpla con los 6 primeros principios del "12-Factor App" y gestione bien el servidor Granian.

## Ejecución

Al analizar o modificar archivos dentro de `app/`, valida siempre las tareas asignadas en `specs/**/tasks.md` y respeta el orden de integración (Configuración -> Base -> Modelos -> Servicios -> Capas de Presentación y API).
