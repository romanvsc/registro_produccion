#!/usr/bin/env python3
"""
FastAPI + Vue.js Project Initializer

Creates a complete fullstack project structure with backend and frontend.

Usage:
    python init_project.py --name my-app [--db postgres] [--auth]

Arguments:
    --name: Project name (required)
    --db: Database type (sqlite|postgres|mysql) - default: sqlite
    --auth: Include JWT authentication setup
"""

import argparse
import os
from pathlib import Path


def create_backend_structure(project_path, project_name, db_type, include_auth):
    """Create FastAPI backend structure"""
    backend_path = project_path / "backend"
    app_path = backend_path / "app"
    
    # Create directories
    dirs = [
        app_path,
        app_path / "api" / "routes",
        app_path / "core",
        app_path / "models",
        app_path / "schemas",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "__init__.py").write_text("", encoding="utf-8")
    
    # main.py
    main_content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import items

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
'''
    
    if include_auth:
        main_content = main_content.replace(
            'from app.api.routes import items',
            'from app.api.routes import items, auth'
        ).replace(
            'app.include_router(items.router, prefix="/api")',
            'app.include_router(auth.router, prefix="/api/auth", tags=["auth"])\napp.include_router(items.router, prefix="/api")'
        )
    
    (app_path / "main.py").write_text(main_content, encoding="utf-8")
    
    # config.py
    db_url_map = {
        "sqlite": "sqlite:///./app.db",
        "postgres": "postgresql://user:password@localhost/dbname",
        "mysql": "mysql://user:password@localhost/dbname"
    }
    
    config_content = f'''from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "{project_name}"
    DATABASE_URL: str = "{db_url_map[db_type]}"
    ALLOWED_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    {'SECRET_KEY: str = "your-secret-key-change-this-in-production"' if include_auth else ''}
    {'ALGORITHM: str = "HS256"' if include_auth else ''}
    {'ACCESS_TOKEN_EXPIRE_MINUTES: int = 30' if include_auth else ''}
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
    (app_path / "core" / "config.py").write_text(config_content, encoding="utf-8")
    
    # database.py
    database_content = '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
    (app_path / "core" / "database.py").write_text(database_content, encoding="utf-8")
    
    # deps.py
    deps_content = '''from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
'''
    (app_path / "api" / "deps.py").write_text(deps_content, encoding="utf-8")
    
    # Item model
    item_model = '''from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
'''
    (app_path / "models" / "item.py").write_text(item_model, encoding="utf-8")
    
    # Item schema
    item_schema = '''from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    
    class Config:
        from_attributes = True
'''
    (app_path / "schemas" / "item.py").write_text(item_schema, encoding="utf-8")
    
    # Items route
    items_route = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[ItemResponse])
async def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Item).offset(skip).limit(limit).all()

@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
'''
    (app_path / "api" / "routes" / "items.py").write_text(items_route, encoding="utf-8")
    
    # requirements.txt
    requirements = '''fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pydantic-settings==2.1.0
python-multipart==0.0.6
'''
    
    if db_type == "postgres":
        requirements += "psycopg2-binary==2.9.9\n"
    elif db_type == "mysql":
        requirements += "pymysql==1.1.0\n"
    
    if include_auth:
        requirements += "python-jose[cryptography]==3.3.0\npasslib[bcrypt]==1.7.4\npython-multipart==0.0.6\n"
    
    (backend_path / "requirements.txt").write_text(requirements, encoding="utf-8")
    
    # .env
    env_content = f'''DATABASE_URL={db_url_map[db_type]}
{'SECRET_KEY=your-secret-key-here-change-in-production' if include_auth else ''}
'''
    (backend_path / ".env").write_text(env_content, encoding="utf-8")
    
    print(f"✓ Backend structure created at {backend_path}")


def create_frontend_structure(project_path, project_name):
    """Create Vue.js frontend structure"""
    frontend_path = project_path / "frontend"
    
    # Create package.json
    package_json = f'''{{
  "name": "{project_name}-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.5"
  }},
  "devDependencies": {{
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }}
}}
'''
    frontend_path.mkdir(parents=True, exist_ok=True)
    (frontend_path / "package.json").write_text(package_json, encoding="utf-8")
    
    # vite.config.js
    vite_config = '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
'''
    (frontend_path / "vite.config.js").write_text(vite_config, encoding="utf-8")
    
    # index.html
    index_html = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
'''
    (frontend_path / "index.html").write_text(index_html, encoding="utf-8")
    
    # Create src structure
    src_path = frontend_path / "src"
    dirs = [
        src_path,
        src_path / "components",
        src_path / "views",
        src_path / "stores",
        src_path / "services",
        src_path / "router",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # main.js
    main_js = '''import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
