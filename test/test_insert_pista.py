import pytest


def test_insertar_y_modificar_pistas(db_setup):
    from services.pista_service import insertar_pista, listar_pistas, actualizar_pista, desactivar_pista, activar_pista

    # Insertar algunas pistas de prueba
    insertar_pista(nombre="Pista 1", tipo="cristal")
    insertar_pista(nombre="Pista 2", tipo="muro")
    insertar_pista(nombre="Pista 3", tipo="cristal")

    pistas = listar_pistas()
    assert len(pistas) == 3

    # Actualizar la pista 1
    from models.orm_models import PistaEstado
    actualizar_pista(1, nombre="Pista 1 Renovada", tipo="cristal", estado=PistaEstado.ACTIVA)
    desactivar_pista(2)
    activar_pista(2)

    pistas = listar_pistas()
    assert pistas[0].nombre == 'Pista 1 Renovada'
