"""Servicios para Reserva usando SQLAlchemy.

Funciones CRUD para `Reserva` y utilidades (p.ej. detección de solapamientos).
Las funciones gestionan sesiones y devuelven instancias ORM.
"""
from typing import List, Optional
from datetime import date, time

from models import orm
from models.orm_models import Reserva as ReservaORM, ReservaEstado
from utils.settings import get_opening_hours


def _to_reserva_estado(value) -> Optional[ReservaEstado]:
    """Normaliza un valor a ReservaEstado.
    
    Args:
        value: None, instancia de ReservaEstado o entero.
    
    Returns:
        Optional[ReservaEstado]: El estado normalizado o None.
    """
    if value is None:
        return None
    if isinstance(value, ReservaEstado):
        return value
    if isinstance(value, int):
        return ReservaEstado(int(value))
    raise ValueError(f"Valor de estado de reserva inválido (esperado Enum o int): {value}")


def insertar_reserva(id_socio: int, id_pista: int, fecha: date, hora_inicio: time, hora_fin: time, estado=ReservaEstado.ACTIVA) -> ReservaORM:
    """Inserta una nueva reserva verificando solapamientos y validaciones de horario.
    
    Comprueba que el horario solicitado esté dentro del horario de apertura del club
    y que la duración sea al menos la mínima configurada. Lanza ValueError si existe
    solapamiento con otra reserva activa.
    
    Args:
        id_socio (int): Identificador del socio que realiza la reserva.
        id_pista (int): Identificador de la pista a reservar.
        fecha (date): Fecha de la reserva.
        hora_inicio (time): Hora de inicio de la reserva.
        hora_fin (time): Hora de fin de la reserva.
        estado: Estado inicial de la reserva (por defecto ACTIVA).
    
    Returns:
        ReservaORM: Instancia de la reserva creada con su ID asignado.
    
    Raises:
        ValueError: Si el horario está fuera de apertura, la duración es insuficiente
                    o existe solapamiento con otra reserva activa.
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
    """Lista reservas con filtros opcionales.
    
    Args:
        id_socio (int): Filtro opcional por identificador de socio.
        id_pista (int): Filtro opcional por identificador de pista.
        estado (str): Filtro opcional por estado de la reserva.
    
    Returns:
        List[ReservaORM]: Lista de instancias de reservas que cumplen los filtros.
    """
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
    """Recupera una reserva por su identificador.
    
    Args:
        id_reserva (int): Identificador de la reserva.
    
    Returns:
        Optional[ReservaORM]: Instancia de la reserva o None si no existe.
    """
    session = orm.SessionLocal()
    try:
        return session.get(ReservaORM, id_reserva)
    finally:
        session.close()


def actualizar_reserva(id_reserva: int, id_socio: int, id_pista: int, fecha: date, hora_inicio: time, hora_fin: time, estado: str = None) -> Optional[ReservaORM]:
    """Actualiza todos los campos de una reserva existente.
    
    Args:
        id_reserva (int): Identificador de la reserva a actualizar.
        id_socio (int): Nuevo identificador del socio.
        id_pista (int): Nuevo identificador de la pista.
        fecha (date): Nueva fecha de la reserva.
        hora_inicio (time): Nueva hora de inicio.
        hora_fin (time): Nueva hora de fin.
        estado (str): Nuevo estado de la reserva (opcional).
    
    Returns:
        Optional[ReservaORM]: Instancia actualizada o None si la reserva no existe.
    """
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


def cancelar_reserva(id_reserva: int) -> Optional[ReservaORM]:
    """Marca una reserva como cancelada.
    
    Args:
        id_reserva (int): Identificador de la reserva a cancelar.
    
    Returns:
        Optional[ReservaORM]: Instancia de la reserva cancelada o None si no existe.
    """
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
    """Verifica si existe una reserva activa que se solape con el rango horario dado.
    
    Args:
        id_pista (int): Identificador de la pista a verificar.
        fecha (date): Fecha a verificar.
        hora_inicio (time): Hora de inicio del rango a verificar.
        hora_fin (time): Hora de fin del rango a verificar.
    
    Returns:
        bool: True si existe solapamiento con una reserva activa, False en caso contrario.
    """
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
