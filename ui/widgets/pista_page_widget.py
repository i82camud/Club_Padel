"""Widget de gestión de Pistas.

Contiene la clase `PistaPage` que permite listar, crear, modificar,
dar de baja y reactivar pistas. Se apoya en `services.pista_service` para
la lógica de persistencia y emite la señal `bus.pistas_changed` cuando
se hacen cambios que deben propagar a otros widgets.

API principal:
- cargar_pistas(): recarga la tabla desde el servicio.
- insertar(), modificar(), baja_pista(), activa_pista(): operaciones CRUD básicas.

Efectos secundarios:
- Emite `bus.pistas_changed` tras cambios.

Notas:
- Diseñado para integrarse en la ventana principal generada por Qt Designer
  (widgets con nombres esperados: tabla, botones, combos, etc.).
"""

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QHeaderView
from ui.pista_page_ui import Ui_PistaPage  # el generado por pyside6-uic
import services.pista_service as pista_service
from utils.events import bus


class PistaPage(QWidget, Ui_PistaPage):
    """Widget para administrar pistas.

    Métodos públicos y comportamiento:
    - cargar_pistas(): re-lee las pistas del servicio y actualiza la tabla.
    - insertar()/modificar()/baja_pista()/activa_pista(): realizan las operaciones
      correspondientes y emiten `bus.pistas_changed`.

    Validaciones:
    - validar_campos() devuelve (bool, mensaje) indicando si los campos son válidos.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Conectar botones
        self.btn_agregar.clicked.connect(self.insertar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_baja.clicked.connect(self.baja_pista)
        self.btn_activar.clicked.connect(self.activa_pista)

        # Conectar tabla para que actualice los campos al seleccionar fila
        self.tabla_pistas.itemSelectionChanged.connect(self.actualizar_campos)
        self.tabla_pistas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Cargar tabla al inicio
        self.cargar_pistas()

    def cargar_pistas(self):
        pistas = pista_service.listar_pistas()
        self.tabla_pistas.setRowCount(len(pistas))
        self.tabla_pistas.setColumnCount(5)
        self.tabla_pistas.setHorizontalHeaderLabels([
            "ID", "Nombre", "Pared", "Tipo", "Estado"
        ])

        for fila, pista in enumerate(pistas):
            # Asumimos objetos ORM: acceder a atributos directamente
            values = [
                pista.id_pista,
                pista.nombre,
                pista.pared,
                pista.tipo,
                (pista.estado.name.capitalize() if hasattr(pista.estado, 'name') else str(pista.estado)),
            ]

            for col, dato in enumerate(values):
                self.tabla_pistas.setItem(fila, col, QTableWidgetItem(str(dato)))

    # validaciones
    def validar_campos(self):
        nombre, pared, tipo = self.normalizar_campos()

        if not nombre:
            return False, "El nombre es obligatorio"

        return True, ""

    # campos
    def vaciar_campos(self):
        self.txt_nombre.clear()
        self.cmb_pared.setCurrentIndex(0)
        self.cmb_tipo.setCurrentIndex(0)

    def actualizar_campos(self):
        fila = self.tabla_pistas.currentRow()
        if fila >= 0:
            self.txt_nombre.setText(self.tabla_pistas.item(fila, 1).text())
            self.cmb_pared.setCurrentText(self.tabla_pistas.item(fila, 2).text())
            self.cmb_tipo.setCurrentText(self.tabla_pistas.item(fila, 3).text())

    def normalizar_campos(self):
        nombre = self.txt_nombre.text().strip()
        pared = self.cmb_pared.currentText()
        tipo = self.cmb_tipo.currentText()
        return nombre, pared, tipo

    # CRUD
    def insertar(self):
        ok, mensaje = self.validar_campos()
        if not ok:
            QMessageBox.warning(self, "Error", mensaje)
            return

        nombre, pared, tipo = self.normalizar_campos()
        pista_service.insertar_pista(nombre, pared, tipo)
        QMessageBox.information(self, "Éxito", "Pista insertada correctamente")
        self.vaciar_campos()
        self.cargar_pistas()
        bus.pistas_changed.emit()

    def modificar(self):
        fila = self.tabla_pistas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona una pista para modificar.")
            return

        id_pista = int(self.tabla_pistas.item(fila, 0).text())
        ok, mensaje = self.validar_campos()
        if not ok:
            QMessageBox.warning(self, "Error", mensaje)
            return

        nombre, pared, tipo = self.normalizar_campos()
        pista_service.modificar_pista(id_pista, nombre, pared, tipo)
        self.vaciar_campos()
        self.cargar_pistas()
        bus.pistas_changed.emit()

    def baja_pista(self):
        row = self.tabla_pistas.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Selecciona una pista para dar de baja.")
            return

        id_pista = int(self.tabla_pistas.item(row, 0).text())
        pista_service.desactivar_pista(id_pista)
        QMessageBox.information(self, "Éxito", "Pista dada de baja correctamente")
        self.vaciar_campos()
        self.cargar_pistas()
        bus.pistas_changed.emit()

    def activa_pista(self):
        row = self.tabla_pistas.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Selecciona una pista para activar.")
            return

        id_pista = int(self.tabla_pistas.item(row, 0).text())
        pista_service.activar_pista(id_pista)
        QMessageBox.information(self, "Éxito", "Pista activada correctamente")
        self.vaciar_campos()
        self.cargar_pistas()
        bus.pistas_changed.emit()
