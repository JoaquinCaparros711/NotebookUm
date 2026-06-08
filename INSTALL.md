# NotebookUm — Guía de instalación

Sistema de notebooks inteligentes con extracción y resumen de PDFs usando IA.

## Repositorios necesarios

Cloná los 6 repos en la misma carpeta:

```bash
git clone https://github.com/LucianoMengarelli/NotebookUm
git clone https://github.com/LucianoMengarelli/persistence-notebookum
git clone https://github.com/LucianoMengarelli/service-user-notebookum
git clone https://github.com/LucianoMengarelli/service-extractor-notebookum
git clone https://github.com/LucianoMengarelli/service-ai-notebookum
git clone https://github.com/LucianoMengarelli/service-controller-notebookum-go
```

## Prerrequisitos

- Docker Desktop (con Docker Compose)
- Java 21 (solo para buildear `persistence-notebookum`)
- Go 1.22+ (solo para buildear `service-controller-notebookum-go`)

---

## Paso 1 — Red Docker

```bash
docker network create notebookum-network
```

---

## Paso 2 — Variables de entorno

Copiá cada `.env.example` como `.env` y completá los valores marcados con ⚠:

```bash
# MySQL y Redis (carpeta NotebookUm)
cp docker/mysql/.env.example   docker/mysql/.env
cp docker/redis/.env.example   docker/redis/.env

# Servicios
cp ../persistence-notebookum/.env.example              ../persistence-notebookum/.env
cp ../service-user-notebookum/.env.example             ../service-user-notebookum/.env
cp ../service-extractor-notebookum/.env.example        ../service-extractor-notebookum/.env
cp ../service-ai-notebookum/.env.example               ../service-ai-notebookum/.env
cp ../service-controller-notebookum-go/.env.example    ../service-controller-notebookum-go/.env
```

### Qué cambiar en cada `.env`

