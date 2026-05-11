# 🚀 Deployment Guide - Microservicio Horario

## ⚠️ CHECKLIST SEGURIDAD ANTES DE PRODUCCIÓN

- [ ] Regenerar TODOS los secrets (JWT_SECRET, ADMIN_CREATION_KEY, etc.)
- [ ] Usar AWS Secrets Manager / HashiCorp Vault (NO .env files)
- [ ] Configurar HTTPS/SSL obligatorio
- [ ] Habilitar rate limiting en endpoints públicos
- [ ] Agregar firewall rules
- [ ] Configurar logging centralizado (ELK Stack / CloudWatch)
- [ ] Hacer backup de BD antes de deployment
- [ ] Monitoreo (Prometheus + Grafana)

---

## 🔒 GESTIÓN DE SECRETS

### Local Development
```bash
# Copiar template
cp services/.env.example services/.env

# Generar secrets fuertes (requiere openssl)
openssl rand -hex 32  # JWT_SECRET
openssl rand -hex 16  # ADMIN_CREATION_KEY
openssl rand -hex 16  # INTERNAL_API_KEY

# Reemplazar en services/.env
export JWT_SECRET=<generated_value>
export ADMIN_CREATION_KEY=<generated_value>
```

### Production (AWS)
```bash
# Usar AWS Secrets Manager
aws secretsmanager create-secret \
  --name microservicio-horario/jwt \
  --secret-string '{
    "JWT_SECRET": "...",
    "ADMIN_CREATION_KEY": "...",
    "INTERNAL_API_KEY": "..."
  }'

# Luego en docker-compose.yml:
services:
  horario-service:
    environment:
      - JWT_SECRET=/run/secrets/jwt_secret
    secrets:
      - jwt_secret
```

---

## 🐳 DOCKER DEPLOYMENT

### Build Images
```bash
cd services
docker compose build
```

### Local Testing
```bash
# Sin .env expuesto
docker compose up -d

# Verificar healthchecks
docker compose ps

# Ver logs
docker compose logs -f horario-service
```

### Production Dockerfile Improvements
Agregar a cada `Dockerfile`:

```dockerfile
# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8004/health || exit 1

# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser
```

---

## 🚀 DESPLIEGUE RÁPIDO EN EC2 + DOCKER COMPOSE

Este es el camino más corto para poner el proyecto en AWS sin rediseñarlo. La idea es levantar todo en una sola instancia EC2: frontend, microservicios, MySQL y PostgreSQL.

### 1. Arquitectura mínima

- 1 EC2 con Ubuntu 22.04
- 1 Elastic IP para tener una IP fija
- Docker + Docker Compose instalados en la instancia
- 1 dominio opcional apuntando a la IP pública o, mejor, a un reverse proxy con Nginx
- 1 volumen EBS para persistir datos de Docker

### 2. Recursos AWS a crear

1. Crear una instancia EC2 tipo `t3.medium` como mínimo; `t3.large` si quieres más margen.
2. Asociar una Elastic IP.
3. Abrir en el Security Group solo estos puertos:
  - `22` para SSH, restringido a tu IP
  - `80` para HTTP
  - `443` para HTTPS
  - Evitar exponer `8001-8004`, `3307` y `5433` al público
4. Crear o montar un volumen EBS si quieres conservar datos de forma persistente.

### 3. Preparar la instancia

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl git unzip

# Instalar Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

# Instalar Docker Compose plugin
docker compose version
```

### 4. Subir el código

```bash
git clone <TU_REPO>
cd Microservicio_Horario/services
```

Si no vas a usar Git en la EC2, también puedes subir el proyecto con `scp` o con un pipeline de CI/CD.

### 5. Configurar variables de entorno

En `services/.env` usa secretos reales, no valores de ejemplo:

```bash
MYSQL_ROOT_PASSWORD=<password_fuerte>
MYSQL_DATABASE=docentes_db

