# Sistema de Microservicios - Documentacion Actualizada

Este README resume el estado actual del proyecto y deja ejemplos de uso end-to-end alineados con la implementacion vigente.

Servicios incluidos:
- usuarios-service
- materias-service
- aulas-service
- horario-service

## 1. Resumen funcional

El sistema permite:
- Registrar docentes y autenticarlos (usuarios-service).
- Gestionar catalogo de materias (materias-service).
- Gestionar aulas (aulas-service).
- Crear disponibilidades, periodos y horarios (horario-service).

Importante:
- horario-service ya no administra catalogos locales de docentes, materias y aulas.
- horario-service consume esos datos desde los otros microservicios.

## 2. Arquitectura de datos y ownership

Cada microservicio es duenio de su propia informacion:
- usuarios-service: docentes/autenticacion (MySQL)
- aulas-service: aulas (MySQL)
- materias-service: materias (PostgreSQL)
- horario-service: periodos, disponibilidades y horarios (PostgreSQL)

Regla operativa:
- No acceder por SQL directo a tablas de otro microservicio.
- Integracion entre servicios por HTTP API.

## 3. Puertos y servicios actuales

Con Docker Compose (carpeta services/):
- usuarios-service: http://localhost:8001
- materias-service: http://localhost:8002
- aulas-service: http://localhost:8003
- horario-service: http://localhost:8004

Bases de datos:
- MySQL: localhost:3307
- PostgreSQL: localhost:5433

## 4. Variables de entorno relevantes

Antes de levantar Docker Compose:

```bash
cp .env.example .env
```

### usuarios-service
- DATABASE_URL=mysql+pymysql://root:tu_password@localhost:3307/docentes_db
- JWT_SECRET=tu_jwt_secret
- ADMIN_CREATION_KEY=tu_admin_creation_key
- INTERNAL_API_KEY=tu_internal_api_key

### materias-service
- DATABASE_URL=postgresql+asyncpg://postgres:tu_password@localhost:5433/materias_db

### aulas-service
- DATABASE_URL=mysql+pymysql://root:tu_password@localhost:3307/aulas_db

### horario-service
- DATABASE_URL=postgresql://postgres:tu_password@localhost:5433/horarios_db
- APP_NAME=Horario Service
- USUARIOS_SERVICE_URL=http://localhost:8001
- MATERIAS_SERVICE_URL=http://localhost:8002
- AULAS_SERVICE_URL=http://localhost:8003
- INTERNAL_API_KEY=tu_internal_api_key
- UPSTREAM_TIMEOUT_SECONDS=5

## 5. Levantar y detener todo

Desde services/:

```bash
docker compose up --build -d
```

Ver estado:

```bash
docker compose ps
```

Ver logs de un servicio:

```bash
docker compose logs -f horario-service
```

Detener stack:

```bash
docker compose down
```

## 6. Health checks

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

Respuestas esperadas:
- usuarios-service: {"status":"ok","service":"usuarios-service"}
- materias-service: {"status":"ok","service":"materias-service"}
- aulas-service: {"status":"ok","service":"aulas-service"}
- horario-service: {"status":"ok"}

## 7. Endpoints clave por microservicio

### usuarios-service
- POST /auth/register
- POST /auth/register-admin
- POST /auth/login
- GET /docentes (con Bearer token)
- GET /internal/docentes (requiere X-Internal-Key)
- GET /internal/docentes/{docente_id} (requiere X-Internal-Key)

### materias-service
Prefijo base: /api/v1
- POST /api/v1/materias/ (requiere token ADMIN)
- GET /api/v1/materias/
- GET /api/v1/materias/{materia_id}
- PUT /api/v1/materias/{materia_id}
- DELETE /api/v1/materias/{materia_id}

### aulas-service
- GET /aulas
- GET /aulas/{aula_id}
- POST /aulas (requiere token ADMIN)
- PUT /aulas/{aula_id} (requiere token ADMIN)
- DELETE /aulas/{aula_id} (requiere token ADMIN)

### horario-service
- POST /periodos
- GET /periodos
- POST /disponibilidades
- GET /disponibilidades/docente/{docente_id}
- POST /horarios
- GET /horarios
- POST /horarios/generar

