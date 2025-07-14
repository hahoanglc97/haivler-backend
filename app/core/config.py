import os
from typing import Optional

class Settings:
    PROJECT_NAME: str = "Haivler - Reddit-like Image Sharing"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:password@localhost:3306/haivler"
    )
    
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "haivler-images")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "true"
    
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:3001"
    ]

settings = Settings()