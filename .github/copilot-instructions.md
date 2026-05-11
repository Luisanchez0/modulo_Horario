# Copilot Instructions for Microservicio Horario

> A distributed microservices system for automated school schedule management using FastAPI and React

## 🛠 Build, Test, and Lint Commands

### Frontend
```bash
# Development server (http://localhost:5173)
npm run dev

# Production build
npm run build

# Lint and style check
npm run lint
```

### Backend Services
All services follow the same pattern. Replace `SERVICE_NAME` with: `usuarios-service`, `horario-service`, `materias-service`, or `aulas-service`.

**Option 1: Docker Compose (Recommended)**
```bash
cd services
docker compose up --build              # Start all services with databases
docker compose up SERVICE_NAME --build # Start single service only
docker compose logs -f SERVICE_NAME    # View logs for specific service
docker compose exec SERVICE_NAME bash  # Enter service container
docker compose down -v                 # Stop and remove volumes
```

**Option 2: Manual Setup (Local development)**
```bash
cd services/SERVICE_NAME
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export JWT_SECRET=$(openssl rand -hex 32)
export ADMIN_CREATION_KEY=$(openssl rand -hex 16)
uvicorn main:app --reload --port 8XXX  # Port: 8001, 8002, 8003, or 8004
```

### Testing

**Security Tests (Usuarios Service)**
```bash
cd services/usuarios-service
pytest test_security.py -v              # Run all security tests
pytest test_security.py::test_name -v  # Run single test
pytest test_security.py -vv             # Verbose output with tracebacks
```

**All Tests**
```bash
# Backend (pytest)
cd services/SERVICE_NAME
pytest                    # Run all tests in service
pytest -v                 # Verbose
pytest --tb=short        # Short traceback format

# Frontend (may vary - check frontend/package.json scripts)
cd frontend
npm run test              # If configured in package.json
npm run test -- --watch  # Watch mode (if available)
```

### Verification

**Health Endpoints (Docker or Manual)**
```bash
curl http://localhost:8001/health  # Usuarios
curl http://localhost:8002/health  # Materias
curl http://localhost:8003/health  # Aulas
curl http://localhost:8004/health  # Horarios
```

**Test Login (After setup)**
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo": "admin@example.com", "password": "1234"}'
```

## 🏗️ High-Level Architecture

### System Overview
- **Frontend**: React 18 + Vite (single-page app at port 5173)
- **Backend**: 4 FastAPI microservices (ports 8001-8004)
- **Databases**: MySQL (port 3307) for users, PostgreSQL (port 5433) for schedules
- **Orchestration**: Docker Compose for local development

### Microservices

| Service | Port | Database | Purpose |
|---------|------|----------|---------|
| `usuarios-service` | 8001 | MySQL | Authentication, JWT, teacher management |
| `materias-service` | 8002 | MySQL | Subject catalog |
| `aulas-service` | 8003 | MySQL | Classroom inventory & capacity |
| `horario-service` | 8004 | PostgreSQL | Schedule generation & retrieval |

### Backend Architecture (Per Service)
Each FastAPI service follows **clean architecture** pattern:

```
src/
├── domain/              # Business logic, entities, use cases
├── application/         # Service interfaces and handlers
├── infrastructure/      # Database, external service integrations
│   └── db/             # SQLAlchemy models, migrations, ORM
└── interfaces/         # API routes, HTTP schemas
    └── api/
        └── routes/     # FastAPI routers
```

### Frontend Architecture
```
frontend/src/
├── pages/              # Page components (logged-in views)
├── components/         # Reusable UI components
├── constants/          # API endpoints, configuration
├── App.jsx             # Main application shell
└── App.css             # Global styles (unified Flexbox layout)
```

### Data Flow
1. React frontend sends HTTP requests to FastAPI services
2. Services validate input with Pydantic models
3. Database operations via SQLAlchemy ORM
4. JWT tokens (HS256) for authentication and rate-limiting
5. CORS headers configured for localhost:5173

## 🔑 Key Conventions

### Authentication & Security
- **JWT**: HS256, issued by usuarios-service
- **Password hashing**: Bcrypt (passlib)
- **Rate limiting**: slowapi on auth endpoints
- **Validation**: Pydantic models on all inputs
- **SQL Injection prevention**: SQLAlchemy ORM (no raw queries)
- **XSS prevention**: React auto-escapes JSX

### Environment Configuration
- All services read from `.env` file or environment variables
- Never commit `.env` files; use `.env.example` template
- Critical secrets: `JWT_SECRET`, `ADMIN_CREATION_KEY`, `DATABASE_URL`, `INTERNAL_API_KEY`
- Use `setup-secrets.sh` to generate secure random keys

### Database & ORM
- **Backend**: SQLAlchemy with connection pooling
- **Queries**: Always use ORM models, never raw SQL
- **Connection strings**: Format varies by database:
  - MySQL: `mysql+pymysql://user:pass@host/db`
  - PostgreSQL: `postgresql://user:pass@host/db`

