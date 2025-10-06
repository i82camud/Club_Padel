import sys
import os
from datetime import date

# Agregar la carpeta padre al path para poder importar models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.db import create_tables
from models.socio_model import listar_socios
from models.pista_model import listar_pistas
from models.reserva_model import insertar_reserva, listar_reservas, cancelar_reserva, actualizar_reserva

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
        hora_fin="19:30"
    )

    print("=== Reservas iniciales ===")
    for r in listar_reservas():
        print(r)

    # Actualizar reserva
    reserva_id = listar_reservas()[0][0]
    actualizar_reserva(
        id_reserva=reserva_id,
        id_socio=socio[0],
        id_pista=pista[0],
        fecha=str(date.today()),
        hora_inicio="19:30",
        hora_fin="21:00",
        estado="activa"
    )

    print("\n=== Reservas después de actualización ===")
    for r in listar_reservas():
        print(r)

    # Cancelar reserva
    cancelar_reserva(reserva_id)
    print("\n=== Reservas después de cancelar ===")
    for r in listar_reservas():
        print(r)

if __name__ == "__main__":
    main()
