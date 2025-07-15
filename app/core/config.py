import os
from typing import Optional

class Settings:
    PROJECT_NAME: str = "Haivler - Reddit-like Image Sharing"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "2a7af6a1f754ab24d54eee4de0c4be9bd6f50685ea6f566c")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://haivler_user:Admin%40123@mysql:3306/haivler"
    )
    
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "haivler-images")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "true"
    
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:3001",
        "http://localhost:80",
        "http://localhost"
    ]

settings = Settings()