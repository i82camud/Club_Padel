from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QMessageBox
from PySide6.QtCore import QFile
from utils.auth import verify_password, ensure_auth_file_exists


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login')
        self.setModal(True)

        # Usar la UI compilada por pyside6-uic
        from ui.login_ui import Ui_Dialog  # generado por pyside6-uic

        # Asegurar fichero de auth antes de mostrar
        ensure_auth_file_exists()

        # Intentar aplicar la misma hoja de estilos que el resto de la app
        try:
            style_file = QFile("ui/styles/style.qss")
            if style_file.open(QFile.ReadOnly):
                qss = str(style_file.readAll(), encoding='utf-8')
                self.setStyleSheet(qss)
        except Exception:
            pass

        # Usar la UI generada
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # Las conexiones `accepted`/`rejected` ya las crea `setupUi` (ver ui/login_ui.py),
        # por lo que no es necesario reconectarlas aquí.

        # Intentar dar foco inicial al campo de contraseña para que el usuario
        # pueda empezar a escribir sin tener que hacer clic.
        try:
            self.ui.txt_clave.setFocus()
            self.ui.txt_clave.selectAll()
        except Exception:
            pass

    def accept(self) -> None:
        """Override de QDialog.accept: valida la contraseña antes de aceptar.

        Si la contraseña es correcta llama a la implementación base para cerrar
        el diálogo; en caso contrario muestra un `QMessageBox` y mantiene el
        diálogo abierto.
        """
        try:
            pwd = self.ui.txt_clave.text()
        except Exception:
            pwd = ''

        if verify_password(pwd):
            super().accept()
            return
        QMessageBox.warning(self, 'Error', 'Contraseña incorrecta')
        # Enfocar y seleccionar el texto del campo de contraseña para facilitar reintento
        try:
            self.ui.txt_clave.setFocus()
            self.ui.txt_clave.selectAll()
        except Exception:
            pass

    def showEvent(self, event):
        """Asegura el foco en el campo de contraseña cuando el diálogo se muestra."""
        try:
            self.ui.txt_clave.setFocus()
            self.ui.txt_clave.selectAll()
        except Exception:
            pass
        return super().showEvent(event)
