# Especificación de Funcionalidad: Microservicio service-extractor-notebookum

**Rama de Funcionalidad**: `002-service-extractor-notebookum`  
**Creado**: 2026-05-26  
**Estado**: Borrador  
**Entrada**: "Crear historias de usuario para el microservicio service-extractor-notebookum, encargado de extraer información de PDFs en NotebookUm, respetando el spec global de API pública /api/v1/, procesamiento asíncrono, validación PDF, límite de 25MB, RFC 9457 y patrones Bulkhead, Rate Limit, Strangler, CQRS, Saga y Circuit Breaker."

## Escenarios de Usuario y Pruebas *(obligatorio)*

### Historia de Usuario 1 - Extraer Texto de un PDF Válido (Prioridad: P1)

Como servicio orquestador de documentos de NotebookUm, necesito enviar un PDF válido al microservicio extractor para obtener el texto extraído sin bloquear el flujo principal de carga del usuario.

**Por qué esta prioridad**: Es la capacidad central del microservicio. Sin extracción de texto no se puede generar resumen, responder preguntas ni completar el procesamiento documental.

**Prueba Independiente**: Puede probarse enviando un PDF válido menor a 25MB al endpoint interno del extractor y verificando que responde con texto extraído, metadatos básicos y un identificador de correlación.

**Escenarios de Aceptación**:

1. **Dado** que el orquestador envía un PDF válido con `content-type: application/pdf` y tamaño menor o igual a 25MB, **Cuando** el extractor procesa la solicitud, **Entonces** devuelve el texto extraído y metadatos del documento
2. **Dado** que el PDF contiene texto seleccionable, **Cuando** se ejecuta la extracción, **Entonces** el resultado incluye contenido no vacío y preserva el orden lógico de lectura en la medida de lo posible
3. **Dado** que la extracción termina correctamente, **Cuando** el extractor responde, **Entonces** incluye `document_id`, `correlation_id`, `status: completed` y métricas mínimas de procesamiento

---

### Historia de Usuario 2 - Rechazar Archivos Inválidos con RFC 9457 (Prioridad: P1)

Como consumidor del microservicio extractor, necesito recibir errores consistentes cuando el archivo no sea un PDF válido, supere 25MB o esté corrupto, para que el monolito/API pública pueda informar el problema de forma clara al usuario.

**Por qué esta prioridad**: Protege al servicio de entradas inválidas y mantiene compatibilidad con el spec global, que exige validación de PDF, límite de 25MB y errores JSON bajo RFC 9457.

**Prueba Independiente**: Puede probarse enviando un archivo no PDF, un PDF mayor a 25MB y un PDF corrupto, verificando códigos HTTP y cuerpo `application/problem+json`.

**Escenarios de Aceptación**:

1. **Dado** que el archivo no tiene `content-type: application/pdf`, **Cuando** se solicita extracción, **Entonces** el servicio devuelve HTTP 400 con Problem Details RFC 9457
2. **Dado** que el archivo supera 25MB, **Cuando** se solicita extracción, **Entonces** el servicio devuelve HTTP 400 indicando que el tamaño máximo permitido fue excedido
3. **Dado** que el archivo declara ser PDF pero está corrupto o no comienza con una firma PDF válida, **Cuando** se intenta procesar, **Entonces** el servicio devuelve un error controlado sin exponer trazas internas
4. **Dado** que ocurre un error de validación, **Cuando** el servicio responde, **Entonces** el cuerpo incluye `type`, `title`, `status`, `detail` e `instance`

---

### Historia de Usuario 3 - Procesar Extracciones de Forma Asíncrona (Prioridad: P1)

Como orquestador del flujo documental, necesito delegar una extracción y consultar su estado después, para que la carga de documentos no dependa del tiempo total de procesamiento del PDF.

**Por qué esta prioridad**: El spec global exige procesamiento asíncrono. Separar aceptación de trabajo y ejecución permite escalar el extractor como microservicio independiente.

**Prueba Independiente**: Puede probarse creando un trabajo de extracción, recibiendo una respuesta inicial rápida y consultando el estado hasta `completed` o `failed`.

**Escenarios de Aceptación**:

