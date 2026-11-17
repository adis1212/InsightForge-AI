# InsightForge AI — Production Deployment & Operations Guide

**Application:** InsightForge AI — Mobile-First B2B SaaS Augmented Commercial Analytics Platform  
**Target Environments:** Docker Swarm / Kubernetes / Cloud VM (AWS EC2, GCP Compute Engine, DigitalOcean Droplet)  
**Security Level:** Production B2B SaaS Multi-Tenant  

---

## 1. System Architecture & Topology

InsightForge AI runs as a containerized or bare-metal modular monolith with three primary runtime services:

```
                          ┌───────────────────────────┐
                          │   Client Web / Mobile     │
                          │   (PWA Service Worker)    │
                          └─────────────┬─────────────┘
                                        │ HTTPS (Port 443)
                          ┌─────────────▼─────────────┐
                          │    Nginx Reverse Proxy    │
                          │    (SSL / Rate Limiting)  │
                          └──────┬─────────────┬──────┘
             Static Assets / PWA │             │ Reverse Proxy /api/
     ┌───────────────────────────┘             └───────────────────────────┐
     ▼                                                                     ▼
┌───────────────────────────┐                         ┌────────────────────────────────────┐
│      Frontend Client      │                         │          Backend API Server        │
│    (Vite / Nginx Port 80) │                         │  (FastAPI / Uvicorn Workers: 8000) │
└───────────────────────────┘                         └─────────────────┬──────────────────┘
                                                                        │
                                                ┌───────────────────────┴───────────────────────┐
                                                │                                               │
                                       ┌────────▼────────┐                             ┌────────▼────────┐
                                       │   PostgreSQL    │                             │ Persistent Disk │
                                       │   Database      │                             │ Storage Volumes │
                                       │  (Port 5432)    │                             │ (/data/uploads) │
                                       └─────────────────┘                             └─────────────────┘
```

---

## 2. Infrastructure Prerequisites

| Component | Minimum Specification | Recommended Production Spec |
| :--- | :--- | :--- |
| **CPU** | 2 vCPU | 4 vCPU |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 20 GB SSD | 50 GB NVMe SSD |
| **Operating System** | Ubuntu 22.04 LTS / Debian 12 | Ubuntu 24.04 LTS |
| **Container Engine**| Docker Engine 24.0+ | Docker Engine 26.0+ & Compose v2 |
| **Node.js** | Node 20 LTS | Node 22 LTS |
| **Python** | Python 3.12+ | Python 3.12+ / 3.14 |

---

## 3. Environment Variable Configuration

Create a production `.env` file in the root and backend directories. Never commit secrets to version control.

### Backend Configuration (`backend/.env`):
```ini
# Application Core
PROJECT_NAME="InsightForge AI"
ENVIRONMENT="production"
DEBUG=False
SECRET_KEY="generate-a-strong-64-character-random-hex-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database Configuration (PostgreSQL)
POSTGRES_SERVER="db"
POSTGRES_PORT=5432
POSTGRES_USER="insightforge_user"
POSTGRES_PASSWORD="strong_production_password_here"
POSTGRES_DB="insightforge"
DATABASE_URL="postgresql+asyncpg://insightforge_user:strong_production_password_here@db:5432/insightforge"

# Storage Paths
UPLOAD_DIR="/data/uploads"
MODEL_CACHE_DIR="/data/models"

# CORS Origins (Comma-separated)
CORS_ORIGINS="https://app.insightforge.ai,https://insightforge.ai"

# Optional Cloud LLM Credentials (Backend Only — Never sent to client)
OPENAI_API_KEY=""
GEMINI_API_KEY=""
DEFAULT_LLM_PROVIDER="deterministic"
```

### Frontend Configuration (`frontend/.env`):
```ini
VITE_API_URL="/api/v1"
```

---

## 4. Docker Compose Deployment (Recommended)

InsightForge includes a production-ready `docker-compose.yml` defining the complete stack:

### Step 1: Verify Stack Definition
Ensure `docker-compose.yml` mounts persistent volumes:
```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-insightforge_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-insightforge_secret}
      POSTGRES_DB: ${POSTGRES_DB:-insightforge}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U insightforge_user -d insightforge"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    depends_on:
      db:
        condition: service_healthy
    env_file:
      - ./backend/.env
    volumes:
      - upload_data:/data/uploads
      - model_cache:/data/models
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  upload_data:
  model_cache:
```

