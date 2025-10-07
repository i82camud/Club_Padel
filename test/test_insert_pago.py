import pytest
from datetime import date


def test_pagos_workflow(db_setup):
    # Importar los servicios dentro de la función para que la fixture
    # pueda monkeypatchear el engine/SessionLocal antes de que los
    # servicios capturen referencias a ellos.
    from services.socio_service import insertar_socio, listar_socios
    from services.pista_service import insertar_pista, listar_pistas
    from services.reserva_service import insertar_reserva, listar_reservas
    from services.pago_service import (
        insertar_pago, insertar_pago_cuota, insertar_pago_reserva, insertar_pago_extra,
        listar_pagos, obtener_pago_por_id
    )

    # Crear socio y pista
    insertar_socio(nombre='Aaa', apellido1='Aaa', apellido2='Aaa', email='aaa@aaa.aaa', telefono='611111111')
    insertar_pista(nombre='Pista 1', tipo='cristal')

    socio = listar_socios()[0]
    pista = listar_pistas()[0]

    # Crear reserva usando los ids de los objetos ORM
    insertar_reserva(id_socio=socio.id_socio, id_pista=pista.id_pista, fecha=str(date.today()), hora_inicio='18:00', hora_fin='19:00')
    reserva = listar_reservas()[0]

    # Crear pagos y las entradas específicas (cuota, reserva, extra)
    pago_cuota = insertar_pago(id_socio=socio.id_socio, importe=50.0, fecha_pago=str(date.today()), tipo='cuota')
    insertar_pago_cuota(pago_cuota.id_pago, periodo='Octubre 2025')

    pago_reserva = insertar_pago(id_socio=socio.id_socio, importe=20.0, fecha_pago=str(date.today()), tipo='reserva')
    insertar_pago_reserva(pago_reserva.id_pago, id_reserva=reserva.id_reserva)

    pago_extra = insertar_pago(id_socio=socio.id_socio, importe=15.0, fecha_pago=str(date.today()), tipo='extra')
    insertar_pago_extra(pago_extra.id_pago, concepto_extra='Bebida energética')

    pagos = listar_pagos()
    assert len(pagos) >= 3

    pago = obtener_pago_por_id(pago_reserva.id_pago)
    assert pago is not None
