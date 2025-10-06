# Pago_model module
from models.db import get_connection

# -----------------------
# CRUD para Pago
# -----------------------

def insertar_pago(id_socio, importe, fecha_pago, tipo, estado="pagado"):
    """
    Inserta un pago genérico y devuelve su id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Pagos (id_socio, importe, fecha_pago, estado, tipo)
        VALUES (?, ?, ?, ?, ?)
    """, (id_socio, importe, fecha_pago, estado, tipo))
    pago_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pago_id


# -----------------------
# Subtipo Pago_Cuota
# -----------------------
def insertar_pago_cuota(id_pago, periodo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Pago_Cuota (id_pago, periodo)
        VALUES (?, ?)
    """, (id_pago, periodo))
    conn.commit()
    conn.close()


# -----------------------
# Subtipo Pago_Reserva
# -----------------------
def insertar_pago_reserva(id_pago, id_reserva):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Pago_Reserva (id_pago, id_reserva)
        VALUES (?, ?)
    """, (id_pago, id_reserva))
    conn.commit()
    conn.close()


# -----------------------
# Subtipo Pago_Extra
# -----------------------
def insertar_pago_extra(id_pago, concepto_extra):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Pago_Extra (id_pago, concepto_extra)
        VALUES (?, ?)
    """, (id_pago, concepto_extra))
    conn.commit()
    conn.close()


# -----------------------
# Consultas
# -----------------------
def listar_pagos(id_socio=None, tipo=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Pagos WHERE 1=1"
    params = []

    if id_socio:
        query += " AND id_socio = ?"
        params.append(id_socio)
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)

    cursor.execute(query, tuple(params))
    pagos = cursor.fetchall()
    conn.close()
    return pagos


def obtener_pago_por_id(id_pago):
    """
    Devuelve un pago genérico por su ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pagos WHERE id_pago = ?", (id_pago,))
    pago = cursor.fetchone()
    conn.close()
    return pago