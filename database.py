from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv


# Безопасное получение URL из .env
DATABASE_URL = os.getenv("DATABASE_URL")
# Только для локального запуска — можно использовать SQLite или выдать предупреждение
if not DATABASE_URL:
    print("❗ DATABASE_URL не задан. Используется тестовая база.")
    DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # Автоматически переподключается при потере соединения
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()