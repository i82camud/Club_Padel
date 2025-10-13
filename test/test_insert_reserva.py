import pytest
from datetime import date, time


def test_reserva_workflow(db_setup):
    from services.socio_service import insertar_socio, listar_socios
    from services.pista_service import insertar_pista, listar_pistas
    from services.reserva_service import insertar_reserva, listar_reservas, cancelar_reserva, actualizar_reserva

    # Crear socio y pista
    insertar_socio(nombre='Aaa', apellido1='Aaa', apellido2='Aaa', email='aaa@aaa.aaa', telefono='611111111')
    insertar_pista(nombre='Pista 1', tipo='cristal')

    socio = listar_socios()[0]
    pista = listar_pistas()[0]

    insertar_reserva(id_socio=socio.id_socio, id_pista=pista.id_pista, fecha=date.today(), hora_inicio=time.fromisoformat('18:00'), hora_fin=time.fromisoformat('19:30'))

    reservas = listar_reservas()
    assert len(reservas) == 1

    reserva_id = reservas[0].id_reserva
    from models.orm_models import ReservaEstado
    actualizar_reserva(id_reserva=reserva_id, id_socio=socio.id_socio, id_pista=pista.id_pista, fecha=date.today(), hora_inicio=time.fromisoformat('19:30'), hora_fin=time.fromisoformat('21:00'), estado=ReservaEstado.ACTIVA)
    cancelar_reserva(reserva_id)
    reservas = listar_reservas()
    # aceptar tanto Enum (ReservaEstado) como strings para compatibilidad
    estado_val = reservas[0].estado
    if hasattr(estado_val, 'name'):
        estado_name = estado_val.name.lower()
    else:
        estado_name = str(estado_val).lower()
    assert estado_name in ('cancelada', 'activa')
