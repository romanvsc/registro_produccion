# FastAPI + Vue.js Project Template

This directory contains a complete boilerplate template for FastAPI + Vue.js applications.

## Usage

The `init_project.py` script automatically generates this structure when you run:

```bash
python scripts/init_project.py --name my-app --db postgres --auth
```

## Structure

```
project-name/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # Application entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py     # Shared dependencies
│   │   │   └── routes/     # API endpoints
│   │   │       ├── __init__.py
│   │   │       ├── auth.py # Authentication routes
│   │   │       ├── users.py
│   │   │       └── items.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py   # Settings
│   │   │   ├── security.py # JWT utilities
│   │   │   └── database.py # DB connection
│   │   ├── models/         # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── item.py
│   │   └── schemas/        # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── user.py
│   │       └── item.py
│   ├── alembic/            # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/              # Backend tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── .env                # Environment variables
│   ├── alembic.ini
│   └── Dockerfile
│
├── frontend/               # Vue.js frontend
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── assets/        # Images, styles
│   │   ├── components/    # Reusable components
│   │   │   ├── Navbar.vue
│   │   │   └── Footer.vue
│   │   ├── views/         # Page components
│   │   │   ├── HomeView.vue
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   └── DashboardView.vue
│   │   ├── router/        # Vue Router
│   │   │   └── index.js
│   │   ├── stores/        # Pinia stores
│   │   │   ├── auth.js
│   │   │   └── items.js
│   │   ├── services/      # API integration
│   │   │   └── api.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── tests/             # Frontend tests
│   │   └── unit/
│   ├── .env.development
│   ├── .env.production
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml      # Full stack with Docker
├── .gitignore
└── README.md
```

## Features Included

### Backend
- FastAPI application with proper structure
- SQLAlchemy ORM with database models
- Pydantic schemas for validation
- JWT authentication (optional)
- CRUD operations example
- CORS middleware configured
- Database migrations with Alembic
- Environment-based configuration
- Docker support

### Frontend
- Vue 3 with Composition API
- Vue Router for navigation
- Pinia for state management
- Axios for API calls
- Authentication flow (optional)
- Responsive layout
- Environment-based config
- Vite for fast development
- Docker support with Nginx

### DevOps
- Docker and Docker Compose setup
- Nginx configuration for production
- Environment variable management
- Ready for CI/CD deployment

## Quick Start

1. **Initialize project:**
   ```bash
   python scripts/init_project.py --name my-app --db postgres --auth
   ```

2. **Backend setup:**
   ```bash
   cd my-app/backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. **Frontend setup:**
   ```bash
   cd my-app/frontend
   npm install
   npm run dev
   ```

4. **Or use Docker:**
   ```bash
   cd my-app
   docker-compose up
   ```

## Customization

After generating the project, customize:

1. **Backend:**
   - Update `app/core/config.py` with your settings
   - Add new models in `app/models/`
   - Add new routes in `app/api/routes/`
   - Configure database in `.env`

2. **Frontend:**
   - Update branding in `src/components/`
   - Add new views in `src/views/`
   - Configure API URL in `.env.*`
   - Customize theme and styles

3. **Database:**
   - Create migrations: `alembic revision --autogenerate -m "description"`
   - Apply migrations: `alembic upgrade head`

## Technologies

### Backend Stack
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **Alembic** - Database migrations
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **Uvicorn** - ASGI server

### Frontend Stack
- **Vue 3** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Axios** - HTTP client
- **Vite** - Build tool and dev server

### Database Options
- **SQLite** - Development (default)
- **PostgreSQL** - Production recommended
- **MySQL** - Alternative production option

## Next Steps

After project generation:

1. Review and update README.md
2. Configure database connection
3. Set up authentication if needed
4. Add your business logic
5. Write tests
6. Set up CI/CD pipeline
7. Deploy to production

## Support

For more details:
- Check `references/auth.md` for authentication setup
- Check `references/database.md` for database configuration
- Check `references/deployment.md` for deployment guide
- Run `python scripts/dev.py` to start both servers
