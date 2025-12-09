"""Módulo para gestionar copias de seguridad y restauración de la base de datos.

Proporciona funciones para crear copias de seguridad de la base de datos SQLite
y restaurarlas. Las copias se guardan con timestamp para fácil identificación.
"""

import shutil
import os
from datetime import datetime
from pathlib import Path
from typing import Tuple


DB_PATH = Path("data") / "club_padel.db"
BACKUP_DIR = Path("data") / "backups"


def _ensure_backup_dir() -> None:
    """Asegura que el directorio de backups existe."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def crear_backup() -> Tuple[bool, str]:
    """Crea una copia de seguridad de la base de datos.
    
    La copia se guarda en data/backups/ con un timestamp en el nombre.
    
    Returns:
        Tuple[bool, str]: (éxito, ruta_archivo_o_mensaje_error)
    """
    try:
        _ensure_backup_dir()
        
        if not DB_PATH.exists():
            return False, "La base de datos no existe."
        
        # Crear nombre con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"club_padel_backup_{timestamp}.db"
        
        # Copiar archivo
        shutil.copy2(str(DB_PATH), str(backup_file))
        
        return True, str(backup_file)
    except Exception as e:
        return False, f"Error al crear backup: {e}"


def restaurar_backup(backup_file: str) -> Tuple[bool, str]:
    """Restaura la base de datos desde una copia de seguridad.
    
    IMPORTANTE: Cierra la aplicación después de restaurar para evitar
    problemas con conexiones abiertas a la BD.
    
    Args:
        backup_file (str): Ruta del archivo de backup a restaurar.
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    try:
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            return False, "El archivo de backup no existe."
        
        if not backup_path.suffix == '.db':
            return False, "El archivo no parece ser una copia de seguridad válida."
        
        # Crear backup de la BD actual antes de restaurar (como medida de seguridad)
        if DB_PATH.exists():
            current_backup = BACKUP_DIR / f"club_padel_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(str(DB_PATH), str(current_backup))
        
        # Restaurar
        shutil.copy2(str(backup_path), str(DB_PATH))
        
        return True, "Backup restaurado correctamente. Reinicia la aplicación para aplicar los cambios."
    except Exception as e:
        return False, f"Error al restaurar backup: {e}"


def listar_backups() -> list:
    """Lista todos los archivos de backup disponibles.
    
    Returns:
        list: Lista de rutas de archivos de backup ordenadas por fecha (más recientes primero).
    """
    try:
        _ensure_backup_dir()
        
        if not BACKUP_DIR.exists():
            return []
        
        backups = sorted(
            BACKUP_DIR.glob("club_padel_backup_*.db"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        return [str(b) for b in backups]
    except Exception:
        return []


def obtener_info_backup(backup_file: str) -> dict:
    """Obtiene información de un archivo de backup.
    
    Args:
        backup_file (str): Ruta del archivo de backup.
    
    Returns:
        dict: Diccionario con información del backup (nombre, tamaño, fecha).
    """
    try:
        path = Path(backup_file)
        if not path.exists():
            return {}
        
        stat = path.stat()
        tamaño_mb = stat.st_size / (1024 * 1024)
        fecha = datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")
        
        return {
            'nombre': path.name,
            'ruta': str(path),
            'tamaño_mb': f"{tamaño_mb:.2f}",
            'fecha': fecha
        }
    except Exception:
        return {}
