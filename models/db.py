# Db module
import sqlite3

DB_NAME = "data/club_padel.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla Socio
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Socios (
        id_socio INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido1 TEXT NOT NULL,
        apellido2 TEXT,
        email TEXT UNIQUE NOT NULL,
        telefono TEXT UNIQUE NOT NULL,
        estado TEXT NOT NULL CHECK (estado IN ('activo', 'inactivo'))
    );
    """)

    # Tabla Pista
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pistas (
        id_pista INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        pared TEXT NOT NULL CHECK (pared IN ('cristal', 'muro')),
        tipo TEXT NOT NULL CHECK (tipo IN ('cubierta', 'descubierta')),
        estado TEXT NOT NULL CHECK (estado IN ('activa', 'inactiva'))
    );
    """)

    # Tabla Reserva
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reservas (
        id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
        id_socio INTEGER NOT NULL,
        id_pista INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        estado TEXT NOT NULL CHECK (estado IN ('activa', 'cancelada', 'finalizada')),
        FOREIGN KEY (id_socio) REFERENCES Socio(id_socio),
        FOREIGN KEY (id_pista) REFERENCES Pista(id_pista)
    );
    """)

    # Superentidad Pago
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pagos (
        id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
        id_socio INTEGER NOT NULL,
        importe REAL NOT NULL,
        fecha_pago TEXT NOT NULL,
        estado TEXT NOT NULL CHECK (estado IN ('pagado', 'anulado', 'pendiente')),
        tipo TEXT NOT NULL CHECK (tipo IN ('cuota', 'reserva', 'extra')),
        FOREIGN KEY (id_socio) REFERENCES Socio(id_socio)
    );
    """)

    # Subtipos de Pago
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pago_Cuota (
        id_pago INTEGER PRIMARY KEY,
        periodo TEXT NOT NULL,
        FOREIGN KEY (id_pago) REFERENCES Pago(id_pago)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pago_Reserva (
        id_pago INTEGER PRIMARY KEY,
        id_reserva INTEGER NOT NULL,
        FOREIGN KEY (id_pago) REFERENCES Pago(id_pago),
        FOREIGN KEY (id_reserva) REFERENCES Reserva(id_reserva)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pago_Extra (
        id_pago INTEGER PRIMARY KEY,
        concepto_extra TEXT NOT NULL,
        FOREIGN KEY (id_pago) REFERENCES Pago(id_pago)
    );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("✅ Tablas creadas en la base de datos:", DB_NAME)