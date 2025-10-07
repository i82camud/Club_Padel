# Club_Padel

Proyecto de ejemplo para la gestión de un club de pádel.

Este repositorio ahora usa SQLAlchemy exclusivamente para el acceso a datos.

## Requisitos

- Python 3.11+
- Virtual environment (recomendado)
- Dependencias en `requirements.txt` (asegúrate de que incluya `SQLAlchemy` y `pytest`)

## Configuración en Windows PowerShell

Abre PowerShell en la raíz del proyecto (por ejemplo `D:\Documents\UCO\Club_Padel`) y ejecuta:

```powershell
# Crear y activar un virtualenv (si no lo tienes)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

Nota: el proyecto ahora depende exclusivamente de SQLAlchemy. El antiguo fallback que usaba sqlite3 directo fue eliminado.

## Resetear la base de datos local

Para eliminar y recrear la base de datos persistente (archivo `data/club_padel.db`) ejecuta:

```powershell
# Asegúrate de usar el virtualenv activado
python scripts/reset_db.py
```

El script intentará crear las tablas mediante SQLAlchemy.

## Ejecutar tests

Los tests usan `pytest` y, mediante SQLAlchemy, ejecutan contra una base SQLite en memoria — no afectan tu base persistente.

```powershell
# Ejecutar pytest desde el virtualenv
python -m pytest -q
```

Si quieres ejecutar un test específico:

```powershell
python -m pytest test/test_insert_socio.py::test_insertar_y_listar_socio -q
```

## Notas importantes

- Si tu entorno no tiene `SQLAlchemy` instalado, las funciones de acceso a datos fallarán (esto ahora es intencional). Instala dependencias con `pip install -r requirements.txt`.


---

Si quieres, actualizo también `requirements.txt` o añado instrucciones para Docker/CI. ¿Qué prefieres que haga ahora?