# Guía de Distribución - Club Padel

## Para que la aplicación funcione en otro PC

### 📋 Lo que necesita el otro PC:
1. **Python 3.8+** instalado
2. **Git** (para clonar) o recibir los archivos en ZIP

---

## ✅ Procedimiento Completo

### Paso 1: Obtener el código

**Opción A - Con Git (recomendado):**
```bash
git clone https://github.com/i82camud/Club_Padel.git
cd Club_Padel
```

**Opción B - Descargar ZIP:**
- Descargar el ZIP desde GitHub
- Extraer en una carpeta
- Abrir terminal en esa carpeta

---

### Paso 2: Crear el entorno virtual

**En Windows (PowerShell o CMD):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

**Se instalan:**
- PySide6 (interfaz gráfica)
- SQLAlchemy (base de datos)
- openpyxl (Excel)
- pytest (testing)

---

### Paso 4: Verificar configuración (OPCIONAL)

```bash
python check_setup.py
```

Esto te mostrará un reporte de todo lo necesario.

---

### Paso 5: Crear la base de datos

```bash
# Crear estructura
python scripts/reset_db.py

# Llenar con datos de prueba
python scripts/seed_test_data.py
```

Se crea:
- `data/club_padel.db` (base de datos)
- Datos iniciales para probar

---

### Paso 6: Ejecutar la aplicación

```bash
python main.py
```

¡La aplicación se abrirá! 🎉

---

## 🔄 Uso en otros PC

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

## 🆘 Solución rápida de errores

### ❌ "No se reconoce el término 'python'"
```
Solución: Instalar Python desde python.org con "Add Python to PATH"
```

### ❌ "No module named 'PySide6'"
```bash
# Asegúrate de que el virtual env está activado:
.venv\Scripts\activate

# Reinstala las dependencias:
pip install -r requirements.txt
```

### ❌ "No se encuentra la base de datos"
```bash
python scripts/reset_db.py
python scripts/seed_test_data.py
```

### ❌ Quiero limpiar todo y empezar de nuevo
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

## 📦 Archivos importantes

| Archivo | Propósito |
|---------|-----------|
| `requirements.txt` | Lista de dependencias (NECESARIO) |
| `main.py` | Punto de entrada (NECESARIO) |
| `check_setup.py` | Verificador de entorno (útil) |
| `scripts/reset_db.py` | Crear base de datos (necesario 1ª vez) |
| `scripts/seed_test_data.py` | Datos de prueba (recomendado) |
| `data/` | Carpeta de datos (se crea automáticamente) |

---

## 🎯 Resumen

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

## ✨ ¡Listo!

Una vez completados estos pasos, la aplicación funcionará igual que en el PC original.

Para **actualizaciones** futuras:
```bash
git pull
pip install -r requirements.txt  # por si hay nuevas dependencias
python main.py
```
