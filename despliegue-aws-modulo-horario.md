# 🚀 Guía de Despliegue — modulo_Horario en AWS

> **Proyecto:** [Luisanchez0/modulo_Horario](https://github.com/Luisanchez0/modulo_Horario)
> **Stack:** FastAPI + React + MySQL + PostgreSQL + Docker
> **Objetivo:** Despliegue completo en AWS EC2 con DuckDNS + HTTPS gratuito

---

## Índice

1. [Preparación en AWS](#fase-1--preparación-en-aws)
2. [VPC y Security Group](#fase-2--vpc-y-security-group)
3. [EC2 + Elastic IP](#fase-3--ec2--elastic-ip)
4. [Configurar el servidor](#fase-4--configurar-el-servidor)
5. [DuckDNS — Dominio gratuito](#fase-5--duckdns--dominio-gratuito)
6. [Clonar el proyecto](#fase-6--clonar-el-proyecto)
7. [Configurar variables de entorno](#fase-7--configurar-variables-de-entorno)
8. [Nginx como Reverse Proxy](#fase-8--nginx-como-reverse-proxy)
9. [HTTPS con Certbot](#fase-9--https-con-certbot)
10. [Levantar servicios](#fase-10--levantar-servicios)
11. [Verificar y solucionar problemas](#fase-11--verificar-y-solucionar-problemas)
12. [Comandos útiles en producción](#extra--comandos-útiles-en-producción)

---

## Arquitectura del proyecto

```
┌─────────────────────────────────────────────────┐
│  Internet                                        │
│  https://tu-app.duckdns.org                      │
└────────────────────┬────────────────────────────┘
                     │ Puerto 443 (HTTPS)
              ┌──────▼──────┐
              │    Nginx    │  Reverse Proxy
              └──────┬──────┘
       ┌─────────────┼──────────────┬──────────────┐
       ▼             ▼              ▼               ▼
  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Frontend │  │ usuarios │  │materias  │  │  aulas   │
  │  Vite   │  │ service  │  │ service  │  │ service  │
  │ :5173   │  │  :8001   │  │  :8002   │  │  :8003   │
  └─────────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
                    │              │              │
               ┌────▼──────────────▼──────────────▼────┐
               │              horario-service            │
               │                  :8004                  │
               └───────────────────────────────────────┘
                    │                        │
             ┌──────▼──────┐        ┌────────▼──────┐
             │    MySQL    │        │  PostgreSQL   │
             │   :3307     │        │    :5433      │
             └─────────────┘        └───────────────┘
```

---

## Fase 1 — Preparación en AWS

### 1.1 Crear cuenta AWS

1. Ve a [aws.amazon.com](https://aws.amazon.com)
2. Clic en **"Create an AWS Account"**
3. Completa el registro (necesitas tarjeta de crédito)
4. El **Free Tier** incluye EC2 t2.micro **gratis 12 meses**

> 💡 Activa MFA desde `IAM → Security Credentials` para proteger tu cuenta.

### 1.2 Crear Key Pair (.pem)

```
AWS Console → EC2 → Network & Security → Key Pairs
→ Create key pair
   Nombre:  horario-key
   Tipo:    RSA
   Formato: .pem
→ Descargar horario-key.pem  ← solo se descarga una vez
```

> ⚠️ Guarda el `.pem` en un lugar seguro. Sin él no puedes acceder al servidor.

---

## Fase 2 — VPC y Security Group

### 2.1 VPC

**No necesitas crear una VPC nueva.** AWS ya tiene una por defecto lista para usar.

### 2.2 Crear Security Group

```
EC2 → Security Groups → Create Security Group

   Nombre:      sg-modulo-horario
   Descripción: Firewall para modulo_Horario

Inbound rules:
   SSH   | TCP | 22  | Mi IP  ← solo tu IP para SSH
   HTTP  | TCP | 80  | 0.0.0.0/0
   HTTPS | TCP | 443 | 0.0.0.0/0

Outbound rules:
   All traffic → 0.0.0.0/0  (dejar por defecto)
```

> ⚠️ **NO** abras los puertos 8001, 8002, 8003, 8004, 3307 ni 5433 al público.
> Los servicios solo deben ser accesibles a través de Nginx.

---

## Fase 3 — EC2 + Elastic IP

### 3.1 Lanzar instancia EC2

```
EC2 → Instances → Launch Instance

   Name:           modulo-horario-server
   AMI:            Ubuntu Server 22.04 LTS  (Free tier eligible)
   Instance type:  t2.micro                 (free tier)
   Key pair:       horario-key
   Security Group: sg-modulo-horario
   Storage:        20 GB gp3

→ Launch Instance
```

### 3.2 Asignar Elastic IP

Sin Elastic IP la IP de tu servidor cambia cada reinicio y el DNS deja de funcionar.

```
EC2 → Elastic IPs → Allocate Elastic IP address → Allocate

Asociar a tu instancia:
   Actions → Associate Elastic IP address
   Instance: modulo-horario-server
   → Associate
```

> 📌 Anota tu Elastic IP — la necesitarás en DuckDNS.

---

## Fase 4 — Configurar el servidor

### 4.1 Conectar por SSH

```bash
# Mac / Linux — dar permisos al archivo .pem
chmod 400 horario-key.pem

# Conectar
ssh -i horario-key.pem ubuntu@TU_ELASTIC_IP
```

> 💡 En Windows usa **Windows Terminal** o **PuTTY**.

### 4.2 Instalar Docker

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker (script oficial)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker ubuntu

# Instalar Docker Compose plugin
sudo apt install docker-compose-plugin -y

# Verificar
docker --version
docker compose version

# Aplicar grupo — IMPORTANTE: cerrar sesión y reconectar
exit
ssh -i horario-key.pem ubuntu@TU_ELASTIC_IP
```

### 4.3 Instalar Nginx y Certbot

```bash
sudo apt install nginx certbot python3-certbot-nginx -y

# Verificar que Nginx está corriendo
sudo systemctl status nginx
```

### 4.4 Instalar Git

```bash
sudo apt install git -y
```

---

## Fase 5 — DuckDNS — Dominio gratuito

### 5.1 Crear el subdominio

1. Ve a [duckdns.org](https://www.duckdns.org)
2. Inicia sesión con Google, GitHub o Reddit
3. En el campo **"sub domain"** escribe tu nombre:
   ```
   modulo-horario   →   modulo-horario.duckdns.org
   ```
4. Clic en **"add domain"**
5. Pon tu **Elastic IP** en el campo de IP
6. Clic en **"update ip"**
7. Copia tu **TOKEN** (está arriba de la página, es un UUID)

### 5.2 Script de actualización automática en EC2

```bash
# En el servidor
mkdir ~/duckdns && cd ~/duckdns
nano duck.sh
```

Pega esto (reemplaza `TU_SUBDOMINIO` y `TU_TOKEN`):

```bash
echo url="https://www.duckdns.org/update?domains=TU_SUBDOMINIO&token=TU_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

```bash
# Guardar: Ctrl+O → Enter → Ctrl+X

# Permisos de ejecución
chmod 700 duck.sh

# Probar
./duck.sh
cat duck.log     # debe mostrar: OK

# Ejecutar automáticamente cada 5 minutos
crontab -e
# Agrega al final:
*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

### 5.3 Verificar que el DNS funciona

```bash
# Desde tu máquina local (espera 2-5 minutos)
nslookup modulo-horario.duckdns.org
# Debe mostrar tu Elastic IP
```

---

## Fase 6 — Clonar el proyecto

```bash
# En el servidor EC2
cd /home/ubuntu
git clone https://github.com/Luisanchez0/modulo_Horario.git
cd modulo_Horario
```

Estructura que verás:
```
modulo_Horario/
├── frontend/          ← React + Vite
├── services/          ← Microservicios FastAPI
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── usuarios-service/   (puerto 8001)
│   ├── materias-service/   (puerto 8002)
│   ├── aulas-service/      (puerto 8003)
│   ├── horario-service/    (puerto 8004)
│   └── docker/
│       ├── mysql-init/
│       └── postgres-init/
└── README.md
```

---

## Fase 7 — Configurar variables de entorno

### 7.1 Generar secrets seguros

```bash
# Generar passwords seguras
echo "MYSQL_ROOT_PASSWORD:"   && openssl rand -base64 24
echo "POSTGRES_PASSWORD:"     && openssl rand -base64 24
echo "JWT_SECRET:"            && openssl rand -hex 32
echo "ADMIN_CREATION_KEY:"    && openssl rand -hex 16
echo "INTERNAL_API_KEY:"      && openssl rand -hex 16
```

Copia los valores generados — los usarás en el `.env`.

### 7.2 Crear el archivo .env

```bash
cd /home/ubuntu/modulo_Horario/services
cp .env.example .env
nano .env
```

Contenido del `.env` para producción:

```env
# ── MySQL ────────────────────────────────────────────────────────
MYSQL_ROOT_PASSWORD=pon_aqui_el_password_mysql_generado
MYSQL_DATABASE=docentes_db

# ── PostgreSQL ───────────────────────────────────────────────────
POSTGRES_USER=postgres
POSTGRES_PASSWORD=pon_aqui_el_password_postgres_generado
POSTGRES_DB=postgres

# ── Seguridad ────────────────────────────────────────────────────
JWT_SECRET=pon_aqui_el_jwt_secret_generado_de_64_chars
ADMIN_CREATION_KEY=pon_aqui_el_admin_key_generado
INTERNAL_API_KEY=pon_aqui_el_internal_key_generado

# ── CORS — tu dominio DuckDNS ────────────────────────────────────
CORS_ALLOW_ORIGINS=https://modulo-horario.duckdns.org
```

> ⚠️ Nunca uses los valores por defecto (`change_me_...`) en producción.

---

## Fase 8 — Nginx como Reverse Proxy

### 8.1 Crear la configuración

```bash
sudo nano /etc/nginx/sites-available/modulo-horario
```

Pega esta configuración completa:

```nginx
server {
    listen 80;
    server_name modulo-horario.duckdns.org;

    # ── Frontend React/Vite ─────────────────────────────────────
    location / {
        proxy_pass http://localhost:5173/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # ── usuarios-service :8001 ──────────────────────────────────
    location /api/usuarios/ {
        proxy_pass http://localhost:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ── materias-service :8002 ──────────────────────────────────
    location /api/materias/ {
        proxy_pass http://localhost:8002/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ── aulas-service :8003 ─────────────────────────────────────
    location /api/aulas/ {
        proxy_pass http://localhost:8003/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ── horario-service :8004 ───────────────────────────────────
    location /api/horario/ {
        proxy_pass http://localhost:8004/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 8.2 Activar y verificar

```bash
# Activar el sitio
sudo ln -s /etc/nginx/sites-available/modulo-horario /etc/nginx/sites-enabled/

# Eliminar el sitio default si interfiere
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar sintaxis — debe decir: syntax is ok
sudo nginx -t

# Aplicar cambios
sudo systemctl reload nginx
```

---

## Fase 9 — HTTPS con Certbot

### 9.1 Generar certificado SSL gratuito

```bash
sudo certbot --nginx -d modulo-horario.duckdns.org
```

Responde al asistente:
```
Enter email address: tu@email.com
Agree to terms: Y
Share email with EFF: N
```

Certbot **modifica Nginx automáticamente** para:
- Activar HTTPS en el puerto 443
- Redirigir HTTP → HTTPS

### 9.2 Verificar renovación automática

Los certificados duran 90 días y se renuevan solos:

```bash
sudo certbot renew --dry-run
# Debe mostrar: Congratulations, all simulated renewals succeeded
```

---

## Fase 10 — Levantar servicios

### 10.1 Levantar los microservicios (backend)

```bash
cd /home/ubuntu/modulo_Horario/services

# Primera vez: construir imágenes y levantar
docker compose up -d --build

# Ver que todos están corriendo
docker compose ps
```

La salida esperada:
```
NAME                STATUS
mysql               Up (healthy)
postgres            Up (healthy)
usuarios-service    Up
materias-service    Up
aulas-service       Up
horario-service     Up
```

### 10.2 Levantar el frontend (React/Vite)

El frontend de Vite en modo `dev` no es apto para producción. Tienes dos opciones:

**Opción A — Build estático (recomendado para producción):**

```bash
# Instalar Node.js en el servidor
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Ir al frontend y construir
cd /home/ubuntu/modulo_Horario/frontend
npm install
npm run build

# El build queda en frontend/dist/
# Configurar Nginx para servir archivos estáticos
```

Actualiza la sección del frontend en Nginx:
```nginx
location / {
    root /home/ubuntu/modulo_Horario/frontend/dist;
    try_files $uri $uri/ /index.html;
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

**Opción B — Modo dev (solo para pruebas rápidas):**

```bash
cd /home/ubuntu/modulo_Horario/frontend
npm install
npm run dev -- --host 0.0.0.0
```

> ⚠️ La Opción A (build estático) es la correcta para producción. Es más rápida, segura y no requiere Node.js corriendo.

---

## Fase 11 — Verificar y solucionar problemas

### 11.1 Verificar cada servicio

```bash
# Probar servicios directamente en el servidor
curl http://localhost:8001/docs   # Swagger usuarios
curl http://localhost:8002/docs   # Swagger materias
curl http://localhost:8003/docs   # Swagger aulas
curl http://localhost:8004/docs   # Swagger horario

# Probar a través de Nginx con HTTPS
curl https://modulo-horario.duckdns.org/api/usuarios/health
```

### 11.2 Rutas disponibles en producción

| URL | Descripción |
|-----|-------------|
| `https://modulo-horario.duckdns.org/` | Frontend React |
| `https://modulo-horario.duckdns.org/api/usuarios/` | Usuarios Service :8001 |
| `https://modulo-horario.duckdns.org/api/usuarios/docs` | Swagger usuarios |
| `https://modulo-horario.duckdns.org/api/materias/` | Materias Service :8002 |
| `https://modulo-horario.duckdns.org/api/aulas/` | Aulas Service :8003 |
| `https://modulo-horario.duckdns.org/api/horario/` | Horario Service :8004 |

### 11.3 Credenciales de prueba

```
Admin:
  Email:    admin@example.com
  Password: 1234

Docente:
  Email:    docente@example.com
  Password: 1234
```

> 🔒 Cambia estas credenciales en producción desde el panel de administración.

### 11.4 Solución de problemas comunes

| Error | Causa probable | Solución |
|-------|---------------|----------|
| `502 Bad Gateway` | Servicio no levantó | `docker compose logs -f nombre-servicio` |
| `Connection refused` | Docker no está corriendo | `docker compose up -d` |
| DNS no resuelve | Propagación pendiente | Esperar 5 min, verificar IP en DuckDNS |
| HTTPS no funciona | Puerto 443 cerrado | Revisar Security Group en AWS |
| DB connection error | Password incorrecto en .env | Revisar `.env` y reiniciar con `docker compose down && docker compose up -d` |
| `permission denied` en .pem | Permisos incorrectos | `chmod 400 horario-key.pem` |
| `Address already in use` | Puerto ocupado | `sudo lsof -i :PUERTO` y matar el proceso |
| MySQL healthcheck falla | MySQL tarda en iniciar | Esperar 30-60 segundos, es normal en el primer arranque |

---

## Extra — Comandos útiles en producción

### Ver estado y logs

```bash
# Estado de todos los contenedores
docker compose ps

# Logs en tiempo real (todos los servicios)
docker compose logs -f

# Logs de un servicio específico
docker compose logs -f usuarios-service
docker compose logs -f horario-service --tail=50

# Uso de CPU y memoria
docker stats
```

### Gestión de servicios

```bash
# Reiniciar un servicio sin bajar el resto
docker compose restart usuarios-service

# Bajar todos los servicios
docker compose down

# ⚠️ Bajar y BORRAR volúmenes (elimina las bases de datos)
docker compose down -v
```

### Actualizar el proyecto

```bash
cd /home/ubuntu/modulo_Horario

# Obtener últimos cambios del repo
git pull

# Reconstruir y reiniciar todos los servicios
cd services
docker compose up -d --build

# Si solo cambió un servicio:
docker compose up -d --build horario-service

# Si cambió el frontend:
cd ../frontend
npm install
npm run build
# Nginx sirve automáticamente el nuevo build desde /dist
```

### Revisar Nginx

```bash
# Ver logs de acceso
sudo tail -f /var/log/nginx/access.log

# Ver logs de errores
sudo tail -f /var/log/nginx/error.log

# Recargar configuración sin downtime
sudo systemctl reload nginx
```

### Seguridad básica adicional

```bash
# Instalar fail2ban (bloquea IPs con muchos intentos fallidos de SSH)
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Ver intentos de acceso bloqueados
sudo fail2ban-client status sshd
```

---

## Resumen de costos

| Recurso | Costo |
|---------|-------|
| EC2 t2.micro (primer año) | **Gratis** (Free Tier) |
| Elastic IP asociada a instancia | **Gratis** |
| Almacenamiento 20 GB gp3 | **Gratis** (primer año) |
| Dominio DuckDNS (`.duckdns.org`) | **Gratis** (siempre) |
| Certificado SSL Let's Encrypt | **Gratis** (siempre) |
| **Total primer año** | **~$0 USD** |

---

## Checklist de despliegue

- [ ] Cuenta AWS creada con MFA activado
- [ ] Key Pair `.pem` descargado y guardado
- [ ] Security Group configurado (puertos 22, 80, 443)
- [ ] Instancia EC2 t2.micro lanzada con Ubuntu 22.04
- [ ] Elastic IP asignada y anotada
- [ ] Conectado por SSH exitosamente
- [ ] Docker y Docker Compose instalados
- [ ] Nginx y Certbot instalados
- [ ] Subdominio DuckDNS creado y apuntando a la Elastic IP
- [ ] Script DuckDNS corriendo en cron
- [ ] DNS verificado con `nslookup`
- [ ] Repositorio clonado en `/home/ubuntu/modulo_Horario`
- [ ] Archivo `.env` configurado con secrets seguros
- [ ] Nginx configurado con los 5 `location` blocks
- [ ] `sudo nginx -t` retorna `syntax is ok`
- [ ] Certbot ejecutado y HTTPS funcionando
- [ ] `docker compose up -d --build` completado
- [ ] Todos los contenedores en estado `Up`
- [ ] Frontend accesible en `https://modulo-horario.duckdns.org`
- [ ] Swagger de cada servicio accesible vía HTTPS

---

*Guía generada para [github.com/Luisanchez0/modulo_Horario](https://github.com/Luisanchez0/modulo_Horario)*
