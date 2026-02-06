"""Diálogos para gestión de copias de seguridad."""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QListWidget, QListWidgetItem, QMessageBox)
from PySide6.QtCore import QFile
from utils.backup import listar_backups, obtener_info_backup


def _obtener_estilos_dialogo() -> str:
    """Obtiene los estilos del archivo style.qss."""
    qss = ""
    try:
        style_file = QFile("ui/styles/style.qss")
        if style_file.open(QFile.ReadOnly):
            qss = str(style_file.readAll(), encoding='utf-8')
    except Exception:
        pass
    return qss


class RestoreBackupDialog(QDialog):
    """Diálogo para seleccionar y restaurar un backup.
    
    Muestra la lista de backups disponibles y permite seleccionar uno
    para restaurar la base de datos.
    """
    
    def __init__(self, parent=None):
        """Inicializa el diálogo de restauración.
        
        Args:
            parent: Widget padre (por defecto None).
        """
        super().__init__(parent)
        self.setWindowTitle("Restaurar Backup")
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        self.setStyleSheet(_obtener_estilos_dialogo())
        
        self.selected_backup = None
        
        layout = QVBoxLayout(self)
        
        # Información
        layout.addWidget(QLabel("Selecciona un backup para restaurar:"))
        
        # Lista de backups
        self.list_backups = QListWidget()
        self._cargar_backups()
        layout.addWidget(self.list_backups)
        
        # Información del backup seleccionado
        self.lbl_info = QLabel("Selecciona un backup para ver detalles")
        self.lbl_info.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.lbl_info)
        
        # Botones
        botones = QHBoxLayout()
        
        btn_restaurar = QPushButton("Restaurar")
        btn_restaurar.clicked.connect(self._on_restaurar)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        botones.addWidget(btn_restaurar)
        botones.addWidget(btn_cancelar)
        layout.addLayout(botones)
        
        # Conectar selección
        self.list_backups.itemSelectionChanged.connect(self._on_backup_seleccionado)
    
    def _cargar_backups(self) -> None:
        """Carga la lista de backups disponibles."""
        backups = listar_backups()
        
        if not backups:
            self.list_backups.addItem("No hay backups disponibles")
            return
        
        for backup in backups:
            info = obtener_info_backup(backup)
            if info:
                texto = f"{info['nombre']} - {info['fecha']}"
                item = QListWidgetItem(texto)
                item.setData(256, backup)  # Guardar ruta en rol personalizado
                self.list_backups.addItem(item)
    
    def _on_backup_seleccionado(self) -> None:
        """Muestra la información del backup seleccionado."""
        item = self.list_backups.currentItem()
        if not item:
            self.lbl_info.setText("Selecciona un backup para ver detalles")
            self.selected_backup = None
            return
        
        backup_path = item.data(256)
        if backup_path:
            info = obtener_info_backup(backup_path)
            if info:
                texto = f"Tamaño: {info['tamaño_mb']} MB | Fecha: {info['fecha']}"
                self.lbl_info.setText(texto)
                self.selected_backup = backup_path
        else:
            self.selected_backup = None
    
    def _on_restaurar(self) -> None:
        """Restaura el backup seleccionado."""
        if not self.selected_backup:
            QMessageBox.warning(self, "Error", "Selecciona un backup válido")
            return
        
        # Confirmación
        ret = QMessageBox.warning(
            self, 
            "Confirmación",
            "¿Estás seguro de que deseas restaurar este backup?\n"
            "La base de datos actual se sobrescribirá.",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        
        if ret != QMessageBox.Ok:
            return
        
        self.accept()
    
    def get_selected_backup(self) -> str:
        """Retorna la ruta del backup seleccionado.
        
        Returns:
            Optional[str]: Ruta del backup o None si no se seleccionó ninguno.
        """
        return self.selected_backup
