"""Servicios para Pista usando SQLAlchemy.

Expone funciones CRUD para `Pista` y helpers de estado. Cada función
gestiona su propia sesión y devuelve instancias ORM.
"""
from typing import List, Optional

from models import orm
from models.orm_models import Pista as PistaORM, PistaEstado


def _to_pista_estado(value):
    """Normaliza un valor a `PistaEstado` (None | Enum | int)."""
    if value is None:
        return None
    if isinstance(value, PistaEstado):
        return value
    if isinstance(value, int):
        return PistaEstado(int(value))
    raise ValueError(f"Valor de estado de pista inválido (esperado Enum o int): {value}")


def insertar_pista(nombre: str, pared: str, tipo: str, estado=PistaEstado.ACTIVA) -> PistaORM:
    """Inserta una nueva pista en la base de datos.
    
    Args:
        nombre (str): Nombre de la pista.
        pared (str): Tipo de pared (ej: 'cristal', 'muro').
        tipo (str): Tipo de pista (ej: 'cubierta', 'descubierta').
        estado (PistaEstado): Estado de la pista (por defecto ACTIVA).
    
    Returns:
        PistaORM: Instancia de la pista creada con su ID asignado.
    
    Raises:
        ValueError: Si ya existe una pista con el mismo nombre.
    """
    # Validar que no exista una pista con el mismo nombre
    pista_existente = obtener_pista_por_nombre(nombre)
    if pista_existente is not None:
        raise ValueError(f"Ya existe una pista con el nombre '{nombre}'")
    
    session = orm.SessionLocal()
    try:
        estado_enum = _to_pista_estado(estado)
        p = PistaORM(nombre=nombre, pared=pared, tipo=tipo, estado=estado_enum)
        session.add(p)
        session.commit()
        session.refresh(p)
        return p
    finally:
        session.close()


def listar_pistas(estado: Optional[PistaEstado] = None) -> List[PistaORM]:
    """Obtiene la lista de pistas con filtro opcional por estado.
    
    Args:
        estado (PistaEstado, optional): Estado a filtrar. Si es None, devuelve todas.
    
    Returns:
        List[PistaORM]: Lista de instancias ORM de pistas.
    """
    session = orm.SessionLocal()
    try:
        q = session.query(PistaORM)
        if estado is not None:
            estado_enum = _to_pista_estado(estado)
            q = q.filter(PistaORM.estado == estado_enum)
        return q.all()
    finally:
        session.close()


def obtener_pista_por_id(id_pista: int) -> Optional[PistaORM]:
    """Obtiene una pista por su ID.
    
    Args:
        id_pista (int): ID de la pista a recuperar.
    
    Returns:
        Optional[PistaORM]: Instancia ORM de la pista o None si no existe.
    """
    session = orm.SessionLocal()
    try:
        return session.get(PistaORM, id_pista)
    finally:
        session.close()


def obtener_pista_por_nombre(nombre: str) -> Optional[PistaORM]:
    """Obtiene una pista por su nombre.
    
    Args:
        nombre (str): Nombre de la pista a buscar.
    
    Returns:
        Optional[PistaORM]: Instancia ORM de la pista o None si no existe.
    """
    session = orm.SessionLocal()
    try:
        return session.query(PistaORM).filter(PistaORM.nombre == nombre).first()
    finally:
        session.close()


def modificar_pista(id_pista: int, nombre: str, pared: str, tipo: str) -> Optional[PistaORM]:
    """Modifica los datos de una pista existente.
    
    Args:
        id_pista (int): ID de la pista a modificar.
        nombre (str): Nuevo nombre de la pista.
        pared (str): Nuevo tipo de pared.
        tipo (str): Nuevo tipo de pista.
    
    Returns:
        Optional[PistaORM]: Pista actualizada o None si no existe.
    
    Raises:
        ValueError: Si ya existe otra pista con el mismo nombre.
    """
    # Validar que no exista otra pista con el mismo nombre
    pista_existente = obtener_pista_por_nombre(nombre)
    if pista_existente is not None and pista_existente.id_pista != id_pista:
        raise ValueError(f"Ya existe otra pista con el nombre '{nombre}'")
    
    session = orm.SessionLocal()
    try:
        p = session.get(PistaORM, id_pista)
        if p is None:
            return None
        p.nombre = nombre
        p.pared = pared
        p.tipo = tipo
        session.commit()
        session.refresh(p)
        return p
    finally:
        session.close()


def actualizar_pista(id_pista: int, nombre: str = None, tipo: str = None, estado: str = None) -> Optional[PistaORM]:
    """Actualiza selectivamente los campos de una pista.
    
    Args:
        id_pista (int): ID de la pista a actualizar.
        nombre (str, optional): Nuevo nombre (si se proporciona).
        tipo (str, optional): Nuevo tipo (si se proporciona).
        estado (str, optional): Nuevo estado (si se proporciona).
    
    Returns:
        Optional[PistaORM]: Pista actualizada o None si no existe.
    """
    p = obtener_pista_por_id(id_pista)
    if p is None:
        return None

    # lógica de actualización similar a la anterior
    if nombre is not None:
        p.nombre = nombre
    if tipo is not None:
        if tipo in ("cristal", "muro"):
            p.pared = tipo
        else:
            p.tipo = tipo
    if estado is not None:
        p.estado = _to_pista_estado(estado)

    session = orm.SessionLocal()
    try:
        p_merged = session.merge(p)
        session.commit()
        session.refresh(p_merged)
        return p_merged
    finally:
        session.close()


def activar_pista(id_pista: int) -> Optional[PistaORM]:
    """Marca una pista como activa.
    
    Args:
        id_pista (int): ID de la pista a activar.
    
    Returns:
        Optional[PistaORM]: Pista actualizada o None si no existe.
    """
    session = orm.SessionLocal()
    try:
        p = session.get(PistaORM, id_pista)
        if p is None:
            return None
        p.estado = PistaEstado.ACTIVA
        session.commit()
        return p
    finally:
        session.close()


def desactivar_pista(id_pista: int) -> Optional[PistaORM]:
    """Marca una pista como inactiva (da de baja).
    
    Args:
        id_pista (int): ID de la pista a desactivar.
    
    Returns:
        Optional[PistaORM]: Pista actualizada o None si no existe.
    """
    session = orm.SessionLocal()
    try:
        p = session.get(PistaORM, id_pista)
        if p is None:
            return None
        p.estado = PistaEstado.INACTIVA
        session.commit()
        return p
    finally:
        session.close()


__all__ = [
    'insertar_pista', 'listar_pistas', 'modificar_pista', 'activar_pista', 'desactivar_pista', 'obtener_pista_por_id', 'obtener_pista_por_nombre', 'actualizar_pista'
]
