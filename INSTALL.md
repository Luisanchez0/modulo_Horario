# 🚀 GUÍA DE INSTALACIÓN

> Instrucciones para instalar y ejecutar Microservicio Horario localmente.

---

## 📋 Requisitos Previos

### Sistema Operativo
- Linux (Ubuntu 20.04+, Debian 10+)
- macOS (10.15+)
- Windows 10/11 + WSL2

### Software Requerido
- **Docker** & **Docker Compose** (recomendado)
- **Node.js** 18+ (para frontend)
- **Python** 3.9+ (si ejecutas servicios sin Docker)
- **Git**
- **openssl** (para generar secrets)

---

## 🐳 Instalación Rápida (Con Docker - Recomendado)

### 1️⃣ Clonar repositorio

```bash
git clone https://github.com/tu-usuario/Microservicio_Horario.git
cd Microservicio_Horario
```

### 2️⃣ Generar secrets seguros

```bash
bash setup-secrets.sh
# Genera archivo services/.env con secrets automáticos
```

**Output esperado:**
```
✅ Archivo .env creado exitosamente
JWT_SECRET:          a3f5b8c2d9e1...
ADMIN_CREATION_KEY:  8f2c5a9b...
...
🚀 Listo para desarrollo local
```

### 3️⃣ Iniciar servicios con Docker Compose

```bash
cd services
docker compose up --build
```

**Espera hasta ver:**
```
✅ usuarios-service_1     | Uvicorn running on http://0.0.0.0:8000
✅ horario-service_1      | Uvicorn running on http://0.0.0.0:8000
✅ materias-service_1     | Uvicorn running on http://0.0.0.0:8000
✅ aulas-service_1        | Uvicorn running on http://0.0.0.0:8000
```

### 4️⃣ En otra terminal, iniciar frontend

```bash
cd frontend
npm install
npm run dev
```

**Output esperado:**
```
✅ VITE v8.0.9  ready in 245 ms
➜  Local:   http://localhost:5173/
➜  press h + enter to show help
```

### 5️⃣ Abre en navegador

```
http://localhost:5173
```

---

## 📱 Credenciales de Prueba

### Admin
- **Email:** admin@example.com
- **Password:** 1234

### Docente
- **Email:** docente@example.com
- **Password:** 1234

> ⚠️ **Nota:** Estas son credenciales de desarrollo. Cambiar en producción.

---

## 🔧 Instalación Manual (Sin Docker)

### Requisito: Bases de Datos Locales

Instalar MySQL y PostgreSQL:

```bash
# Ubuntu/Debian
sudo apt install mysql-server postgresql postgresql-contrib

# macOS
brew install mysql postgresql
```

Crear bases de datos:

```bash
# MySQL
mysql -u root -p
CREATE DATABASE docentes_db;
exit;

# PostgreSQL
psql -U postgres
CREATE DATABASE postgres;
\q
```

### Backend - Usuarios Service

```bash
cd services/usuarios-service

# Virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# o: venv\Scripts\activate  (Windows)

# Instalar dependencias
pip install -r requirements.txt

# Generar secrets
export JWT_SECRET=$(openssl rand -hex 32)
export ADMIN_CREATION_KEY=$(openssl rand -hex 16)

# Ejecutar
uvicorn main:app --reload --port 8001
```

### Backend - Horario Service

```bash
cd services/horario-service

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export DATABASE_URL="postgresql://postgres:password@localhost:5432/postgres"
export JWT_SECRET=$(openssl rand -hex 32)

uvicorn main:app --reload --port 8004
```

**Repetir similar para:**
- `services/materias-service` (puerto 8002)
- `services/aulas-service` (puerto 8003)

### Frontend

```bash
cd frontend

npm install
npm run dev
```

---

## 🧪 Verificar Que Todo Funciona

### Test Health Endpoints

```bash
# Usuarios service
curl http://localhost:8001/health

# Horario service
curl http://localhost:8004/health

# Materias service
curl http://localhost:8002/health

# Aulas service
curl http://localhost:8003/health
```

