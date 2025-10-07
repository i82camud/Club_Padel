# Reserva_model module
"""Model de Reserva (SQLAlchemy-only)."""
from . import orm as orm_module


def _get_sqlalchemy_components():
    try:
        from . import orm as orm_module
        from .orm_models import Reserva as ReservaORM
        return orm_module.SessionLocal, ReservaORM
    except Exception:
        return None, None


# -----------------------
# CRUD para Reserva
# -----------------------


def insertar_reserva(id_socio, id_pista, fecha, hora_inicio, hora_fin, estado="activa"):
    SessionLocal, ReservaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            r = ReservaORM(
                id_socio=id_socio,
                id_pista=id_pista,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                estado=estado,
            )
            session.add(r)
            session.commit()
            return r.id_reserva
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def obtener_reserva_por_id(id_reserva):
    SessionLocal, ReservaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            r = session.get(ReservaORM, id_reserva)
            if r is None:
                return None
            return (r.id_reserva, r.id_socio, r.id_pista, r.fecha, r.hora_inicio, r.hora_fin, r.estado)
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def listar_reservas(id_socio=None, id_pista=None, estado=None):
    SessionLocal, ReservaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            q = session.query(ReservaORM)
            if id_socio:
                q = q.filter(ReservaORM.id_socio == id_socio)
            if id_pista:
                q = q.filter(ReservaORM.id_pista == id_pista)
            if estado:
                q = q.filter(ReservaORM.estado == estado)
            rows = q.all()
            return [(r.id_reserva, r.id_socio, r.id_pista, r.fecha, r.hora_inicio, r.hora_fin, r.estado) for r in rows]
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def actualizar_reserva(id_reserva, id_socio, id_pista, fecha, hora_inicio, hora_fin, estado):
    SessionLocal, ReservaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            r = session.get(ReservaORM, id_reserva)
            if r is None:
                return
            r.id_socio = id_socio
            r.id_pista = id_pista
            r.fecha = fecha
            r.hora_inicio = hora_inicio
            r.hora_fin = hora_fin
            r.estado = estado
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def cancelar_reserva(id_reserva):
    SessionLocal, ReservaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            r = session.get(ReservaORM, id_reserva)
            if r is None:
                return
            r.estado = 'cancelada'
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")
