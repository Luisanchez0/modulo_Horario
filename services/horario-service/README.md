# horario-service-corregido

Microservicio de horarios escolares con arquitectura hexagonal y FastAPI.

## Estructura

- `src/domain`: modelos y reglas de negocio
- `src/application`: casos de uso
- `src/infrastructure`: SQLAlchemy, repositorios y persistencia
- `src/interfaces`: routers y schemas HTTP

## Periodos

El modelo `Periodo` soporta `SEMESTRE` y `CUATRIMESTRE` mediante el campo `tipo`.

## Ejecución

```bash
uvicorn main:app --reload
```

## Variables de entorno

- `DATABASE_URL`: cadena de conexión a la base de datos
- `APP_NAME`: nombre de la aplicación

## Modo catalogos remotos

En modo remoto, este servicio no administra catalogos locales de docentes, materias y aulas.

- `GET /docentes` consume `usuarios-service`
- `GET /materias` consume `materias-service`
- `GET /aulas` consume `aulas-service`
- `POST /docentes`, `POST /materias`, `POST /aulas` retornan `405`

`POST /horarios` y `POST /horarios/generar` validan IDs contra APIs externas antes de persistir.

Si quieres limpiar tablas locales de catalogo en PostgreSQL, usa:

```bash
psql "$DATABASE_URL" -f sql/cleanup_remote_catalogs.sql
```
