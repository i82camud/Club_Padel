"""Widget de gestión de Pistas.

Contiene la clase `PistaPage` que permite listar, crear, modificar,
dar de baja y reactivar pistas. Se apoya en `services.pista_service` para
la lógica de persistencia y emite la señal `bus.pistas_changed` cuando
se hacen cambios que deben propagar a otros widgets.

API principal:
- cargar_pistas(): recarga la tabla desde el servicio.
- insertar(), modificar(), baja_pista(), activa_pista(): operaciones CRUD básicas.
- generar_listado(): genera un listado Excel de pistas con filtros.

Efectos secundarios:
- Emite `bus.pistas_changed` tras cambios.

Notas:
- Diseñado para integrarse en la ventana principal generada por Qt Designer
  (widgets con nombres esperados: tabla, botones, combos, etc.).
"""

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFileDialog
from PySide6.QtCore import QDate
from ui.pista_page_ui import Ui_PistaPage  # el generado por pyside6-uic
import services.pista_service as pista_service
from utils.events import bus
from ui.widgets.filtros_dialog import FiltrosPistasDialog, _obtener_estilos_dialogo
from models.orm_models import PistaEstado
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


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
        self.btn_listar.clicked.connect(self.generar_listado)

        # Conectar tabla para que actualice los campos al seleccionar fila
        self.tabla_pistas.itemSelectionChanged.connect(self.actualizar_campos)
        self.tabla_pistas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Cargar tabla al inicio
        self.cargar_pistas()

    def cargar_pistas(self) -> None:
        """Recarga la tabla de pistas desde el servicio.
        
        Obtiene todas las pistas de la base de datos y actualiza la tabla con sus datos.
        Muestra el estado de forma legible (Activa/Inactiva).
        """
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
    def validar_campos(self) -> tuple:
        """Valida que los campos del formulario cumplan con los requisitos.
        
        Verifica que el nombre de la pista no esté vacío.
        
        Returns:
            tuple: (bool, str) - Tupla con éxito de validación y mensaje de error si aplica.
        """
        nombre, pared, tipo = self.normalizar_campos()

        if not nombre:
            return False, "El nombre es obligatorio"

        return True, ""

    # campos
    def vaciar_campos(self) -> None:
        """Limpia todos los campos del formulario de pistas.
        
        Borra el contenido del campo de nombre y resetea los combos a su primer elemento.
        """
        self.txt_nombre.clear()
        self.cmb_pared.setCurrentIndex(0)
        self.cmb_tipo.setCurrentIndex(0)

    def actualizar_campos(self) -> None:
        """Carga los datos de la fila seleccionada en los campos del formulario.
        
        Lee la fila actualmente seleccionada en la tabla y rellena los campos de entrada
        con los datos de la pista seleccionada.
        """
        fila = self.tabla_pistas.currentRow()
        if fila >= 0:
            self.txt_nombre.setText(self.tabla_pistas.item(fila, 1).text())
            self.cmb_pared.setCurrentText(self.tabla_pistas.item(fila, 2).text())
            self.cmb_tipo.setCurrentText(self.tabla_pistas.item(fila, 3).text())

    def normalizar_campos(self) -> tuple:
        """Normaliza el formato de los datos ingresados en los campos del formulario.
        
        Aplica transformaciones como trim de espacios en el nombre, obtiene los valores
        seleccionados en los combos.
        
        Returns:
            tuple: (nombre, pared, tipo) normalizados.
        """
        nombre = self.txt_nombre.text().strip().title()  # .title() para poner la primera letra en mayúscula
        pared = self.cmb_pared.currentText()
        tipo = self.cmb_tipo.currentText()
        return nombre, pared, tipo

    # CRUD
    def insertar(self) -> None:
        """Inserta una nueva pista en la base de datos.
        
        Valida los campos, normaliza los datos y crea un nuevo registro de pista.
        Emite la señal bus.pistas_changed para actualizar otros widgets.
        """
        ok, mensaje = self.validar_campos()
        if not ok:
            QMessageBox.warning(self, "Error", mensaje)
            return

        nombre, pared, tipo = self.normalizar_campos()
        try:
            pista_service.insertar_pista(nombre, pared, tipo)
            QMessageBox.information(self, "Éxito", "Pista insertada correctamente")
            self.vaciar_campos()
            self.cargar_pistas()
            bus.pistas_changed.emit()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def modificar(self) -> None:
        """Actualiza los datos de la pista seleccionada.
        
        Valida los campos, normaliza los datos y actualiza el registro de la pista.
        Emite la señal bus.pistas_changed para actualizar otros widgets.
        """
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
        try:
            pista_service.modificar_pista(id_pista, nombre, pared, tipo)
            QMessageBox.information(self, "Éxito", "Pista modificada correctamente")
            self.vaciar_campos()
            self.cargar_pistas()
            bus.pistas_changed.emit()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def baja_pista(self) -> None:
        """Marca la pista seleccionada como inactiva (baja).
        
        Cambia el estado de la pista a INACTIVA. Emite la señal bus.pistas_changed
        para actualizar otros widgets.
        """
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

    def activa_pista(self) -> None:
        """Marca la pista seleccionada como activa (reactivación).
        
        Cambia el estado de la pista a ACTIVA. Emite la señal bus.pistas_changed
        para actualizar otros widgets.
        """
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

    def generar_listado(self) -> None:
        """Genera un listado de pistas en formato XLSX con filtros.
        
        Muestra un diálogo para seleccionar filtros (estado: Todas/Activas/Inactivas),
        solicita la ubicación del archivo y exporta los datos a Excel.
        """
        from PySide6.QtWidgets import QDialog
        # Mostrar diálogo de filtros
        dlg = FiltrosPistasDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        
        filtros = dlg.get_filtros()
        
        # Obtener todas las pistas
        pistas = pista_service.listar_pistas()
        
        # Filtrar por estado
        if filtros['estado'] == "Activas":
            pistas = [p for p in pistas if p.estado == PistaEstado.ACTIVA]
        elif filtros['estado'] == "Inactivas":
            pistas = [p for p in pistas if p.estado == PistaEstado.INACTIVA]
        
        # Validar que hay datos
        if not pistas:
            QMessageBox.information(self, "Sin datos", "No hay pistas que coincidan con los criterios de filtro.")
            return
        
        # Mostrar diálogo para guardar
        estado_filtro = filtros['estado'].lower()
        archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Listado de Pistas",
            f"listado_pistas_{estado_filtro}.xlsx",
            "Excel (*.xlsx)"
        )
        
        if not archivo:
            return
        
        # Generar Excel
        self._generar_xlsx_pistas(archivo, pistas)
        QMessageBox.information(self, "Éxito", f"Listado guardado en:\n{archivo}")

    def _generar_xlsx_pistas(self, archivo: str, pistas: list) -> None:
        """Genera un archivo Excel con el listado de pistas.
        
        Args:
            archivo (str): Ruta del archivo XLSX a crear.
            pistas (list): Lista de objetos pista a exportar.
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Pistas"
        
        # Cabecera con estilo
        cabecera = ["ID", "Nombre", "Pared", "Tipo", "Estado"]
        ws.append(cabecera)
        
        # Aplicar estilos a la cabecera
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Añadir datos
        for pista in pistas:
            estado_display = pista.estado.name.capitalize() if hasattr(pista.estado, 'name') else str(pista.estado)
            fila = [
                pista.id_pista,
                pista.nombre,
                pista.pared,
                pista.tipo,
                estado_display
            ]
            ws.append(fila)
        
        # Ajustar ancho de columnas
        anchos = [8, 20, 15, 15, 12]
        for i, ancho in enumerate(anchos, start=1):
            col_letter = get_column_letter(i)
            ws.column_dimensions[col_letter].width = ancho
        
        wb.save(archivo)
