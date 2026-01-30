"""Funciones auxiliares para formateo de fechas y horas.

Proporciona utilidades para convertir objetos date y time a formato de texto
legible para el usuario (DD/MM/YYYY y HH:MM).
"""
from datetime import date, time, datetime
from typing import Any


def formatear_fecha(obj: Any) -> str:
	"""Formatea una fecha tipo date/datetime a 'DD/MM/YYYY'.

	Si el objeto no tiene el atributo year, devuelve str(obj).
	"""
	try:
		if isinstance(obj, datetime):
			return obj.strftime('%d/%m/%Y')
		if isinstance(obj, date):
			return obj.strftime('%d/%m/%Y')
		# intentar usar strftime si está presente
		if hasattr(obj, 'strftime'):
			return obj.strftime('%d/%m/%Y')
	except Exception:
		pass
	return str(obj)


def formatear_hora(obj: Any) -> str:
	"""Formatea un objeto horario a 'HH:MM' si es posible."""
	try:
		if isinstance(obj, time):
			return obj.strftime('%H:%M')
		if hasattr(obj, 'strftime'):
			return obj.strftime('%H:%M')
	except Exception:
		pass
	return str(obj)


__all__ = ['formatear_fecha', 'formatear_hora']
