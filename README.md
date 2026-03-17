# 📓 NotebookUm

> Sistema de extracción y análisis profundo de documentos PDF utilizando un flujo de trabajo agéntico con modelos locales y optimización de Markdown.

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Backend](https://img.shields.io/badge/backend-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Package Manager](https://img.shields.io/badge/pkg%20manager-uv-purple.svg)](https://github.com/astral-sh/uv)

## 🛠 Stack Tecnológico

- **Core:** Python 3.12+ con `uv`
- **Backend:** Flask
- **Procesamiento:** Docling (PDF a MD) & DeepSeek OCR (Fallback)
- **Modelos (Ollama/vLLM):** 
  - Gemma3-4b (Summarization)
  - Nemotron-3-nano-30b (Q&A)
  - GPT-OSS-20b (Deep Research)
- **Vector DB:** FAISS / LanceDB

---

## 🚀 Configuración del Entorno

### Requisitos Previos

Asegúrate de tener instalado [uv](https://github.com/astral-sh/uv) en tu sistema.

### Instalación Rápida

Inicializa y configura el entorno con `uv`:

```bash
uv init
uv add flask docling faiss-cpu sentence-transformers ollama
```

---

## 💻 Uso Básico

**Correr la aplicación:**
```bash
uv run flask --app main run --debug
```

**Correr los tests:**
```bash
uv run pytest tests/ -v
```

**Agregar nuevas dependencias:**
```bash
uv add <paquete>
```

---

## 📚 Documentación Adicional

- [**Agentes (AGENTS.md)**](./AGENTS.md): Definición detallada del set de agentes, sus objetivos y razonamiento.
- [**Habilidades (SKILLS.md)**](./SKILLS.md): Capacidades técnicas y herramientas integradas en el pipeline.
