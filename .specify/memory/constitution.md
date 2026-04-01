<!--
SYNC IMPACT REPORT:
Version: 0.0.0 → 1.0.0
Modified Principles: Initial creation - all principles established from README.md
Added Sections: All sections (Core Principles, Technology Stack, Development Methodology, Governance)
Removed Sections: None
Templates Status:
  ✅ plan-template.md: Constitution Check section aligns with 8 core principles
  ✅ spec-template.md: User Scenarios & Testing aligns with TDD/SDD methodology
  ✅ tasks-template.md: Test-first workflow aligns with TDD principle
Follow-up TODOs: None - all placeholders filled
-->

# Constitución de NotebookUM

## Principios Básicos

### I. KISS (Keep It Simple, Stupid - Mantenlo Simple, Estúpido)
La simplicidad es primordial en todas las decisiones de diseño e implementación. Las soluciones DEBEN ser lo más simples posible, pero no más simples de lo necesario. Las soluciones complejas requieren una justificación explícita y las alternativas más simples deben documentarse como rechazadas.

**Justificación**: La complejidad aumenta la carga de mantenimiento, introduce errores y reduce la velocidad del equipo. El código simple es más fácil de probar, depurar y extender.

### II. DRY (Don't Repeat Yourself - No te Repitas)
Cada pieza de conocimiento DEBE tener una representación única, inequívoca y autorizada dentro del sistema. La duplicación de código está prohibida, excepto cuando la abstracción introduciría un acoplamiento inapropiado.

**Justificación**: La duplicación conduce a la inconsistencia, aumenta el costo de mantenimiento y crea oportunidades para errores cuando la lógica necesita cambiar.

### III. YAGNI (You Aren't Gonna Need It - No lo vas a Necesitar)
Las funcionalidades y abstracciones NO DEBEN implementarse hasta que sean realmente necesarias. La generalidad especulativa está prohibida. Construye para los requisitos actuales, no para necesidades futuras hipotéticas.

**Justificación**: La optimización prematura y la sobre-ingeniería desperdician recursos y agregan una complejidad que podría nunca utilizarse.

### IV. Principios SOLID
Todo el código orientado a objetos DEBE adherirse a los principios SOLID:
- **Responsabilidad Única (Single Responsibility)**: Cada clase/módulo tiene una sola razón para cambiar.
- **Abierto/Cerrado (Open/Closed)**: Abierto para la extensión, cerrado para la modificación.
- **Sustitución de Liskov (Liskov Substitution)**: Los subtipos deben ser sustituibles por sus tipos base.
- **Segregación de Interfaces (Interface Segregation)**: Los clientes no deben depender de interfaces que no utilizan.
- **Inversión de Dependencias (Dependency Inversion)**: Depender de abstracciones, no de concreciones.

**Justificación**: Los principios SOLID crean arquitecturas de código mantenibles, flexibles y testeables que escalan con la complejidad.

### V. Desarrollo Guiado por Pruebas - TDD (NO NEGOCIABLE)
El TDD es obligatorio para todo el código de producción. DEBE seguirse el ciclo red-green-refactor (rojo-verde-refactorizar):
1. Escribir primero una prueba que falle.
2. Escribir el código mínimo para que la prueba pase.
3. Refactorizar manteniendo las pruebas en verde.

No se puede escribir código de producción sin una prueba fallida que lo requiera.

**Justificación**: El TDD garantiza la testabilidad, impulsa un mejor diseño, proporciona documentación viva y crea una red de seguridad para la refactorización.

### VI. Desarrollo Guiado por Especificaciones (SDD)
Todas las funcionalidades DEBEN comenzar con una especificación escrita antes de la implementación. Las especificaciones definen escenarios de usuario, criterios de aceptación y métricas de éxito. La implementación no puede comenzar hasta que la especificación sea aprobada.

**Justificación**: Las especificaciones claras evitan malentendidos, permiten una mejor estimación y proporcionan criterios de éxito medibles.

### VII. Cumplimiento de PEP 8 (Estilo de Código Python)
Todo el código Python DEBE ajustarse a las guías de estilo PEP 8. El formateo del código y las comprobaciones de estilo DEBEN pasar antes de la revisión del código (code review). Utiliza herramientas automatizadas (black, flake8, pylint) para forzar el cumplimiento.

**Justificación**: Un estilo de código consistente mejora la legibilidad, reduce la carga cognitiva y facilita la colaboración en todo el equipo.

