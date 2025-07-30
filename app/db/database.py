from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from dotenv import load_dotenv
from pathlib import Path
import os

# Method 1: Explicitly specify the path to root .env file
root_dir = Path(__file__).parent.parent.parent  # Go up from db/ to root/
env_path = root_dir / '.env'

# Load with explicit path and verify it loaded
loaded = load_dotenv(dotenv_path=env_path)

# Use DATABASE_URL from environment or build from individual components as fallback
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # Fallback: build from individual components
    from urllib.parse import quote_plus
    
    DB_USER = os.getenv("MYSQL_USER", "haivler_user")
    DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "Admin@123")
    DB_HOST = os.getenv("DB_HOST", "mysql")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("MYSQL_DATABASE", "haivler")
    
    # URL encode the password to handle special characters
    encoded_password = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


CONNECTION_URL = URL.create(
    "mysql+pymysql",
    username=os.getenv("MYSQL_USER", "haivler_user"), #"haivler_user",
    password=os.getenv("MYSQL_PASSWORD", "Admin@123"), #"Admin@123",
    host=os.getenv("DB_HOST", "localhost"), #"localhost",
    port=os.getenv("DB_PORT", "3306"), #"3306",
    database=os.getenv("MYSQL_DATABASE", "haivler") #"haivler"
)

engine = create_engine(CONNECTION_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()