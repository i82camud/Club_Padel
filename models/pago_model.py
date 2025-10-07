"""Model de Pago (SQLAlchemy-only)."""
from . import orm as orm_module


def _get_sqlalchemy_components():
    try:
        from . import orm as orm_module
        from .orm_models import Pago as PagoORM, PagoCuota, PagoReserva, PagoExtra
        return orm_module.SessionLocal, PagoORM, PagoCuota, PagoReserva, PagoExtra
    except Exception:
        return (None, None, None, None, None)


# -----------------------
# CRUD para Pago
# -----------------------


def insertar_pago(id_socio, importe, fecha_pago, tipo, estado="pagado"):
    """
    Inserta un pago genérico y devuelve su id.
    """
    SessionLocal, PagoORM, PagoCuota, PagoReserva, PagoExtra = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            p = PagoORM(id_socio=id_socio, importe=importe, fecha_pago=fecha_pago, tipo=tipo, estado=estado)
            session.add(p)
            session.commit()
            return p.id_pago
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


# -----------------------
# Subtipo Pago_Cuota
# -----------------------
def insertar_pago_cuota(id_pago, periodo):
    SessionLocal, PagoORM, PagoCuota, PagoReserva, PagoExtra = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            pc = PagoCuota(id_pago=id_pago, periodo=periodo)
            session.add(pc)
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


# -----------------------
# Subtipo Pago_Reserva
# -----------------------
def insertar_pago_reserva(id_pago, id_reserva):
    SessionLocal, PagoORM, PagoCuota, PagoReserva, PagoExtra = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            pr = PagoReserva(id_pago=id_pago, id_reserva=id_reserva)
            session.add(pr)
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


# -----------------------
# Subtipo Pago_Extra
# -----------------------
def insertar_pago_extra(id_pago, concepto_extra):
    SessionLocal, PagoORM, PagoCuota, PagoReserva, PagoExtra = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            pe = PagoExtra(id_pago=id_pago, concepto_extra=concepto_extra)
            session.add(pe)
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


# -----------------------
# Consultas
# -----------------------
def listar_pagos(id_socio=None, tipo=None):
    SessionLocal, PagoORM, PagoCuota, PagoReserva, PagoExtra = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            q = session.query(PagoORM)
            if id_socio:
                q = q.filter(PagoORM.id_socio == id_socio)
            if tipo:
                q = q.filter(PagoORM.tipo == tipo)
            rows = q.all()
            return [(p.id_pago, p.id_socio, p.importe, p.fecha_pago, p.estado, p.tipo) for p in rows]
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def obtener_pago_por_id(id_pago):
    """
    Devuelve un pago genérico por su ID.
    """
    SessionLocal, PagoORM, PagoCuota, PagoReserva, PagoExtra = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            p = session.get(PagoORM, id_pago)
            if p is None:
                return None
            return (p.id_pago, p.id_socio, p.importe, p.fecha_pago, p.estado, p.tipo)
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")