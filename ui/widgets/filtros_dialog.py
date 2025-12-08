"""Diálogos personalizados para filtros de listados.

Proporciona diálogos para solicitar filtros de fechas, estados, tipos, etc.
para la generación de listados en XLSX.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QDateEdit, QPushButton, QGroupBox, QFormLayout)
from PySide6.QtCore import QDate, QFile
from datetime import date


def _configurar_date_edit(date_edit, es_fecha_fin=False):
    """Configura un QDateEdit con formato personalizado y fechas por defecto del año actual."""
    date_edit.setCalendarPopup(True)
    date_edit.setDisplayFormat("dd/MM/yyyy")
    date_edit.setMinimumDate(QDate(1900, 1, 1))
    date_edit.setMaximumDate(QDate(2100, 12, 31))
    
    # Fechas por defecto: primer día del año actual o último día
    año_actual = date.today().year
    if es_fecha_fin:
        date_edit.setDate(QDate(año_actual, 12, 31))
    else:
        date_edit.setDate(QDate(año_actual, 1, 1))


def _validar_rango_fechas(fecha_inicio, fecha_fin, etiqueta=""):
    """Valida que fecha_fin no sea menor que fecha_inicio.
    
    Args:
        fecha_inicio (QDate): Fecha de inicio
        fecha_fin (QDate): Fecha de fin
        etiqueta (str): Etiqueta para el mensaje de error
    
    Returns:
        tuple: (bool, str) - (es_válido, mensaje_error)
    """
    if fecha_fin < fecha_inicio:
        return False, f"La fecha de fin no puede ser menor que la de inicio{' en ' + etiqueta if etiqueta else ''}."
    return True, ""


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
        _configurar_date_edit(self.fecha_inicio, es_fecha_fin=False)
        
        self.fecha_fin = QDateEdit()
        _configurar_date_edit(self.fecha_fin, es_fecha_fin=True)
        
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
        self.btn_aceptar.clicked.connect(self._validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(self.btn_aceptar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)
    
    def _validar_y_aceptar(self):
        """Valida los filtros antes de aceptar."""
        es_valido, mensaje = _validar_rango_fechas(
            self.fecha_inicio.date(),
            self.fecha_fin.date(),
            "Filtro de Reservas"
        )
        if not es_valido:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error de validación", mensaje)
            return
        self.accept()
    
    def get_filtros(self):
        """Retorna un diccionario con los filtros seleccionados."""
        return {
            'fecha_inicio': self.fecha_inicio.date().toPython(),
            'fecha_fin': self.fecha_fin.date().toPython(),
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
        _configurar_date_edit(self.fecha_inicio, es_fecha_fin=False)
        
        self.fecha_fin = QDateEdit()
        _configurar_date_edit(self.fecha_fin, es_fecha_fin=True)
        
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
            'fecha_inicio': self.fecha_inicio.date().toPython(),
            'fecha_fin': self.fecha_fin.date().toPython(),
            'estado': self.cmb_estado.currentText()
        }


class FiltrosPistasDialog(QDialog):
    """Diálogo para filtrar pagos globales (no por socio) por tipo, fechas y estado."""
    
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
        _configurar_date_edit(self.fecha_inicio, es_fecha_fin=False)
        
        self.fecha_fin = QDateEdit()
        _configurar_date_edit(self.fecha_fin, es_fecha_fin=True)
        
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
        self.btn_aceptar.clicked.connect(self._validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(self.btn_aceptar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)
    
    def _validar_y_aceptar(self):
        """Valida los filtros antes de aceptar."""
        es_valido, mensaje = _validar_rango_fechas(
            self.fecha_inicio.date(),
            self.fecha_fin.date(),
            "Filtro de Pagos"
        )
        if not es_valido:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error de validación", mensaje)
            return
        self.accept()
    
    def get_filtros(self):
        """Retorna un diccionario con los filtros seleccionados."""
        return {
            'tipo': self.cmb_tipo.currentText(),
            'fecha_inicio': self.fecha_inicio.date().toPython(),
            'fecha_fin': self.fecha_fin.date().toPython(),
            'estado': self.cmb_estado.currentText()
        }


class FiltrosPagePagosDialog(QDialog):
    """Diálogo para filtrar pagos globales (no por socio) por tipo, fechas y estado."""
    
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
        _configurar_date_edit(self.fecha_inicio, es_fecha_fin=False)
        
        self.fecha_fin = QDateEdit()
        _configurar_date_edit(self.fecha_fin, es_fecha_fin=True)
        
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
        self.btn_aceptar.clicked.connect(self._validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)
        botones.addWidget(self.btn_aceptar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)
    
    def _validar_y_aceptar(self):
        """Valida los filtros antes de aceptar."""
        es_valido, mensaje = _validar_rango_fechas(
            self.fecha_inicio.date(),
            self.fecha_fin.date(),
            "Filtro de Pagos Globales"
        )
        if not es_valido:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error de validación", mensaje)
            return
        self.accept()
    
    def get_filtros(self):
        """Retorna un diccionario con los filtros seleccionados."""
        return {
            'tipo': self.cmb_tipo.currentText(),
            'fecha_inicio': self.fecha_inicio.date().toPython(),
            'fecha_fin': self.fecha_fin.date().toPython(),
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

