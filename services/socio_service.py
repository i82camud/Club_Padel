"""Servicios para Socio usando SQLAlchemy.

Los servicios gestionan las sesiones y devuelven instancias ORM (no tuplas).
Mantienen nombres de función compatibles con la capa superior.
"""
from typing import List, Optional

from models import orm
from models.orm_models import Socio as SocioORM


def insertar_socio(nombre: str, apellido1: str, apellido2: str, email: str, telefono: str, estado: str = "activo") -> SocioORM:
	session = orm.SessionLocal()
	try:
		s = SocioORM(nombre=nombre, apellido1=apellido1, apellido2=apellido2, email=email, telefono=telefono, estado=estado)
		session.add(s)
		session.commit()
		session.refresh(s)
		return s
	finally:
		session.close()


def listar_socios() -> List[SocioORM]:
	session = orm.SessionLocal()
	try:
		return session.query(SocioORM).all()
	finally:
		session.close()


def obtener_socio_por_id(id_socio: int) -> Optional[SocioORM]:
	session = orm.SessionLocal()
	try:
		return session.get(SocioORM, id_socio)
	finally:
		session.close()


def modificar_socio(id_socio: int, nombre: str, apellido1: str, apellido2: str, email: str, telefono: str):
	session = orm.SessionLocal()
	try:
		s = session.get(SocioORM, id_socio)
		if s is None:
			return None
		s.nombre = nombre
		s.apellido1 = apellido1
		s.apellido2 = apellido2
		s.email = email
		s.telefono = telefono
		session.commit()
		session.refresh(s)
		return s
	finally:
		session.close()


def baja_socio(id_socio: int):
	session = orm.SessionLocal()
	try:
		s = session.get(SocioORM, id_socio)
		if s is None:
			return None
		s.estado = 'inactivo'
		session.commit()
		return s
	finally:
		session.close()


def activa_socio(id_socio: int):
	session = orm.SessionLocal()
	try:
		s = session.get(SocioORM, id_socio)
		if s is None:
			return None
		s.estado = 'activo'
		session.commit()
		return s
	finally:
		session.close()


def existe_correo_id(correo: str, id_socio: int = None) -> bool:
	session = orm.SessionLocal()
	try:
		q = session.query(SocioORM).filter(SocioORM.email == correo)
		if id_socio:
			q = q.filter(SocioORM.id_socio != id_socio)
		return session.query(q.exists()).scalar()
	finally:
		session.close()


__all__ = [
	'insertar_socio', 'listar_socios', 'obtener_socio_por_id', 'modificar_socio',
	'baja_socio', 'activa_socio', 'existe_correo_id'
]
