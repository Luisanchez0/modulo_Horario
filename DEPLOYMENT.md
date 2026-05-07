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
