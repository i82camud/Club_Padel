# 🔐 Credenciales de Acceso - Club Pádel

## Acceso Inicial

**Contraseña por defecto:** `admin`

Esta contraseña se establece automáticamente cuando se inicializa la aplicación por primera vez (al ejecutar `python scripts/reset_db.py`).

---

## ⚠️ Importante

1. **Primera sesión**: La contraseña es `admin`
2. **Cambiar contraseña**: Se recomienda cambiarla inmediatamente en la página de **Configuración**
3. **Seguridad**: La contraseña se almacena hasheada en `data/auth.json` usando PBKDF2-SHA256

---

## Cambiar la Contraseña

1. Ejecutar la aplicación: `python main.py`
2. Acceder con contraseña: `admin`
3. Ir a **Configuración** (esquina inferior izquierda)
4. Hacer clic en **Cambiar Contraseña**
5. Introducir contraseña actual (`admin`)
6. Introducir nueva contraseña (x2)
7. Guardar

---

## Si Olvidaste la Contraseña

1. Localiza el archivo `data/auth.json`
2. Elimínalo: `rm data/auth.json` o `del data\auth.json` (Windows)
3. Reinicia la aplicación: `python main.py`
4. Se recreará con contraseña por defecto: `admin`
5. Cambia nuevamente la contraseña

---

## Detalles Técnicos

- **Algoritmo**: PBKDF2-HMAC-SHA256
- **Iteraciones**: 200,000
- **Salt**: 16 bytes aleatorios
- **Almacenamiento**: `data/auth.json` en formato JSON hexadecimal
- **Código fuente**: `utils/auth.py`

---

## Código de Ejemplo

```python
from utils.auth import verify_password, set_password, change_password

# Verificar contraseña
if verify_password('admin'):
    print("Contraseña correcta")

# Cambiar contraseña
if change_password('admin', 'nueva_contrasena'):
    print("Contraseña cambiada")
else:
    print("Contraseña actual incorrecta")

# Establecer nueva contraseña directamente (no recomendado)
set_password('nueva_contrasena')
```

---

## Distribución a Otros PCs

Cuando distribuyas la aplicación a otros PCs:

1. **Primera vez**: Todos los usuarios acceden con `admin`
2. **Seguridad**: Cada instalación tiene su propio `data/auth.json`
3. **Sincronización**: Las contraseñas NO se sincronizan entre PCs (cada PC tiene su contraseña independiente)

Si necesitas la misma contraseña en varios PCs, puedes copiar manualmente el archivo `data/auth.json` entre instalaciones.

---

## Contacto

Para reportar problemas de seguridad o autenticación, contacta con el equipo de desarrollo.
