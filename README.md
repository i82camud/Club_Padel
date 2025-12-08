# Club_Padel

**Sistema de gestión para clubs de pádel** - Aplicación de escritorio con interfaz gráfica.

Proyecto en Python usando PySide6, SQLAlchemy y Excel para exportar reportes.

## 🚀 Inicio rápido

### Opción 1: Desde otro PC (cliente nuevo)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/i82camud/Club_Padel.git
   cd Club_Padel
   ```

2. **Configurar entorno:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Inicializar base de datos:**
   ```bash
   python scripts/reset_db.py
   python scripts/seed_test_data.py
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

### Verificar configuración

Antes de ejecutar, puedes verificar que todo está bien:
```bash
python check_setup.py
```

---

## 📋 Requisitos

- **Python 3.8+** (3.11+ recomendado)
- **pip** (gestor de paquetes)
- **Git** (opcional, para clonar)

## 📦 Dependencias

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| PySide6 | 6.8.0 | Interfaz gráfica |
| SQLAlchemy | 2.0.43 | ORM para base de datos |
| openpyxl | 3.1.5 | Exportación a Excel |
| pytest | 8.4.2 | Testing |

Todas instaladas con: `pip install -r requirements.txt`

---

## 🏗️ Estructura del Proyecto

```
Club_Padel/
├── main.py                 # Punto de entrada
├── check_setup.py          # Verificador de configuración
├── requirements.txt        # Dependencias
├── SETUP.md               # Guía de instalación detallada
│
├── data/
│   ├── club_padel.db      # Base de datos SQLite
│   ├── auth.json
│   └── config.json
│
├── models/                # Capa de datos
│   ├── orm.py            # Configuración SQLAlchemy
│   ├── orm_models.py     # Definición de modelos
│   └── db.py
│
├── services/              # Lógica de negocio
│   ├── socio_service.py
│   ├── pista_service.py
│   ├── reserva_service.py
│   └── pago_service.py
│
├── ui/                    # Interfaz gráfica
│   ├── main_window.py
│   ├── widgets/
│   └── qt/
│
├── utils/                 # Utilidades
│   ├── helpers.py
│   ├── validators.py
│   ├── auth.py
│   └── settings.py
│
├── scripts/               # Herramientas
│   ├── reset_db.py
│   └── seed_test_data.py
│
└── test/                  # Tests unitarios
    └── test_*.py
```

---

## 💻 Funcionalidades

### ✅ Implementadas
- ✓ CRUD completo de Socios, Pistas, Reservas y Pagos
- ✓ Filtrado por estado en todas las entidades
- ✓ Exportación a Excel con formato profesional
- ✓ Validación de datos de entrada
- ✓ Gestión de sesiones SQLAlchemy
- ✓ Tests unitarios

### 📊 Listados con Excel
- Socios (filtro por estado)
- Pistas (filtro por estado)
- Reservas (filtro por fecha y estado)
- Pagos globales (filtro por tipo, fecha y estado)
- Pagos por socio (filtro por tipo, fecha y estado)
- Reservas por socio (filtro por fecha y estado)

---

## ⚙️ Configuración Windows PowerShell

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Verificar
python check_setup.py

# Inicializar BD
python scripts/reset_db.py
python scripts/seed_test_data.py

# Ejecutar
python main.py
```

---

## 🧪 Ejecutar Tests

```bash
# Tests unitarios
python -m pytest -q

# Un test específico
python -m pytest test/test_insert_socio.py::test_insertar_socio -v
```

---

## 📚 Documentación

Para instrucciones más detalladas, ver:
- **[SETUP.md](SETUP.md)** - Guía completa de instalación
- **Docstrings** - En el código de cada módulo

---

## 🐛 Solución de problemas

### Error: "No module named 'PySide6'"
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### Error de base de datos
```bash
# Reinicializar
python scripts/reset_db.py
python scripts/seed_test_data.py
```

### Verificar entorno
```bash
python check_setup.py
```

---

## 👥 Contribuciones

Para colaborar:
1. Crear una rama: `git checkout -b feature/tu-feature`
2. Commit: `git commit -m "Descripción"`
3. Push: `git push origin feature/tu-feature`
4. Pull Request

---

## 📝 Notas
python -m pytest test/test_insert_socio.py::test_insertar_y_listar_socio -q
```

## Notas importantes

- Si tu entorno no tiene `SQLAlchemy` instalado, las funciones de acceso a datos fallarán (esto ahora es intencional). Instala dependencias con `pip install -r requirements.txt`.