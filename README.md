# NotebookUM 🚀
> **SaaS-grade Intelligent Document Processing & AI Summarization**

NotebookUM es una plataforma avanzada diseñada para la extracción, análisis y síntesis de documentos técnicos. Inspirada en NotebookLM, esta implementación versión SaaS se enfoca en la eficiencia asincrónica y la precisión en la recuperación de información utilizando modelos de lenguaje de última generación.

---

## 🛠 Features Principales
* **High-Fidelity Extraction:** Procesamiento de documentos complejos mediante la librería **Docling**.
* **AI Summarization:** Generación de resúmenes de alta precisión con el modelo **Nemotron-3 nano 30B**.
* **Async Processing:** Pipeline de procesamiento asincrónico para mejorar el throughput de la plataforma.
* **Smart Storage:** Persistencia de metadatos y resúmenes sin almacenamiento de archivos binarios para mayor seguridad y ligereza.

---

## 🏗 Arquitectura y Estándares de Ingeniería

El proyecto ha sido construido siguiendo principios de arquitectura robusta para garantizar escalabilidad:

### Principios de Diseño
* **SOLID:** Arquitectura orientada a objetos con responsabilidades claras.
* **KISS & DRY:** Código legible, simple y sin duplicación de lógica.
* **YAGNI:** Implementación estricta de requerimientos funcionales.

### Metodologías de Desarrollo
* **TDD (Test Driven Development):** Desarrollo guiado por pruebas para asegurar la integridad del sistema.
* **SDD (Software Design Document):** Especificación técnica previa al desarrollo.
* **SCRUM:** Gestión ágil de proyectos basada en iteraciones y entregables.

### Factor App (First 6 Factors)
1. **Codebase:** Repositorio único y versionado.
2. **Dependencias:** Aislamiento y gestión mediante `uv`.
3. **Config:** Configuración estricta a través de variables de entorno.
4. **Backing services:** Servicios de terceros (MySQL) tratados como recursos adjuntos.
5. **Build, release, run:** Separación total de las etapas de despliegue.
6. **Processes:** Aplicación ejecutada como procesos sin estado (stateless).

---

## 💻 Tech Stack

| Componente | Tecnología |
| :--- | :--- |
| **Language** | Python (PEP8 Standard) |
| **Framework** | Flask (Async support) |
| **Package Manager** | [uv](https://github.com/astral-sh/uv) |
| **Database** | MySQL |
| **NLP/Parsing** | Docling |
| **LLM Model** | Nemotron-3 nano 30B |

---

## 📑 Especificación Técnica (v1)

### Estructura de Base de Datos
Las tablas están normalizadas, nombradas en minúsculas y en plural:
* `usuarios`: Gestión de perfiles y credenciales.
* `historial_documentos`: Auditoría de archivos procesados por el usuario.
* `historial_preguntas`: Registro de interacciones con el modelo de IA.
* `resumenes`: Almacenamiento indexado de los resultados del modelo.

### API Endpoints
Todos los recursos están versionados bajo el prefijo `/api/v1/`.

| Método | Endpoint | Funcionalidad |
| :--- | :--- | :--- |
| `POST` | `/api/v1/users` | Registro de nuevos usuarios. |
| `GET` | `/api/v1/users/{id}` | Recuperación de perfil de usuario. |
| `POST` | `/api/v1/documento/upload` | Carga asincrónica, extracción y resumen. |
| `GET` | `/api/v1/summaries/document/{id}` | Consulta de resumen por ID de documento. |

#### Reglas de Validación y Negocio:
1. **Validación de Archivos:** Solo se admiten archivos con `contentType: application/pdf`. Cualquier otro formato devuelve un error `400 Bad Request`.
2. **Restricción de Tamaño:** Límite máximo de **25MB**. El incumplimiento genera un error `400` siguiendo el estándar **RFC 9457**.
3. **Seguridad de Datos:** El servidor **no almacena el archivo físico**; procesa la información en memoria/stream y persiste únicamente el texto extraído y el resumen.

---

## 🚀 Instalación y Configuración

### Requisitos
* Python 3.12+
* Instancia de MySQL activa.
* `uv` (Fast Python package installer).

### Configuración del Entorno
1. Instalar dependencias:
   ```bash
   uv sync
2. Configurar el archivo .env:

    ```bash
    FLASK_APP=src/app.py
    DATABASE_URL=mysql://user:password@localhost/notebookum
    MODEL_ID=nemotron-3-nano-30B
    ```
3. Ejecutar migraciones de base de datos e iniciar servidor:
    uv run flask run

## 📌 Convenciones del Proyecto
***Programación***: Todo el código fuente (clases, variables, comentarios técnicos) se encuentra en Inglés.

***Documentación***: El README, manuales y especificaciones funcionales se mantienen en Español.