import json
from pathlib import Path
from datetime import time

CONFIG_PATH = Path("data") / "config.json"


def _ensure_config_exists():
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        # valores por defecto
        default = {
            "timeApertura": "09:00",
            "timeCierre": "22:00",
            "timeReserva": "01:30"
        }
        CONFIG_PATH.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_raw() -> dict:
    _ensure_config_exists()
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_raw(data: dict):
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_config(key: str, default=None):
    cfg = _read_raw()
    return cfg.get(key, default)


def set_config(key: str, value):
    cfg = _read_raw()
    cfg[key] = value
    _write_raw(cfg)


def get_opening_hours() -> (time, time):
    """Devuelve (hora_apertura, hora_cierre) como objetos datetime.time.

    Los valores se almacenan en formato 'HH:MM'. Si no existen, se usan
    valores por defecto (09:00 - 22:00).
    """
    s_open = get_config("timeApertura", "09:00")
    s_close = get_config("timeCierre", "22:00")
    try:
        h, m = [int(x) for x in s_open.split(":")]
        apertura = time(h, m)
    except Exception:
        apertura = time(9, 0)
    try:
        h, m = [int(x) for x in s_close.split(":")]
        cierre = time(h, m)
    except Exception:
        cierre = time(22, 0)
    return apertura, cierre


def get_reservation_duration() -> int:
    """Devuelve la duración de reserva en minutos.

    El valor se almacena en formato 'HH:MM'. Si no existe, se usa
    el valor por defecto (01:30 = 90 minutos).
    """
    s_duration = get_config("timeReserva", "01:30")
    try:
        h, m = [int(x) for x in s_duration.split(":")]
        return h * 60 + m
    except Exception:
        return 90  # 1h 30min por defecto
