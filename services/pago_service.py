"""Servicios para Pago usando SQLAlchemy.

Este módulo expone funciones para insertar y consultar pagos y sus
subtipos (cuota, reserva, extra). Cada función gestiona su propia
sesión (SessionLocal) y devuelve instancias ORM.

Convenciones:
- Los parámetros de tipo/estado aceptan la Enum correspondiente o un entero
    (se normalizan internamente mediante helpers).
"""
from typing import List, Optional
from datetime import date

from models import orm
from models.orm_models import (
    Pago as PagoORM, PagoCuota as PagoCuotaORM, PagoReserva as PagoReservaORM, PagoExtra as PagoExtraORM,
    PagoEstado, PagoTipo
)


def _to_pago_estado(value) -> Optional[PagoEstado]:
    """Normaliza un valor a PagoEstado.
    
    Args:
        value: None, instancia de PagoEstado o entero.
    
    Returns:
        Optional[PagoEstado]: El estado normalizado o None.
    """
    if value is None:
        return None
    if isinstance(value, PagoEstado):
        return value
    if isinstance(value, int):
        return PagoEstado(int(value))
    raise ValueError(f"Valor de estado de pago inválido (esperado Enum o int): {value}")


def _to_pago_tipo(value) -> Optional[PagoTipo]:
    """Normaliza un valor a PagoTipo.
    
    Args:
        value: None, instancia de PagoTipo o entero.
    
    Returns:
        Optional[PagoTipo]: El tipo normalizado o None.
    """
    if value is None:
        return None
    if isinstance(value, PagoTipo):
        return value
    if isinstance(value, int):
        return PagoTipo(int(value))
    raise ValueError(f"Valor de tipo de pago inválido (esperado Enum o int): {value}")



def insertar_pago(id_socio: int, importe: float, fecha_pago: date, tipo, estado=PagoEstado.PAGADO) -> PagoORM:
    """Inserta un nuevo pago general en la base de datos.
    
    Args:
        id_socio (int): Identificador del socio que realiza el pago.
        importe (float): Cantidad a pagar.
        fecha_pago (date): Fecha del pago.
        tipo: Tipo de pago (PagoTipo o entero).
        estado: Estado del pago (por defecto PAGADO).
    
    Returns:
        PagoORM: Instancia del pago creado con su ID asignado.
    
    Raises:
        ValueError: Si el importe es negativo.
    """
    # Validar que el importe no sea negativo
    if importe < 0:
        raise ValueError("El importe no puede ser negativo")
    
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


def insertar_pago_cuota(id_pago: int, periodo: str) -> PagoCuotaORM:
    """Crea una entrada de tipo cuota asociada a un pago.
    
    Args:
        id_pago (int): Identificador del pago asociado.
        periodo (str): Etiqueta del periodo (p.ej. '2025-09').
    
    Returns:
        PagoCuotaORM: Instancia de la cuota creada.
    """
    session = orm.SessionLocal()
    try:
        pc = PagoCuotaORM(id_pago=id_pago, periodo=periodo)
        session.add(pc)
        session.commit()
        return pc
    finally:
        session.close()


def insertar_pago_reserva(id_pago: int, id_reserva: int) -> PagoReservaORM:
    """Asocia un pago a una reserva creando una entrada PagoReserva.
    
    Args:
        id_pago (int): Identificador del pago.
        id_reserva (int): Identificador de la reserva asociada.
    
    Returns:
        PagoReservaORM: Instancia de la relación pago-reserva creada.
    """
    session = orm.SessionLocal()
    try:
        pr = PagoReservaORM(id_pago=id_pago, id_reserva=id_reserva)
        session.add(pr)
        session.commit()
        return pr
    finally:
        session.close()


def insertar_pago_extra(id_pago: int, concepto: str) -> PagoExtraORM:
    """Crea una entrada de tipo 'extra' asociada a un pago.
    
    Args:
        id_pago (int): Identificador del pago.
        concepto (str): Descripción del concepto adicional.
    
    Returns:
        PagoExtraORM: Instancia del pago extra creado.
    """
    session = orm.SessionLocal()
    try:
        pe = PagoExtraORM(id_pago=id_pago, concepto=concepto)
        session.add(pe)
        session.commit()
        return pe
    finally:
        session.close()