### VIII. Metodología 12-Factor App (Primeros Seis Factores)
La aplicación DEBE adherirse a los primeros seis factores de la metodología 12-Factor App:
- **I. Código Base (Codebase)**: Un código base rastreado en control de versiones, muchos despliegues.
- **II. Dependencias**: Declarar y aislar explícitamente las dependencias (usando uv).
- **III. Configuraciones (Config)**: Almacenar la configuración en variables de entorno.
- **IV. Servicios de Respaldo (Backing Services)**: Tratar los servicios de respaldo como recursos adjuntos (MySQL).
- **V. Construcción, Despliegue, Ejecución (Build, Release, Run)**: Separar estrictamente las etapas de construcción y ejecución.
- **VI. Procesos**: Ejecutar la aplicación como uno o más procesos sin estado (stateless).

**Justificación**: Los principios de 12-Factor crean aplicaciones portátiles y escalables adecuadas para las plataformas de despliegue modernas.

## Stack Tecnológico

### Tecnologías Requeridas
- **Lenguaje**: Python (cumplimiento de PEP 8)
- **Framework**: Flask para la API web
- **Gestión de Dependencias**: uv para la gestión de paquetes y entornos
- **Base de Datos**: MySQL para almacenamiento persistente
- **Procesamiento de Documentos**: Librería Docling para la extracción de texto de archivos
- **Modelo de IA**: Nemotron-3 nano 30B para el resumen de texto

### Restricciones Tecnológicas
- Todo el código Python DEBE seguir las guías de estilo PEP 8.
- Las dependencias DEBEN gestionarse a través de uv (no solo pip).
- Las interacciones con la base de datos DEBEN usar consultas parametrizadas para prevenir la inyección SQL.
- Los endpoints de la API DEBEN seguir las convenciones RESTful.
- La configuración específica del entorno DEBE usar variables de entorno (12-Factor Config).

## Metodología de Desarrollo

### Gestión de Proyecto
- **Metodología**: Marco de trabajo SCRUM para el desarrollo iterativo.
- Se DEBEN seguir los Sprints, standups diarios, planificación de sprint y retrospectivas.
- Las historias de usuario DEBEN estar priorizadas y ser independientemente testeables.
- El trabajo en curso (Work-in-progress) DEBE ser visible y estar rastreado.

### Flujo de Trabajo de Desarrollo
1. **Especificación**: Crear `spec.md` con escenarios de usuario y criterios de aceptación.
2. **Planificación**: Generar un plan de implementación con diseño técnico.
3. **Diseño de Pruebas**: Escribir pruebas fallidas (fase roja de TDD).
4. **Implementación**: Escribir el código mínimo para pasar las pruebas (fase verde).
5. **Refactorización**: Mejorar el código manteniendo la cobertura de pruebas (fase de refactorización).
6. **Revisión**: La revisión de código verifica el cumplimiento de la constitución.
7. **Integración**: Fusionar (merge) solo después de que las pruebas pasen y la revisión apruebe.

### Filtros de Calidad (Quality Gates)
- Todas las pruebas DEBEN pasar antes de la fusión.
- La cobertura de código DEBE mantenerse o mejorarse.
- Se DEBE verificar el cumplimiento de PEP 8.
- Se DEBE comprobar el cumplimiento de la constitución.
- No se permite código comentado en las ramas de producción.
- No se permiten credenciales o configuraciones "hardcodeadas" (escritas directamente en el código).

## Gobernanza

Esta constitución prevalece sobre todas las demás prácticas y preferencias de desarrollo. Todas las revisiones de código, decisiones de diseño e implementaciones DEBEN verificar el cumplimiento de estos principios.

### Proceso de Enmienda
- Las enmiendas requieren la documentación de la justificación y los sistemas afectados.
- El número de versión DEBE incrementarse de acuerdo con el versionado semántico.
- Los cambios disruptivos (Breaking changes) requieren un aumento de versión MAYOR (MAJOR).
- Los nuevos principios requieren un aumento de versión MENOR (MINOR).
- Las aclaraciones requieren un aumento de versión de PARCHE (PATCH).
- Todos los miembros del equipo DEBEN ser notificados de las enmiendas.

### Cumplimiento
- Todos los Pull Requests (PRs) DEBEN incluir la verificación de cumplimiento de la constitución.
- Las violaciones DEBEN justificarse por escrito con las alternativas más simples rechazadas.
- Las violaciones repetidas requieren una revisión arquitectónica.
- Se requiere una revisión de la constitución trimestralmente o cuando los principios entren en conflicto.

### Control de Versiones
- Esta constitución está controlada por versiones junto con el código.
- Los cambios siguen el proceso estándar de PR con requisitos de revisión mejorados.
- Las versiones históricas se preservan para referencia.

**Versión**: 1.0.0 | **Ratificada**: 2026-03-31 | **Última Enmienda**: 2026-03-31