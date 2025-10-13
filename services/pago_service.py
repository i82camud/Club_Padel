"""Servicios para Pago usando SQLAlchemy.

Este módulo expone funciones para insertar y consultar pagos y sus
subtipos (cuota, reserva, extra). Cada función gestiona su propia
sesión (SessionLocal) y devuelve instancias ORM.

Convenciones:
- Los parámetros de tipo/estado aceptan la Enum correspondiente o un entero
	(se normalizan internamente mediante helpers)._
"""
from typing import List, Optional
from datetime import date

from models import orm
from models.orm_models import (
	Pago as PagoORM, PagoCuota as PagoCuotaORM, PagoReserva as PagoReservaORM, PagoExtra as PagoExtraORM,
	PagoEstado, PagoTipo
)


def _to_pago_estado(value):
	"""Normaliza un valor a `PagoEstado`.

	Acepta None, una instancia de PagoEstado, o un entero. Lanza ValueError
	si no se puede convertir.
	"""
	if value is None:
		return None
	if isinstance(value, PagoEstado):
		return value
	if isinstance(value, int):
		return PagoEstado(int(value))
	raise ValueError(f"Valor de estado de pago inválido (esperado Enum o int): {value}")


def _to_pago_tipo(value):
	"""Normaliza un valor a `PagoTipo`.

	Acepta None, una instancia de PagoTipo, o un entero. Lanza ValueError
	si no se puede convertir.
	"""
	if value is None:
		return None
	if isinstance(value, PagoTipo):
		return value
	if isinstance(value, int):
		return PagoTipo(int(value))
	raise ValueError(f"Valor de tipo de pago inválido (esperado Enum o int): {value}")



def insertar_pago(id_socio: int, importe: float, fecha_pago: date, tipo, estado=PagoEstado.PAGADO) -> PagoORM:
	"""Inserta un pago y devuelve la instancia ORM.

	Parámetros:
	- id_socio: int
	- importe: float
	- fecha_pago: datetime.date
	- tipo: PagoTipo | int
	- estado: PagoEstado | int (por defecto PagoEstado.PAGADO)
	"""
	session = orm.SessionLocal()
	try:
		estado_enum = _to_pago_estado(estado)
		tipo_enum = _to_pago_tipo(tipo)
		p = PagoORM(id_socio=id_socio, importe=importe, fecha_pago=fecha_pago, tipo=tipo_enum, estado=estado_enum)
		session.add(p)
		session.commit()
		session.refresh(p)
		return p
	finally:
		session.close()


def insertar_pago_cuota(id_pago: int, periodo: str):
	"""Crea una entrada de tipo cuota asociada a `id_pago`.

	- periodo: etiqueta del periodo (p.ej. '2025-09').
	"""
	session = orm.SessionLocal()
	try:
		pc = PagoCuotaORM(id_pago=id_pago, periodo=periodo)
		session.add(pc)
		session.commit()
		return pc
	finally:
		session.close()


def insertar_pago_reserva(id_pago: int, id_reserva: int, concepto: str = None):
	"""Asocia un pago a una reserva (PagoReserva).

	- concepto: texto legible que se almacena junto al enlace a la reserva.
	"""
	session = orm.SessionLocal()
	try:
		pr = PagoReservaORM(id_pago=id_pago, id_reserva=id_reserva, concepto=concepto)
		session.add(pr)
		session.commit()
		return pr
	finally:
		session.close()


def insertar_pago_extra(id_pago: int, concepto_extra: str):
	"""Crea una entrada de tipo 'extra' asociada a `id_pago`.

	- concepto_extra: descripción libre.
	"""
	session = orm.SessionLocal()
	try:
		pe = PagoExtraORM(id_pago=id_pago, concepto_extra=concepto_extra)
		session.add(pe)
		session.commit()
		return pe
	finally:
		session.close()


def listar_pagos(id_socio: int = None, tipo: str = None) -> List[PagoORM]:
	"""Lista pagos. Opcionalmente filtra por `id_socio` o `tipo`.

	`tipo` puede ser `PagoTipo` o int.
	"""
	session = orm.SessionLocal()
	try:
		q = session.query(PagoORM)
		if id_socio:
			q = q.filter(PagoORM.id_socio == id_socio)
		if tipo:
			q = q.filter(PagoORM.tipo == _to_pago_tipo(tipo))
		return q.all()
	finally:
		session.close()


def obtener_pago_por_id(id_pago: int) -> Optional[PagoORM]:
	"""Recupera un pago por id o devuelve None si no existe."""
	session = orm.SessionLocal()
	try:
		return session.get(PagoORM, id_pago)
	finally:
		session.close()


__all__ = [
	'insertar_pago', 'insertar_pago_cuota', 'insertar_pago_reserva', 'insertar_pago_extra',
	'listar_pagos', 'obtener_pago_por_id'
]
