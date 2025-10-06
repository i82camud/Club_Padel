# Pista_model module
from models.db import get_connection

# -----------------------
# CRUD para Pista
# -----------------------

def insertar_pista(nombre, pared, tipo, estado="activa"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pistas (nombre, pared, tipo, estado)
        VALUES (?, ?, ?, ?)
    """, (nombre, pared, tipo, estado))
    conn.commit()
    conn.close()


def obtener_pista_por_id(id_pista):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pistas WHERE id_pista = ?", (id_pista,))
    pista = cursor.fetchone()
    conn.close()
    return pista


def listar_pistas(estado=None):
    conn = get_connection()
    cursor = conn.cursor()
    if estado:
        cursor.execute("SELECT * FROM Pistas WHERE estado = ?", (estado,))
    else:
        cursor.execute("SELECT * FROM Pistas")
    pistas = cursor.fetchall()
    conn.close()
    return pistas


def modificar_pista(id_pista, nombre, pared, tipo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE pistas 
        SET nombre=?, pared=?, tipo=?
        WHERE id_pista=?
    """, (nombre, pared, tipo, id_pista))
    conn.commit()
    conn.close()


def activar_pista(id_pista):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Pistas SET estado = 'activa' WHERE id_pista = ?", (id_pista,))
    conn.commit()
    conn.close()


def desactivar_pista(id_pista):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Pistas SET estado = 'inactiva' WHERE id_pista = ?", (id_pista,))
    conn.commit()
    conn.close()
