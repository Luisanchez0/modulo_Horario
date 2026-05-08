# Usuarios Docentes Service

Microservicio `usuarios/docentes-service` para un sistema educativo basado en microservicios.

## Descripción

Este proyecto implementa un servicio de gestión de docentes con FastAPI y una arquitectura hexagonal (dominio, aplicación, infraestructura e interfaces). Permite registrar docentes, autenticarlos y listar docentes protegidos por JWT.

## Tecnologías

- Python 3.12
- FastAPI
- SQLAlchemy
- MySQL / MariaDB
- PyMySQL
- Passlib (bcrypt)
- python-jose
- Pydantic

## Estructura

- `main.py`: arranca la aplicación y crea las tablas en startup.
- `src/domain`: entidades del dominio.
- `src/application`: casos de uso y puertos.
- `src/infrastructure`: repositorios, conexión DB y seguridad.
- `src/interfaces/api`: rutas y esquemas API.

## Instalación

```bash
cd c:/Taller4/usuariosdocentes-service
python -m venv rabbit
rabbit\Scripts\activate
pip install -r requirements.txt
```

> Si usas WSL o Linux, ajusta las rutas a `/mnt/c/taller4/usuariosdocentes-service`.

## Configuración

Crea un archivo `.env` con al menos:

```env
DATABASE_URL=mysql+pymysql://root:1234@localhost/docentes_db
JWT_SECRET=tu_secreto
```

El servicio intentará crear la base de datos `docentes_db` si no existe.

## Ejecución

```bash
uvicorn main:app --reload --port 8001
```

## Endpoints principales

- `POST /auth/register`: registrar docente (rol DOCENTE)
- `POST /auth/register-admin`: registrar administrador (requiere header `X-Admin-Key` con clave desde `.env`)
- `POST /auth/login`: obtener token JWT
- `GET /docentes`: listar docentes según rol
  - ADMIN: todos los docentes
  - DOCENTE: solo su registro

## Administradores

En `.env` agrega:

```env
ADMIN_CREATION_KEY=una_clave_super_secreta
```

Crear administrador:

```bash
curl -X POST http://127.0.0.1:8001/auth/register-admin \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: una_clave_super_secreta" \
  -d '{"nombre":"Admin","correo":"admin@example.com","password":"1234"}'
```

Luego iniciar sesión y usar el JWT para `/docentes`.

## Notas

- Se recomienda no versionar la carpeta `rabbit/` ni `.env`.
- Ya está inicializado el repositorio Git y subido al remoto:
  - `https://github.com/EstebanGonzalez88/Usuarios-Docentes-service`
