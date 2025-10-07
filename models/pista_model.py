# Pista_model module
"""Model de Pista (SQLAlchemy-only)."""
from . import orm as orm_module


def _get_sqlalchemy_components():
    try:
        from . import orm as orm_module
        from .orm_models import Pista as PistaORM
        return orm_module.SessionLocal, PistaORM
    except Exception:
        return None, None


# -----------------------
# CRUD para Pista
# -----------------------


def insertar_pista(nombre, tipo, pared=None, estado="activa"):
    """Insertar pista.

    Compatibilidad: los tests llaman a esta función con `tipo` usando valores
    que en realidad podrían corresponder a la columna `pared` ('cristal'|'muro').
    Para mantener compatibilidad, si `pared` es None y `tipo` tiene valor de
    pared, lo tratamos como `pared` y fijamos `tipo` a 'cubierta' por defecto.
    """
    # Inferir pared/tipo si se pasaron en orden distinto
    if pared is None and tipo in ("cristal", "muro"):
        pared = tipo
        tipo = "cubierta"

    SessionLocal, PistaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            p = PistaORM(nombre=nombre, pared=pared, tipo=tipo, estado=estado)
            session.add(p)
            session.commit()
            return p.id_pista
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def obtener_pista_por_id(id_pista):
    SessionLocal, PistaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            p = session.get(PistaORM, id_pista)
            if p is None:
                return None
            return (p.id_pista, p.nombre, p.pared, p.tipo, p.estado)
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def listar_pistas(estado=None):
    SessionLocal, PistaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            q = session.query(PistaORM)
            if estado:
                q = q.filter(PistaORM.estado == estado)
            rows = q.all()
            return [(p.id_pista, p.nombre, p.pared, p.tipo, p.estado) for p in rows]
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def modificar_pista(id_pista, nombre, pared, tipo):
    SessionLocal, PistaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            p = session.get(PistaORM, id_pista)
            if p is None:
                return
            p.nombre = nombre
            p.pared = pared
            p.tipo = tipo
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def actualizar_pista(id_pista, nombre, tipo, estado=None):
    """Alias de compatibilidad con tests que usan `actualizar_pista`.

    Nota: firma esperada en tests es (id, nombre, tipo, estado). Internamente
    delegamos en `modificar_pista` y actualizamos estado si se proporciona.
    """
    # Obtener valores actuales y conservarlos cuando no se indiquen
    current = obtener_pista_por_id(id_pista)
    if current is None:
        return

    # current: (id_pista, nombre, pared, tipo, estado)
    _, curr_nombre, curr_pared, curr_tipo, curr_estado = current

    new_nombre = nombre if nombre is not None else curr_nombre

    # El parámetro `tipo` pasado por tests puede indicar la pared (cristal/muro)
    # o el tipo (cubierta/descubierta). Detectamos y asignamos en consecuencia.
    if tipo in ("cristal", "muro"):
        new_pared = tipo
        new_tipo = curr_tipo
    else:
        new_pared = curr_pared
        new_tipo = tipo if tipo is not None else curr_tipo

    modificar_pista(id_pista, new_nombre, new_pared, new_tipo)

    if estado is not None:
        if estado == 'activa':
            activar_pista(id_pista)
        elif estado == 'inactiva' or estado == 'inactivo':
            desactivar_pista(id_pista)


def activar_pista(id_pista):
    SessionLocal, PistaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            p = session.get(PistaORM, id_pista)
            if p is None:
                return
            p.estado = 'activa'
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")


def desactivar_pista(id_pista):
    SessionLocal, PistaORM = _get_sqlalchemy_components()
    if SessionLocal:
        session = SessionLocal()
        try:
            p = session.get(PistaORM, id_pista)
            if p is None:
                return
            p.estado = 'inactiva'
            session.commit()
            return
        finally:
            session.close()

    raise RuntimeError("SQLAlchemy must be available (project is SQLAlchemy-only)")