### Step 2: Build and Launch Containers
```bash
# Pull images and build containers
docker compose build --no-cache

# Start containers in detached mode
docker compose up -d

# Verify container health
docker compose ps
```

### Step 3: Run Alembic Database Migrations
```bash
docker compose exec backend alembic upgrade head
```

---

## 5. Bare-Metal / Cloud VM Deployment (Systemd & Nginx)

For bare-metal or cloud virtual machine deployments without Docker:

### 5.1 Backend Systemd Service
Create `/etc/systemd/system/insightforge-backend.service`:
```ini
[Unit]
Description=InsightForge AI FastAPI Application
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/insightforge/backend
EnvironmentFile=/var/www/insightforge/backend/.env
ExecStart=/var/www/insightforge/backend/venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/insightforge/access.log \
    --error-logfile /var/log/insightforge/error.log

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable insightforge-backend
sudo systemctl start insightforge-backend
```

### 5.2 Frontend Build & Static Serving
```bash
cd /var/www/insightforge/frontend
npm ci
npm run build
# Output files located in dist/
```

### 5.3 Nginx Configuration with SSL and Caching
Create `/etc/nginx/sites-available/insightforge`:
```nginx
server {
    listen 80;
    server_name app.insightforge.ai;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.insightforge.ai;

    ssl_certificate /etc/letsencrypt/live/app.insightforge.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.insightforge.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Static Frontend and PWA Assets
    root /var/www/insightforge/frontend/dist;
    index index.html;

    # Service Worker Caching Policy
    location /sw.js {
        add_header Cache-Control "no-cache";
        expires 0;
    }

    location /manifest.webmanifest {
        add_header Cache-Control "no-cache";
        expires 0;
    }

    # Single Page Application (SPA) Fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API Reverse Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Upload Size Limit (Matches 50MB bound)
        client_max_body_size 50M;

        # WebSocket Support (for real-time streaming)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/insightforge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 6. Security Hardening Checklist

- [x] **Strict Secret Key Isolation:** Ensure `SECRET_KEY` is a 256-bit cryptographically random string generated via `openssl rand -hex 32`.
- [x] **HTTPS Everywhere:** Enforce HSTS (`Strict-Transport-Security: max-age=31536000; includeSubDomains`).
- [x] **Multi-Tenant Authorization:** Verify that every query passes through `_check_workspace_access` to eliminate cross-tenant data leakage.
- [x] **File Upload Protection:** Enforce 50 MB bounded file size limits and validate MIME extensions (`.csv`, `.xlsx`, `.pdf`, `.txt`).
- [x] **Prompt Injection Defense:** Maintain active pre-embedding and pre-execution sanitizers to neutralize adversarial prompts.
- [x] **No Arbitrary Code Execution:** Verify that no `eval()`, `exec()`, or raw dynamic SQL is permitted in the codebase.
- [x] **Database Backups:** Configure daily automated snapshots of the PostgreSQL database and upload volumes.

---

## 7. Monitoring, Health Checks & Diagnostics

### 7.1 Health Check Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/health
```
Expected response:
```json
{
  "status": "healthy",
  "app_name": "InsightForge AI",
  "version": "1.0.0",
  "timestamp": "2026-11-17T17:15:00.000000Z"
}
```

### 7.2 Automated Pytest Regression Check
```powershell
# Run full suite (110 tests)
python -m pytest app/tests/ -v
```

### 7.3 Academic Evaluation Harness
```powershell
# Run full 12-benchmark empirical evaluation
python scripts/run_academic_evaluation.py
```
Outputs factual metrics to `data/samples/academic_research_evaluation.json`.

---

## 8. Backup and Disaster Recovery

### PostgreSQL Database Dump:
```bash
# Backup
docker compose exec db pg_dump -U insightforge_user insightforge > backup_$(date +%F).sql

# Restore
cat backup_2026-11-17.sql | docker compose exec -T db psql -U insightforge_user -d insightforge
```

### Dataset Volume Backup:
```bash
# Archive uploaded datasets and persistent model artifacts
tar -czvf insightforge_data_$(date +%F).tar.gz /data/uploads /data/models
```
