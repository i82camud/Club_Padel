# Club Padel - Guía de Instalación y Distribución

## Requisitos previos
- **Python 3.8+** instalado en el sistema
- **Git** para clonar el repositorio (opcional si descargas como ZIP)

## Pasos de instalación

### 1. Obtener el código
```bash
# Opción A: Clonar desde git
git clone https://github.com/i82camud/Club_Padel.git
cd Club_Padel

# Opción B: Descargar como ZIP y extraer
# Luego navegar a la carpeta en la terminal
cd ruta/al/Club_Padel
```

### 2. Crear el entorno virtual
```bash
# En Windows (PowerShell o CMD)
python -m venv .venv
.venv\Scripts\activate

# En macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

**Dependencias instaladas:**
- **PySide6**: Framework de interfaz gráfica
- **SQLAlchemy**: ORM para la base de datos
- **openpyxl**: Generación de archivos Excel

### 4. Verificar configuración (opcional)
```bash
python check_setup.py
```

Esto te mostrará un reporte de todo lo necesario.

### 5. Crear la base de datos
```bash
# Crear las tablas
python scripts/reset_db.py

# Llenar con datos de prueba
python scripts/seed_test_data.py
```

Esto creará:
- Base de datos SQLite en `data/club_padel.db`
- 5 socios (4 activos)
- 3 pistas (2 cubiertas, 1 descubierta)
- 5 reservas de ejemplo
- Varios pagos
- Archivo de autenticación con contraseña por defecto

### 6. Ejecutar la aplicación
```bash
python main.py
```

La aplicación se abrirá en una ventana de escritorio.

**🔐 Acceso inicial:**
- **Contraseña por defecto:** `admin`
- Se recomienda cambiar la contraseña en la página de Configuración tras el primer acceso

---

## Uso en otros PC

Después de la primera instalación, en futuros PCs solo necesita:

```bash
# 1. Clonar o descargar
git clone https://github.com/i82camud/Club_Padel.git
cd Club_Padel

# 2. Entorno virtual (1 sola vez)
python -m venv .venv
.venv\Scripts\activate

# 3. Dependencias (1 sola vez)
pip install -r requirements.txt

# 4. Base de datos (1 sola vez)
python scripts/reset_db.py
python scripts/seed_test_data.py

# 5. Ejecutar (cada vez que quiera usar)
python main.py
```

---

## Solución de problemas

### Error: "No module named 'PySide6'"
**Solución:** Asegúrate de que el entorno virtual está activado y las dependencias están instaladas:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "No such file or directory: data/club_padel.db"
**Solución:** Ejecuta los scripts de inicialización:
```bash
python scripts/reset_db.py
python scripts/seed_test_data.py
```

### La base de datos está corrupta o vacía
**Solución:** Reinicializar desde cero:
```bash
python scripts/reset_db.py
python scripts/seed_test_data.py
```

### Quiero limpiar todo y empezar de nuevo
```bash
# Elimina el entorno
rmdir .venv /s /q

# Crea uno nuevo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/reset_db.py
python scripts/seed_test_data.py
python main.py
```

---

## Estructura de carpetas

```
Club_Padel/
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias de Python
├── data/
│   ├── club_padel.db       # Base de datos SQLite (se crea automáticamente)
│   ├── auth.json           # Configuración de autenticación
│   └── config.json         # Configuración general
├── models/
│   ├── orm.py             # Configuración SQLAlchemy
│   ├── orm_models.py      # Modelos de datos
│   └── db.py              # Utilidades de base de datos
├── services/              # Lógica de negocio
│   ├── socio_service.py
│   ├── pista_service.py
│   ├── reserva_service.py
│   └── pago_service.py
├── ui/                    # Interfaz gráfica
│   ├── main_window.py
│   ├── widgets/           # Widgets personalizados
│   └── qt/                # Archivos UI compilados
├── utils/                 # Utilidades
│   ├── helpers.py
│   ├── auth.py
│   └── settings.py
├── scripts/               # Scripts de utilidad
│   ├── reset_db.py
│   └── seed_test_data.py
```

---

## Funcionalidades principales

### 📋 Gestión de Socios
- Listar, crear, modificar y eliminar socios
- Exportar a Excel con filtros por estado
- Listar reservas y pagos por socio

### 🏐 Gestión de Pistas
- Listar pistas
- Exportar a Excel con filtros por estado

### 📅 Gestión de Reservas
- Crear, modificar y cancelar reservas
- Asignar pista y socio a cada reserva
- Exportar a Excel con filtros por fecha y estado
- Navegar directamente a pagos desde una reserva

### 💰 Gestión de Pagos
- Registrar pagos (Cuota, Reserva, Extra)
- Filtrar por tipo, fecha y estado
- Exportar a Excel global o por socio

### 🔍 Listados con filtros
- Todos los listados permiten filtrar datos
- Exportación a archivos Excel profesionales
- Validación de rangos de fechas

---

## Resumen rápido

```
PC NUEVO:
1. git clone ... → descargar código
2. python -m venv .venv → crear entorno
3. .venv\Scripts\activate → activar entorno
4. pip install -r requirements.txt → instalar dependencias
5. python scripts/reset_db.py → crear BD
6. python scripts/seed_test_data.py → datos de prueba
7. python main.py → ¡EJECUTAR!
```

---

## Contacto y soporte

Para reportar problemas o sugerencias, contáctate con el equipo de desarrollo.
