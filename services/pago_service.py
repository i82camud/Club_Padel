"""Servicios para Pago usando SQLAlchemy: gestionan sesiones y devuelven objetos ORM."""
from typing import List, Optional

from models import orm
from models.orm_models import Pago as PagoORM, PagoCuota as PagoCuotaORM, PagoReserva as PagoReservaORM, PagoExtra as PagoExtraORM


def insertar_pago(id_socio: int, importe: float, fecha_pago: str, tipo: str, estado: str = 'pagado') -> PagoORM:
	session = orm.SessionLocal()
	try:
		p = PagoORM(id_socio=id_socio, importe=importe, fecha_pago=fecha_pago, tipo=tipo, estado=estado)
		session.add(p)
		session.commit()
		session.refresh(p)
		return p
	finally:
		session.close()


def insertar_pago_cuota(id_pago: int, periodo: str):
	session = orm.SessionLocal()
	try:
		pc = PagoCuotaORM(id_pago=id_pago, periodo=periodo)
		session.add(pc)
		session.commit()
		return pc
	finally:
		session.close()


def insertar_pago_reserva(id_pago: int, id_reserva: int):
	session = orm.SessionLocal()
	try:
		pr = PagoReservaORM(id_pago=id_pago, id_reserva=id_reserva)
		session.add(pr)
		session.commit()
		return pr
	finally:
		session.close()


def insertar_pago_extra(id_pago: int, concepto_extra: str):
	session = orm.SessionLocal()
	try:
		pe = PagoExtraORM(id_pago=id_pago, concepto_extra=concepto_extra)
		session.add(pe)
		session.commit()
		return pe
	finally:
		session.close()


def listar_pagos(id_socio: int = None, tipo: str = None) -> List[PagoORM]:
	session = orm.SessionLocal()
	try:
		q = session.query(PagoORM)
		if id_socio:
			q = q.filter(PagoORM.id_socio == id_socio)
		if tipo:
			q = q.filter(PagoORM.tipo == tipo)
		return q.all()
	finally:
		session.close()


def obtener_pago_por_id(id_pago: int) -> Optional[PagoORM]:
	session = orm.SessionLocal()
	try:
		return session.get(PagoORM, id_pago)
	finally:
		session.close()


__all__ = [
	'insertar_pago', 'insertar_pago_cuota', 'insertar_pago_reserva', 'insertar_pago_extra',
	'listar_pagos', 'obtener_pago_por_id'
]