POSTGRES_USER=postgres
POSTGRES_PASSWORD=<password_fuerte>
POSTGRES_DB=postgres

JWT_SECRET=<secret_largo>
ADMIN_CREATION_KEY=<secret_largo>
INTERNAL_API_KEY=<secret_largo>

CORS_ALLOW_ORIGINS=http://<IP_O_DOMINIO_FRONTEND>,http://localhost:5173
```

### 6. Levantar el stack

```bash
docker compose up -d --build
docker compose ps
```

### 7. Verificación básica

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

Si todo responde bien, ya puedes abrir el frontend desde el navegador usando el dominio o la IP pública de la EC2.

### 8. Frontend en producción

Antes del build, apunta las variables `VITE_*` al backend público:

```bash
cd ../frontend
export VITE_USUARIOS_API_URL=http://<IP_O_DOMINIO>:8001
export VITE_MATERIAS_API_URL=http://<IP_O_DOMINIO>:8002
export VITE_AULAS_API_URL=http://<IP_O_DOMINIO>:8003
export VITE_HORARIO_API_URL=http://<IP_O_DOMINIO>:8004
npm install
npm run build
```

Si quieres servir el frontend desde la misma EC2, usa Nginx para publicar `dist/` y hacer proxy hacia los servicios internos.

### 9. Reverse proxy recomendado

Lo más limpio es poner Nginx en la misma EC2 y dejarlo escuchando en `80/443`.

- `/` sirve el frontend
- `/auth`, `/docentes`, `/api/v1/materias`, `/aulas`, `/horarios` hacen proxy a los microservicios
- `80` redirige a `443`
- `443` usa un certificado de Let's Encrypt

### 10. Operación diaria

```bash
# Ver logs
docker compose logs -f

# Reiniciar un servicio
docker compose restart horario-service

# Actualizar despliegue
git pull
docker compose up -d --build

