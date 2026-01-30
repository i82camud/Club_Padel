"""Script para resetear la base de datos local.

Uso: python scripts/reset_db.py

Elimina `data/club_padel.db` si existe y recrea las tablas usando
`models.orm.inicializar_bd()` (prefiere SQLAlchemy) o el fallback de `models.db.crear_tablas()`.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT, 'data', 'club_padel.db')

def eliminar_bd():
    if os.path.exists(DB_PATH):
        print(f"Removing {DB_PATH}")
        os.remove(DB_PATH)
    else:
        print(f"No existing DB at {DB_PATH}")

def crear_tablas():
    try:
        # Asegurar que el path del proyecto está en sys.path para poder importar models
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        # Prefer SQLAlchemy init
        from models.orm import inicializar_bd
        inicializar_bd()
        print("Created tables via SQLAlchemy")
    except Exception:
        # Fallback
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from models.db import crear_tablas as ct
        ct()
    print("Created tables via SQLAlchemy fallback (sqlite SQL fallback used)")

def main():
    eliminar_bd()
    crear_tablas()

if __name__ == '__main__':
    main()
