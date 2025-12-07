import json
import os
import hashlib
import secrets
from typing import Dict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AUTH_PATH = os.path.join(ROOT, 'data', 'auth.json')


def _pbkdf2_hash(password: str, salt: bytes, iterations: int = 200_000) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)


def _write_auth(data: Dict):
    os.makedirs(os.path.dirname(AUTH_PATH), exist_ok=True)
    with open(AUTH_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def _read_auth() -> Dict:
    if not os.path.exists(AUTH_PATH):
        return {}
    with open(AUTH_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_auth_file_exists(default_password: str = 'admin') -> None:
    """Crea el fichero de autenticación con una contraseña por defecto si no existe.

    ADVERTENCIA: la contraseña por defecto debe ser cambiada por el administrador
    en el primer arranque.
    """
    data = _read_auth()
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
    _write_auth(payload)


def verify_password(password: str) -> bool:
    data = _read_auth()
    if not data:
        return False
    salt = bytes.fromhex(data['salt'])
    iterations = int(data.get('iterations', 200_000))
    expected = bytes.fromhex(data['hash'])
    h = _pbkdf2_hash(password, salt, iterations)
    return secrets.compare_digest(h, expected)


def set_password(new_password: str) -> None:
    salt = secrets.token_bytes(16)
    iterations = 200_000
    h = _pbkdf2_hash(new_password, salt, iterations)
    payload = {
        'salt': salt.hex(),
        'iterations': iterations,
        'hash': h.hex()
    }
    _write_auth(payload)


def change_password(current_password: str, new_password: str) -> bool:
    if not verify_password(current_password):
        return False
    set_password(new_password)
    return True
