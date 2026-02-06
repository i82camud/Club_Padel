"""Servicios para Socio usando SQLAlchemy.

Proporciona funciones CRUD y validaciones de unicidad para socios.
Las funciones administran sesiones y devuelven instancias ORM.
"""

from typing import List, Optional

from models import orm
from models.orm_models import Socio as SocioORM, SocioEstado


def _to_socio_estado(value):
	"""Normaliza un valor a `SocioEstado` (None | Enum | int)."""
	if value is None:
		return None
	if isinstance(value, SocioEstado):
		return value
	if isinstance(value, int):
		return SocioEstado(int(value))
	# no longer accept strings; expect Enum or int
	raise ValueError(f"Valor de estado de socio inválido (esperado Enum o int): {value}")


def insertar_socio(nombre: str, apellido1: str, apellido2: str, email: str, telefono: str, estado=SocioEstado.ACTIVO) -> SocioORM:
	"""Inserta un nuevo socio en la base de datos.
	
	Args:
		nombre (str): Nombre del socio.
		apellido1 (str): Primer apellido del socio.
		apellido2 (str): Segundo apellido del socio.
		email (str): Correo electrónico del socio.
		telefono (str): Número de teléfono del socio.
		estado (SocioEstado | int): Estado del socio (por defecto ACTIVO).
	
	Returns:
		SocioORM: Instancia del socio creada con su ID asignado.
	"""
	session = orm.SessionLocal()
	try:
		estado_enum = _to_socio_estado(estado)
		s = SocioORM(nombre=nombre, apellido1=apellido1, apellido2=apellido2, email=email, telefono=telefono, estado=estado_enum)
		session.add(s)
		session.commit()
		session.refresh(s)
		return s
	finally:
		session.close()


def listar_socios(estado: Optional[SocioEstado] = None) -> List[SocioORM]:
	"""Obtiene la lista de socios de la base de datos con filtro opcional de estado.
	
	Args:
		estado (SocioEstado | int, optional): Filtro por estado. Si es None, devuelve todos. Defaults to None.
	
	Returns:
		List[SocioORM]: Lista de instancias ORM de socios.
	"""
	session = orm.SessionLocal()
	try:
		query = session.query(SocioORM)
		if estado is not None:
			estado_enum = _to_socio_estado(estado)
			query = query.filter(SocioORM.estado == estado_enum)
		return query.all()
	finally:
		session.close()


def obtener_socio_por_id(id_socio: int) -> Optional[SocioORM]:
	"""Recupera un socio por id o devuelve None."""
	session = orm.SessionLocal()
	try:
		return session.get(SocioORM, id_socio)
	finally:
		session.close()


def modificar_socio(id_socio: int, nombre: str, apellido1: str, apellido2: str, email: str, telefono: str):
	"""Actualiza los datos de un socio existente y devuelve la instancia o None."""
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
	"""Marca un socio como inactivo y devuelve la instancia."""
	session = orm.SessionLocal()
	try:
		s = session.get(SocioORM, id_socio)
		if s is None:
			return None
		s.estado = SocioEstado.INACTIVO
		session.commit()
		return s
	finally:
		session.close()


def activa_socio(id_socio: int):
	"""Marca un socio como activo y devuelve la instancia."""
	session = orm.SessionLocal()
	try:
		s = session.get(SocioORM, id_socio)
		if s is None:
			return None
		s.estado = SocioEstado.ACTIVO
		session.commit()
		return s
	finally:
		session.close()


def existe_correo_id(correo: str, id_socio: int = None) -> bool:
	"""Verifica si un correo ya está registrado en otro socio.
	
	Args:
		correo (str): Correo electrónico a verificar.
		id_socio (int, optional): ID de socio a excluir de la búsqueda (para validar modificaciones).
	
	Returns:
		bool: True si el correo existe en otro socio, False en caso contrario.
	"""
	session = orm.SessionLocal()
	try:
		q = session.query(SocioORM).filter(SocioORM.email == correo)
		if id_socio:
			q = q.filter(SocioORM.id_socio != id_socio)
		return session.query(q.exists()).scalar()
	finally:
		session.close()


def existe_telefono_id(telefono: str, id_socio: int = None) -> bool:
    """Comprueba si existe un teléfono registrado en otro socio.
    
    Excluye de la búsqueda el socio indicado por id_socio si es proporcionado.
    
    Args:
        telefono (str): Número de teléfono a verificar.
        id_socio (int): Identificador del socio a excluir de la búsqueda (opcional).
    
    Returns:
        bool: True si el teléfono existe en otro socio, False en caso contrario.
    """
    session = orm.SessionLocal()
    try:
        q = session.query(SocioORM).filter(SocioORM.telefono == telefono)
        if id_socio:
            q = q.filter(SocioORM.id_socio != id_socio)
        return session.query(q.exists()).scalar()
    finally:
        session.close()


__all__ = [
    'insertar_socio', 'listar_socios', 'obtener_socio_por_id', 'modificar_socio',
    'baja_socio', 'activa_socio', 'existe_correo_id', 'existe_telefono_id'
]
