"""Script para insertar datos de prueba en la base de datos para los listados."""

import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, time, timedelta
from models.orm import SessionLocal, Base, engine
from models.orm_models import (
    Socio, SocioEstado, Pista, PistaEstado, Reserva, ReservaEstado,
    Pago, PagoEstado, PagoTipo, PagoCuota, PagoReserva, PagoExtra
)


def reset_database():
    """Resetea la base de datos eliminando todas las tablas y recreándolas."""
    try:
        print("🔄 Reseteando base de datos...")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        print("✓ Base de datos reseteada correctamente\n")
    except Exception as e:
        print(f"✗ Error al resetear la base de datos: {e}")
        raise


def seed_socios():
    """Inserta socios de prueba."""
    session = SessionLocal()
    try:
        # Limpiar socios existentes (opcional)
        # session.query(Socio).delete()
        
        socios = [
            Socio(
                nombre="Juan",
                apellido1="García",
                apellido2="López",
                email="juan.garcia@example.com",
                telefono="600111111",
                estado=SocioEstado.ACTIVO
            ),
            Socio(
                nombre="María",
                apellido1="Rodríguez",
                apellido2="Martínez",
                email="maria.rodriguez@example.com",
                telefono="600222222",
                estado=SocioEstado.ACTIVO
            ),
            Socio(
                nombre="Carlos",
                apellido1="Fernández",
                apellido2="García",
                email="carlos.fernandez@example.com",
                telefono="600333333",
                estado=SocioEstado.ACTIVO
            ),
            Socio(
                nombre="Ana",
                apellido1="Pérez",
                apellido2="González",
                email="ana.perez@example.com",
                telefono="600444444",
                estado=SocioEstado.INACTIVO
            ),
            Socio(
                nombre="Luis",
                apellido1="López",
                apellido2="Sánchez",
                email="luis.lopez@example.com",
                telefono="600555555",
                estado=SocioEstado.ACTIVO
            ),
        ]
        
        for socio in socios:
            # Verificar si ya existe
            existing = session.query(Socio).filter_by(email=socio.email).first()
            if not existing:
                session.add(socio)
        
        session.commit()
        print("✓ Socios insertados correctamente")
    except Exception as e:
        print(f"✗ Error al insertar socios: {e}")
        session.rollback()
    finally:
        session.close()


def seed_pistas():
    """Inserta pistas de prueba."""
    session = SessionLocal()
    try:
        pistas = [
            Pista(
                nombre="Pista 1",
                pared="cristal",
                tipo="cubierta",
                estado=PistaEstado.ACTIVA
            ),
            Pista(
                nombre="Pista 2",
                pared="cristal",
                tipo="cubierta",
                estado=PistaEstado.ACTIVA
            ),
            Pista(
                nombre="Pista 3",
                pared="muro",
                tipo="descubierta",
                estado=PistaEstado.INACTIVA
            ),
        ]
        
        for pista in pistas:
            existing = session.query(Pista).filter_by(nombre=pista.nombre).first()
            if not existing:
                session.add(pista)
        
        session.commit()
        print("✓ Pistas insertadas correctamente")
    except Exception as e:
        print(f"✗ Error al insertar pistas: {e}")
        session.rollback()
    finally:
        session.close()


def seed_reservas():
    """Inserta reservas de prueba."""
    session = SessionLocal()
    try:
        # Obtener socios y pistas
        socios = session.query(Socio).filter_by(estado=SocioEstado.ACTIVO).all()
        pistas = session.query(Pista).filter_by(estado=PistaEstado.ACTIVA).all()
        
        if not socios or not pistas:
            print("⚠ No hay socios o pistas activos. Inserta primero socios y pistas.")
            return
        
        hoy = date.today()
        
        reservas = [
            Reserva(
                id_socio=socios[0].id_socio,
                id_pista=pistas[0].id_pista,
                fecha=hoy,
                hora_inicio=time(10, 0),
                hora_fin=time(11, 30),
                estado=ReservaEstado.ACTIVA
            ),
            Reserva(
                id_socio=socios[1].id_socio,
                id_pista=pistas[1].id_pista,
                fecha=hoy,
                hora_inicio=time(12, 0),
                hora_fin=time(13, 30),
                estado=ReservaEstado.ACTIVA
            ),
            Reserva(
                id_socio=socios[0].id_socio,
                id_pista=pistas[0].id_pista,
                fecha=hoy + timedelta(days=1),
                hora_inicio=time(18, 0),
                hora_fin=time(19, 30),
                estado=ReservaEstado.ACTIVA
            ),
            Reserva(
                id_socio=socios[2].id_socio,
                id_pista=pistas[1].id_pista,
                fecha=hoy - timedelta(days=2),
                hora_inicio=time(14, 0),
                hora_fin=time(15, 30),
                estado=ReservaEstado.CANCELADA
            ),
            Reserva(
                id_socio=socios[1].id_socio,
                id_pista=pistas[0].id_pista,
                fecha=hoy + timedelta(days=3),
                hora_inicio=time(16, 0),
                hora_fin=time(17, 30),
                estado=ReservaEstado.ACTIVA
            ),
        ]
        
        for reserva in reservas:
            session.add(reserva)
        
        session.commit()
        print("✓ Reservas insertadas correctamente")
    except Exception as e:
        print(f"✗ Error al insertar reservas: {e}")
        session.rollback()
    finally:
        session.close()


