"""Db module.

Este módulo centraliza la creación de tablas usando SQLAlchemy.
"""
from .orm import init_db


def crear_tablas():
    """Crear tablas usando SQLAlchemy declarative Base.

    `inicializar_bd()` usa el engine configurado en `models.orm` para crear las tablas.
    """
    inicializar_bd()


if __name__ == "__main__":
    crear_tablas()
    print("✅ Tablas creadas usando SQLAlchemy)