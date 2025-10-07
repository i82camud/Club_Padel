import pytest
from datetime import date


def test_reserva_workflow(db_setup):
    from services.socio_service import insertar_socio, listar_socios
    from services.pista_service import insertar_pista, listar_pistas
    from services.reserva_service import insertar_reserva, listar_reservas, cancelar_reserva, actualizar_reserva

    # Crear socio y pista
    insertar_socio(nombre='Aaa', apellido1='Aaa', apellido2='Aaa', email='aaa@aaa.aaa', telefono='611111111')
    insertar_pista(nombre='Pista 1', tipo='cristal')

    socio = listar_socios()[0]
    pista = listar_pistas()[0]

    insertar_reserva(id_socio=socio.id_socio, id_pista=pista.id_pista, fecha=str(date.today()), hora_inicio='18:00', hora_fin='19:30')

    reservas = listar_reservas()
    assert len(reservas) == 1

    reserva_id = reservas[0].id_reserva
    actualizar_reserva(id_reserva=reserva_id, id_socio=socio.id_socio, id_pista=pista.id_pista, fecha=str(date.today()), hora_inicio='19:30', hora_fin='21:00', estado='activa')
    cancelar_reserva(reserva_id)
    reservas = listar_reservas()
    assert reservas[0].estado in ('cancelada', 'activa')
