from PySide6.QtWidgets import QWidget, QPushButton, QMessageBox
from PySide6.QtCore import QTime
from ui.configuracion_page_ui import Ui_configuracion_page
from ui.widgets.change_password_dialog import ChangePasswordDialog
from utils.settings import get_opening_hours, set_config, get_config


class ConfiguracionPage(QWidget):
    
    def __init__(self, parent=None):
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

    def _open_change_password(self):
        dlg = ChangePasswordDialog(self)
        dlg.exec()

    # Slot compatible con connectSlotsByName de la UI compilada
    def on_btn_clave_clicked(self):
        self._open_change_password()

    def _on_guardar(self):
        """Guardar valores de configuración y mostrar confirmación general.
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
