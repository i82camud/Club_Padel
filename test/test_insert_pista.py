import sys
import os

# Agregar la carpeta padre al path para poder importar models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.db import create_tables
from models.pista_model import insertar_pista, listar_pistas, actualizar_pista, desactivar_pista, activar_pista

def main():
    # Asegurarse de que las tablas existen
    create_tables()

    # Insertar algunas pistas de prueba
    insertar_pista(nombre="Pista 1", tipo="cristal")
    insertar_pista(nombre="Pista 2", tipo="muro")
    insertar_pista(nombre="Pista 3", tipo="cristal")

    print("=== Pistas iniciales ===")
    for p in listar_pistas():
        print(p)

    # Actualizar la pista 1
    actualizar_pista(1, nombre="Pista 1 Renovada", tipo="cristal", estado="activa")

    # Desactivar la pista 2
    desactivar_pista(2)

    print("\n=== Pistas después de actualizar y desactivar ===")
    for p in listar_pistas():
        print(p)

    # Activar la pista 2 de nuevo
    activar_pista(2)

    print("\n=== Pistas después de reactivar la pista 2 ===")
    for p in listar_pistas():
        print(p)

if __name__ == "__main__":
    main()