# Detener todo
docker compose down
```

### 11. Checklist final

- [ ] EC2 con IP fija
- [ ] Docker instalado
- [ ] `.env` con secretos reales
- [ ] Puertos públicos limitados a `80/443`
- [ ] Backend levantado con `docker compose up -d --build`
- [ ] Frontend compilado con URLs correctas
- [ ] HTTPS activo con Nginx y certificado válido

---

## 🌐 NGINX REVERSE PROXY + SSL

### Setup
```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado (Let's Encrypt)
sudo certbot certonly --standalone \
  -d api.tudominio.com \
  -d www.tudominio.com
```

### /etc/nginx/nginx.conf
```nginx
upstream horario_backend {
    server localhost:8004;
}
upstream usuarios_backend {
    server localhost:8001;
}
upstream materias_backend {
    server localhost:8002;
}
upstream aulas_backend {
    server localhost:8003;
}

server {
    listen 80;
    server_name api.tudominio.com;
    return 301 https://$server_name$request_uri;  # Redirect to HTTPS
}

server {
    listen 443 ssl http2;
    server_name api.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/api.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.tudominio.com/privkey.pem;
    
    # Seguridad SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=loginzone:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=apizone:10m rate=100r/m;

    location /auth/login {
        limit_req zone=loginzone burst=10 nodelay;
        proxy_pass http://usuarios_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /horarios {
        limit_req zone=apizone burst=50 nodelay;
        proxy_pass http://horario_backend;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
    }

    location /docentes {
        limit_req zone=apizone burst=50 nodelay;
        proxy_pass http://usuarios_backend;
    }

    location /api/v1/materias {
        limit_req zone=apizone burst=50 nodelay;
        proxy_pass http://materias_backend;
    }

    location /aulas {
        limit_req zone=apizone burst=50 nodelay;
        proxy_pass http://aulas_backend;
    }
}
```

### Iniciar Nginx
```bash
sudo systemctl restart nginx
sudo systemctl status nginx

# Verificar certificado Auto-renovación
sudo systemctl enable certbot.timer
```

---

## 📊 DATABASE SETUP (PRODUCCIÓN)

### AWS RDS
```bash
# Crear PostgreSQL RDS
aws rds create-db-instance \
  --db-instance-identifier microservicio-horario-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password '<STRONG_PASSWORD>' \
  --allocated-storage 20 \
  --publicly-accessible false

# Obtener endpoint
aws rds describe-db-instances \
  --db-instance-identifier microservicio-horario-db
```

### Ejecutar Migrations
```bash
# En horario-service
export DATABASE_URL="postgresql://postgres:password@rds-endpoint:5432/horarios"
alembic upgrade head
```

---

## 📝 LOGGING & MONITORING

### Logging Centralizado (ELK Stack)

#### Docker Compose Addon
```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    ports:
      - "5601:5601"

  horario-service:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

#### En cada microservicio (Python)
```python
import logging.handlers
import json

# Structured logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    json.dumps({
        'timestamp': '%(asctime)s',
        'level': '%(levelname)s',
        'service': 'horario-service',
        'message': '%(message)s'
    })
)
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.post("/horarios")
def crear_horario(...):
    logger.info("Creating schedule", extra={
        'user_id': current_user.id,
        'docente_id': payload.docente_id
    })
```

### Monitoreo (Prometheus)
```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

---

## 🧪 TESTING ANTES DE DEPLOYMENT

### Load Testing
```bash
# Instalar Apache Bench
sudo apt-get install apache2-utils

# Test endpoint horarios
ab -n 1000 -c 10 http://localhost:8004/horarios
```

### Security Testing
```bash
# OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8004

# SQL Injection test
curl "http://localhost:8004/horarios?docente_id=1' OR '1'='1"
# Debe retornar error validación, NO datos

# JWT test
curl -H "Authorization: invalid.jwt.token" \
  http://localhost:8004/horarios
# Debe retornar 401/403
```

---

## 🔄 CI/CD (GITHUB ACTIONS)

### .github/workflows/deploy.yml
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: cd services && docker compose -f docker-compose.test.yml up

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: cd services && docker compose build
      
      - name: Push to ECR
        run: |
          aws ecr get-login-password --region ${{ secrets.AWS_REGION }} | \
          docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}
          docker tag microservicio-horario ${{ secrets.ECR_REGISTRY }}/horario-service:latest
          docker push ${{ secrets.ECR_REGISTRY }}/horario-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: SSH Deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /app/microservicio-horario
            docker pull ${{ secrets.ECR_REGISTRY }}/horario-service:latest
            docker compose up -d
```

---

## 📋 PRODUCCIÓN CHECKLIST FINAL

**Antes de Go-Live:**
- [ ] Todos los tests pasando ✅
- [ ] Security scan completado
- [ ] Load testing exitoso (1000+ req/s)
- [ ] Backup automatizado configurado
- [ ] Alertas de monitoring en lugar
- [ ] Runbook de rollback disponible
- [ ] Equipo on-call configurado
- [ ] Logs centralizados funcionando
- [ ] SSL/TLS activo y certificado válido
- [ ] Rate limiting activo en todos endpoints

**Post-Launch:**
- [ ] Monitorear métricas (CPU, memoria, latencia)
- [ ] Revisar logs cada hora primera semana
- [ ] Plan de escalado si load aumenta

---

## 🆘 TROUBLESHOOTING

### Service no responde
```bash
# Ver logs
docker compose logs horario-service | tail -100

# Verificar health
curl http://localhost:8004/health

# Restart
docker compose restart horario-service
```

### Database connection error
```bash
# Verificar conexión
psql postgresql://user:pass@host:5432/db

# Check migrations
docker compose exec horario-service alembic current
```

### JWT inválido
```bash
# Regenerar con setup correcto
openssl rand -hex 32
# Actualizar secrets
docker compose restart
```

---

**Contacto Soporte:** [correo del equipo]  
**Última actualización:** 2026-05-07
