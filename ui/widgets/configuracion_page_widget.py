"""Widget de página de configuración de la aplicación."""

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import QTime
from ui.configuracion_page_ui import Ui_configuracion_page
from ui.widgets.change_password_dialog import ChangePasswordDialog
from ui.widgets.backup_dialog import RestoreBackupDialog
from utils.settings import get_opening_hours, set_config, get_config
from utils.backup import crear_backup, restaurar_backup


class ConfiguracionPage(QWidget):
    """Widget para la página de configuración de la aplicación.
    
    Permite al usuario cambiar la contraseña de administrador, configurar
    los parámetros del club (horarios de apertura/cierre, duración de reservas),
    y gestionar copias de seguridad de la base de datos.
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
        self.ui.btn_copia.clicked.connect(self._on_crear_backup)
        self.ui.btn_restaurar.clicked.connect(self._on_restaurar_backup)

        # Inicializar campos
        apertura, cierre = get_opening_hours()
        self.ui.timeApertura.setTime(QTime(apertura.hour, apertura.minute))
        self.ui.timeCierre.setTime(QTime(cierre.hour, cierre.minute))
        
        s_duration = get_config("timeReserva", "01:30")
        h, m = [int(x) for x in s_duration.split(":")]
        self.ui.timeReserva.setTime(QTime(h, m))

    def _open_change_password(self) -> None:
        """Abre el diálogo para cambiar la contraseña del administrador."""
        dlg = ChangePasswordDialog(self)
        dlg.exec()

    def on_btn_clave_clicked(self) -> None:
        """Manejador del botón de cambio de contraseña (slot de Qt)."""
        self._open_change_password()

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

    def _on_crear_backup(self) -> None:
        """Crea una copia de seguridad de la base de datos.
        
        La copia se guarda en data/backups/ con timestamp.
        """
        # Confirmación
        ret = QMessageBox.question(
            self,
            "Crear Copia de Seguridad",
            "¿Deseas crear una copia de seguridad de la base de datos?",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        
        if ret != QMessageBox.Ok:
            return
        
        ok, mensaje = crear_backup()
        
        if ok:
            QMessageBox.information(
                self,
                "Éxito",
                f"Copia de seguridad creada correctamente:\n{mensaje}"
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo crear la copia de seguridad:\n{mensaje}"
            )

    def _on_restaurar_backup(self) -> None:
        """Restaura la base de datos desde una copia de seguridad.
        
        Abre un diálogo para seleccionar el backup a restaurar.
        """
        # Confirmación
        ret = QMessageBox.warning(
            self,
            "Restaurar Copia de Seguridad",
            "La aplicación debe reiniciarse para completar la restauración.\n"
            "¿Deseas continuar?",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        
        if ret != QMessageBox.Ok:
            return
        
        # Abrir diálogo de selección
        dlg = RestoreBackupDialog(self)
        if dlg.exec() != QMessageBox.Accepted:
            return
        
        backup_path = dlg.get_selected_backup()
        if not backup_path:
            QMessageBox.warning(self, "Error", "No se seleccionó ningún backup")
            return
        
        # Restaurar
        ok, mensaje = restaurar_backup(backup_path)
        
        if ok:
            QMessageBox.information(
                self,
                "Éxito",
                f"{mensaje}\n\nPor favor, reinicia la aplicación para aplicar los cambios."
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo restaurar el backup:\n{mensaje}"
            )

