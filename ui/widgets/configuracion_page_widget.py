from PySide6.QtWidgets import QWidget
from ui.configuracion_page_ui import Ui_configuracion_page
from ui.widgets.change_password_dialog import ChangePasswordDialog


class ConfiguracionPage(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_configuracion_page()
        self.ui.setupUi(self)

        # Alternativa explícita: conectar el botón si prefieres no usar
        # QMetaObject.connectSlotsByName. La UI generada ya llama a
        # connectSlotsByName, por lo que el método `on_btn_clave_clicked`
        # se conectará automáticamente si existe.
        try:
            self.ui.btn_clave.clicked.connect(self._open_change_password)
        except Exception:
            pass

    def _open_change_password(self):
        dlg = ChangePasswordDialog(self)
        dlg.exec()

    # Slot compatible con connectSlotsByName de la UI compilada
    def on_btn_clave_clicked(self):
        self._open_change_password()
