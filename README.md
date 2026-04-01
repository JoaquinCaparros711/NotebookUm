A tener en cuenta: Programación en Ingles y documentación en Español

# Proyecto NotebookUM
Es un proyecto que tiene como funcionalidades: 
•⁠  ⁠extraer texto de archivos, utilizando la libreria Docling, 
•⁠  ⁠El texto extraído debe ser pasado al modelo Nemotron-3 nano 30B para ser resumido.
•⁠  ⁠El texto resumido va a ser guardado en base de datos.
## Tecnologías utilizadas en el proyecto
Se utilizarán las siguientes tecnologías:
•⁠  ⁠Metodologia de gestion de proyecto: SCRUM
•⁠  ⁠Lenguaje: Python (Usar PEP8)
•⁠  Framework: Flask
•⁠  ⁠Herramienta de dependencia: uv
•⁠  ⁠Base de datos: MySql
## Principios
Se aplicarán los siguientes principios:
•⁠  ⁠KISS
•⁠  ⁠DRY
•⁠  ⁠YAGNI
•⁠  ⁠SOLID
## Metodologías
•⁠  ⁠TDD
•⁠  ⁠SDD
## Factor App
Se aplicará los seis primeros factores:
•⁠  ⁠Codebase
•⁠  ⁠Dependencias
•⁠  ⁠Config
•⁠  ⁠Backing services
•⁠  ⁠Build, release, run
•⁠  ⁠Processes
## Diagramas 
## Configuración de las tablas en base de datos
## Funcionalidad de la base de datos
## Especificación Técnica (v1)
•⁠  ⁠los endpoint deben de empezar con /api/v1/
•⁠  ⁠deben crearse las siguentes tablas: Usuario, Historial de documentos subidos por usuarios, Historial de preguntas, Resumenes (los nombres de tablas en plural y en minuscula)
•⁠  ⁠Cada tabla debe de tener su CRUD, 
•⁠  ⁠Los usuarios envian los archivos al endpoint /api/v1/documento/upload con el metodo POST, debe de ser asincronico. El endpoint debe: Permite subir archivo, Extraer texto, Generar resumen y Guardar información. No debe de guardar el archiv
•⁠  ⁠Los archivos validos deben ser contentType: application/pdf y deben ser validados en el servidor, si no son de pdf se mandara json un error 400
•⁠  ⁠Los archivos no deben superar los 25MB, si superan ese tamaño se mandara json un error status code 400 utilizando rfc9457
•⁠  ⁠El Usuarios debe de crearse un cuenta en POST /api/v1/users y se obtendra en GET /api/v1/users/{id}
•⁠  ⁠El usuario obtendra el resumen en: GET /api/v1/summaries/document/{document_id}

