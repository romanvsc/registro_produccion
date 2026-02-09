from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "registro_produccion"
    DATABASE_URL: str = "mysql://user:password@localhost/dbname"
    ALLOWED_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    
    
    
    class Config:
        env_file = ".env"

settings = Settings()
