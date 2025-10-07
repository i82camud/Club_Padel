from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .orm import Base


class Socio(Base):
    __tablename__ = "Socios"

    id_socio = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    apellido1 = Column(String, nullable=False)
    apellido2 = Column(String)
    email = Column(String, nullable=False, unique=True)
    telefono = Column(String, nullable=False, unique=True)
    estado = Column(String, nullable=False)

    pagos = relationship("Pago", back_populates="socio")
    reservas = relationship("Reserva", back_populates="socio")


class Pista(Base):
    __tablename__ = "Pistas"

    id_pista = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    pared = Column(String, nullable=True)
    tipo = Column(String, nullable=False)
    estado = Column(String, nullable=False)

    reservas = relationship("Reserva", back_populates="pista")


class Reserva(Base):
    __tablename__ = "Reservas"

    id_reserva = Column(Integer, primary_key=True, autoincrement=True)
    id_socio = Column(Integer, ForeignKey("Socios.id_socio"), nullable=False)
    id_pista = Column(Integer, ForeignKey("Pistas.id_pista"), nullable=False)
    fecha = Column(String, nullable=False)
    hora_inicio = Column(String, nullable=False)
    hora_fin = Column(String, nullable=False)
    estado = Column(String, nullable=False)

    socio = relationship("Socio", back_populates="reservas")
    pista = relationship("Pista", back_populates="reservas")


class Pago(Base):
    __tablename__ = "Pagos"

    id_pago = Column(Integer, primary_key=True, autoincrement=True)
    id_socio = Column(Integer, ForeignKey("Socios.id_socio"), nullable=False)
    importe = Column(Float, nullable=False)
    fecha_pago = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    tipo = Column(String, nullable=False)

    socio = relationship("Socio", back_populates="pagos")
    cuota = relationship("PagoCuota", uselist=False, back_populates="pago")
    pago_reserva = relationship("PagoReserva", uselist=False, back_populates="pago")
    pago_extra = relationship("PagoExtra", uselist=False, back_populates="pago")


class PagoCuota(Base):
    __tablename__ = "Pago_Cuota"

    id_pago = Column(Integer, ForeignKey("Pagos.id_pago"), primary_key=True)
    periodo = Column(String, nullable=False)

    pago = relationship("Pago", back_populates="cuota")


class PagoReserva(Base):
    __tablename__ = "Pago_Reserva"

    id_pago = Column(Integer, ForeignKey("Pagos.id_pago"), primary_key=True)
    id_reserva = Column(Integer, ForeignKey("Reservas.id_reserva"), nullable=False)

    pago = relationship("Pago", back_populates="pago_reserva")


class PagoExtra(Base):
    __tablename__ = "Pago_Extra"

    id_pago = Column(Integer, ForeignKey("Pagos.id_pago"), primary_key=True)
    concepto_extra = Column(String, nullable=False)

    pago = relationship("Pago", back_populates="pago_extra")
