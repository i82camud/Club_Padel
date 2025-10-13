from datetime import date, time, datetime
from typing import Any


def format_date(obj: Any) -> str:
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


def format_time(obj: Any) -> str:
	"""Formatea un objeto horario a 'HH:MM' si es posible."""
	try:
		if isinstance(obj, time):
			return obj.strftime('%H:%M')
		if hasattr(obj, 'strftime'):
			return obj.strftime('%H:%M')
	except Exception:
		pass
	return str(obj)


__all__ = ['format_date', 'format_time']
