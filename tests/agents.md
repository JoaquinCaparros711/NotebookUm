# 🤖 Agentes de Calidad y Testing (TESTS)

Este documento instruye a los agentes sobre su funcionamiento dentro de la carpeta `/tests`, estableciendo reglas fundamentales para el diseño de pruebas automatizadas en NotebookUm.

## Rol General

La meta principal en este directorio es asegurar un robusto Test-Driven Development (TDD) para validar todo el código en el que opere el sistema (desde la capa de base de datos hasta los contratos de la API), maximizando la cobertura con integraciones `pytest` y `pytest-flask`.

## Directrices de Desarrollo de Pruebas

1. **Constitución de TDD (Rojo-Verde-Refactor)**: Los agentes tienen estrictamente prohibido generar código fuente en `app/` para un caso de uso sin primero haber establecido una prueba fallida en `tests/`.
2. **Jerarquía y Aislamiento**:
   - `/tests/unit`: Mocking exhaustivo. Los servicios externos (OpenAI, base de datos) NUNCA deben lanzarse de forma real aquí.
   - `/tests/integration`: Validar integraciones cruzadas reales, como el comportamiento asíncrono con Celery en la carga de PDFs y extracción con Docling.
   - `/tests/contract`: Validar respuestas exactas de API (códigos de estado, formatos RFC 9457 para errores 400s y esquemas JSON).
3. **Casos Límite por SDD**: Los agentes deben extraer los casos extremos (archivos inválidos, >25MB, caídas asíncronas) desde `spec.md` y forzarlos como tests obligatorios antes de darlos como válidos en `tasks.md`.

## Roles por Tipo de Agente

- **El Sintetizador (Gemma3-4b)**: Genera resúmenes de cobertura (`pytest --cov`) e identifica qué funciones particulares del código o endpoints restan probar tras una iteración.
- **El Interrogador (Nemotron-3-nano-30b)**: Revisa el diseño del test para inyectar fallos. *¿Se está probando que pasa si la base de datos devuelve timeout? ¿Se está confirmando en el mock qué sucede si OpenAI envía un error 500?*
- **El Investigador (GPT-OSS-20b)**: Construye los fixtures complejos de `pytest` (como usuarios autenticados o documentos PDF falsos válidos) y el mock del entorno entero en las pruebas de integración asíncrona. 

## Reglas de Control de Calidad

Los agentes se detendrán en los bloqueos (`PARAR Y VALIDAR`) especificados en los flujos de tareas si los tests detectan caídas en la cobertura del 80% o incumplen dictámenes PEP 8 (reportados por `flake8` y `black`).
