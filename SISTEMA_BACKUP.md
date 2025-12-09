# Sistema de Copia de Seguridad - Club Pádel

## Descripción

Se ha implementado un sistema completo de copia de seguridad y restauración de la base de datos SQLite. Los usuarios pueden crear copias de seguridad manualmente desde la página de configuración y restaurarlas cuando sea necesario.

## Componentes

### 1. `utils/backup.py`
Módulo principal de backup con las funciones:

- **`crear_backup() -> Tuple[bool, str]`**: Crea una copia de seguridad con timestamp
  - Guarda en: `data/backups/club_padel_backup_YYYYMMDD_HHMMSS.db`
  - Retorna: (éxito, ruta_archivo_o_error)

- **`restaurar_backup(backup_file: str) -> Tuple[bool, str]`**: Restaura desde backup
  - Crea backup de seguridad de la BD actual antes de restaurar
  - Retorna: (éxito, mensaje)
  - **IMPORTANTE**: Requiere reiniciar la aplicación

- **`listar_backups() -> list`**: Lista todos los backups disponibles
  - Ordenados por fecha (más recientes primero)
  - Retorna: lista de rutas

- **`obtener_info_backup(backup_file: str) -> dict`**: Información del backup
  - Retorna: diccionario con nombre, ruta, tamaño (MB), fecha

### 2. `ui/widgets/backup_dialog.py`
Diálogo para seleccionar backup a restaurar:

- **`RestoreBackupDialog`**: Widget QDialog
  - Muestra lista de backups disponibles
  - Información de cada backup (tamaño, fecha)
  - Confirmación antes de restaurar
  - `get_selected_backup() -> str`: Retorna ruta del backup seleccionado

### 3. `ui/widgets/configuracion_page_widget.py`
Widget de configuración actualizado con:

- **`_on_crear_backup()`**: Crea backup con confirmación
  - Mensaje de confirmación
  - Resultado de éxito/error

- **`_on_restaurar_backup()`**: Abre diálogo de restauración
  - Confirmación inicial
  - Abre `RestoreBackupDialog`
  - Mensaje de éxito con instrucción de reinicio

## Flujo de Uso

### Crear Backup
1. Usuario hace clic en `btn_copia` (Crear Copia)
2. Se muestra confirmación
3. Se crea backup en `data/backups/`
4. Se muestra mensaje con ruta del archivo

### Restaurar Backup
1. Usuario hace clic en `btn_restaurar` (Restaurar)
2. Se muestra advertencia de reinicio
3. Se abre diálogo `RestoreBackupDialog`
4. Usuario selecciona backup (ve fecha y tamaño)
5. Se pide confirmación final
6. Se restaura el archivo
7. Se muestra mensaje pidiendo reinicio de la aplicación

## Estructura de Directorios

```
data/
├── club_padel.db (base de datos actual)
├── config.json
├── auth.json
└── backups/ (directorio creado automáticamente)
    ├── club_padel_backup_20251209_143022.db
    ├── club_padel_backup_20251209_120515.db
    ├── club_padel_pre_restore_20251209_143050.db (seguridad antes de restaurar)
    └── ...
```

## Características de Seguridad

1. **Timestamping**: Cada backup incluye fecha/hora en el nombre
2. **Pre-restore backup**: Se crea copia de seguridad de la BD actual antes de restaurar
3. **Confirmaciones**: Múltiples confirmaciones antes de operaciones críticas
4. **Validaciones**: Verifica que los archivos sean válidos antes de restaurar
5. **Requerimiento de reinicio**: Obliga al usuario a reiniciar la aplicación tras restaurar

## Notas Técnicas

- Las copias de seguridad usan `shutil.copy2()` (preserva metadatos)
- Se crean directorios automáticamente si no existen
- Los backups se muestran ordenados por fecha (más recientes primero)
- Tamaño mostrado en MB con 2 decimales
- Compatible con SQLite (archivos .db)

## Ejemplo de Uso Programático

```python
from utils.backup import crear_backup, restaurar_backup, listar_backups

# Crear backup
ok, mensaje = crear_backup()
if ok:
    print(f"Backup guardado en: {mensaje}")

# Listar backups
backups = listar_backups()
for backup in backups:
    print(backup)

# Restaurar
ok, mensaje = restaurar_backup(backups[0])
if ok:
    print("Backup restaurado. Reinicia la aplicación.")
```

## Integración en UI

Los botones en la página de configuración están conectados a:

- `btn_copia` → `_on_crear_backup()`
- `btn_restaurar` → `_on_restaurar_backup()`

Los botones se conectan dinámicamente si existen en la UI (`hasattr` check).
