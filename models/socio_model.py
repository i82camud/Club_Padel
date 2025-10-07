"""Model de Socio (SQLAlchemy-only).

Este módulo ahora utiliza exclusivamente SQLAlchemy. Las funciones devuelven
tuplas (compatibilidad con el resto del código) pero internamente usan ORM.
"""
from . import orm as orm_module


def _get_sqlalchemy_components():
    """Resolver SessionLocal y Socio ORM en tiempo de llamada.

    Evita capturar referencias a un engine/SessionLocal creado al importar el
    módulo (esto rompe las pruebas que monkeypatchan `models.orm`).
    """
    try:
        from . import orm as orm_module
        from .orm_models import Socio as SocioORM
        return orm_module.SessionLocal, SocioORM
    except Exception:
        return None, None


# -----------------------
# CRUD para Socio
# -----------------------


def insertar_socio(nombre, apellido1, apellido2, email, telefono, estado="activo"):
    SessionLocal, SocioORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            s = SocioORM(
                nombre=nombre,
                apellido1=apellido1,
                apellido2=apellido2,
                email=email,
                telefono=telefono,
                estado=estado,
            )
            session.add(s)
            session.commit()
            return s.id_socio
        finally:
            session.close()

    # Si no hay SQLAlchemy disponible, esto lanzará en la resolución al vuelo.
    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def obtener_socio_por_id(id_socio):
    SessionLocal, SocioORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            s = session.get(SocioORM, id_socio)
            if s is None:
                return None
            # Devolver tupla (id, nombre, ...)
            return (s.id_socio, s.nombre, s.apellido1, s.apellido2, s.email, s.telefono, s.estado)
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def listar_socios():
    SessionLocal, SocioORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            rows = session.query(SocioORM).all()
            return [(s.id_socio, s.nombre, s.apellido1, s.apellido2, s.email, s.telefono, s.estado) for s in rows]
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def modificar_socio(id_socio, nombre, apellido1, apellido2, email, telefono):
    SessionLocal, SocioORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            s = session.get(SocioORM, id_socio)
            if s is None:
                return
            s.nombre = nombre
            s.apellido1 = apellido1
            s.apellido2 = apellido2
            s.email = email
            s.telefono = telefono
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def baja_socio(id_socio):
    SessionLocal, SocioORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            s = session.get(SocioORM, id_socio)
            if s is None:
                return
            s.estado = 'inactivo'
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def activa_socio(id_socio):
    SessionLocal, SocioORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            s = session.get(SocioORM, id_socio)
            if s is None:
                return
            s.estado = 'activo'
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def existe_correo_id(correo, id_socio=None):
    SessionLocal, SocioORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            q = session.query(SocioORM).filter(SocioORM.email == correo)
            if id_socio:
                q = q.filter(SocioORM.id_socio != id_socio)
            return session.query(q.exists()).scalar()
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")