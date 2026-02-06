"""Tests de funcionalidad de servicios de Socio.

Prueba las operaciones CRUD básicas del módulo socio_service.
"""


def test_insertar_y_listar_socio(db_setup):
    from services.socio_service import insertar_socio, listar_socios

    insertar_socio(
        nombre="Diego",
        apellido1="Gómez",
        apellido2="López",
        email="diego@example.com",
        telefono="123456789"
    )

    socios = listar_socios()
    assert len(socios) == 1
    assert socios[0].nombre == 'Diego'