1. **Dado** que se envía un PDF válido para extracción asíncrona, **Cuando** el extractor acepta el trabajo, **Entonces** responde en menos de 5 segundos con `job_id`, `document_id`, `correlation_id` y `status: accepted`
2. **Dado** que existe un `job_id`, **Cuando** el orquestador consulta el estado, **Entonces** recibe `accepted`, `processing`, `completed` o `failed`
3. **Dado** que el trabajo finaliza correctamente, **Cuando** se consulta el resultado, **Entonces** el servicio entrega el texto extraído sin requerir reenviar el PDF original
4. **Dado** que el trabajo falla, **Cuando** se consulta el estado, **Entonces** el servicio informa una causa funcional y recuperable mediante Problem Details

---

### Historia de Usuario 4 - Aislar Recursos de Extracción con Bulkhead (Prioridad: P2)

Como operador de NotebookUm, necesito que el extractor limite y separe sus recursos de procesamiento para que PDFs lentos, grandes o complejos no bloqueen todos los trabajos del sistema.

**Por qué esta prioridad**: La extracción de PDFs puede consumir CPU y memoria. El Bulkhead evita que un grupo de trabajos degrade todo el microservicio o el resto de la plataforma.

**Prueba Independiente**: Puede probarse enviando múltiples PDFs complejos simultáneamente y verificando que el servicio mantiene capacidad reservada para solicitudes livianas y para health checks.

**Escenarios de Aceptación**:

1. **Dado** que hay varios PDFs pesados en procesamiento, **Cuando** ingresa un PDF liviano, **Entonces** el servicio puede procesarlo si existe capacidad en su partición correspondiente
2. **Dado** que la cola de trabajos pesados está saturada, **Cuando** llega un nuevo PDF pesado, **Entonces** el servicio rechaza o difiere el trabajo con una respuesta controlada
3. **Dado** que el pool de extracción está saturado, **Cuando** se consulta `/health`, **Entonces** el endpoint responde sin depender del pool saturado
4. **Dado** que un proceso de extracción consume demasiados recursos, **Cuando** supera los límites definidos, **Entonces** el trabajo falla de forma aislada sin detener el servicio completo

---

### Historia de Usuario 5 - Aplicar Rate Limit al Ingreso de Trabajos (Prioridad: P2)

Como responsable de plataforma, necesito limitar la cantidad de solicitudes de extracción por consumidor para evitar abuso, picos accidentales y agotamiento de recursos.

**Por qué esta prioridad**: El extractor será un punto intensivo en CPU/memoria. El Rate Limit protege la estabilidad y permite operar con capacidad predecible.

**Prueba Independiente**: Puede probarse enviando solicitudes por encima del límite configurado para un mismo cliente interno y verificando HTTP 429.

**Escenarios de Aceptación**:

1. **Dado** que un consumidor interno supera el límite de solicitudes configurado, **Cuando** intenta crear otro trabajo, **Entonces** recibe HTTP 429 con Problem Details
2. **Dado** que el límite se aplica por `client_id` o credencial de servicio, **Cuando** otro consumidor está dentro de su cuota, **Entonces** puede seguir creando trabajos
3. **Dado** que una respuesta fue limitada, **Cuando** el servicio responde, **Entonces** incluye información suficiente para reintento controlado, como `Retry-After`

---

### Historia de Usuario 6 - Migrar desde el Monolito con Strangler Pattern (Prioridad: P2)

Como equipo de desarrollo, necesito reemplazar gradualmente la extracción local del monolito por llamadas al microservicio extractor para reducir riesgo y mantener compatibilidad con la API pública existente.

**Por qué esta prioridad**: Permite migrar sin reescribir todo el sistema. La API pública `/api/v1/documento/upload` puede seguir igual mientras internamente se redirige la extracción.

**Prueba Independiente**: Puede probarse activando una bandera de configuración para usar el extractor externo y desactivándola para volver al extractor local.

**Escenarios de Aceptación**:

1. **Dado** que la bandera `EXTRACTOR_SERVICE_ENABLED` está activa, **Cuando** el monolito necesita extraer texto, **Entonces** delega la operación al microservicio
2. **Dado** que la bandera está inactiva, **Cuando** el monolito procesa un PDF, **Entonces** utiliza el extractor local actual como fallback temporal
3. **Dado** que el microservicio extractor falla, **Cuando** el Circuit Breaker abre el circuito, **Entonces** el monolito no insiste indefinidamente contra el extractor
4. **Dado** que la migración se completa, **Cuando** el extractor local ya no recibe tráfico, **Entonces** puede planificarse su remoción en una historia posterior

