#!/usr/bin/env python
"""Script para verificar que el entorno está configurado correctamente."""

import sys
import os

def check_python_version():
    """Verificar versión de Python."""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ⚠️  Se recomienda Python 3.8 o superior")
        return False
    return True

def check_dependencies():
    """Verificar que todas las dependencias están instaladas."""
    dependencies = {
        'PySide6': 'PySide6',
        'sqlalchemy': 'SQLAlchemy',
        'openpyxl': 'openpyxl',
        'pytest': 'pytest'
    }
    
    all_ok = True
    for module_name, display_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"✓ {display_name} instalado")
        except ImportError:
            print(f"✗ {display_name} NO instalado")
            all_ok = False
    
    return all_ok

def check_database():
    """Verificar que la base de datos existe."""
    db_path = os.path.join(os.path.dirname(__file__), "data", "club_padel.db")
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"✓ Base de datos existe ({size_mb:.2f} MB)")
        return True
    else:
        print(f"✗ Base de datos NO existe: {db_path}")
        print("  Ejecuta: python scripts/reset_db.py")
        return False

def check_config_files():
    """Verificar archivos de configuración."""
    config_files = [
        'data/auth.json',
        'data/config.json'
    ]
    
    all_ok = True
    for config_file in config_files:
        path = os.path.join(os.path.dirname(__file__), config_file)
        if os.path.exists(path):
            print(f"✓ {config_file} existe")
        else:
            print(f"✗ {config_file} NO existe")
            all_ok = False
    
    return all_ok

def main():
    """Ejecutar todas las verificaciones."""
    print("\n" + "="*50)
    print("  VERIFICACIÓN DE ENTORNO - Club Padel")
    print("="*50 + "\n")
    
    checks = [
        ("Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Configuración", check_config_files),
        ("Base de datos", check_database),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        results.append((name, check_func()))
    
    print("\n" + "="*50)
    all_ok = all(result for _, result in results)
    
    if all_ok:
        print("✓ ¡Todo está correctamente configurado!")
        print("  Ejecuta: python main.py")
    else:
        print("✗ Hay problemas en la configuración")
        print("  Revisa los mensajes arriba ↑")
        sys.exit(1)
    
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
