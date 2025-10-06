# Reserva_model module
from models.db import get_connection

# -----------------------
# CRUD para Reserva
# -----------------------

def insertar_reserva(id_socio, id_pista, fecha, hora_inicio, hora_fin, estado="activa"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Reservas (id_socio, id_pista, fecha, hora_inicio, hora_fin, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id_socio, id_pista, fecha, hora_inicio, hora_fin, estado))
    conn.commit()
    conn.close()


def obtener_reserva_por_id(id_reserva):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Reservas WHERE id_reserva = ?", (id_reserva,))
    reserva = cursor.fetchone()
    conn.close()
    return reserva


def listar_reservas(id_socio=None, id_pista=None, estado=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Reservas WHERE 1=1"
    params = []

    if id_socio:
        query += " AND id_socio = ?"
        params.append(id_socio)
    if id_pista:
        query += " AND id_pista = ?"
        params.append(id_pista)
    if estado:
        query += " AND estado = ?"
        params.append(estado)

    cursor.execute(query, tuple(params))
    reservas = cursor.fetchall()
    conn.close()
    return reservas


def actualizar_reserva(id_reserva, id_socio, id_pista, fecha, hora_inicio, hora_fin, estado):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Reservas
        SET id_socio = ?, id_pista = ?, fecha = ?, hora_inicio = ?, hora_fin = ?, estado = ?
        WHERE id_reserva = ?
    """, (id_socio, id_pista, fecha, hora_inicio, hora_fin, estado, id_reserva))
    conn.commit()
    conn.close()


def cancelar_reserva(id_reserva):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Reservas SET estado = 'cancelada' WHERE id_reserva = ?", (id_reserva,))
    conn.commit()
    conn.close()
