import sys
import os
from datetime import date

# Agregar la carpeta padre al path para poder importar models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.db import create_tables
from models.socio_model import listar_socios
from models.pista_model import listar_pistas
from models.reserva_model import insertar_reserva, listar_reservas
from models.pago_model import (
    insertar_pago, insertar_pago_cuota, insertar_pago_reserva, insertar_pago_extra,
    listar_pagos, obtener_pago_por_id
)

def main():
    # Asegurarse de que las tablas existen
    create_tables()

    # Obtener IDs de socio y pista
    socio = listar_socios()[0]
    pista = listar_pistas()[0]

    # Crear reserva
    insertar_reserva(
        id_socio=socio[0],
        id_pista=pista[0],
        fecha=str(date.today()),
        hora_inicio="18:00",
        hora_fin="19:00"
    )
    reserva = listar_reservas()[0]

    # Crear pago de cuota
    pago_cuota_id = insertar_pago(id_socio=socio[0], importe=50.0, fecha_pago=str(date.today()), tipo="cuota")
    insertar_pago_cuota(pago_cuota_id, periodo="Octubre 2025")

    # Crear pago de reserva
    pago_reserva_id = insertar_pago(id_socio=socio[0], importe=20.0, fecha_pago=str(date.today()), tipo="reserva")
    insertar_pago_reserva(pago_reserva_id, id_reserva=reserva[0])

    # Crear pago extra
    pago_extra_id = insertar_pago(id_socio=socio[0], importe=15.0, fecha_pago=str(date.today()), tipo="extra")
    insertar_pago_extra(pago_extra_id, concepto_extra="Bebida energética")

    # Listar todos los pagos
    print("=== Todos los pagos ===")
    for p in listar_pagos():
        print(p)

    # Probar obtener pago por id
    print("\n=== Pago por ID ===")
    pago = obtener_pago_por_id(pago_reserva_id)
    print(pago)

if __name__ == "__main__":
    main()
