# Production Deployment Guide

Complete guide for deploying FastAPI + Vue.js applications to production.

## Overview

Common deployment architectures:
- **Separated**: Frontend on CDN/static hosting, backend on server
- **Unified**: Frontend served by FastAPI backend
- **Containerized**: Docker containers with orchestration

## Backend Deployment

### Option 1: Direct Deployment (VPS/Server)

#### 1. Server Setup (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx supervisor -y

# Install PostgreSQL (if needed)
sudo apt install postgresql postgresql-contrib -y
```

#### 2. Application Setup

```bash
# Create app user
sudo useradd -m -s /bin/bash appuser

# Clone repository
cd /home/appuser
sudo -u appuser git clone https://github.com/yourname/yourapp.git
cd yourapp/backend

# Create virtual environment
sudo -u appuser python3 -m venv venv
sudo -u appuser venv/bin/pip install -r requirements.txt

# Setup environment variables
sudo -u appuser nano .env
```

#### 3. Gunicorn Setup

```bash
# Install Gunicorn
venv/bin/pip install gunicorn

# Test Gunicorn
venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Create systemd service** (`/etc/systemd/system/fastapi.service`):

```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=appuser
Group=appuser
WorkingDirectory=/home/appuser/yourapp/backend
Environment="PATH=/home/appuser/yourapp/backend/venv/bin"
EnvironmentFile=/home/appuser/yourapp/backend/.env
ExecStart=/home/appuser/yourapp/backend/venv/bin/gunicorn \
    app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/fastapi/access.log \
    --error-logfile /var/log/fastapi/error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/fastapi
sudo chown appuser:appuser /var/log/fastapi

# Enable and start service
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

#### 4. Nginx Configuration

**Create config** (`/etc/nginx/sites-available/yourapp`):

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/yourapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

### Option 2: Docker Deployment

#### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build and Run

```bash
# Build
docker build -t yourapp-backend:latest ./backend

# Run
docker run -d \
    --name fastapi-app \
    -p 8000:8000 \
    -e DATABASE_URL="postgresql://..." \
    -e SECRET_KEY="..." \
    --restart unless-stopped \
    yourapp-backend:latest
```

### Option 3: Cloud Platforms

#### Render.com

**render.yaml**:
```yaml
services:
  - type: web
    name: yourapp-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: yourapp-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
        
databases:
  - name: yourapp-db
    databaseName: yourapp
    user: yourapp
```

#### Railway.app

**railway.json**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### AWS Elastic Beanstalk

**Procfile**:
```
web: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**.ebextensions/01_packages.config**:
```yaml
packages:
  yum:
    postgresql-devel: []
```

## Frontend Deployment

### Option 1: Static Hosting (Recommended)

#### Build Production Files

```bash
cd frontend
npm run build  # Creates dist/ folder
```

#### Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod --dir=dist
```

**netlify.toml**:
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  VITE_API_URL = "https://api.yourdomain.com"
```

#### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

**vercel.json**:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

#### Deploy to AWS S3 + CloudFront

```bash
# Build
npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Option 2: Nginx Static Files

**Nginx config** (`/etc/nginx/sites-available/yourapp-frontend`):
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/yourapp/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (if serving from same domain)
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Option 3: Serve Frontend from FastAPI

```python
# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

# API routes
app.include_router(api_router, prefix="/api")

# Mount frontend static files
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
```

## Docker Compose (Full Stack)

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/appdb
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

**Frontend Dockerfile**:
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**frontend/nginx.conf**:
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables

### Backend (.env)

```bash
# Production .env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-very-long-secret-key-change-this
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ENVIRONMENT=production
```

### Frontend (.env.production)

```bash
VITE_API_URL=https://api.yourdomain.com
```

## Database Migrations in Production

```bash
# SSH into server
ssh user@server

# Navigate to app
cd /home/appuser/yourapp/backend

# Activate venv
source venv/bin/activate

# Backup database first!
pg_dump dbname > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
alembic upgrade head

# Restart application
sudo systemctl restart fastapi
```

## Monitoring and Logging

### Sentry Integration

```python
# backend
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    environment="production",
    traces_sample_rate=1.0
)
```

```javascript
// frontend
import * as Sentry from "@sentry/vue"

Sentry.init({
  app,
  dsn: "your-sentry-dsn",
  environment: "production"
})
```

### Log Rotation

**/etc/logrotate.d/fastapi**:
```
/var/log/fastapi/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 appuser appuser
    sharedscripts
    postrotate
        systemctl reload fastapi
    endscript
}
```

## Performance Optimization

### Backend

```python
# Enable response caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Use gzip compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40
)
```

### Frontend

```javascript
// vite.config.js - production optimizations
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          utils: ['axios']
        }
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true
      }
    }
  }
})
```

## Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Use environment variables for secrets
- [ ] Keep dependencies updated
- [ ] Enable security headers
- [ ] Use parameterized queries (SQLAlchemy handles this)
- [ ] Validate all inputs
- [ ] Implement authentication properly
- [ ] Use CSRF protection for forms
- [ ] Enable database backups
- [ ] Set up monitoring and alerts
- [ ] Review logs regularly
- [ ] Implement proper error handling (don't expose internals)

## CI/CD Pipeline Example (GitHub Actions)

**.github/workflows/deploy.yml**:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/appuser/yourapp
            git pull
            cd backend
            source venv/bin/activate
            pip install -r requirements.txt
            alembic upgrade head
            sudo systemctl restart fastapi

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Build
        working-directory: ./frontend
        run: |
          npm ci
          npm run build
      
      - name: Deploy to Netlify
        uses: netlify/actions/cli@master
        with:
          args: deploy --prod --dir=frontend/dist
        env:
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
```

## Health Checks

```python
# app/api/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/health/db")
async def database_health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

## Troubleshooting

### Common Issues

1. **CORS errors**: Check ALLOWED_ORIGINS in backend
2. **Database connection failed**: Verify DATABASE_URL and network
3. **502 Bad Gateway**: Check if backend is running
4. **Frontend 404 on refresh**: Configure SPA routing in Nginx
5. **Slow queries**: Add database indexes, use connection pooling
6. **Memory issues**: Adjust Gunicorn worker count, check for leaks

### Useful Commands

```bash
# Check service status
sudo systemctl status fastapi

# View logs
sudo journalctl -u fastapi -f

# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check database connections
SELECT * FROM pg_stat_activity;

# Monitor system resources
htop
```
