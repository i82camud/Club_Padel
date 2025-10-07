"""Servicios para Reserva usando SQLAlchemy: gestionan sesiones y devuelven objetos ORM."""
from typing import List, Optional

from models import orm
from models.orm_models import Reserva as ReservaORM


def insertar_reserva(id_socio: int, id_pista: int, fecha: str, hora_inicio: str, hora_fin: str, estado: str = 'activa') -> ReservaORM:
	session = orm.SessionLocal()
	try:
		r = ReservaORM(id_socio=id_socio, id_pista=id_pista, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, estado=estado)
		session.add(r)
		session.commit()
		session.refresh(r)
		return r
	finally:
		session.close()


def listar_reservas(id_socio: int = None, id_pista: int = None, estado: str = None) -> List[ReservaORM]:
	session = orm.SessionLocal()
	try:
		q = session.query(ReservaORM)
		if id_socio:
			q = q.filter(ReservaORM.id_socio == id_socio)
		if id_pista:
			q = q.filter(ReservaORM.id_pista == id_pista)
		if estado:
			q = q.filter(ReservaORM.estado == estado)
		return q.all()
	finally:
		session.close()


def obtener_reserva_por_id(id_reserva: int) -> Optional[ReservaORM]:
	session = orm.SessionLocal()
	try:
		return session.get(ReservaORM, id_reserva)
	finally:
		session.close()


def actualizar_reserva(id_reserva: int, id_socio: int, id_pista: int, fecha: str, hora_inicio: str, hora_fin: str, estado: str = None):
	session = orm.SessionLocal()
	try:
		r = session.get(ReservaORM, id_reserva)
		if r is None:
			return None
		r.id_socio = id_socio
		r.id_pista = id_pista
		r.fecha = fecha
		r.hora_inicio = hora_inicio
		r.hora_fin = hora_fin
		if estado is not None:
			r.estado = estado
		session.commit()
		session.refresh(r)
		return r
	finally:
		session.close()


def cancelar_reserva(id_reserva: int):
	session = orm.SessionLocal()
	try:
		r = session.get(ReservaORM, id_reserva)
		if r is None:
			return None
		r.estado = 'cancelada'
		session.commit()
		return r
	finally:
		session.close()


__all__ = [
	'insertar_reserva', 'listar_reservas', 'obtener_reserva_por_id', 'actualizar_reserva',
	'cancelar_reserva'
]