---

### Historia de Usuario 7 - Separar Comandos y Consultas con CQRS (Prioridad: P2)

Como consumidor interno del extractor, necesito que la creación de trabajos de extracción y la consulta de estados/resultados estén separadas para simplificar escalabilidad, auditoría y consistencia eventual.

**Por qué esta prioridad**: CQRS encaja con el flujo asíncrono. Crear un trabajo es un comando; consultar estado o resultado es una consulta.

**Prueba Independiente**: Puede probarse que el endpoint de comando solo acepta trabajos y que los endpoints de consulta no modifican el estado.

**Escenarios de Aceptación**:

1. **Dado** que el orquestador crea una extracción, **Cuando** llama al endpoint de comando, **Entonces** el servicio registra intención de procesamiento y responde con `job_id`
2. **Dado** que el orquestador consulta un `job_id`, **Cuando** llama al endpoint de consulta, **Entonces** recibe estado o resultado sin disparar una nueva extracción
3. **Dado** que se repite una consulta de resultado, **Cuando** el trabajo ya está `completed`, **Entonces** el servicio devuelve una respuesta idempotente

---

### Historia de Usuario 8 - Participar en una Saga de Procesamiento Documental (Prioridad: P2)

Como orquestador de NotebookUm, necesito que el extractor emita estados claros para coordinar la saga completa de carga, extracción, resumen y persistencia del documento.

**Por qué esta prioridad**: En microservicios, la carga de documentos deja de ser una transacción local única. La Saga permite coordinar pasos y compensaciones entre servicios.

**Prueba Independiente**: Puede probarse simulando éxito y fallo de extracción y verificando que el orquestador puede avanzar al resumen o marcar el documento como fallido.

**Escenarios de Aceptación**:

1. **Dado** que la extracción finaliza con éxito, **Cuando** el extractor publica o expone el estado `extraction.completed`, **Entonces** el orquestador puede iniciar generación de resumen
2. **Dado** que la extracción falla por PDF corrupto, **Cuando** el extractor publica o expone `extraction.failed`, **Entonces** el orquestador marca el documento como fallido y no invoca el servicio de resumen
3. **Dado** que el orquestador reintenta un comando con el mismo `idempotency_key`, **Cuando** el extractor ya aceptó ese trabajo, **Entonces** devuelve el mismo `job_id` sin duplicar procesamiento
4. **Dado** que el flujo requiere compensación, **Cuando** un trabajo queda fallido, **Entonces** el extractor no conserva el PDF original y deja disponible solo metadata mínima de auditoría

---

### Historia de Usuario 9 - Proteger Dependencias con Circuit Breaker (Prioridad: P3)

Como operador del microservicio, necesito que las dependencias internas de extracción estén protegidas por Circuit Breaker para evitar cascadas de fallos cuando Docling u otro motor de extracción no responda correctamente.

**Por qué esta prioridad**: Aunque el extractor sea autónomo, puede depender de librerías pesadas o procesos externos. Circuit Breaker evita saturación por reintentos inútiles.

**Prueba Independiente**: Puede probarse forzando fallos repetidos del motor de extracción y verificando que el servicio abre el circuito, responde rápido y luego permite recuperación.

**Escenarios de Aceptación**:

1. **Dado** que el motor principal de extracción falla repetidamente, **Cuando** se alcanza el umbral configurado, **Entonces** el Circuit Breaker abre el circuito
2. **Dado** que el circuito está abierto, **Cuando** llega una nueva extracción, **Entonces** el servicio responde rápido con error controlado o usa fallback permitido
3. **Dado** que pasa la ventana de recuperación, **Cuando** se realiza una solicitud de prueba exitosa, **Entonces** el circuito vuelve a estado cerrado
4. **Dado** que existe un parser fallback básico, **Cuando** el motor principal no está disponible y el PDF lo permite, **Entonces** el servicio puede devolver una extracción degradada identificada como `degraded`

---

### Historia de Usuario 10 - Observar y Auditar Extracciones (Prioridad: P3)

Como equipo de soporte, necesito trazabilidad de cada extracción para diagnosticar errores, medir tiempos y correlacionar solicitudes entre el monolito/API gateway y el microservicio.

**Por qué esta prioridad**: La observabilidad reduce el costo operativo de migrar a microservicios y permite comprobar los criterios de éxito.

