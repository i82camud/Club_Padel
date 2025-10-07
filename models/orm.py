from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "club_padel.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def init_db():
    """Crea las tablas a partir de los modelos declarativos."""
    from . import orm_models  # import models so they are registered on Base
    Base.metadata.create_all(bind=engine)
