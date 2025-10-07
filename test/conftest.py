import os
import sys
import pytest

# Asegurar que el proyecto está en sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models.orm import engine, Base, SessionLocal, init_db
from models import orm


@pytest.fixture(scope='function')
def db_setup(monkeypatch):
    """Fixture que configura un engine SQLite en memoria para las pruebas.

    Monkeypatch reemplaza `models.orm.engine` y `SessionLocal` por un engine
    en memoria; luego crea y elimina las tablas usando `Base.metadata`.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    db_url = 'sqlite:///:memory:'
    engine_mem = create_engine(db_url, future=True)
    SessionLocal_mem = sessionmaker(bind=engine_mem, autoflush=False, autocommit=False, future=True)

    monkeypatch.setattr(orm, 'engine', engine_mem)
    monkeypatch.setattr(orm, 'SessionLocal', SessionLocal_mem)

    # Importar modelos ORM para registrar las tablas en Base
    import models.orm_models  # noqa: F401
    Base.metadata.create_all(bind=engine_mem)

    yield

    Base.metadata.drop_all(bind=engine_mem)