### API & HTTP
- **Route pattern**: Centralized in `src/interfaces/api/routes/`
- **Request/Response**: Pydantic models for schema validation
- **Status codes**: Standard HTTP (200, 201, 400, 401, 404, 500)
- **Error format**: JSON with error message and status code

### Frontend Components
- **State management**: React hooks (useState, useContext, etc.)
- **Routing**: react-router-dom
- **Calendar**: @fullcalendar/react with multiple views
- **PDF export**: html2canvas + jspdf
- **Styling**: Single CSS file (App.css) with BEM-like classes
- **Notifications**: Toast/modal system in App.jsx

### Code Organization
- Backend: Domain-driven with clean architecture layers
- Frontend: Component-based with page and component directories
- No hardcoded values: use constants/ directory (frontend) or config objects (backend)
- Test files: Pytest naming convention `test_*.py` in services

### Testing
- **Unit tests**: Located in service root or `tests/` directory
- **Test client**: FastAPI's TestClient for endpoint testing
- **Mocking**: Mock environment variables and database connections in setup
- **Coverage goal**: 80% (noted in README)

### Deployment
- **Secrets management**: AWS Secrets Manager for production (see DEPLOYMENT.md)
- **Container images**: Docker per service with multi-stage builds
- **Environment parity**: .env.example matches production variables
- **Health checks**: `/health` endpoint on all services (Docker healthcheck)

## 📝 Important File Locations

| File | Purpose |
|------|---------|
| `services/docker-compose.yml` | Orchestrates all services and databases locally |
| `services/.env` | Environment variables (do not commit) |
| `services/.env.example` | Template for environment setup |
| `setup-secrets.sh` | Generates secure JWT and admin keys |
| `SEGURIDAD.md` | Security best practices and implementation details |
| `DEPLOYMENT.md` | Production deployment guide |
| `services/*/main.py` | FastAPI app entry point for each service |
| `frontend/vite.config.js` | Vite build configuration and dev server |

## ⚠️ Common Gotchas

1. **Port conflicts**: Services use fixed ports (8001-8004, 3307, 5433). Kill existing processes if they conflict.
2. **Database initialization**: First `docker compose up` creates schemas from models; manually run migrations if schema changes.
3. **JWT expiration**: Token lifespan is service-dependent; check `src/domain/` or auth routes.
4. **CORS errors**: Frontend on port 5173 must be in `CORS_ALLOW_ORIGINS` env variable.
5. **Database URL format**: Each service expects specific format (MySQL vs PostgreSQL); check `.env.example`.

## 🚀 Getting Started for New Contributors

1. Run `bash setup-secrets.sh` to generate `.env` with secure keys
2. Start services: `cd services && docker compose up --build`
3. Start frontend: `cd frontend && npm install && npm run dev`
4. Log in with test credentials: admin@example.com / 1234
5. Run tests: `cd services/usuarios-service && pytest test_security.py -v`
6. Check logs: `docker compose logs -f SERVICE_NAME`

## 📚 Related Documentation

- **README.md**: System overview, features, architecture diagram
- **SEGURIDAD.md**: Security implementation and best practices
- **DEPLOYMENT.md**: Production deployment (AWS, Kubernetes, etc.)
- **services/README.md**: Detailed service documentation
- **services/EJEMPLOS_USO_HORARIO.md**: API usage examples
- **frontend/README.md**: React frontend specifics

---

**Last Updated:** 2026-05-09  
**Status:** Pre-production (Phase 1 Security Complete)