def seed_pagos():
    """Inserta pagos de prueba (cuotas, extras y reservas)."""
    session = SessionLocal()
    try:
        socios = session.query(Socio).filter_by(estado=SocioEstado.ACTIVO).all()
        reservas = session.query(Reserva).all()
        
        if not socios:
            print("⚠ No hay socios activos. Inserta primero socios.")
            return
        
        hoy = date.today()
        
        # Pagos de cuota
        for i, socio in enumerate(socios[:3]):
            # Pago de cuota pagado
            pago_cuota_pagado = Pago(
                id_socio=socio.id_socio,
                importe=50.0,
                fecha_pago=hoy - timedelta(days=7),
                estado=PagoEstado.PAGADO,
                tipo=PagoTipo.CUOTA
            )
            session.add(pago_cuota_pagado)
            session.flush()
            
            pago_cuota_det = PagoCuota(
                id_pago=pago_cuota_pagado.id_pago,
                periodo="Diciembre 2025"
            )
            session.add(pago_cuota_det)
            
            # Pago de cuota anulado
            if i == 1:
                pago_cuota_anulado = Pago(
                    id_socio=socio.id_socio,
                    importe=50.0,
                    fecha_pago=hoy - timedelta(days=14),
                    estado=PagoEstado.ANULADO,
                    tipo=PagoTipo.CUOTA
                )
                session.add(pago_cuota_anulado)
                session.flush()
                
                pago_cuota_det2 = PagoCuota(
                    id_pago=pago_cuota_anulado.id_pago,
                    periodo="Noviembre 2025"
                )
                session.add(pago_cuota_det2)
        
        # Pagos extras
        for i, socio in enumerate(socios[:2]):
            pago_extra = Pago(
                id_socio=socio.id_socio,
                importe=25.0 + (i * 5),
                fecha_pago=hoy - timedelta(days=3),
                estado=PagoEstado.PAGADO,
                tipo=PagoTipo.EXTRA
            )
            session.add(pago_extra)
            session.flush()
            
            concepto = "Bolas" if i == 0 else "Cintas adhesivas"
            pago_extra_det = PagoExtra(
                id_pago=pago_extra.id_pago,
                concepto=concepto
            )
            session.add(pago_extra_det)
        
        # Pagos de reserva
        if reservas:
            for i, reserva in enumerate(reservas[:2]):
                pago_reserva = Pago(
                    id_socio=reserva.id_socio,
                    importe=30.0,
                    fecha_pago=hoy,
                    estado=PagoEstado.PAGADO if i == 0 else PagoEstado.PAGADO,
                    tipo=PagoTipo.RESERVA
                )
                session.add(pago_reserva)
                session.flush()
                
                pago_reserva_det = PagoReserva(
                    id_pago=pago_reserva.id_pago,
                    id_reserva=reserva.id_reserva
                )
                session.add(pago_reserva_det)
        
        session.commit()
        print("✓ Pagos insertados correctamente")
    except Exception as e:
        print(f"✗ Error al insertar pagos: {e}")
        session.rollback()
    finally:
        session.close()


def main():
    """Inserta todos los datos de prueba."""
    print("\n=== Datos de Prueba ===\n")
    
    reset_database()
    
    print("=== Insertando datos de prueba ===\n")
    
    seed_socios()
    seed_pistas()
    seed_reservas()
    seed_pagos()
    
    print("\n=== Datos de prueba insertados correctamente ===\n")


if __name__ == "__main__":
    main()
