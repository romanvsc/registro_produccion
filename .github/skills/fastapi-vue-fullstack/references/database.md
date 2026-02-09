# Database Setup and Migrations

Complete guide for setting up databases and managing migrations with Alembic in FastAPI projects.

## Database Configuration

### SQLite (Development)

```python
# app/core/config.py
DATABASE_URL = "sqlite:///./app.db"

# app/core/database.py
from sqlalchemy import create_engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)
```

### PostgreSQL (Production Recommended)

```python
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# app/core/database.py
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
```

**Install driver:**
```bash
pip install psycopg2-binary
```

### MySQL

```python
# .env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname

# Install driver
pip install pymysql
```

## Database Connection Setup

### Complete Database Module

```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    # SQLite only
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    # Connection pooling for production
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables (development only)
def init_db():
    Base.metadata.create_all(bind=engine)
```

## Alembic Setup (Migrations)

### Installation

```bash
pip install alembic
```

### Initialize Alembic

```bash
# In backend directory
alembic init alembic
```

This creates:
```
backend/
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── README
└── alembic.ini
```

### Configure Alembic

#### 1. Update `alembic.ini`

```ini
# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .

# Get from environment
sqlalchemy.url = 

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### 2. Update `alembic/env.py`

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your models and config
from app.core.config import settings
from app.core.database import Base
from app.models import user, item  # Import all model modules

# Alembic Config object
config = context.config

# Set database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Creating and Running Migrations

### Auto-generate Migration

```bash
# Create migration from model changes
alembic revision --autogenerate -m "Create users table"
```

This creates a file in `alembic/versions/` with upgrade/downgrade functions.

### Review Migration

```python
# alembic/versions/xxxx_create_users_table.py
def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

### Run Migration

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade +1

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Show current version
alembic current

# Show migration history
alembic history
```

## Model Examples

### User Model with Relationships

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author")
```

### Related Model

```python
# app/models/item.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="items")
```

### Many-to-Many Relationship

```python
# app/models/tag.py
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

# Association table
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    
    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
```

## Common Migration Scenarios

### Add Column

```bash
alembic revision -m "Add phone to users"
```

```python
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'phone')
```

### Rename Column

```python
def upgrade():
    op.alter_column('users', 'username', new_column_name='user_name')

def downgrade():
    op.alter_column('users', 'user_name', new_column_name='username')
```

### Add Index

```python
def upgrade():
    op.create_index('ix_items_name', 'items', ['name'])

def downgrade():
    op.drop_index('ix_items_name')
```

### Add Foreign Key

```python
def upgrade():
    op.add_column('items', sa.Column('category_id', sa.Integer()))
    op.create_foreign_key(
        'fk_items_category',
        'items', 'categories',
        ['category_id'], ['id']
    )

def downgrade():
    op.drop_constraint('fk_items_category', 'items')
    op.drop_column('items', 'category_id')
```

## Database Query Patterns

### Basic CRUD

```python
from sqlalchemy.orm import Session
from app.models.user import User

# Create
def create_user(db: Session, email: str, username: str):
    user = User(email=email, username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Read
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

# Update
def update_user(db: Session, user_id: int, email: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.email = email
        db.commit()
        db.refresh(user)
    return user

# Delete
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user
```

### Complex Queries

```python
from sqlalchemy import and_, or_, func

# Multiple filters
users = db.query(User).filter(
    and_(User.is_active == True, User.is_superuser == False)
).all()

# OR condition
users = db.query(User).filter(
    or_(User.email.like('%@gmail.com'), User.username.startswith('admin'))
).all()

# Count
user_count = db.query(func.count(User.id)).scalar()

# Join
from app.models.item import Item
results = db.query(User, Item).join(Item).filter(Item.name == 'Test').all()

# Eager loading (avoid N+1 queries)
from sqlalchemy.orm import joinedload
users = db.query(User).options(joinedload(User.items)).all()
```

## Connection Pooling

```python
# app/core/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,           # Number of connections to keep
    max_overflow=20,        # Additional connections when pool full
    pool_timeout=30,        # Seconds to wait for connection
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True      # Test connections before use
)
```

## Testing with Database

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.main import app
from app.api.deps import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

## Best Practices

1. **Use migrations in production** - Never use `Base.metadata.create_all()` in production
2. **Test migrations** - Test both upgrade and downgrade
3. **Backup before migration** - Always backup production database
4. **Review auto-generated migrations** - Alembic may miss some changes
5. **Use transactions** - Wrap multiple operations in transactions
6. **Close connections** - Use dependency injection to manage sessions
7. **Eager loading** - Use `joinedload()` to avoid N+1 queries
8. **Connection pooling** - Configure appropriate pool sizes
9. **Index strategically** - Add indexes on frequently queried columns
10. **Version control migrations** - Commit migration files to git
