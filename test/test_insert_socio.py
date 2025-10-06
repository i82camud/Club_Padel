# prueba de inserción de un socio
import sys
import os

# Agregar la carpeta padre al path para poder importar models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.db import create_tables
from models.socio_model import insertar_socio, listar_socios

def main():
    # Asegurarse de que las tablas existen
    create_tables()

    # Insertar un socio de prueba
    insertar_socio(
        nombre="Diego",
        apellido1="Gómez",
        apellido2="López",
        email="diego@example.com",
        telefono="123456789"
    )

    # Listar todos los socios para comprobar
    socios = listar_socios()
    print("Socios en la base de datos:")
    for s in socios:
        print(s)

if __name__ == "__main__":
    main()