**Respuesta esperada:**
```json
{
  "status": "ok"
}
```

### Test Login

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "correo": "admin@example.com",
    "password": "1234"
  }'
```

**Respuesta esperada:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 📁 Estructura del Proyecto

```
Microservicio_Horario/
├── frontend/                    # React + Vite
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── services/                    # Microservicios FastAPI
│   ├── docker-compose.yml
│   ├── usuarios-service/
│   ├── horario-service/
│   ├── materias-service/
│   └── aulas-service/
│
├── SEGURIDAD.md                 # Guía de seguridad
├── DEPLOYMENT.md                # Deployment a producción
├── INSTALL.md                   # Este archivo
├── README.md                    # Documentación general
└── setup-secrets.sh             # Script para generar secrets
```

---

## 🆘 Troubleshooting

### Error: "Port already in use"

```bash
# Encontrar qué está usando el puerto
lsof -i :8001  # Cambiar número de puerto según necesites

# Matar el proceso
kill -9 <PID>

# O usar otro puerto
uvicorn main:app --port 8005
```

### Error: "Cannot find module"

```bash
# Frontend
cd frontend
npm install

# Backend (dentro de venv)
pip install -r requirements.txt
```

### Docker: "permission denied"

```bash
sudo usermod -aG docker $USER
newgrp docker
# Re-login o restart terminal
```

### "Connection refused" en servicios

```bash
# Verificar Docker está corriendo
docker ps

# Ver logs
docker compose logs -f

# Reiniciar
docker compose restart
```

### Database connection error

```bash
# Verificar MySQL está corriendo
sudo systemctl status mysql

# Verificar PostgreSQL está corriendo
sudo systemctl status postgresql

# Reiniciar si es necesario
sudo systemctl restart mysql
sudo systemctl restart postgresql
```

---

## 📚 Documentación Importante

| Documento | Propósito |
|-----------|----------|
| [README.md](README.md) | Visión general del proyecto |
| [SEGURIDAD.md](SEGURIDAD.md) | Buenas prácticas de seguridad |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Guía para producción |
| [INSTALL.md](INSTALL.md) | Este archivo (instalación) |

---

## 🎯 Próximos Pasos

Después de instalar:

1. **Explorar UI**
   - Dashboard
   - Crear usuarios
   - Crear horarios
   - Ver calendario

2. **Ejecutar Tests**
   ```bash
   cd services/usuarios-service
   pytest test_security.py -v
   ```

3. **Leer Documentación**
   - [SEGURIDAD.md](SEGURIDAD.md) - Cómo está protegido
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Cómo deployar a producción

4. **Contribuir**
   - Ver instrucciones en [README.md](README.md#contribuyendo)

---

## 💡 Tips Útiles

### Ver logs en tiempo real

```bash
# Docker
docker compose logs -f horario-service

# Specific service
docker compose logs -f --tail=50 usuarios-service

# All services
docker compose logs -f
```

### Entrar a un contenedor

```bash
docker compose exec usuarios-service bash
# Ahora estás dentro del contenedor
ls -la
python -c "import fastapi; print(fastapi.__version__)"
```

### Resetear base de datos

```bash
docker compose down -v  # Remove volumes
docker compose up --build  # Recrear (se inicializa vacío)
```

### Rebuild sin cache

```bash
docker compose build --no-cache
docker compose up
```

---

## 📞 ¿Ayuda?

- **Issues:** Abre un GitHub issue con detalles
- **Docs:** Consulta [README.md](README.md) y [SEGURIDAD.md](SEGURIDAD.md)
- **Logs:** Siempre útiles para debugging

---

**¡Listo para comenzar! 🚀**

Si todo funciona, deberías ver:
- ✅ Frontend en http://localhost:5173
- ✅ Puedas loguearte con admin@example.com / 1234
- ✅ Servicios respondiendo en localhost:8001-8004
