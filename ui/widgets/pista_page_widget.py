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

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFileDialog, QDialog, QComboBox
from PySide6.QtCore import QDate, Qt
from ui.pista_page_ui import Ui_PistaPage  # el generado por pyside6-uic
import services.pista_service as pista_service
from utils.events import bus
from ui.widgets.filtros_dialog import FiltrosPistasDialog, FiltrosReservasDialog, _obtener_estilos_dialogo
from models.orm_models import PistaEstado, ReservaEstado
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from utils.helpers import formatear_fecha, formatear_hora


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
        self.btn_listar_reservas.clicked.connect(self.generar_listado_reservas)
        self.btn_limpiar.clicked.connect(self.vaciar_campos)
        self.txt_buscar.textChanged.connect(self.filtrar_tabla)
        
        # Crear combo de estado
        self.cmb_estado = QComboBox(self)
        self.cmb_estado.addItem("Todos", None)
        self.cmb_estado.addItem("Activa", PistaEstado.ACTIVA)
        self.cmb_estado.addItem("Inactiva", PistaEstado.INACTIVA)
        self.cmb_estado.currentIndexChanged.connect(self._on_estado_changed)
        
        # Estado actual para filtrado
        self.estado_actual = None

        # Conectar tabla para que actualice los campos al seleccionar fila
        self.tabla_pistas.itemSelectionChanged.connect(self.actualizar_campos)
        self.tabla_pistas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Lista para almacenar las pistas originales para filtrado
        self.pistas_originales = []

        # Cargar tabla al inicio
        self.cargar_pistas()

        # Conectar evento de resize para responsividad
        self.resizeEvent = self._on_redimensionar_pagina

    def _on_redimensionar_pagina(self, event) -> None:
        """Ajusta la geometría de widgets al redimensionar la página."""
        width = self.width()
        height = self.height()
        
        # Margen general
        margin = 20
        
        # Label "Pistas" (título)
        self.label_socios.setGeometry(margin, margin, 200, 31)
        
        # GroupBox de botones: ancho completo, alto fijo
        gb_y = margin + 35
        gb_height = 41
        self.groupBox.setGeometry(margin, gb_y, width - 2*margin, gb_height)
        
        # GridLayoutWidget_2 (campos de entrada): ancho completo, alto fijo
        grid_y = gb_y + gb_height + 10
        grid_height = 71
        if hasattr(self, 'gridLayoutWidget_2'):
            self.gridLayoutWidget_2.setGeometry(margin, grid_y, width - 2*margin, grid_height)
        
        # Botón Limpiar y GridLayoutWidget_3 (búsqueda)
        search_y = grid_y + grid_height + 10
        search_height = 35
        if hasattr(self, 'btn_limpiar'):
            self.btn_limpiar.setGeometry(margin, search_y, 71, search_height)
        if hasattr(self, 'gridLayoutWidget_3'):
            # Reducir ancho del campo de búsqueda para dejar espacio al combo
            self.gridLayoutWidget_3.setGeometry(margin + 90, search_y, width - 2*margin - 90 - 140, search_height)
        
        # Combo de estado en la barra de búsqueda
        if hasattr(self, 'cmb_estado'):
            self.cmb_estado.setGeometry(width - margin - 130, search_y, 120, search_height)
        
        # Tabla (resto del espacio disponible)
        table_y = search_y + 51 + 10
        table_height = height - table_y - margin
        self.tabla_pistas.setGeometry(margin, table_y, width - 2*margin, table_height)

    def _on_estado_changed(self) -> None:
        """Actualiza el filtro de estado y recarga la tabla de pistas."""
        self.estado_actual = self.cmb_estado.currentData()
        self.cargar_pistas()

    def cargar_pistas(self) -> None:
        """Recarga la tabla de pistas desde el servicio.
        
        Obtiene las pistas de la base de datos con filtro de estado y actualiza la tabla.
        Muestra el estado de forma legible (Activa/Inactiva).
        """
        pistas = pista_service.listar_pistas(estado=self.estado_actual)
        self.pistas_originales = pistas
        self.tabla_pistas.setRowCount(len(pistas))
        self.tabla_pistas.setColumnCount(4)
        self.tabla_pistas.setHorizontalHeaderLabels([
            "Nombre", "Pared", "Tipo", "Estado"
        ])

        for fila, pista in enumerate(pistas):
            # Asumimos objetos ORM: acceder a atributos directamente
            values = [
                pista.nombre,
                pista.pared,
                pista.tipo,
                (pista.estado.name.capitalize() if hasattr(pista.estado, 'name') else str(pista.estado)),
            ]

            for col, dato in enumerate(values):
                item = QTableWidgetItem(str(dato))
                # Almacenar el ID de la pista en el primer item como dato oculto
                if col == 0:
                    item.setData(Qt.UserRole, pista.id_pista)
                self.tabla_pistas.setItem(fila, col, item)

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
        self.txt_buscar.clear()

    def filtrar_tabla(self) -> None:
        """Filtra la tabla de pistas según el texto del campo de búsqueda.
        
        Busca en las columnas Nombre, Pared y Tipo de forma case-insensitive.
        Si el campo está vacío, muestra todas las pistas.
        """
        texto_busqueda = self.txt_buscar.text().strip().lower()
        
        if not texto_busqueda:
            # Si no hay búsqueda, mostrar todas las pistas
            self.cargar_pistas()
            return
        
        # Filtrar pistas por el texto de búsqueda en nombre, pared y tipo
        pistas_filtradas = [
            p for p in self.pistas_originales
            if texto_busqueda in p.nombre.lower() 
            or texto_busqueda in p.pared.lower()
            or texto_busqueda in p.tipo.lower()
        ]
        
        # Actualizar tabla con resultados filtrados
        self.tabla_pistas.setRowCount(len(pistas_filtradas))
        self.tabla_pistas.setColumnCount(4)
        self.tabla_pistas.setHorizontalHeaderLabels([
            "Nombre", "Pared", "Tipo", "Estado"
        ])
        
        for fila, pista in enumerate(pistas_filtradas):
            values = [
                pista.nombre,
                pista.pared,
                pista.tipo,
                "Activa" if pista.estado == PistaEstado.ACTIVA else "Inactiva"
            ]
            for col, dato in enumerate(values):
                item = QTableWidgetItem(str(dato))
                # Almacenar el ID de la pista en el primer item como dato oculto
                if col == 0:
                    item.setData(Qt.UserRole, pista.id_pista)
                self.tabla_pistas.setItem(fila, col, item)

    def actualizar_campos(self) -> None:
        """Carga los datos de la fila seleccionada en los campos del formulario.
        
        Lee la fila actualmente seleccionada en la tabla y rellena los campos de entrada
        con los datos de la pista seleccionada.
        """
        fila = self.tabla_pistas.currentRow()
        if fila >= 0:
            self.txt_nombre.setText(self.tabla_pistas.item(fila, 0).text())
            self.cmb_pared.setCurrentText(self.tabla_pistas.item(fila, 1).text())
            self.cmb_tipo.setCurrentText(self.tabla_pistas.item(fila, 2).text())

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

        # Obtener el ID de la pista del UserRole
        item0 = self.tabla_pistas.item(fila, 0)
        if item0 is None:
            return
        id_pista = item0.data(Qt.UserRole)
        if id_pista is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la pista")
            return

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

        # Obtener el ID de la pista del UserRole
        item0 = self.tabla_pistas.item(row, 0)
        if item0 is None:
            return
        id_pista = item0.data(Qt.UserRole)
        if id_pista is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la pista")
            return

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

        # Obtener el ID de la pista del UserRole
        item0 = self.tabla_pistas.item(row, 0)
        if item0 is None:
            return
        id_pista = item0.data(Qt.UserRole)
        if id_pista is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la pista")
            return

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
        cabecera = ["Nombre", "Pared", "Tipo", "Estado"]
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
                pista.nombre,
                pista.pared,
                pista.tipo,
                estado_display
            ]
            ws.append(fila)
        
        # Ajustar ancho de columnas
        anchos = [20, 15, 15, 12]
        for i, ancho in enumerate(anchos, start=1):
            col_letter = get_column_letter(i)
            ws.column_dimensions[col_letter].width = ancho
        
        wb.save(archivo)

    def generar_listado_reservas(self) -> None:
        """Genera un listado de reservas de la pista seleccionada en formato XLSX.
        
        Requiere que haya una pista seleccionada en la tabla. Muestra un diálogo
        de filtros (fechas y estado) y exporta las reservas a Excel.
        """
        # Verificar que hay una pista seleccionada
        fila = self.tabla_pistas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona una pista para listar sus reservas")
            return
        
        # Obtener el ID de la pista del UserRole
        item0 = self.tabla_pistas.item(fila, 0)
        if item0 is None:
            return
        id_pista = item0.data(Qt.UserRole)
        if id_pista is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la pista")
            return
        
        nombre_pista = self.tabla_pistas.item(fila, 0).text()
        
        # Mostrar diálogo de filtros
        dialogo = FiltrosReservasDialog(self)
        if dialogo.exec() != QDialog.Accepted:
            return
        
        filtros = dialogo.get_filtros()
        
        # Verificar si hay datos con los filtros actuales
        from services.reserva_service import listar_reservas
        reservas = listar_reservas(id_pista=id_pista)
        
        # Aplicar filtros temporalmente para verificar
        if filtros['fecha_inicio'] and filtros['fecha_fin']:
            reservas_filtradas = [r for r in reservas if filtros['fecha_inicio'] <= r.fecha <= filtros['fecha_fin']]
        elif filtros['fecha_inicio']:
            reservas_filtradas = [r for r in reservas if r.fecha >= filtros['fecha_inicio']]
        elif filtros['fecha_fin']:
            reservas_filtradas = [r for r in reservas if r.fecha <= filtros['fecha_fin']]
        else:
            reservas_filtradas = reservas
        
        if filtros['estado'] == "Activas":
            reservas_filtradas = [r for r in reservas_filtradas if r.estado == ReservaEstado.ACTIVA]
        elif filtros['estado'] == "Canceladas":
            reservas_filtradas = [r for r in reservas_filtradas if r.estado == ReservaEstado.CANCELADA]
        
        if not reservas_filtradas:
            QMessageBox.information(self, "Sin datos", "No hay reservas que cumplan los criterios de filtro.")
            return
        
        # Preguntar dónde guardar
        archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Listado de Reservas",
            f"reservas_{nombre_pista.replace(' ', '_').lower()}.xlsx",
            "Excel (*.xlsx)"
        )
        
        if not archivo:
            return
        
        # Generar el archivo
        try:
            self._generar_xlsx_reservas(archivo, id_pista, nombre_pista, filtros)
            QMessageBox.information(self, "Éxito", f"Listado guardado en:\n{archivo}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el listado:\n{e}")

    def _generar_xlsx_reservas(self, archivo: str, id_pista: int, nombre_pista: str, filtros: dict) -> None:
        """Genera el archivo XLSX con las reservas de la pista filtradas.
        
        Args:
            archivo (str): Ruta del archivo XLSX a crear.
            id_pista (int): ID de la pista.
            nombre_pista (str): Nombre de la pista para el título.
            filtros (dict): Diccionario con filtros (fecha_inicio, fecha_fin, estado).
        """
        from services.reserva_service import listar_reservas
        from services.socio_service import listar_socios
        
        # Obtener todas las reservas de la pista
        reservas = listar_reservas(id_pista=id_pista)
        
        # Filtrar por fechas si se especificaron
        if filtros['fecha_inicio'] and filtros['fecha_fin']:
            reservas = [r for r in reservas if filtros['fecha_inicio'] <= r.fecha <= filtros['fecha_fin']]
        elif filtros['fecha_inicio']:
            reservas = [r for r in reservas if r.fecha >= filtros['fecha_inicio']]
        elif filtros['fecha_fin']:
            reservas = [r for r in reservas if r.fecha <= filtros['fecha_fin']]
        
        # Filtrar por estado
        if filtros['estado'] == "Activas":
            reservas = [r for r in reservas if r.estado == ReservaEstado.ACTIVA]
        elif filtros['estado'] == "Canceladas":
            reservas = [r for r in reservas if r.estado == ReservaEstado.CANCELADA]
        
        # Crear mapa de socios para evitar lazy loading
        socios = listar_socios()
        mapa_socios = {s.id_socio: f"{s.nombre} {s.apellido1}" for s in socios}
        
        # Crear libro y hoja
        wb = Workbook()
        ws = wb.active
        ws.title = "Reservas"
        
        # Título
        ws.merge_cells('A1:F1')
        titulo = ws['A1']
        titulo.value = f"Reservas de {nombre_pista}"
        titulo.font = Font(bold=True, size=14)
        titulo.alignment = Alignment(horizontal="center", vertical="center")
        
        # Cabecera con estilo
        cabecera = ["Socio", "Fecha", "Hora Inicio", "Hora Fin", "Estado", "Duración (min)"]
        ws.append(cabecera)
        
        # Aplicar estilos a la cabecera
        for cell in ws[2]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Añadir datos
        for reserva in reservas:
            estado_display = reserva.estado.name.capitalize() if hasattr(reserva.estado, 'name') else str(reserva.estado)
            socio_nombre = mapa_socios.get(reserva.id_socio, str(reserva.id_socio))
            
            # Calcular duración
            duracion_min = (reserva.hora_fin.hour * 60 + reserva.hora_fin.minute) - (reserva.hora_inicio.hour * 60 + reserva.hora_inicio.minute)
            
            fila = [
                socio_nombre,
                formatear_fecha(reserva.fecha),
                formatear_hora(reserva.hora_inicio),
                formatear_hora(reserva.hora_fin),
                estado_display,
                duracion_min
            ]
            ws.append(fila)
        
        # Ajustar ancho de columnas
        anchos = [25, 15, 15, 15, 12, 15]
        for i, ancho in enumerate(anchos, start=1):
            ws.column_dimensions[get_column_letter(i)].width = ancho
        
        # Guardar archivo
        wb.save(archivo)

