import pytest
from types import SimpleNamespace

# These tests run headless and only verify that the widget methods that fill
# QTableWidgets accept both ORM-like objects (with attributes) and tuple/list
# rows without raising exceptions.


def _make_qapp():
    # Create a single QApplication for Qt widgets; PySide6 will reuse it.
    from PySide6.QtWidgets import QApplication
    import sys
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    return QApplication.instance()


def test_cargar_socios_accepts_orm_objects(monkeypatch):
    _make_qapp()
    from ui.widgets.socio_page_widget import SocioPage

    # Fake listar_socios to return an ORM-like object
    from models.orm_models import SocioEstado
    orm_obj = SimpleNamespace(id_socio=1, nombre='X', apellido1='Y', apellido2='Z', email='x@y.z', telefono='000', estado=SocioEstado.ACTIVO)
    monkeypatch.setattr('services.socio_service.listar_socios', lambda: [orm_obj])

    page = SocioPage()
    # Should not raise
    page.cargar_socios()


def test_cargar_pistas_accepts_orm_objects(monkeypatch):
    _make_qapp()
    from ui.widgets.pista_page_widget import PistaPage

    from models.orm_models import PistaEstado
    orm_obj = SimpleNamespace(id_pista=1, nombre='P1', pared=None, tipo='cristal', estado=PistaEstado.ACTIVA)
    monkeypatch.setattr('services.pista_service.listar_pistas', lambda: [orm_obj])

    page = PistaPage()
    page.cargar_pistas()
