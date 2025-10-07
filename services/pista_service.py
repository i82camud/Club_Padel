"""Servicios para Pista usando SQLAlchemy: gestionan sesiones y devuelven objetos ORM."""
from typing import List, Optional

from models import orm
from models.orm_models import Pista as PistaORM


def insertar_pista(nombre: str, tipo: str, pared: str = None, estado: str = 'activa') -> PistaORM:
    session = orm.SessionLocal()
    try:
        p = PistaORM(nombre=nombre, pared=pared, tipo=tipo, estado=estado)
        session.add(p)
        session.commit()
        session.refresh(p)
        return p
    finally:
        session.close()


def listar_pistas(estado: str = None) -> List[PistaORM]:
    session = orm.SessionLocal()
    try:
        q = session.query(PistaORM)
        if estado:
            q = q.filter(PistaORM.estado == estado)
        return q.all()
    finally:
        session.close()


def obtener_pista_por_id(id_pista: int) -> Optional[PistaORM]:
    session = orm.SessionLocal()
    try:
        return session.get(PistaORM, id_pista)
    finally:
        session.close()


def modificar_pista(id_pista: int, nombre: str, pared: str, tipo: str):
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


def actualizar_pista(id_pista: int, nombre: str = None, tipo: str = None, estado: str = None):
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
        p.estado = estado

    session = orm.SessionLocal()
    try:
        p_merged = session.merge(p)
        session.commit()
        session.refresh(p_merged)
        return p_merged
    finally:
        session.close()


def activar_pista(id_pista: int):
    session = orm.SessionLocal()
    try:
        p = session.get(PistaORM, id_pista)
        if p is None:
            return None
        p.estado = 'activa'
        session.commit()
        return p
    finally:
        session.close()


def desactivar_pista(id_pista: int):
    session = orm.SessionLocal()
    try:
        p = session.get(PistaORM, id_pista)
        if p is None:
            return None
        p.estado = 'inactiva'
        session.commit()
        return p
    finally:
        session.close()


__all__ = [
    'insertar_pista', 'listar_pistas', 'modificar_pista', 'activar_pista', 'desactivar_pista', 'obtener_pista_por_id', 'actualizar_pista'
]
