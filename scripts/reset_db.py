"""Script para resetear la base de datos local.

Uso: python scripts/reset_db.py

Elimina `data/club_padel.db` si existe y recrea las tablas usando
`models.orm.init_db()` (prefiere SQLAlchemy) o el fallback de `models.db.create_tables()`.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT, 'data', 'club_padel.db')

def remove_db():
    if os.path.exists(DB_PATH):
        print(f"Removing {DB_PATH}")
        os.remove(DB_PATH)
    else:
        print(f"No existing DB at {DB_PATH}")

def create_tables():
    try:
        # Asegurar que el path del proyecto está en sys.path para poder importar models
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        # Prefer SQLAlchemy init
        from models.orm import init_db
        init_db()
        print("Created tables via SQLAlchemy")
    except Exception:
        # Fallback
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from models.db import create_tables as ct
        ct()
    print("Created tables via SQLAlchemy fallback (sqlite SQL fallback used)")

def main():
    remove_db()
    create_tables()

if __name__ == '__main__':
    main()
