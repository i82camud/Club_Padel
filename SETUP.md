# Club Padel - Guía de Instalación

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
- **pytest**: Testing (opcional)

### 4. Crear la base de datos
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

### 5. Ejecutar la aplicación
```bash
python main.py
```

La aplicación se abrirá en una ventana de escritorio.

**🔐 Acceso inicial:**
- **Contraseña por defecto:** `admin`
- Se recomienda cambiar la contraseña en la página de Configuración tras el primer acceso

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
│   ├── validators.py
│   ├── auth.py
│   └── settings.py
├── scripts/               # Scripts de utilidad
│   ├── reset_db.py
│   └── seed_test_data.py
└── test/                  # Tests unitarios
    └── test_*.py
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

## Contacto y soporte

Para reportar problemas o sugerencias, contáctate con el equipo de desarrollo.
