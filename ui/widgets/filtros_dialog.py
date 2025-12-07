"""Diálogos personalizados para filtros de listados.

Proporciona diálogos para solicitar filtros de fechas, estados, tipos, etc.
para la generación de listados en XLSX.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QDateEdit, QPushButton, QGroupBox, QFormLayout)
from PySide6.QtCore import QDate, QFile


def _obtener_estilos_dialogo():
    """Obtiene los estilos del archivo style.qss."""
    qss = ""
    try:
        style_file = QFile("ui/styles/style.qss")
        if style_file.open(QFile.ReadOnly):
            qss = str(style_file.readAll(), encoding='utf-8')
    except Exception:
        pass
    return qss


class FiltrosSociosDialog(QDialog):
    """Diálogo para filtrar socios por estado."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtros para Listado de Socios")
        self.setMinimumWidth(350)
        self.setStyleSheet(_obtener_estilos_dialogo())
        
        layout = QVBoxLayout(self)
        
        # Estado
        layout.addWidget(QLabel("Estado de Socio:"))
        self.cmb_estado = QComboBox()
        self.cmb_estado.addItems(["Todos", "Activos", "Inactivos"])
        layout.addWidget(self.cmb_estado)
        
        # Botones
        botones = QHBoxLayout()
        self.btn_aceptar = QPushButton("Generar")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_aceptar.clicked.connect(self.accept)
        self.btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(self.btn_aceptar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)
    
    def get_filtros(self):
        """Retorna un diccionario con los filtros seleccionados."""
        return {
            'estado': self.cmb_estado.currentText()
        }


class FiltrosReservasDialog(QDialog):
    """Diálogo para filtrar reservas por fechas y estado."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtros para Listado de Reservas")
        self.setMinimumWidth(400)
        self.setStyleSheet(_obtener_estilos_dialogo())
        
        layout = QVBoxLayout(self)
        
        # Grupo de fechas
        grupo_fechas = QGroupBox("Rango de Fechas (opcional)")
        form_fechas = QFormLayout()
        
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setSpecialValueText("Sin filtro")  # Cuando está en mínimo
        self.fecha_inicio.setMinimumDate(QDate(2000, 1, 1))
        self.fecha_inicio.setDate(QDate(2000, 1, 1))  # Empezar en mínimo = sin filtro
        
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setSpecialValueText("Sin filtro")
        self.fecha_fin.setMinimumDate(QDate(2000, 1, 1))
        self.fecha_fin.setDate(QDate(2000, 1, 1))  # Empezar en mínimo = sin filtro
        
        # Checkbox para habilitar/deshabilitar filtro de fechas
        form_fechas.addRow("Desde:", self.fecha_inicio)
        form_fechas.addRow("Hasta:", self.fecha_fin)
        grupo_fechas.setLayout(form_fechas)
        layout.addWidget(grupo_fechas)
        
        # Estado
        layout.addWidget(QLabel("Estado de Reserva:"))
        self.cmb_estado = QComboBox()
        self.cmb_estado.addItems(["Todas", "Activas", "Canceladas"])
        layout.addWidget(self.cmb_estado)
        
        # Botones
        botones = QHBoxLayout()
        self.btn_aceptar = QPushButton("Generar")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_aceptar.clicked.connect(self.accept)
        self.btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(self.btn_aceptar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)
    
    def get_filtros(self):
        """Retorna un diccionario con los filtros seleccionados."""
        return {
            'fecha_inicio': self.fecha_inicio.date().toPython() if self.fecha_inicio.date() > QDate(2000, 1, 1) else None,
            'fecha_fin': self.fecha_fin.date().toPython() if self.fecha_fin.date() > QDate(2000, 1, 1) else None,
            'estado': self.cmb_estado.currentText()
        }


class FiltrosPagosDialog(QDialog):
    """Diálogo para filtrar pagos por tipo, fechas y estado."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtros para Listado de Pagos")
        self.setMinimumWidth(400)
        self.setStyleSheet(_obtener_estilos_dialogo())
        
        layout = QVBoxLayout(self)
        
        # Tipo de pago
        layout.addWidget(QLabel("Tipo de Pago:"))
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["Todos", "Cuota", "Reserva", "Extra"])
        layout.addWidget(self.cmb_tipo)
        
        # Grupo de fechas
        grupo_fechas = QGroupBox("Rango de Fechas (opcional)")
        form_fechas = QFormLayout()
        
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setSpecialValueText("Sin filtro")
        self.fecha_inicio.setMinimumDate(QDate(2000, 1, 1))
        self.fecha_inicio.setDate(QDate(2000, 1, 1))  # Empezar en mínimo = sin filtro
        
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setSpecialValueText("Sin filtro")
        self.fecha_fin.setMinimumDate(QDate(2000, 1, 1))
        self.fecha_fin.setDate(QDate(2000, 1, 1))  # Empezar en mínimo = sin filtro
        
        form_fechas.addRow("Desde:", self.fecha_inicio)
        form_fechas.addRow("Hasta:", self.fecha_fin)
        grupo_fechas.setLayout(form_fechas)
        layout.addWidget(grupo_fechas)
        
        # Estado
        layout.addWidget(QLabel("Estado de Pago:"))
        self.cmb_estado = QComboBox()
        self.cmb_estado.addItems(["Todos", "Pagados", "Anulados"])
        layout.addWidget(self.cmb_estado)
        
        # Botones
        botones = QHBoxLayout()
        self.btn_aceptar = QPushButton("Generar")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_aceptar.clicked.connect(self.accept)
        self.btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(self.btn_aceptar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)
    
    def get_filtros(self):
        """Retorna un diccionario con los filtros seleccionados."""
        return {
            'tipo': self.cmb_tipo.currentText(),
            'fecha_inicio': self.fecha_inicio.date().toPython() if self.fecha_inicio.date() > QDate(2000, 1, 1) else None,
            'fecha_fin': self.fecha_fin.date().toPython() if self.fecha_fin.date() > QDate(2000, 1, 1) else None,
            'estado': self.cmb_estado.currentText()
        }


class FiltrosPistasDialog(QDialog):
    """Diálogo para filtrar pistas por estado."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtros para Listado de Pistas")
        self.setMinimumWidth(350)
        self.setStyleSheet(_obtener_estilos_dialogo())
        
        layout = QVBoxLayout(self)
        
        # Estado
        layout.addWidget(QLabel("Estado de Pista:"))
        self.cmb_estado = QComboBox()
        self.cmb_estado.addItems(["Todas", "Activas", "Inactivas"])
        layout.addWidget(self.cmb_estado)
        
        # Botones
        botones = QHBoxLayout()
        self.btn_aceptar = QPushButton("Generar")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_aceptar.clicked.connect(self.accept)
        self.btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(self.btn_aceptar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)
    
    def get_filtros(self):
        """Retorna un diccionario con los filtros seleccionados."""
        return {
            'estado': self.cmb_estado.currentText()
        }

