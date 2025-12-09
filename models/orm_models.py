from enum import IntEnum

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, CheckConstraint, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from .orm import Base


class IntEnumType(TypeDecorator):
    """Tipo personalizado para almacenar IntEnum en la base de datos como Integer.
    
    Almacena un IntEnum en la base de datos como Integer y lo convierte
    automáticamente al recuperar valores.
    
    Uso:
        Column(IntEnumType(MyEnum), ...)
    """
    impl = Integer
    cache_ok = True

    def __init__(self, enum_class, *args, **kwargs):
        """Inicializa el tipo con la clase Enum a usar.
        
        Args:
            enum_class: Clase IntEnum a usar para conversión.
        """
        super().__init__(*args, **kwargs)
        self._enum_class = enum_class

    def process_bind_param(self, value, dialect):
        """Convierte el valor Enum a entero para almacenar en BD.
        
        Args:
            value: Valor Enum o entero.
            dialect: Dialecto de SQLAlchemy.
        
        Returns:
            int: Valor entero o None.
        """
        if value is None:
            return None
        if isinstance(value, self._enum_class):
            return int(value.value)
        # Only accept IntEnum instances or ints; legacy string handling removed
        return int(value)

    def process_result_value(self, value, dialect):
        """Convierte el valor entero de BD a Enum.
        
        Args:
            value: Valor entero de la BD.
            dialect: Dialecto de SQLAlchemy.
        
        Returns:
            IntEnum: Valor Enum o None.
        """
        if value is None:
            return None
        # Expect integer storage; convert to Enum
        return self._enum_class(int(value))


class SocioEstado(IntEnum):
    ACTIVO = 1
    INACTIVO = 2


class PistaEstado(IntEnum):
    ACTIVA = 1
    INACTIVA = 2


class ReservaEstado(IntEnum):
    ACTIVA = 1
    CANCELADA = 2


class PagoEstado(IntEnum):
    PAGADO = 1
    ANULADO = 2


class PagoTipo(IntEnum):
    CUOTA = 1
    RESERVA = 2
    EXTRA = 3


class Socio(Base):
    __tablename__ = "Socios"

    id_socio = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    apellido1 = Column(String, nullable=False)
    apellido2 = Column(String)
    email = Column(String, nullable=False, unique=True)
    telefono = Column(String, nullable=False, unique=True)
    estado = Column(IntEnumType(SocioEstado), nullable=False, default=SocioEstado.ACTIVO)

    pagos = relationship("Pago", back_populates="socio")
    reservas = relationship("Reserva", back_populates="socio")


class Pista(Base):
    __tablename__ = "Pistas"

    id_pista = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    pared = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    estado = Column(IntEnumType(PistaEstado), nullable=False, default=PistaEstado.ACTIVA)

    reservas = relationship("Reserva", back_populates="pista")


class Reserva(Base):
    __tablename__ = "Reservas"

    id_reserva = Column(Integer, primary_key=True, autoincrement=True)
    id_socio = Column(Integer, ForeignKey("Socios.id_socio"), nullable=False)
    id_pista = Column(Integer, ForeignKey("Pistas.id_pista"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(IntEnumType(ReservaEstado), nullable=False, default=ReservaEstado.ACTIVA)

    socio = relationship("Socio", back_populates="reservas")
    pista = relationship("Pista", back_populates="reservas")


class Pago(Base):
    __tablename__ = "Pagos"

    id_pago = Column(Integer, primary_key=True, autoincrement=True)
    id_socio = Column(Integer, ForeignKey("Socios.id_socio"), nullable=False)
    importe = Column(Float, nullable=False)
    fecha_pago = Column(Date, nullable=False)
    estado = Column(IntEnumType(PagoEstado), nullable=False, default=PagoEstado.PAGADO)
    tipo = Column(IntEnumType(PagoTipo), nullable=False)

    socio = relationship("Socio", back_populates="pagos")
    pago_cuota = relationship("PagoCuota", uselist=False, back_populates="pago")
    pago_reserva = relationship("PagoReserva", uselist=False, back_populates="pago")
    pago_extra = relationship("PagoExtra", uselist=False, back_populates="pago")


class PagoCuota(Base):
    __tablename__ = "Pago_Cuota"

    id_pago = Column(Integer, ForeignKey("Pagos.id_pago"), primary_key=True)
    periodo = Column(String, nullable=False)

    pago = relationship("Pago", back_populates="pago_cuota")


class PagoReserva(Base):
    __tablename__ = "Pago_Reserva"

    id_pago = Column(Integer, ForeignKey("Pagos.id_pago"), primary_key=True)
    id_reserva = Column(Integer, ForeignKey("Reservas.id_reserva"), nullable=False)

    pago = relationship("Pago", back_populates="pago_reserva")


class PagoExtra(Base):
    __tablename__ = "Pago_Extra"

    id_pago = Column(Integer, ForeignKey("Pagos.id_pago"), primary_key=True)
    concepto = Column(String, nullable=False)

    pago = relationship("Pago", back_populates="pago_extra")
