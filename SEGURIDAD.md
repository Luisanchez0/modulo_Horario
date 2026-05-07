# 🔒 GUÍA DE SEGURIDAD - Microservicio Horario

## 📋 Tabla de Contenidos
1. [Secrets Management](#secrets-management)
2. [Autenticación & JWT](#autenticación--jwt)
3. [Rate Limiting](#rate-limiting)
4. [Validación de Input](#validación-de-input)
5. [HTTPS/TLS](#httpstls)
6. [SQL Injection Prevention](#sql-injection-prevention)
7. [XSS Prevention](#xss-prevention)
8. [CORS](#cors)
9. [Logging Seguro](#logging-seguro)
10. [Checklist de Seguridad](#checklist-de-seguridad)

---

## 🔑 Secrets Management

### ❌ LO QUE NO DEBES HACER
```bash
# NO commitar .env
git add services/.env  # ❌ NUNCA

# NO hardcodear en código
JWT_SECRET = "mi_clave_super_secreta"  # ❌ NUNCA

# NO compartir en Slack/Email
# "Aquí está la password de producción: ..."  # ❌ NUNCA
```

### ✅ LO CORRECTO

**Desarrollo Local:**
```bash
# 1. Generar secrets
bash setup-secrets.sh

# 2. Verificar que no está commiteado
git status  # .env should NOT appear

# 3. El archivo está protegido
cat services/.env  # ✅ Solo localmente
```

**Producción (AWS):**
```bash
# Usar AWS Secrets Manager
aws secretsmanager create-secret \
  --name prod/horario-service \
  --secret-string '{
    "JWT_SECRET": "...",
    "ADMIN_CREATION_KEY": "...",
    "INTERNAL_API_KEY": "..."
  }'

# En docker-compose.yml:
services:
  horario-service:
    secrets:
      - jwt_secret
    environment:
      JWT_SECRET: /run/secrets/jwt_secret
```

### Rotación de Secrets
```bash
# Cada 30 días en producción
# 1. Generar nuevo secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Actualizar en Vault
aws secretsmanager update-secret \
  --secret-id prod/horario-service \
  --secret-string '{"JWT_SECRET": "'$NEW_SECRET'"}'

# 3. Redeploy servicios (con 0 downtime)
docker compose up -d --no-deps --build horario-service
```

---

## 🔐 Autenticación & JWT

### Token JWT
- **Algoritmo:** HS256 (HMAC con SHA-256)
- **Expira en:** 24 horas (configurable)
- **Payload contiene:** id, correo, rol

```python
# Generar token (correcto)
from src.infrastructure.security.jwt import create_token

token = create_token(
    subject=docente.id,
    data={"rol": docente.rol}
)
# Resultado: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Validación de Token
```python
# Verificar token en requests
@router.get("/protected")
def protected_endpoint(authorization: str | None = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return {"user_id": payload["sub"], "rol": payload.get("rol")}
```

### Storage de Contraseñas
- **Hash:** bcrypt (NOT MD5, NOT plaintext)
- **Salt:** incluido automáticamente
- **Rounds:** 12 (default seguro)

```python
# Crear usuario
from src.infrastructure.security.hash import hash

hashed_pwd = hash("password123")
# Almacenar solo: $2b$12$...

# Verificar login
from src.infrastructure.security.hash import verify

if not verify("password123", stored_hash):
    raise ValueError("Password inválida")
```

---

## 🛡️ Rate Limiting

### Login Endpoint (CRÍTICO)
- **Límite:** 5 intentos por minuto
- **Implementación:** Nginx (producción) + slowapi (desarrollo)

```nginx
# /etc/nginx/nginx.conf
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

location /auth/login {
    limit_req zone=login burst=10 nodelay;
    proxy_pass http://backend;
}
```

**Respuesta cuando se excede:**
```json
{
  "status_code": 429,
  "detail": "Demasiadas solicitudes. Intenta de nuevo más tarde."
}
```

### API Endpoints (General)
- **Límite:** 100 requests por minuto
- **Burst:** 50 peticiones adicionales permitidas

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

location /horarios {
    limit_req zone=api burst=50 nodelay;
    proxy_pass http://backend;
}
```

---

## ✅ Validación de Input

### Pydantic Validators
Todos los endpoints usan Pydantic para validación automática:

```python
from pydantic import BaseModel, EmailStr, Field

class DocenteCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=255)
    correo: EmailStr  # Valida formato email
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('nombre')
    @classmethod
    def nombre_no_vacio(cls, v):
        if not v.strip():
            raise ValueError("Nombre no puede estar vacío")
        return v.strip()
```

**Errores rechazados automáticamente:**
- ✅ Emails inválidos
- ✅ Campos faltantes
- ✅ Tipos de dato incorrectos
- ✅ Strings vacíos

```bash
# Ejemplo: POST /auth/register con datos inválidos
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "",
    "correo": "not-an-email",
    "password": "123"
  }'

# Respuesta:
# 422 Unprocessable Entity
# {
#   "detail": [
#     {"loc": ["body", "nombre"], "msg": "..."}
#   ]
# }
```

---

## 🔒 HTTPS/TLS

### Desarrollo Local
```bash
# Sin HTTPS (OK para desarrollo)
http://localhost:5173
http://localhost:8001
```

### Producción (OBLIGATORIO)
```bash
# Configurar Let's Encrypt + Nginx
sudo certbot certonly --standalone -d api.tudominio.com

# Forzar HTTPS en Nginx
server {
    listen 80;
    server_name api.tudominio.com;
    return 301 https://$server_name$request_uri;  # ← Redirige a HTTPS
}

server {
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/api.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.tudominio.com/privkey.pem;
}
```

**Headers de Seguridad:**
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## 🛡️ SQL Injection Prevention

### ✅ PROTEGIDO: SQLAlchemy ORM
```python
# Seguro contra SQL injection
horarios = session.query(HorarioModel).filter(
    HorarioModel.docente_id == docente_id  # ← Parameterizado
).all()

# SQL ejecutado: SELECT * FROM horarios WHERE docente_id = %s
# El parámetro NUNCA se interpreta como SQL
```

### ❌ VULNERABLE: String interpolation
```python
# NUNCA hagas esto
query = f"SELECT * FROM horarios WHERE docente_id = {docente_id}"
# Si docente_id = "1; DROP TABLE horarios; --"
# SQL ejecutado: SELECT * FROM horarios WHERE docente_id = 1; DROP TABLE horarios; --
```

### Test de Inyección SQL
```bash
# Intentar inyección
curl http://localhost:8004/horarios?docente_id=1%27%20OR%20%271%27=%271

# Resultado esperado:
# 422 Unprocessable Entity (validación rechaza)
# Si llegara a BD:
# Postgres parametrizado buscaría literalmente "1' OR '1'='1"
# No encontraría nada (seguro)
```

---

## 🌐 XSS Prevention

### Frontend (React)
React escapa HTML automáticamente:

```jsx
// ✅ SEGURO: React escapa caracteres especiales
const mensaje = "<script>alert('xss')</script>";
return <div>{mensaje}</div>;
// Renderizado: &lt;script&gt;alert('xss')&lt;/script&gt;
```

### Backend (JSON)
```python
# ✅ SEGURO: JSON no ejecuta código
@router.get("/horarios")
def get_horarios():
    return {
        "data": "<script>alert('xss')</script>"
    }
# Cliente recibe JSON string, no HTML executable
```

### Test de XSS
```bash
curl http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "<img src=x onerror=alert(1)>",
    "correo": "test@example.com",
    "password": "Password123!"
  }'

# Respuesta: El payload se almacena como string, no se ejecuta
# Si se muestra en UI, React lo escapa: &lt;img src=x ...&gt;
```

---

## 🔄 CORS

### Configuración Actual
```python
# services/usuarios-service/main.py
CORSMiddleware(
    allow_origins=[
        "http://localhost:5173",  # Frontend
        "http://localhost:8001",  # Usuarios API
        "http://localhost:8002",  # Materias API
        "http://localhost:8003",  # Aulas API
        "http://localhost:8004",  # Horarios API
    ],
    allow_credentials=False,  # No permitir credenciales via CORS
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Para Producción
```python
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
# Configurar en .env: CORS_ALLOW_ORIGINS=https://app.tudominio.com

# ✅ NUNCA usar:
allow_origins=["*"]  # Permite cualquier origen (inseguro)
```

---

## 📝 Logging Seguro

### ✅ QUÉ LOGUEAR
```python
logger.info("Docente login", extra={
    'user_id': docente.id,
    'ip_address': request.client.host,
    'timestamp': datetime.utcnow()
})

logger.error("Auth failed", extra={
    'attempt_count': failed_attempts,
    'ip_address': request.client.host,
    'reason': 'invalid_credentials'
})
```

### ❌ QUÉ NO LOGUEAR
```python
# NUNCA loguear
logger.info(f"Login con password {password}")  # ❌
logger.info(f"JWT token: {token}")             # ❌
logger.info(docente.contraseña_hash)            # ❌
logger.info(f"Secrets: {os.getenv('JWT_SECRET')}")  # ❌
```

### Configuración Logging en Producción
```python
import logging.handlers
import json

# Logging a archivo rotativo (no en stdout)
handler = logging.handlers.RotatingFileHandler(
    '/var/log/microservicio/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10      # Keep 10 backups
)

# Formato JSON para ELK Stack
formatter = logging.Formatter(json.dumps({
    'timestamp': '%(asctime)s',
    'level': '%(levelname)s',
    'service': 'horario-service',
    'message': '%(message)s'
}))

logger.addHandler(handler)
```

---

## ☑️ Checklist de Seguridad

### Antes de Desarrollo
- [ ] Generar secrets con `bash setup-secrets.sh`
- [ ] Verificar `.env` en `.gitignore`
- [ ] No hacer commit de `.env`

### Antes de Push a GitHub
```bash
# Verificar que no hay secrets
git diff --cached | grep -i "password\|secret\|key" && echo "PELIGRO" || echo "OK"

# Verificar .env no está tracked
git status | grep ".env"  # No debe aparecer
```

### Antes de Deployment
- [ ] Regenerar todos los secrets
- [ ] Configurar HTTPS en Nginx
- [ ] Habilitar rate limiting
- [ ] Configurar logging centralizado
- [ ] Hacer security test

### En Producción (Semanal)
- [ ] Revisar logs de acceso
- [ ] Verificar alertas de rate limiting
- [ ] Revisar failed login attempts
- [ ] Actualizar certificados SSL

### En Producción (Mensual)
- [ ] Rotar secrets
- [ ] Patch de dependencias
- [ ] Security audit
- [ ] Backup testing

---

## 🆘 Incidente de Seguridad

**Si descubres un secret fue commiteado:**

```bash
# 1. INMEDIATAMENTE revocar el secret
# 2. Generar nuevo secret
# 3. Rewrite git history (si aún no en main)
git filter-branch --tree-filter 'rm -f services/.env' -- --all
git push origin --force --all

# 4. Notificar al equipo
# 5. Regenerar en todos los ambientes
```

---

**Última actualización:** 2026-05-07  
**Responsable:** Equipo de Seguridad
