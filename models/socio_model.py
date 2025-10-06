# Socio_model module
from models.db import get_connection

# -----------------------
# CRUD para Socio
# -----------------------

def insertar_socio(nombre, apellido1, apellido2, email, telefono, estado="activo"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Socios (nombre, apellido1, apellido2, email, telefono, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, apellido1, apellido2, email, telefono, estado))
    conn.commit()
    conn.close()


def obtener_socio_por_id(id_socio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Socios WHERE id_socio = ?", (id_socio,))
    socio = cursor.fetchone()
    conn.close()
    return socio


def listar_socios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Socios")
    socios = cursor.fetchall()
    conn.close()
    return socios


def modificar_socio(id_socio, nombre, apellido1, apellido2, email, telefono):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Socios
        SET nombre = ?, apellido1 = ?, apellido2 = ?, email = ?, telefono = ?
        WHERE id_socio = ?
    """, (nombre, apellido1, apellido2, email, telefono, id_socio))
    conn.commit()
    conn.close()


def baja_socio(id_socio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Socios SET estado = 'inactivo' WHERE id_socio = ?", (id_socio,))
    conn.commit()
    conn.close()


def activa_socio(id_socio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Socios SET estado = 'activo' WHERE id_socio = ?", (id_socio,))
    conn.commit()
    conn.close()


def existe_correo_id(correo, id_socio=None):
    conn = get_connection()
    cursor = conn.cursor()
    if id_socio:
        # Para que al modificar no compruebe por su ID
        cursor.execute("SELECT 1 FROM Socios WHERE email=? AND id_socio<>?", (correo, id_socio))
    else:
        cursor.execute("SELECT 1 FROM Socios WHERE email=?", (correo,))
    return cursor.fetchone() is not None