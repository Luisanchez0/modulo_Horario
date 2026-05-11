# API Endpoints

Documentacion rapida de todos los endpoints expuestos por los microservicios del proyecto.

## Base URLs

Si ejecutas el proyecto con Docker Compose, las URLs locales son:

- Usuarios service: `http://localhost:8001`
- Materias service: `http://localhost:8002`
- Aulas service: `http://localhost:8003`
- Horario service: `http://localhost:8004`

## Autenticacion y headers

- `Authorization: Bearer <token>`: requerido en endpoints protegidos por JWT.
- `X-Admin-Key: <clave>`: requerido para crear administradores en usuarios-service.
- `X-Internal-Key: <clave>`: requerido para endpoints internos en usuarios-service.

## 1. usuarios-service

### Health

- `GET /health` - Estado del servicio.

### Auth

- `POST /auth/register` - Registra un docente con rol normal.
- `POST /auth/register-admin` - Registra un administrador. Requiere `X-Admin-Key`.
- `POST /auth/login` - Inicia sesion y devuelve un token JWT.
- `GET /auth/me` - Devuelve el payload del token actual. Requiere `Authorization`.

### Docentes

- `GET /docentes` - Lista docentes visibles para el usuario autenticado. Requiere `Authorization`.
- `POST /docentes` - Crea un docente. Requiere rol `ADMIN`.
- `PUT /docentes/{docente_id}` - Actualiza un docente. Requiere rol `ADMIN`.
- `DELETE /docentes/{docente_id}` - Elimina un docente. Requiere rol `ADMIN`.

### Endpoints internos

- `GET /internal/docentes` - Lista todos los docentes. Requiere `X-Internal-Key`.
- `GET /internal/docentes/{docente_id}` - Obtiene un docente por ID. Requiere `X-Internal-Key`.

## 2. materias-service

Base path: `/api/v1`

### Health

- `GET /health` - Estado del servicio.

### Materias

- `POST /api/v1/materias/` - Crea una materia. Requiere rol `ADMIN`.
- `GET /api/v1/materias/` - Lista todas las materias.
- `GET /api/v1/materias/{materia_id}` - Obtiene una materia por ID.
- `PUT /api/v1/materias/{materia_id}` - Actualiza una materia. Requiere rol `ADMIN`.
- `DELETE /api/v1/materias/{materia_id}` - Elimina una materia. Requiere rol `ADMIN`.

## 3. aulas-service

### Health

- `GET /health` - Estado del servicio.

### Aulas

- `GET /aulas` - Lista todas las aulas.
- `GET /aulas/{aula_id}` - Obtiene un aula por ID.
- `POST /aulas` - Crea un aula. Requiere rol `ADMIN`.
- `PUT /aulas/{aula_id}` - Actualiza un aula. Requiere rol `ADMIN`.
- `DELETE /aulas/{aula_id}` - Elimina un aula. Requiere rol `ADMIN`.

## 4. horario-service

### Health

- `GET /health` - Estado del servicio.

### Docentes

- `POST /docentes` - Crea un docente en el catalogo del servicio.
- `GET /docentes` - Lista docentes.
- `GET /docentes/{docente_id}` - Obtiene un docente por ID.

### Materias

- `POST /materias` - Crea una materia en el catalogo del servicio.
- `GET /materias` - Lista materias.

### Aulas

- `POST /aulas` - Crea un aula en el catalogo del servicio.
- `GET /aulas` - Lista aulas.

### Periodos

- `POST /periodos` - Crea un periodo. Requiere rol `ADMIN`.
- `GET /periodos` - Lista periodos.
- `GET /periodos/{periodo_id}` - Obtiene un periodo por ID.
- `DELETE /periodos/{periodo_id}` - Elimina un periodo. Requiere rol `ADMIN`.

### Disponibilidades

- `POST /disponibilidades` - Crea una disponibilidad.
- `GET /disponibilidades/docente/{docente_id}` - Lista disponibilidades de un docente.

### Horarios

- `POST /horarios` - Crea un horario manual. Requiere rol `ADMIN`.
- `GET /horarios` - Lista los horarios generados o creados.
- `PUT /horarios/{horario_id}` - Actualiza un horario. Requiere rol `ADMIN`.
- `DELETE /horarios/{horario_id}` - Elimina un horario. Requiere rol `ADMIN`.
- `POST /horarios/generar` - Genera horarios automaticamente. Requiere rol `ADMIN`.

## Notas importantes

- Los codigos `401`, `403`, `404`, `409` y `502` dependen de validaciones internas y de llamadas entre servicios.
- En horario-service, varios endpoints validan existencia de docentes, materias, aulas y periodos antes de persistir datos.
- En usuarios-service, `POST /auth/register-admin` solo funciona con una clave valida en `X-Admin-Key`.
- En materias-service y aulas-service, las operaciones de escritura requieren token JWT con rol `ADMIN`.

## Resumen rapido

Si solo quieres el mapa general, estos son los bloques principales:

- Auth y docentes: usuarios-service
- Catalogo de materias: materias-service
- Catalogo de aulas: aulas-service
- Periodos, disponibilidades y horarios: horario-service