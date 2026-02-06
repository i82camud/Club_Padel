"""Diálogo de autenticación inicial de la aplicación.

Proporciona el formulario de login para verificar la contraseña
antes de permitir el acceso a la aplicación principal.
"""
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtGui import QIcon
from utils.auth import verificar_contrasena, asegurar_fichero_auth_existe


class LoginDialog(QDialog):
    """Diálogo de autenticación para la aplicación.
    
    Permite al usuario ingresar su contraseña para acceder a la aplicación.
    Valida la contraseña contra el sistema de autenticación antes de permitir el acceso.
    """
    def __init__(self, parent=None):
        """Inicializa el diálogo de login.
        
        Args:
            parent: Widget padre (por defecto None).
        """
        super().__init__(parent)
        self.setWindowTitle('Login')
        self.setModal(True)

        # Usar la UI compilada por pyside6-uic
        from ui.login_ui import Ui_Dialog  # generado por pyside6-uic

        # Asegurar fichero de auth antes de mostrar
        asegurar_fichero_auth_existe()

        # Intentar aplicar la misma hoja de estilos que el resto de la app
        try:
            style_file = QFile("ui/styles/style.qss")
            if style_file.open(QFile.ReadOnly):
                qss = str(style_file.readAll(), encoding='utf-8')
                self.setStyleSheet(qss)
        except Exception:
            pass

        # Cargar y establecer icono del diálogo
        try:
            self.setWindowIcon(QIcon("ui/icons/aplicacion.ico"))
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

        if verificar_contrasena(pwd):
            super().accept()
            return
        QMessageBox.warning(self, 'Error', 'Contraseña incorrecta')
        # Enfocar y seleccionar el texto del campo de contraseña para facilitar reintento
        try:
            self.ui.txt_clave.setFocus()
            self.ui.txt_clave.selectAll()
        except Exception:
            pass

    def showEvent(self, event) -> None:
        """Asegura que el foco esté en el campo de contraseña cuando el diálogo se muestra.
        
        Args:
            event: Evento de Qt.
        """
        try:
            self.ui.txt_clave.setFocus()
            self.ui.txt_clave.selectAll()
        except Exception:
            pass
        return super().showEvent(event)
