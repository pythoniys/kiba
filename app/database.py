from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://damsel:damsel@localhost:5555/damsel_kursach"

# Создаем объект подключения
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем базовый класс для всех моделей
Base = declarative_base()

# Создаем сессию
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
