"""Servicios para Reserva usando SQLAlchemy.

Funciones CRUD para `Reserva` y utilidades (p.ej. detección de solapamientos).
Las funciones gestionan sesiones y devuelven instancias ORM.
"""
from typing import List, Optional
from datetime import date, time, datetime, timedelta

from models import orm
from models.orm_models import Reserva as ReservaORM, ReservaEstado
from utils.settings import get_horario_apertura, get_max_reservas_simultaneas, get_antelacion_minima, get_antelacion_maxima


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
    """Inserta una nueva reserva verificando solapamientos, antelación y validaciones de horario.
    
    Comprueba que el horario solicitado esté dentro del horario de apertura del club,
    que la duración sea al menos la mínima configurada, que se respeten los tiempos
    de antelación mínima y máxima, que el socio no haya excedido el máximo de reservas
    simultáneas activas. Lanza ValueError si existe solapamiento con otra reserva activa.
    
    Args:
        id_socio (int): Identificador del socio que realiza la reserva.
        id_pista (int): Identificador de la pista a reservar.
        fecha (date): Fecha de la reserva.
        hora_inicio (time): Hora de inicio de la reserva.
        hora_fin (time): Hora de fin de la reserva.
        estado (ReservaEstado | int): Estado inicial de la reserva (por defecto ACTIVA).
    
    Returns:
        ReservaORM: Instancia de la reserva creada con su ID asignado.
    
    Raises:
        ValueError: Si el horario está fuera de apertura, la duración es insuficiente,
                    no se respeta la antelación, el socio ha excedido el máximo de 
                    reservas simultáneas, o existe solapamiento con otra reserva activa.
    """
    session = orm.SessionLocal()
    try:
        # Comprobar que la reserva está dentro del horario de apertura configurado
        apertura, cierre = get_horario_apertura()
        if hora_inicio < apertura or hora_fin > cierre:
            raise ValueError(f"Horario fuera de apertura: el club abre a {apertura.strftime('%H:%M')} y cierra a {cierre.strftime('%H:%M')}")
        
        # Validar que la duración de la reserva sea al menos la configurada
        from utils.settings import get_duracion_reserva
        duracion_minima = get_duracion_reserva()
        # Calcular duración en minutos
        duracion_actual = (hora_fin.hour * 60 + hora_fin.minute) - (hora_inicio.hour * 60 + hora_inicio.minute)
        if duracion_actual < duracion_minima:
            horas = duracion_minima // 60
            minutos = duracion_minima % 60
            raise ValueError(f"La duración de la reserva debe ser de al menos {horas:02d}:{minutos:02d}")

        # Validar antelación: calcular fecha y hora actual
        ahora = datetime.now()
        fecha_hora_reserva = datetime.combine(fecha, hora_inicio)
        diferencia = fecha_hora_reserva - ahora
        
        # Validar antelación mínima (solo si es mayor que 0)
        antel_min_minutos = get_antelacion_minima()
        if antel_min_minutos > 0 and diferencia < timedelta(minutes=antel_min_minutos):
            horas = antel_min_minutos // 60
            minutos = antel_min_minutos % 60
            raise ValueError(f"La reserva debe hacerse con una antelación mínima de {horas:02d}:{minutos:02d}")
        
        # Validar antelación máxima (solo si es mayor que 0)
        antel_max_dias = get_antelacion_maxima()
        if antel_max_dias > 0 and diferencia > timedelta(days=antel_max_dias):
            raise ValueError(f"La reserva no puede hacerse con más de {antel_max_dias} días de antelación")

        # Validar máximo de reservas simultáneas activas (solo si es mayor que 0)
        max_reservas = get_max_reservas_simultaneas()
        if max_reservas > 0:
            reservas_activas = session.query(ReservaORM).filter(
                ReservaORM.id_socio == id_socio,
                ReservaORM.estado == ReservaEstado.ACTIVA,
                ReservaORM.fecha >= date.today()  # Solo reservas futuras o de hoy
            ).count()
            
            if reservas_activas >= max_reservas:
                raise ValueError(f"El socio ha alcanzado el máximo de {max_reservas} reservas simultáneas.")

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


def listar_reservas(id_socio: int = None, id_pista: int = None, estado: str = None, mes: int = None, anio: int = None) -> List[ReservaORM]:
    """Lista reservas con filtros opcionales.
    
    Args:
        id_socio (int): Filtro opcional por identificador de socio.
        id_pista (int): Filtro opcional por identificador de pista.
        estado (ReservaEstado | int): Filtro opcional por estado de la reserva.
        mes (int): Filtro opcional por mes (1-12).
        anio (int): Filtro opcional por año.
    
    Returns:
        List[ReservaORM]: Lista de instancias de reservas que cumplen los filtros, ordenadas por fecha y hora ascendente.
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
        if mes is not None and anio is not None:
            from sqlalchemy import extract
            q = q.filter(extract('month', ReservaORM.fecha) == mes)
            q = q.filter(extract('year', ReservaORM.fecha) == anio)
        elif anio is not None:
            from sqlalchemy import extract
            q = q.filter(extract('year', ReservaORM.fecha) == anio)
        # Ordenar por fecha y hora ascendente
        q = q.order_by(ReservaORM.fecha.asc(), ReservaORM.hora_inicio.asc())
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
        estado (ReservaEstado | int): Nuevo estado de la reserva (opcional).
    
    Returns:
        Optional[ReservaORM]: Instancia actualizada o None si la reserva no existe.
    """
    session = orm.SessionLocal()
    try:
        r = session.get(ReservaORM, id_reserva)
        if r is None:
            return None
        if r.estado == ReservaEstado.CANCELADA:
            raise ValueError("No se puede modificar una reserva cancelada")
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
