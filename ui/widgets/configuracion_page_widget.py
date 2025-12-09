from PySide6.QtWidgets import QWidget, QPushButton, QMessageBox
from PySide6.QtCore import QTime
from ui.configuracion_page_ui import Ui_configuracion_page
from ui.widgets.change_password_dialog import ChangePasswordDialog
from utils.settings import get_opening_hours, set_config, get_config


class ConfiguracionPage(QWidget):
    """Widget para la página de configuración de la aplicación.
    
    Permite al usuario cambiar la contraseña de administrador y configurar
    los parámetros del club (horarios de apertura/cierre, duración de reservas).
    """
    
    def __init__(self, parent=None):
        """Inicializa la página de configuración.
        
        Args:
            parent: Widget padre (por defecto None).
        """
        super().__init__(parent)
        self.ui = Ui_configuracion_page()
        self.ui.setupUi(self)

        # Conectar botones
        self.ui.btn_clave.clicked.connect(self._open_change_password)
        self.ui.btn_guardar.clicked.connect(self._on_guardar)

        # Inicializar campos
        apertura, cierre = get_opening_hours()
        self.ui.timeApertura.setTime(QTime(apertura.hour, apertura.minute))
        self.ui.timeCierre.setTime(QTime(cierre.hour, cierre.minute))
        
        s_duration = get_config("timeReserva", "01:30")
        h, m = [int(x) for x in s_duration.split(":")]
        self.ui.timeReserva.setTime(QTime(h, m))

    def _open_change_password(self) -> None:
        """Abre el diálogo para cambiar la contraseña del administrador."""
        dlg.exec()

    # Slot compatible con connectSlotsByName de la UI compilada
    def on_btn_clave_clicked(self) -> None:
        """Manejador del botón de cambio de contraseña (slot de Qt)."""

    def _on_guardar(self) -> None:
        """Guarda los valores de configuración (horarios y duración de reservas).
        
        Valida que la hora de apertura sea anterior a la de cierre,
        y que la duración de reserva sea mayor a 0, antes de guardar.
        """
        try:
            t1 = self.ui.timeApertura.time()
            t2 = self.ui.timeCierre.time()
            t3 = self.ui.timeReserva.time()
            
            # Validación mínima: apertura < cierre
            if (t1.hour(), t1.minute()) >= (t2.hour(), t2.minute()):
                raise ValueError('La hora de apertura debe ser anterior a la de cierre.')
            
            # Validar que la duración de reserva no sea cero
            if t3.hour() == 0 and t3.minute() == 0:
                raise ValueError('La duración de la reserva debe ser mayor a 0.')

            s1 = f"{t1.hour():02d}:{t1.minute():02d}"
            s2 = f"{t2.hour():02d}:{t2.minute():02d}"
            s3 = f"{t3.hour():02d}:{t3.minute():02d}"
            
            set_config('timeApertura', s1)
            set_config('timeCierre', s2)
            set_config('timeReserva', s3)
            
            QMessageBox.information(self, 'Configuración', 'Se ha guardado la configuración.')
        except Exception as e:
            QMessageBox.warning(self, 'Configuración', f'No se ha guardado la configuración: {e}')