**Prueba Independiente**: Puede probarse enviando una solicitud con `correlation_id` y verificando logs estructurados, métricas de duración y estado final.

**Escenarios de Aceptación**:

1. **Dado** que una solicitud incluye `correlation_id`, **Cuando** el extractor registra eventos, **Entonces** todos los logs del trabajo incluyen ese valor
2. **Dado** que una extracción termina, **Cuando** se registran métricas, **Entonces** se informa duración, tamaño de archivo, estado final y estrategia usada
3. **Dado** que ocurre un error, **Cuando** se consulta la auditoría técnica del trabajo, **Entonces** se puede identificar el tipo de fallo sin exponer contenido sensible del PDF

## Casos Extremos

- ¿Qué sucede si un PDF válido contiene cero caracteres extraíbles?
- ¿Cómo responde el servicio ante PDFs escaneados sin OCR disponible?
- ¿Qué ocurre si el mismo `idempotency_key` se envía con un archivo distinto?
- ¿Cómo se comporta el extractor cuando la cola está llena?
- ¿Qué ocurre si el consumidor cancela el flujo después de aceptar un trabajo?
- ¿Cómo se limpian resultados temporales si el orquestador nunca consulta el resultado?
- ¿Qué sucede si el PDF tiene miles de páginas pero pesa menos de 25MB?
- ¿Cómo se diferencia un fallo funcional del PDF de una falla técnica del extractor?

## Requisitos Funcionales Derivados

- **RF-EXT-001**: El microservicio DEBE aceptar únicamente PDFs con `content-type: application/pdf`
- **RF-EXT-002**: El microservicio DEBE rechazar archivos mayores a 25MB
- **RF-EXT-003**: El microservicio DEBE devolver errores en formato RFC 9457
- **RF-EXT-004**: El microservicio NO DEBE persistir el PDF original después de la extracción
- **RF-EXT-005**: El microservicio DEBE exponer comandos para crear trabajos de extracción y consultas para estado/resultado
- **RF-EXT-006**: El microservicio DEBE soportar idempotencia mediante `idempotency_key`
- **RF-EXT-007**: El microservicio DEBE incluir `correlation_id` en respuestas, logs y eventos
- **RF-EXT-008**: El microservicio DEBE aplicar límites de concurrencia por Bulkhead
- **RF-EXT-009**: El microservicio DEBE aplicar Rate Limit por consumidor interno
- **RF-EXT-010**: El microservicio DEBE permitir migración gradual desde el extractor local del monolito mediante Strangler Pattern
- **RF-EXT-011**: El microservicio DEBE integrarse con la Saga de procesamiento documental mediante estados `accepted`, `processing`, `completed` y `failed`
- **RF-EXT-012**: El microservicio DEBE proteger dependencias de extracción con Circuit Breaker

## Criterios de Éxito *(obligatorio)*

- **CE-EXT-001**: El servicio acepta trabajos válidos y responde con `status: accepted` en menos de 5 segundos
- **CE-EXT-002**: El 100% de archivos no PDF o mayores a 25MB son rechazados antes de iniciar extracción
- **CE-EXT-003**: El 100% de errores 400 usan formato RFC 9457
- **CE-EXT-004**: El 95% de PDFs con texto seleccionable finaliza con `status: completed`
- **CE-EXT-005**: El extractor soporta al menos 100 trabajos concurrentes sin bloquear health checks
- **CE-EXT-006**: Las solicitudes repetidas con la misma `idempotency_key` no duplican trabajos
- **CE-EXT-007**: El Circuit Breaker responde en menos de 1 segundo cuando el motor principal está en estado abierto
- **CE-EXT-008**: La migración Strangler permite alternar entre extractor local y microservicio sin cambiar la API pública `/api/v1/documento/upload`

## Supuestos

- El endpoint público de carga de documentos permanece en el monolito o API gateway bajo `/api/v1/documento/upload` durante la migración inicial
- El microservicio extractor expone endpoints internos, no necesariamente públicos para usuarios finales
- La generación de resumen queda fuera del alcance de este microservicio
- La persistencia final de documentos, resúmenes e historiales queda en el servicio/orquestador correspondiente
- El extractor puede usar Docling como motor principal y un parser básico como fallback temporal
- La autenticación entre servicios se resolverá con credenciales internas o mecanismo equivalente en el plan técnico