'''
    (src_path / "main.js").write_text(main_js, encoding="utf-8")
    
    # App.vue
    app_vue = '''<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/items">Items</router-link>
    </nav>
    <router-view />
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  padding: 20px;
}
nav {
  padding: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid #ccc;
}
nav a {
  margin-right: 15px;
  text-decoration: none;
}
</style>
'''
    (src_path / "App.vue").write_text(app_vue, encoding="utf-8")
    
    # router/index.js
    router_js = '''import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ItemsView from '../views/ItemsView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/items', name: 'items', component: ItemsView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
'''
    (src_path / "router" / "index.js").write_text(router_js, encoding="utf-8")
    
    # services/api.js
    api_js = '''import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
})

export default api
'''
    (src_path / "services" / "api.js").write_text(api_js, encoding="utf-8")
    
    # stores/items.js
    items_store = '''import { defineStore } from 'pinia'
import api from '@/services/api'

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchItems() {
      this.loading = true
      try {
        const { data } = await api.get('/api/items')
        this.items = data
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },
    
    async createItem(item) {
      const { data } = await api.post('/api/items', item)
      this.items.push(data)
      return data
    }
  }
})
'''
    (src_path / "stores" / "items.js").write_text(items_store, encoding="utf-8")
    
    # views/HomeView.vue
    home_view = f'''<template>
  <div>
    <h1>Welcome to {project_name}</h1>
    <p>FastAPI + Vue.js Fullstack Application</p>
  </div>
</template>
'''
    (src_path / "views" / "HomeView.vue").write_text(home_view, encoding="utf-8")
    
    # views/ItemsView.vue
    items_view = '''<template>
  <div>
    <h1>Items</h1>
    <button @click="fetchItems">Refresh</button>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <ul v-else>
      <li v-for="item in items" :key="item.id">
        {{ item.name }} - {{ item.description }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useItemsStore } from '@/stores/items'
import { onMounted } from 'vue'

const itemsStore = useItemsStore()
const { items, loading, error } = storeToRefs(itemsStore)
const { fetchItems } = itemsStore

onMounted(() => {
  fetchItems()
})
</script>
'''
    (src_path / "views" / "ItemsView.vue").write_text(items_view, encoding="utf-8")
    
    print(f"✓ Frontend structure created at {frontend_path}")


def create_readme(project_path, project_name, db_type):
    """Create README with setup instructions"""
    readme_content = f'''# {project_name}

FastAPI + Vue.js Fullstack Application

## Setup

### Backend

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Update .env with your database credentials

5. Run database migrations (if using Alembic):
   ```bash
   alembic upgrade head
   ```

6. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

   Backend will run on http://localhost:8000

### Frontend

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start dev server:
   ```bash
   npm run dev
   ```

   Frontend will run on http://localhost:5173

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
{project_name}/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Config, DB, security
│   │   ├── models/   # SQLAlchemy models
│   │   └── schemas/  # Pydantic schemas
│   └── requirements.txt
└── frontend/         # Vue.js application
    ├── src/
    │   ├── components/
    │   ├── views/
    │   ├── stores/   # Pinia stores
    │   └── services/ # API integration
    └── package.json
```

## Database

Current database: {db_type}
Connection string in: backend/.env
'''
    
    (project_path / "README.md").write_text(readme_content, encoding="utf-8")
    print(f"✓ README.md created")


def main():
    parser = argparse.ArgumentParser(description="Initialize FastAPI + Vue.js project")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--db", default="sqlite", choices=["sqlite", "postgres", "mysql"], 
                       help="Database type")
    parser.add_argument("--auth", action="store_true", help="Include JWT authentication")
    
    args = parser.parse_args()
    
    project_name = args.name
    project_path = Path.cwd() / project_name
    
    if project_path.exists():
        print(f"Error: Directory {project_path} already exists")
        return
    
    print(f"Creating project: {project_name}")
    print(f"Database: {args.db}")
    print(f"Authentication: {'Yes' if args.auth else 'No'}")
    print()
    
    project_path.mkdir(parents=True)
    
    create_backend_structure(project_path, project_name, args.db, args.auth)
    create_frontend_structure(project_path, project_name)
    create_readme(project_path, project_name, args.db)
    
    print()
    print(f"✓ Project '{project_name}' created successfully!")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")
    print("  # Setup backend (see README.md)")
    print("  # Setup frontend (see README.md)")


if __name__ == "__main__":
    main()
