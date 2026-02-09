# FastAPI + Vue.js Fullstack Development Skill

Skill completo para desarrollo de aplicaciones fullstack modernas con FastAPI (backend) y Vue.js (frontend).

## Descripción

Este skill proporciona conocimiento especializado, workflows y herramientas para construir aplicaciones web completas con:

- **Backend**: FastAPI con Python
- **Frontend**: Vue.js 3 con Composition API
- **Base de datos**: SQLAlchemy ORM (SQLite, PostgreSQL, MySQL)
- **Autenticación**: JWT tokens
- **Estado**: Pinia para manejo de estado
- **Build tools**: Vite para desarrollo rápido

## Estructura del Skill

```
fastapi-vue-fullstack/
├── SKILL.md                    # Guía principal y referencia rápida
├── scripts/
│   ├── init_project.py         # Inicializa nuevos proyectos
│   └── dev.py                  # Ejecuta backend y frontend simultáneamente
├── references/
│   ├── auth.md                 # Implementación completa de autenticación JWT
│   ├── database.md             # Configuración de base de datos y migraciones
│   └── deployment.md           # Guía de despliegue a producción
└── assets/
    └── project-template/       # Template base del proyecto
        ├── README.md
        └── .gitignore
```

## Cuándo Usar Este Skill

- Crear una nueva aplicación web fullstack
- Implementar una REST API con FastAPI
- Desarrollar una SPA (Single Page Application) con Vue
- Configurar autenticación con JWT
- Diseñar modelos de base de datos con SQLAlchemy
- Integrar frontend y backend
- Desplegar aplicaciones a producción

## Inicio Rápido

### 1. Crear un Nuevo Proyecto

```bash
# Con el skill activo en Codex, simplemente pide:
"Crea un nuevo proyecto FastAPI + Vue con autenticación y base de datos PostgreSQL"

# O ejecuta manualmente:
python scripts/init_project.py --name mi-app --db postgres --auth
```

### 2. Desarrollar

```bash
# Iniciar ambos servidores
python scripts/dev.py

# O manualmente:
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Tareas Comunes

El skill te ayudará con:

- "Crea un endpoint CRUD para productos"
- "Añade autenticación JWT al backend"
- "Crea un componente Vue para mostrar una lista de items"
- "Configura CORS entre frontend y backend"
- "Añade modelos de base de datos con relaciones"
- "Implementa un store de Pinia para el carrito de compras"

## Características Principales

### Backend (FastAPI)

- ✅ Estructura de proyecto modular
- ✅ Endpoints CRUD con patrones establecidos
- ✅ Autenticación JWT completa
- ✅ Modelos SQLAlchemy con relaciones
- ✅ Schemas Pydantic para validación
- ✅ Migraciones con Alembic
- ✅ Middleware CORS configurado
- ✅ Documentación automática (Swagger/ReDoc)
- ✅ Manejo de errores consistente

### Frontend (Vue.js)

- ✅ Vue 3 con Composition API
- ✅ Vue Router con guardias de navegación
- ✅ Pinia para manejo de estado
- ✅ Axios con interceptores configurados
- ✅ Integración API centralizada
- ✅ Componentes reutilizables
- ✅ Formularios con validación
- ✅ Autenticación y autorización
- ✅ Build optimizado con Vite

### DevOps

- ✅ Docker y Docker Compose
- ✅ Variables de entorno
- ✅ Configuración Nginx
- ✅ Despliegue a múltiples plataformas
- ✅ CI/CD con GitHub Actions
- ✅ Monitoreo y logging

## Recursos Detallados

### Scripts

#### `init_project.py`
Inicializa un proyecto completo con estructura backend/frontend.

**Uso:**
```bash
python scripts/init_project.py --name mi-app [--db postgres] [--auth]
```

**Opciones:**
- `--name`: Nombre del proyecto (requerido)
- `--db`: Tipo de base de datos (sqlite|postgres|mysql)
- `--auth`: Incluir configuración de autenticación JWT

**Genera:**
- Estructura completa backend y frontend
- Modelos y schemas básicos
- Rutas CRUD de ejemplo
- Configuración de base de datos
- README con instrucciones

#### `dev.py`
Ejecuta backend y frontend concurrentemente para desarrollo.

**Uso:**
```bash
python scripts/dev.py [--backend-port 8000] [--frontend-port 5173]
```

### Referencias

#### `auth.md` - Autenticación JWT
Implementación completa de autenticación con JWT incluyendo:
- Utilities de seguridad (hash de contraseñas, tokens)
- Modelos y schemas de usuario
- Endpoints de registro/login/logout
- Dependencias de autenticación
- Rutas protegidas
- Integración frontend con stores de Pinia
- Guards de navegación
- Manejo de tokens en API calls
- Tests de autenticación

#### `database.md` - Base de Datos
Configuración y manejo de base de datos con:
- Setup de SQLAlchemy para SQLite/PostgreSQL/MySQL
- Configuración de Alembic para migraciones
- Modelos con relaciones (one-to-many, many-to-many)
- Patrones de query comunes
- Connection pooling
- Testing con base de datos
- Mejores prácticas

#### `deployment.md` - Despliegue
Guía completa de despliegue a producción:
- Despliegue directo en VPS/servidor
- Configuración de Gunicorn y systemd
- Nginx como reverse proxy
- SSL con Let's Encrypt
- Docker y Docker Compose
- Despliegue a plataformas cloud (Render, Railway, AWS)
- Frontend en CDN (Netlify, Vercel)
- Variables de entorno
- Monitoreo y logging
- Optimizaciones de performance
- Security checklist
- CI/CD con GitHub Actions

### Assets

#### `project-template/`
Template completo de proyecto incluyendo:
- README con estructura y uso
- .gitignore configurado
- Ejemplos de archivos de configuración

## Ejemplos de Uso con Codex

```
Usuario: "Necesito crear una API REST para gestionar tareas con autenticación"

