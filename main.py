"""Launcher que muestra antes un diálogo de login y luego la ventana principal."""
import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.widgets.login_dialog import LoginDialog
from utils.auth import asegurar_fichero_auth_existe
from models.orm import inicializar_bd


def main():
    app = QApplication(sys.argv)

    # Asegurar que existe el fichero de autenticación (crea contraseña por defecto si falta)
    asegurar_fichero_auth_existe()

    login = LoginDialog()
    if login.exec() != 1:
        # Cancelado o fallo de autenticación
        sys.exit(0)

    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()