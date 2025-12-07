"""Servicios para Reserva usando SQLAlchemy.

Funciones CRUD para `Reserva` y utilidades (p.ej. detección de solapamientos).
Las funciones gestionan sesiones y devuelven instancias ORM.
"""
from typing import List, Optional
from datetime import date, time

from models import orm
from models.orm_models import Reserva as ReservaORM, ReservaEstado
from utils.settings import get_opening_hours


def _to_reserva_estado(value):
	"""Normaliza un valor a `ReservaEstado` (None | Enum | int)."""
	if value is None:
		return None
	if isinstance(value, ReservaEstado):
		return value
	if isinstance(value, int):
		return ReservaEstado(int(value))
	raise ValueError(f"Valor de estado de reserva inválido (esperado Enum o int): {value}")


def insertar_reserva(id_socio: int, id_pista: int, fecha: date, hora_inicio: time, hora_fin: time, estado=ReservaEstado.ACTIVA) -> ReservaORM:
	"""Crea una reserva verificando solapamientos y devuelve la instancia.

	Lanza ValueError si existe solapamiento con otra reserva activa.
	"""
	session = orm.SessionLocal()
	try:
		# Comprobar que la reserva está dentro del horario de apertura configurado
		apertura, cierre = get_opening_hours()
		if hora_inicio < apertura or hora_fin > cierre:
			raise ValueError(f"Horario fuera de apertura: el club abre a {apertura.strftime('%H:%M')} y cierra a {cierre.strftime('%H:%M')}")
		
		# Validar que la duración de la reserva sea al menos la configurada
		from utils.settings import get_reservation_duration
		duracion_minima = get_reservation_duration()
		# Calcular duración en minutos
		duracion_actual = (hora_fin.hour * 60 + hora_fin.minute) - (hora_inicio.hour * 60 + hora_inicio.minute)
		if duracion_actual < duracion_minima:
			horas = duracion_minima // 60
			minutos = duracion_minima % 60
			raise ValueError(f"La duración de la reserva debe ser de al menos {horas:02d}:{minutos:02d}")

		if hay_solapamiento(id_pista, fecha, hora_inicio, hora_fin):
			raise ValueError("La pista ya está reservada en ese horario.")

		estado_enum = _to_reserva_estado(estado)
		r = ReservaORM(id_socio=id_socio, id_pista=id_pista, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin, estado=estado_enum)
		session.add(r)
		session.commit()
		session.refresh(r)
		return r
	finally:
		session.close()


def listar_reservas(id_socio: int = None, id_pista: int = None, estado: str = None) -> List[ReservaORM]:
	"""Lista reservas con filtros opcionales (id_socio, id_pista, estado)."""
	session = orm.SessionLocal()
	try:
		q = session.query(ReservaORM)
		if id_socio:
			q = q.filter(ReservaORM.id_socio == id_socio)
		if id_pista:
			q = q.filter(ReservaORM.id_pista == id_pista)
		if estado:
			q = q.filter(ReservaORM.estado == _to_reserva_estado(estado))
		return q.all()
	finally:
		session.close()


def obtener_reserva_por_id(id_reserva: int) -> Optional[ReservaORM]:
	"""Recupera una reserva por id o devuelve None si no existe."""
	session = orm.SessionLocal()
	try:
		return session.get(ReservaORM, id_reserva)
	finally:
		session.close()


def actualizar_reserva(id_reserva: int, id_socio: int, id_pista: int, fecha: date, hora_inicio: time, hora_fin: time, estado: str = None):
	"""Actualiza los campos de una reserva y devuelve la instancia actualizada."""
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
			r.estado = _to_reserva_estado(estado)
		session.commit()
		session.refresh(r)
		return r
	finally:
		session.close()


def cancelar_reserva(id_reserva: int):
	"""Marca una reserva como cancelada y la devuelve."""
	session = orm.SessionLocal()
	try:
		r = session.get(ReservaORM, id_reserva)
		if r is None:
			return None
		r.estado = ReservaEstado.CANCELADA
		session.commit()
		return r
	finally:
		session.close()


def hay_solapamiento(id_pista: int, fecha: date, hora_inicio: time, hora_fin: time) -> bool:
	"""Comprueba si existe una reserva activa que se solape con el rango dado."""
	session = orm.SessionLocal()
	try:
		q = session.query(ReservaORM).filter(
			ReservaORM.id_pista == id_pista,
			ReservaORM.fecha == fecha,
			ReservaORM.estado == ReservaEstado.ACTIVA,
			ReservaORM.hora_inicio < hora_fin,
			ReservaORM.hora_fin > hora_inicio
		)
		return session.query(q.exists()).scalar()
	finally:
		session.close()

__all__ = [
	'insertar_reserva', 'listar_reservas', 'obtener_reserva_por_id', 'actualizar_reserva',
	'cancelar_reserva'
]