| Archivo | Variable | Descripción |
|---|---|---|
| `docker/mysql/.env` | `DB_PASSWORD` | Contraseña root de MySQL |
| `docker/mysql/.env` | `DB_USER_PASSWORD` | Contraseña del usuario de app |
| `docker/redis/.env` | `REDIS_PASSWORD` | Contraseña de Redis |
| `service-ai-notebookum/.env` | `NVIDIA_API_KEY` | API key de NVIDIA NIM → [build.nvidia.com](https://build.nvidia.com) |
| `service-user-notebookum/.env` | `SECRET_KEY` | Clave para firmar JWT (cualquier string largo y aleatorio) |
| todos los servicios | `REDIS_PASSWORD` | Debe ser **igual** al de `docker/redis/.env` |
| `persistence-notebookum/.env` | `DB_PASSWORD` | Debe ser **igual** al de `docker/mysql/.env` |

### Archivos de entorno de MySQL y Redis

Creá estos dos archivos si no existen:

**`docker/mysql/.env`**
```env
DB_PASSWORD=changeme
DB_NAME=notebookum
DB_USER=appuser
DB_USER_PASSWORD=changeme
```

**`docker/redis/.env`**
```env
REDIS_PASSWORD=changeme
```

---

## Paso 3 — Hosts (Windows)

Abrí `C:\Windows\System32\drivers\etc\hosts` como administrador y agregá:

```
127.0.0.1 api.universidad.localhost
127.0.0.1 users.universidad.localhost
127.0.0.1 extractor.universidad.localhost
127.0.0.1 ai.universidad.localhost
127.0.0.1 persistence-java.universidad.localhost
127.0.0.1 notebookum.universidad.localhost
```

En macOS/Linux editá `/etc/hosts` con `sudo`.

---

## Paso 4 — Obtener las imágenes Docker

Hay dos formas de obtener las imágenes. Usá **una sola**.

---

### Opción A — Recibir los `.tar` (recomendado, sin compilar nada)

Luciano te va a pasar los archivos `.tar` con las imágenes ya buildeadas.
Una vez que los tengas, cargalos con:

```bash
docker load -i notebookum-persistence.tar
docker load -i notebookum-user.tar
docker load -i notebookum-extractor.tar
docker load -i notebookum-ai.tar
docker load -i notebookum-controller.tar
```

Verificá que se cargaron bien:

```bash
docker images | grep notebookum
```

Deberías ver:

```
notebookum-persistence   v1.0.0   ...
notebookum-user          v1.0.2   ...
notebookum-extractor     v1.0.0   ...
notebookum-ai            v1.0.0   ...
notebookum-controller    v1.0.0   ...
```

---

### Opción B — Buildear desde el código fuente

> Requiere Java 21 y Go 1.22+ instalados.

```bash
# Persistencia (Java — tarda ~3 min la primera vez)
cd persistence-notebookum
docker build -t notebookum-persistence:v1.0.0 .

# Usuario
cd ../service-user-notebookum
docker build -t notebookum-user:v1.0.2 .

# Extractor de PDFs
cd ../service-extractor-notebookum
docker build -t notebookum-extractor:v1.0.0 .

# IA (resúmenes)
cd ../service-ai-notebookum
docker build -t notebookum-ai:v1.0.0 .

# Controller (Go)
cd ../service-controller-notebookum-go
docker build -t notebookum-controller:v1.0.0 .
```

---

> **Para Luciano — cómo exportar las imágenes:**
> ```bash
> docker save notebookum-persistence:v1.0.0  -o notebookum-persistence.tar
> docker save notebookum-user:v1.0.2         -o notebookum-user.tar
> docker save notebookum-extractor:v1.0.0    -o notebookum-extractor.tar
> docker save notebookum-ai:v1.0.0           -o notebookum-ai.tar
> docker save notebookum-controller:v1.0.0   -o notebookum-controller.tar
> ```

---

## Paso 5 — Levantar infraestructura

El orden importa. Ejecutá desde la carpeta `NotebookUm/`:

```bash
# 1. Reverse proxy (Traefik)
cd docker/traefik
docker compose up -d

# 2. Base de datos
cd ../mysql
docker compose up -d

# 3. Redis
cd ../redis
docker compose up -d
```

Esperá ~15 segundos para que MySQL esté listo.

---

## Paso 6 — Levantar servicios

Desde la carpeta de cada repo (el orden no importa):

```bash
cd persistence-notebookum         && docker compose up -d && cd ..
cd service-user-notebookum        && docker compose up -d && cd ..
cd service-extractor-notebookum   && docker compose up -d && cd ..
cd service-ai-notebookum          && docker compose up -d && cd ..
cd service-controller-notebookum-go && docker compose up -d && cd ..
```

---

## Paso 7 — Verificar

```bash
# Ver todos los contenedores corriendo
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

# Health check del controller
curl -k https://api.universidad.localhost/health
```

Deberías ver algo como:
```json
{"status": "ok"}
```

---

## Flujo de uso

```
1. Registrarse     POST /api/v1/users          {"name","email","password"}
2. Login           POST /api/v1/users/login     {"email","password"}  → token JWT
3. Subir PDF       POST /api/v1/documento/upload  (multipart, Bearer token)  → {job_id, document_id}
4. Ver estado      GET  /api/v1/documents/{job_id}/status
5. Generar resumen POST /api/v1/summaries/document  {"document_id": "..."}
6. Ver resumen     GET  /api/v1/summaries/{document_id}
```

Todos los endpoints (excepto registro y login) requieren `Authorization: Bearer <token>`.

---

## Apagar todo

```bash
cd service-controller-notebookum-go && docker compose down && cd ..
cd service-ai-notebookum            && docker compose down && cd ..
cd service-extractor-notebookum     && docker compose down && cd ..
cd service-user-notebookum          && docker compose down && cd ..
cd persistence-notebookum           && docker compose down && cd ..
cd NotebookUm/docker/redis          && docker compose down && cd ../..
cd docker/mysql                     && docker compose down && cd ../..
cd docker/traefik                   && docker compose down
```
