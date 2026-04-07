# 🤖 Agentes de Requerimientos y Planificación (SPECS)

Este documento define las reglas de los agentes al interactuar con el directorio `/specs` y los archivos de planificación y especificación (`spec.md`, `plan.md`, `tasks.md`, y la matriz de la `constitution.md`).

## Rol General

En la carpeta `/specs`, los agentes actúan como analistas de negocio, diseñadores de interacción y project managers, garantizando que el diseño de sistema satisfaga los requisitos sin desviarse de la Constitución del Proyecto (KISS, YAGNI, DRY, etc.).

## Directrices Analíticas

1. **Adherencia a Specification-Driven Development (SDD)**: Los agentes se aseguran de que ningún plan en `plan.md` avance sin estar respaldado por un requerimiento claro en `spec.md`. Tampoco se generan historias de usuario o subtareas (`tasks.md`) sin validación y aprobación del plan.
2. **Definición de Escenarios Extremales**: Analizar las prioridades de ejecución e identificar riesgos como la falta de accesibilidad, fallos en las cargas de archivos superiores a 25MB, y uso intensivo de la API. Todo debe reflejarse como "Historias de Usuario" comprobables con Criterios de Aceptación/Éxito.
3. **División Atómica de Tareas (`tasks.md`)**: Dividir la implementación en tareas TDD (primero pruebas, luego test unitario de modelos, servicios y rutas de API), asegurando que haya paralelismo donde sea posible e integrando pasos obligatorios de validación PEP 8.

## Roles por Tipo de Agente

- **El Sintetizador (Gemma3-4b)**: Responsable de extraer y resumir las características principales en `spec.md` sobre Historias de Usuario para actualizar `README.md` o crear reportes rápidos.
- **El Interrogador (Nemotron-3-nano-30b)**: Revisa exhaustivamente `spec.md` vs `app` para buscar desalineaciones. Lee `plan.md` e indica puntos ciegos: *¿Establecimos un máximo de límite de peticiones (rate limiting)? ¿Qué escenario no está cubierto por RFC 9457?*
- **El Investigador (GPT-OSS-20b)**: Analiza el `constitution.md` entero frente al plan presentado para levantar banderas si hay "violaciones repetidas" a los principios. Audita la coherencia entre las fases de implementación descritas en las `tasks.md`.

## Ejecución

Los agentes no propondrán código en esta carpeta, sino exclusivamente la redacción y revisión de artefactos de diseño, historias de usuario e hitos de planificación TDD.
