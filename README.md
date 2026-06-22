# 🏛️ Proyecto NotebookUm: Monolito de Referencia y Constitución

![Python](https://img.shields.io/badge/Python-3.12-blue.svg?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-darkgreen.svg?style=flat-square&logo=flask&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.3+-green.svg?style=flat-square&logo=celery&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-blue.svg?style=flat-square&logo=mysql&logoColor=white)

Este repositorio contiene la arquitectura **monolítica original de referencia** de la plataforma **NotebookUm**. Funciona como base histórica, marco de diseño y guía constitucional del ecosistema de microservicios.

---

## 📋 Responsabilidades y Estado del Repositorio

- **Base de Referencia:** Define los modelos de datos, flujos de servicios y pruebas originales antes de la distribución en la malla de microservicios.
- **Constitución Técnica:** Establece las reglas de diseño (KISS, DRY, YAGNI, SOLID) y metodologías obligatorias que rigen a todos los repositorios derivados.
- **Lógica Asíncrona Celery:** Implementación original del procesamiento en segundo plano con Celery + Redis para tareas costosas de extracción.

---

## ⚡ Características y Principios Arquitectónicos

Todo avance propuesto en el código o arquitectura debe ampararse en los pilares formales descritos en `constitution.md`:

- **KISS (Keep It Simple, Stupid):** Soluciones simples y directas; si la complejidad es necesaria, se documenta la alternativa simple como inválida.
- **DRY (Don't Repeat Yourself):** Evitar duplicaciones en favor de una abstracción unificada y mantenible.
- **YAGNI (You Aren't Gonna Need It):** Evitar infraestructura hipotética; implementación condicionada estrictamente a la especificación activa (`spec.md`).
- **SOLID:** Diseño orientado a objetos robusto y extensible.

### Metodologías Obligatorias

- **TDD (Test-Driven Development):** Escribir los tests unitarios en `/tests` antes de tocar una sola línea de `/app`. El ciclo *Rojo-Verde-Refactor* rige cada tarea.
- **SDD (Specification-Driven Development):** Todas las implementaciones provienen estrictamente de las historias de usuario del directorio `/specs`.
- **12-Factor App:** Cumplimiento de los principios cloud-native (variables de entorno, backing services, procesos sin estado).

---

## 📁 Estructura del Proyecto

```text
NotebookUm/
├── app/             # Lógica de negocio monolítica (Flask, modelos, servicios, views)
├── specs/           # Planificación de arquitectura e historias de usuario (SDD)
├── tests/           # Fixtures de pruebas, validaciones y contratos 
├── migrations/      # Historial de cambios de base de datos (Alembic)
└── main.py          # Entrypoint ASGI mediante el servidor Granian
```

---

## 🤖 Guía de Commits para Agentes de IA

Antes de realizar cualquier commit, la IA debe validar los cambios contra la constitución de NotebookUM y asegurarse de seguir este estándar de mensajes.

### Estándar de Mensajes (Conventional Commits)

Todos los commits deben seguir la estructura: `<type>(<scope>): <description>`

| Tipo | Descripción | Ejemplo |
| :--- | :--- | :--- |
| **feat** | Nueva funcionalidad | `feat(api): add 25MB file size validation` |
| **fix** | Corrección de un bug | `fix(db): resolve users table migration error` |
| **refactor** | Mejora interna sin cambiar comportamiento | `refactor: extract docling parsing to service layer` |
| **chore** | Tareas rutinarias o dependencias | `chore(deps): update flask via uv` |
| **perf** | Optimización de velocidad o recursos | `perf(ai): optimize nemotron inference latency` |
| **docs** | Cambios en la documentación | `docs: update api endpoint reference` |

### Reglas de Mensajes:
1. El mensaje del commit debe redactarse obligatoriamente en **Inglés**.
2. Usar modo imperativo (ej. `add`, no `added` ni `adds`).
3. No utilizar formato markdown en el mensaje del commit (solo texto plano).

---

## 🚀 Ejecución y Despliegue Local

### Requisitos Previos

- Python 3.12 con el gestor de dependencias `uv` instalado.
- Instancia activa de MySQL y Redis.

### Instalación Rápida

1. Instalar las dependencias del proyecto:
   ```bash
   uv sync
   ```

2. Configurar el archivo `.env` en la raíz con las credenciales de base de datos y la clave de la API de OpenAI.

3. Ejecutar el servidor web Granian:
   ```bash
   uv run granian --interface asgi main:app --port 5000
   ```

### Despliegue Completo con Docker Compose

El directorio `docker/` contiene las recetas necesarias para levantar de manera coordinada todo el stack tecnológico:

```bash
# Iniciar servicios
docker compose up -d
```
Esto levantará el proxy inverso Traefik, la base de datos MySQL, el bróker Redis y el backend monolítico de Flask.