import json
import os
import hashlib
import secrets
from typing import Dict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AUTH_PATH = os.path.join(ROOT, 'data', 'auth.json')


def _pbkdf2_hash(password: str, salt: bytes, iterations: int = 200_000) -> bytes:
    """Genera un hash PBKDF2-SHA256 para una contraseña.
    
    Args:
        password (str): Contraseña a hashear.
        salt (bytes): Salt para el hash.
        iterations (int): Número de iteraciones (por defecto 200000).
    
    Returns:
        bytes: Hash PBKDF2 calculado.
    """
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)


def _escribir_auth(data: Dict) -> None:
    """Escribe los datos de autenticación en el fichero de configuración.
    
    Args:
        data (Dict): Diccionario con los datos de autenticación (salt, iterations, hash).
    """
    os.makedirs(os.path.dirname(AUTH_PATH), exist_ok=True)
    with open(AUTH_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def _leer_auth() -> Dict:
    """Lee los datos de autenticación del fichero de configuración.
    
    Returns:
        Dict: Diccionario con datos de autenticación o {} si no existe.
    """
    if not os.path.exists(AUTH_PATH):
        return {}
    with open(AUTH_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def asegurar_fichero_auth_existe(default_password: str = 'admin') -> None:
    """Crea el fichero de autenticación con una contraseña por defecto si no existe.

    ADVERTENCIA: la contraseña por defecto debe ser cambiada por el administrador
    en el primer arranque.
    """
    data = _leer_auth()
    if data:
        return
    salt = secrets.token_bytes(16)
    iterations = 200_000
    h = _pbkdf2_hash(default_password, salt, iterations)
    payload = {
        'salt': salt.hex(),
        'iterations': iterations,
        'hash': h.hex()
    }
    _escribir_auth(payload)


def verificar_contrasena(password: str) -> bool:
    """Verifica una contraseña contra el hash almacenado.
    
    Args:
        password (str): Contraseña a verificar.
    
    Returns:
        bool: True si la contraseña es correcta, False en caso contrario.
    """
    data = _leer_auth()
    if not data:
        return False
    salt = bytes.fromhex(data['salt'])
    iterations = int(data.get('iterations', 200_000))
    expected = bytes.fromhex(data['hash'])
    h = _pbkdf2_hash(password, salt, iterations)
    return secrets.compare_digest(h, expected)


def establecer_contrasena(new_password: str) -> None:
    """Establece una nueva contraseña en el sistema de autenticación.
    
    Args:
        new_password (str): Nueva contraseña a guardar.
    """
    salt = secrets.token_bytes(16)
    iterations = 200_000
    h = _pbkdf2_hash(new_password, salt, iterations)
    payload = {
        'salt': salt.hex(),
        'iterations': iterations,
        'hash': h.hex()
    }
    _escribir_auth(payload)


def cambiar_contrasena(current_password: str, new_password: str) -> bool:
    """Cambia la contraseña actual por una nueva después de verificar la actual.
    
    Args:
        current_password (str): Contraseña actual para verificación.
        new_password (str): Nueva contraseña a guardar.
    
    Returns:
        bool: True si el cambio fue exitoso, False si la contraseña actual es incorrecta.
    """
    if not verificar_contrasena(current_password):
        return False
    establecer_contrasena(new_password)
    return True
