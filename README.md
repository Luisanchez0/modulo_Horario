# 🎓 Microservicio Horario - Sistema de Gestión de Horarios Escolares

> Sistema distribuido con microservicios para la generación automática y gestión de horarios académicos.

## 📑 Tabla de Contenidos

- [Características](#características)
- [Tecnología](#tecnología)
- [Inicio Rápido](#inicio-rápido)
- [Documentación](#documentación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Desarrollo Local](#desarrollo-local)
- [Testing](#testing)
- [Deployment](#deployment)
- [Seguridad](#seguridad)

---

## ✨ Características

### ✅ Funcionalidad Core
- 👥 **Gestión de Docentes** - CRUD + autenticación JWT
- 📚 **Catálogo de Materias** - Asignación y códigos
- 🏛️ **Inventario de Aulas** - Gestión de espacios y capacidad
- ⏰ **Generación Automática** - Algoritmo de horarios inteligente
- 📅 **Calendario Interactivo** - Vista por semana/aula/docente
- 🖨️ **Exportación PDF** - Impresión de horarios
- 🔔 **Notificaciones** - Toasts y modales en tiempo real

### 🔒 Seguridad (Fase 1)
- ✅ JWT con HS256
- ✅ Bcrypt para contraseñas
- ✅ Rate limiting en auth
- ✅ Validación Pydantic
- ✅ SQL Injection prevention (ORM)
- ✅ XSS protection (React)

---

## 🛠 Tecnología

| Componente | Stack |
|-----------|-------|
| **Backend Microservicios** | FastAPI + SQLAlchemy + PostgreSQL/MySQL |
| **Frontend** | React 18 + Vite + FullCalendar |
| **Auth** | JWT (HS256) + Bcrypt |
| **Contenedorización** | Docker + Docker Compose |
| **Testing** | Pytest + React Testing Library |

**Microservicios:**
- `usuarios-service` (8001) - Autenticación y docentes
- `horario-service` (8004) - Generación y gestión de horarios
- `materias-service` (8002) - Catálogo de materias
- `aulas-service` (8003) - Inventario de aulas

---

## 🚀 Inicio Rápido

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (si desarrollo local sin Docker)
- openssl (para generación de secrets)

### Setup Local (Recomendado - Con Docker)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd Microservicio_Horario

# 2. Generar secrets seguros
bash setup-secrets.sh

# 3. Iniciar servicios
cd services
docker compose up --build

# 4. Iniciar frontend
cd ../frontend
npm install
npm run dev
```

**Acceso:**
- Frontend: http://localhost:5173
- Usuarios API: http://localhost:8001
- Materias API: http://localhost:8002
- Aulas API: http://localhost:8003
- Horarios API: http://localhost:8004

### Credenciales de Prueba

```bash
# Admin
Email: admin@example.com
Password: 1234

# Docente
Email: docente@example.com
Password: 1234
```

---

## 📚 Documentación

### Guías Principales
| Documento | Propósito |
|-----------|----------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | 🚀 Guía completa de deployment a producción |
| [SEGURIDAD.md](SEGURIDAD.md) | 🔒 Mejores prácticas de seguridad |
| [services/README.md](services/README.md) | 🔧 Documentación de microservicios |
| [frontend/README.md](frontend/README.md) | ⚛️ Documentación del frontend |

### Documentación de Servicios
- [usuarios-service](services/usuarios-service/README.md)
- [horario-service](services/horario-service/README.md)
- [materias-service](services/materias-service/README.md)
- [aulas-service](services/aulas-service/README.md)

---

## 📁 Estructura del Proyecto

```
Microservicio_Horario/
├── 📄 DEPLOYMENT.md           # Guía deployment
├── 📄 SEGURIDAD.md            # Mejores prácticas seguridad
├── 📄 setup-secrets.sh        # Script para generar secrets
│
├── frontend/                  # React + Vite
│   ├── src/
│   │   ├── pages/            # Páginas principales
│   │   ├── components/       # Componentes reutilizables
│   │   ├── App.jsx           # Aplicación principal
│   │   └── App.css           # Estilos unificados
│   ├── package.json
│   └── vite.config.js
│
└── services/                  # Microservicios FastAPI
    ├── docker-compose.yml    # Orquestación servicios
    ├── .env.example          # Template de variables
    │
    ├── usuarios-service/     # Autenticación & Docentes
    ├── horario-service/      # Generación de horarios
    ├── materias-service/     # Catálogo de materias
    └── aulas-service/        # Inventario de aulas
```

---

## 💻 Desarrollo Local

### Sin Docker (Recomendado para desarrollo rápido)

#### 1. Configurar Backend

```bash
# Terminal 1: Usuarios Service
cd services/usuarios-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Generar secrets
export JWT_SECRET=$(openssl rand -hex 32)
export ADMIN_CREATION_KEY=$(openssl rand -hex 16)
uvicorn main:app --reload --port 8001

# Terminal 2: Horario Service
cd services/horario-service
# ... similar setup
uvicorn main:app --reload --port 8004

# ... repetir para materias y aulas
```

#### 2. Configurar Frontend

```bash
cd frontend
npm install
npm run dev
# Abre http://localhost:5173
```

### Con Docker (Recomendado para testing)

```bash
cd services
docker compose up --build
# Logs: docker compose logs -f

# Test un servicio
curl http://localhost:8001/health

# Entrar a bash en contenedor
docker compose exec horario-service bash
```

---

## 🧪 Testing

### Tests de Seguridad
```bash
# Usuarios service
cd services/usuarios-service
pip install pytest
pytest test_security.py -v

# Resultados esperados:
# ✓ test_login_without_credentials
# ✓ test_sql_injection_attempt
# ✓ test_xss_injection_attempt
# ✓ test_jwt_token_invalid
```

### Tests de Horario
```bash
cd services/horario-service
pytest tests/test_generar_horarios.py -v
```

### Testing en Frontend
```bash
cd frontend
npm run test              # Ejecutar tests
npm run test -- --coverage  # Con cobertura
```

---

## 🚀 Deployment

### Pre-Deployment Checklist
- [ ] Todos los tests pasando ✅
- [ ] Security scan completado
- [ ] Secrets rotados
- [ ] HTTPS configurado
- [ ] Rate limiting activado
- [ ] Logging centralizado

### Deployment a Producción
**Ver [DEPLOYMENT.md](DEPLOYMENT.md) para guía completa**

Quick summary:
```bash
# 1. Configurar secrets en AWS Secrets Manager
aws secretsmanager create-secret --name prod/horario-service ...

# 2. Build y push a registry
docker build -t horario-service:latest .
docker push <registry>/horario-service:latest

# 3. Deploy con Kubernetes o Docker Compose
kubectl apply -f k8s/
# O
docker compose up -d

# 4. Verificar health
curl https://api.tudominio.com/health
```

---

## 🔒 Seguridad

### Implementado (Fase 1)
✅ Secrets fuera del repositorio  
✅ JWT autenticación  
✅ Bcrypt password hashing  
✅ Rate limiting en auth  
✅ Validación Pydantic  
✅ SQL Injection prevention  
✅ XSS protection  
✅ CORS configurado  

### En Progreso (Fase 2)
🟡 Tests completos (80% cobertura)  
🟡 Logging estructurado  
🟡 Database indexes  
🟡 Batch endpoints  

### Roadmap (Fase 3)
🔲 HTTPS/SSL obligatorio  
🔲 Constraints de concurrencia  
🔲 Refresh tokens  
🔲 Monitoreo con Prometheus  
🔲 CI/CD con GitHub Actions  

**Ver [SEGURIDAD.md](SEGURIDAD.md) para detalles completos**

---

## 📊 Diagrama de Arquitectura

```
┌─────────────────────────────────────────┐
│          Frontend (React)                │
│       http://localhost:5173              │
└────────────────────┬────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Usuarios │   │ Horarios │   │ Materias │
│ Service  │   │ Service  │   │ Service  │
│ (8001)   │   │ (8004)   │   │ (8002)   │
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────┬───┴──────────┬───┘
                │              │
            ┌───▼────┐    ┌────▼───┐
            │ MySQL  │    │PostgreSQL│
            │        │    │          │
            └────────┘    └──────────┘
```

---

## 🆘 Troubleshooting

### "Connection refused" en servicios
```bash
# Verificar que Docker compose está corriendo
docker compose ps

# Revisar logs
docker compose logs horario-service

# Reiniciar
docker compose restart
```

### JWT inválido
```bash
# Regenerar secret y reiniciar
bash setup-secrets.sh
cd services && docker compose up -d
```

### Tests fallando
```bash
# Instalar dependencias
pip install -r services/usuarios-service/requirements.txt

# Correr tests con debug
pytest -vv --tb=short
```

---

## 📝 Cambios Recientes

### v1.2.0 - Fase 1 Seguridad ✨
- ✅ Implementado rate limiting
- ✅ Documentación de seguridad
- ✅ Script de setup de secrets
- ✅ Tests de seguridad básicos
- ✅ Deployment guide completo

### v1.1.0 - UX Improvements
- ✅ Toast notifications en esquina derecha
- ✅ Modal unificado para confirmaciones
- ✅ Botón editar en horarios
- ✅ PDF export mejorado

### v1.0.0 - MVP
- ✅ Autenticación JWT
- ✅ CRUD completo
- ✅ Generación automática horarios
- ✅ Frontend React + FullCalendar

---

## 🤝 Contribuyendo

1. Fork el repositorio
2. Crear rama de feature (`git checkout -b feature/amazing`)
3. Commit cambios (`git commit -am 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing`)
5. Abrir Pull Request

**Checklist antes de PR:**
- [ ] Tests pasando
- [ ] Sin `console.log` en código
- [ ] Sin secrets en commits
- [ ] README actualizado si es necesario

---

## 📄 Licencia

MIT License - Ver LICENSE.md

---

## 📧 Soporte

**Issues:** GitHub Issues  
**Email:** [equipo@example.com](mailto:equipo@example.com)  
**Docs:** [DEPLOYMENT.md](DEPLOYMENT.md) | [SEGURIDAD.md](SEGURIDAD.md)

---

**Última actualización:** 2026-05-07  
**Status:** 🟡 Pre-Producción (Fase 1 Seguridad Completada)
