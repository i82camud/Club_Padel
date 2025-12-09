from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QMessageBox
from utils.auth import change_password, verify_password


class ChangePasswordDialog(QDialog):
    """Diálogo para cambiar la contraseña del administrador.
    
    Permite al usuario cambiar su contraseña actual por una nueva después
    de verificar que la contraseña actual es correcta.
    """
    def __init__(self, parent=None):
        """Inicializa el diálogo de cambio de contraseña.
        
        Args:
            parent: Widget padre (por defecto None).
        """
        super().__init__(parent)
        self.setWindowTitle('Cambiar contraseña')
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel('Contraseña actual:'))
        self.current = QLineEdit(self)
        self.current.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.current)

        layout.addWidget(QLabel('Nueva contraseña:'))
        self.new = QLineEdit(self)
        self.new.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new)

        layout.addWidget(QLabel('Repetir nueva contraseña:'))
        self.new2 = QLineEdit(self)
        self.new2.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new2)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        """Maneja la aceptación del diálogo validando y aplicando el cambio de contraseña.
        
        Verifica que todos los campos estén llenos, que las nuevas contraseñas coincidan,
        y que la contraseña actual sea correcta antes de guardar el cambio.
        """
        n1 = self.new.text()
        n2 = self.new2.text()
        if not cur or not n1:
            QMessageBox.warning(self, 'Error', 'Rellena todos los campos')
            return
        if n1 != n2:
            QMessageBox.warning(self, 'Error', 'Las contraseñas no coinciden')
            return
        if not verify_password(cur):
            QMessageBox.warning(self, 'Error', 'Contraseña actual incorrecta')
            return
        ok = change_password(cur, n1)
        if ok:
            QMessageBox.information(self, 'Éxito', 'Contraseña cambiada')
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'No se pudo cambiar la contraseña')
