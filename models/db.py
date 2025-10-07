"""Db module.

Este módulo centraliza la creación de tablas usando SQLAlchemy.
"""
from .orm import init_db


def create_tables():
    """Crear tablas usando SQLAlchemy declarative Base.

    `init_db()` usa el engine configurado en `models.orm` para crear las tablas.
    """
    init_db()


if __name__ == "__main__":
    create_tables()
    print("✅ Tablas creadas usando SQLAlchemy")