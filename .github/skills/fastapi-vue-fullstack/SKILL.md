---
name: fastapi-vue-fullstack
description: Build fullstack web applications with FastAPI (Python backend) and Vue.js (frontend). Use when creating REST APIs, SPAs, CRUD apps, or any project requiring modern backend + frontend architecture. Handles project setup, routing, state management, API integration, authentication, database models, and deployment.
---

# FastAPI + Vue.js Fullstack Development

Enables rapid development of modern web applications with FastAPI backend and Vue.js frontend, including project scaffolding, API design, component architecture, and best practices.

## Quick Start

**Creating a new project:**
```bash
# Initialize with script
python scripts/init_project.py --name my-app --db postgres
```

**Common tasks:**
- "Create a REST API for users with CRUD operations"
- "Add authentication with JWT tokens"
- "Create a Vue component for displaying data from the API"
- "Set up CORS between frontend and backend"
- "Add database models with SQLAlchemy"

## Project Structure

### Backend (FastAPI)
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependencies (DB, auth)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── items.py
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── security.py      # Auth utils
│   │   └── database.py      # DB connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   └── schemas/             # Pydantic schemas
│       ├── __init__.py
│       ├── user.py
│       └── item.py
├── requirements.txt
└── .env
```

### Frontend (Vue.js)
```
frontend/
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/
│   │   └── index.js
│   ├── stores/              # Pinia stores
│   │   ├── user.js
│   │   └── items.js
│   ├── views/               # Page components
│   │   ├── HomeView.vue
│   │   ├── LoginView.vue
│   │   └── DashboardView.vue
│   ├── components/          # Reusable components
│   │   ├── Navbar.vue
│   │   └── ItemCard.vue
│   └── services/            # API calls
│       └── api.js
├── package.json
└── vite.config.js
```

## Backend Development

### FastAPI Basics

**Minimal API:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

**CRUD endpoint pattern:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[ItemSchema])
async def list_items(skip: int = 0, limit: int = 100, 
                     db: Session = Depends(get_db)):
    return db.query(Item).offset(skip).limit(limit).all()

@router.post("/", response_model=ItemSchema, status_code=201)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{item_id}", response_model=ItemSchema)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemSchema)
async def update_item(item_id: int, item: ItemUpdate, 
                      db: Session = Depends(get_db)):
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
```

### Authentication with JWT

See `references/auth.md` for complete JWT implementation including token generation, refresh tokens, and protected routes.

### Database Models

**SQLAlchemy model example:**
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Pydantic schemas for validation:**
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## Frontend Development

### Vue.js Setup

**Use Vite for fast development:**
```bash
npm create vue@latest
# Select: Router, Pinia, ESLint
cd frontend
npm install axios
```

### API Integration

**Centralized API service (`services/api.js`):**
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
})

// Request interceptor for auth token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

**Using API in components:**
```javascript
import api from '@/services/api'

export default {
  data() {
    return { items: [], loading: false, error: null }
  },
  async mounted() {
    await this.fetchItems()
  },
  methods: {
    async fetchItems() {
      this.loading = true
      try {
        const { data } = await api.get('/items')
        this.items = data
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    }
  }
}
```

### State Management with Pinia

```javascript
import { defineStore } from 'pinia'
import api from '@/services/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token')
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  
  actions: {
    async login(email, password) {
      const { data } = await api.post('/auth/login', { email, password })
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('token', this.token)
    },
    
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
```

### Vue Router Guards

```javascript
import { createRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  routes: [
    { path: '/login', component: () => import('@/views/LoginView.vue') },
    { 
      path: '/dashboard', 
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

## Development Workflow

**1. Start backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**2. Start frontend:**
```bash
cd frontend
npm run dev  # Usually runs on port 5173
```

**3. Run both concurrently:** Use `scripts/dev.py` to start both servers simultaneously.

## Common Patterns

### Form Handling
```vue
<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="form.name" required />
    <button :disabled="loading">Submit</button>
    <p v-if="error">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'

const form = ref({ name: '' })
const loading = ref(false)
const error = ref(null)

async function handleSubmit() {
  loading.value = true
  error.value = null
  try {
    await api.post('/items', form.value)
    form.value = { name: '' }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error occurred'
  } finally {
    loading.value = false
  }
}
</script>
```

### Data Tables with Actions
```vue
<template>
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in items" :key="item.id">
        <td>{{ item.name }}</td>
        <td>
          <button @click="editItem(item)">Edit</button>
          <button @click="deleteItem(item.id)">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
```

## Testing

**Backend tests (pytest):**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_item():
    response = client.post("/items/", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

**Frontend tests (Vitest):**
```javascript
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ItemCard from '@/components/ItemCard.vue'

describe('ItemCard', () => {
  it('displays item name', () => {
    const wrapper = mount(ItemCard, {
      props: { item: { name: 'Test' } }
    })
    expect(wrapper.text()).toContain('Test')
  })
})
```

## Deployment

**Backend (Docker):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Frontend (build):**
```bash
npm run build  # Creates dist/ folder
# Deploy dist/ to static hosting (Netlify, Vercel, etc.)
```

## Resources

### scripts/
- `init_project.py` - Initialize new FastAPI + Vue project structure
- `dev.py` - Run both backend and frontend concurrently

### references/
- `auth.md` - Complete JWT authentication implementation
- `database.md` - Database setup, migrations with Alembic
- `deployment.md` - Production deployment guide

### assets/
- `project-template/` - Complete boilerplate project structure