Codex (con skill):
- Inicializa proyecto con auth
- Crea modelo Task con relación a User
- Implementa endpoints CRUD protegidos
- Añade componentes Vue para UI
- Configura store de Pinia

---

Usuario: "Añade paginación a la lista de items"

Codex (con skill):
- Modifica endpoint backend para soportar skip/limit
- Actualiza componente frontend con controles de paginación
- Añade lógica al store de Pinia

---

Usuario: "Prepara la app para producción"

Codex (con skill):
- Consulta deployment.md
- Crea Dockerfiles y docker-compose
- Configura variables de entorno
- Añade checks de salud
- Documenta pasos de despliegue
```

## Tecnologías Soportadas

### Backend
- Python 3.11+
- FastAPI 0.109+
- SQLAlchemy 2.0+
- Alembic (migraciones)
- Pydantic (validación)
- python-jose (JWT)
- passlib (hashing)
- Uvicorn/Gunicorn

### Frontend
- Vue.js 3
- Vue Router 4
- Pinia (state management)
- Axios (HTTP client)
- Vite 5 (build tool)

### Bases de Datos
- SQLite (desarrollo)
- PostgreSQL (producción)
- MySQL/MariaDB

### DevOps
- Docker & Docker Compose
- Nginx
- GitHub Actions
- Render, Railway, AWS, Netlify, Vercel

## Mejores Prácticas Incluidas

1. **Separación de concerns**: Backend/Frontend independientes
2. **Código modular**: Estructura clara y mantenible
3. **Type safety**: Pydantic schemas en backend, TypeScript opcional en frontend
4. **Seguridad**: JWT, CORS, password hashing, validación
5. **Testing**: Estructura para tests backend y frontend
6. **Documentación**: Auto-documentación con FastAPI
7. **Escalabilidad**: Connection pooling, estado centralizado
8. **DevOps**: Containerización, CI/CD, monitoreo

## Validación

El skill ha sido validado con `quick_validate.py` y cumple con todos los requisitos:
- ✅ Frontmatter YAML válido
- ✅ Nombre en formato correcto (hyphen-case)
- ✅ Descripción completa y descriptiva
- ✅ Estructura de archivos correcta
- ✅ Scripts ejecutables funcionales
- ✅ Referencias detalladas
- ✅ Assets organizados

## Contribuir

Para mejorar este skill:
1. Actualiza SKILL.md con nuevos patrones
2. Añade scripts útiles a `scripts/`
3. Expande referencias en `references/`
4. Actualiza templates en `assets/`

## Versión

v1.0.0 - Enero 2026

## Licencia

Este skill es parte del sistema de skills de desarrollo y puede ser usado libremente para proyectos de desarrollo.