Modo remoto de catalogos en horario-service:
- GET /docentes, GET /materias, GET /aulas: proxy de lectura a servicios externos.
- POST /docentes, POST /materias, POST /aulas: 405 Method Not Allowed.

## 8. Flujo recomendado de uso (demo)

1. Crear docente en usuarios-service.
2. Crear materia en materias-service.
3. Crear aula en aulas-service.
4. Crear periodo y disponibilidad en horario-service.
5. Crear horario manual o generar automaticamente.
6. Consultar horarios enriquecidos.

## 9. Ejemplos de uso end-to-end

### 9.1 Registrar docente

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Docente Demo",
    "correo":"demo@unach.edu",
    "password":"abc123",
    "role":"DOCENTE"
  }'
```

### 9.2 Crear materia

```bash
curl -X POST http://localhost:8002/api/v1/materias/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Base de Datos",
    "codigo":"BD101",
    "creditos":4,
    "descripcion":"Modelo relacional y SQL"
  }'
```

### 9.3 Crear aula

```bash
curl -X POST http://localhost:8003/aulas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Aula Demo",
    "capacidad":35
  }'
```

### 9.4 Crear periodo

```bash
curl -X POST http://localhost:8004/periodos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"2026-1",
    "tipo":"SEMESTRE",
    "fecha_inicio":"2026-04-01",
    "fecha_fin":"2026-08-15"
  }'
```

### 9.5 Crear disponibilidad

```bash
curl -X POST http://localhost:8004/disponibilidades \
  -H "Content-Type: application/json" \
  -d '{
    "docente_id":1,
    "dia":"LUNES",
    "hora_inicio":"08:00",
    "hora_fin":"12:00"
  }'
```

### 9.6 Crear horario manual

```bash
curl -X POST http://localhost:8004/horarios \
  -H "Content-Type: application/json" \
  -d '{
    "docente_id":1,
    "materia_id":1,
    "aula_id":1,
    "periodo_id":1,
    "dia":"MARTES",
    "hora_inicio":"08:00",
    "hora_fin":"10:00"
  }'
```

### 9.7 Listar horarios (respuesta enriquecida)

```bash
curl http://localhost:8004/horarios
```

Se espera que cada horario incluya campos enriquecidos desde catalogos remotos, por ejemplo:
- docente_nombre
- docente_correo
- materia_nombre
- materia_codigo
- aula_nombre
- aula_capacidad

### 9.8 Generar horarios automaticamente

```bash
curl -X POST http://localhost:8004/horarios/generar \
  -H "Content-Type: application/json" \
  -d '{
    "periodo_id":1,
    "duracion_minutos":120,
    "hora_inicio_jornada":"08:00",
    "hora_fin_jornada":"12:00",
    "dias":["LUNES","MARTES"],
    "docente_ids":[1],
    "materia_ids":[1],
    "aula_ids":[1]
  }'
```

## 10. Validaciones cruzadas en horario-service

Antes de crear/generar horarios, horario-service valida que existan:
- docente en usuarios-service
- materia en materias-service
- aula en aulas-service

Errores comunes:
- 400 Bad Request: IDs externos inexistentes.
- 502 Bad Gateway: servicio externo caido o no accesible.

## 11. Catalogos remotos y limpieza opcional de tablas legacy

Si migraste desde modo local y aun ves tablas de catalogo legacy en horarios_db, puedes limpiar con:

```bash
cd horario-service
psql "$DATABASE_URL" -f sql/cleanup_remote_catalogs.sql
```

Nota:
- El sistema puede funcionar aunque existan tablas legacy, pero el modo operativo actual es catalogo remoto.

## 12. Troubleshooting rapido

### Error bcrypt/passlib en usuarios-service

Si aparece un error similar a:
- module 'bcrypt' has no attribute '__about__'

Usar versiones compatibles en usuarios-service/requirements.txt:
- passlib[bcrypt]==1.7.4
- bcrypt==4.0.1

Y reconstruir:

```bash
cd services
docker compose up --build -d usuarios-service
```

---

Documento actualizado al estado actual del proyecto (abril 2026).
