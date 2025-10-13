from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    """Bus de eventos ligero para comunicación entre widgets.

    Señales:
    - socios_changed: emitir cuando cambien los socios (insertar/modificar/baja)
    - pistas_changed: emitir cuando cambien las pistas
    """

    socios_changed = Signal()
    pistas_changed = Signal()


# Singleton compartido
bus = EventBus()
