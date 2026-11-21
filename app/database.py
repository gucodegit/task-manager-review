# app/database.py
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Получаем URL базы данных из переменной окружения (передается через docker-compose)
# Если переменной нет, используем локальную (для запуска без Docker)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:password@localhost:5432/tasksdb"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Описываем таблицу для базы данных (ORM-модель)
class DBTask(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    priority = Column(String, default="medium") # Храним как строку
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# Зависимость (Dependency) для получения сессии БД в эндпоинтах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
