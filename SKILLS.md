# ⚙️ Capacidades del Sistema (Skills)

A continuación se detallan las habilidades principales y las herramientas subyacentes que construyen el pipeline de procesamiento de **NotebookUm**.

---

### 1️⃣ Skill 1: Smart Markdown Extraction
- **Herramienta:** `docling`
- **Lógica:** Intenta la extracción estructural de tablas y headers. Si la confianza del texto es < 70%, activa el motor de `DeepSeek OCR` como método de respaldo.

### 2️⃣ Skill 2: Contextual Vector Retrieval
- **Herramienta:** `FAISS` + `SentenceTransformers`
- **Lógica:** Indexa el Markdown generado. Permite que el agente Interrogator busque fragmentos específicos para responder con precisión (RAG).

### 3️⃣ Skill 3: Asynchronous Pipeline
- **Herramienta:** `Python ThreadPoolExecutor`
- **Lógica:** Ejecuta las llamadas a los tres modelos simultáneamente después de la fase de extracción para minimizar el tiempo de espera del usuario.

### 4️⃣ Skill 4: Markdown Formatting
- **Herramienta:** Custom Python Script
- **Lógica:** Limpia y normaliza el output de los modelos para asegurar que el documento final sea un archivo Markdown perfectamente válido para cualquier lector.