def listar_pagos(id_socio: int = None, tipo: str = None, mes: int = None, anio: int = None) -> List[PagoORM]:
    """Lista pagos con filtros opcionales.
    
    Args:
        id_socio (int): Filtro opcional por identificador de socio.
        tipo (str): Filtro opcional por tipo de pago (PagoTipo o entero).
        mes (int): Filtro opcional por mes (1-12).
        anio (int): Filtro opcional por año.
    
    Returns:
        List[PagoORM]: Lista de instancias de pagos que cumplen los filtros, ordenados por fecha ascendente.
    """
    session = orm.SessionLocal()
    try:
        q = session.query(PagoORM)
        if id_socio:
            q = q.filter(PagoORM.id_socio == id_socio)
        if tipo:
            q = q.filter(PagoORM.tipo == _to_pago_tipo(tipo))
        if mes is not None and anio is not None:
            from sqlalchemy import extract
            q = q.filter(extract('month', PagoORM.fecha_pago) == mes)
            q = q.filter(extract('year', PagoORM.fecha_pago) == anio)
        elif anio is not None:
            from sqlalchemy import extract
            q = q.filter(extract('year', PagoORM.fecha_pago) == anio)
        # Ordenar por fecha ascendente
        q = q.order_by(PagoORM.fecha_pago.asc())
        return q.all()
    finally:
        session.close()


def listar_pagos_por_socio(id_socio: int) -> List[PagoORM]:
    """Lista todos los pagos de un socio específico.
    
    Args:
        id_socio (int): Identificador del socio.
    
    Returns:
        List[PagoORM]: Lista de instancias de pagos del socio.
    """
    return listar_pagos(id_socio=id_socio)


def obtener_pago_por_id(id_pago: int) -> Optional[PagoORM]:
    """Recupera un pago por su identificador.
    
    Args:
        id_pago (int): Identificador del pago.
    
    Returns:
        Optional[PagoORM]: Instancia del pago o None si no existe.
    """
    session = orm.SessionLocal()
    try:
        return session.get(PagoORM, id_pago)
    finally:
        session.close()


def anular_pago(id_pago: int) -> Optional[PagoORM]:
    """Marca un pago como anulado.
    
    Args:
        id_pago (int): Identificador del pago a anular.
    
    Returns:
        Optional[PagoORM]: Instancia del pago anulado o None si no existe.
    """
    session = orm.SessionLocal()
    try:
        p = session.get(PagoORM, id_pago)
        if p is None:
            return None
        p.estado = PagoEstado.ANULADO
        session.commit()
        return p
    finally:
        session.close()


def modificar_pago(id_pago: int, id_socio: int, importe: float, fecha_pago: date) -> Optional[PagoORM]:
    """Modifica los datos de un pago existente.
    
    Args:
        id_pago (int): Identificador del pago a modificar.
        id_socio (int): Nuevo identificador del socio.
        importe (float): Nuevo importe del pago.
        fecha_pago (date): Nueva fecha del pago.
    
    Returns:
        Optional[PagoORM]: Instancia del pago modificado o None si no existe.
    
    Raises:
        ValueError: Si el importe es negativo.
    """
    # Validar que el importe no sea negativo
    if importe < 0:
        raise ValueError("El importe no puede ser negativo")
    
    session = orm.SessionLocal()
    try:
        p = session.get(PagoORM, id_pago)
        if p is None:
            return None
        p.id_socio = id_socio
        p.importe = importe
        p.fecha_pago = fecha_pago
        session.commit()
        session.refresh(p)
        return p
    finally:
        session.close()


__all__ = [
    'insertar_pago', 'insertar_pago_cuota', 'insertar_pago_reserva', 'insertar_pago_extra',
    'listar_pagos', 'listar_pagos_por_socio', 'obtener_pago_por_id', 'anular_pago', 'modificar_pago'
]
