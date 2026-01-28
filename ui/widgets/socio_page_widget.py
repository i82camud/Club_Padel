"""Widget de gestión de Socios.

Contiene la clase `SocioPage` para listar, crear, modificar, desactivar
y reactivar socios. Incluye validaciones de correo y teléfono y evita
duplicados consultando `services.socio_service`.

API pública:
- cargar_socios(): recarga la tabla de socios.
- insertar()/modificar()/desactivar_socio()/activar_socio(): operaciones CRUD.

Validaciones relevantes:
- `validar_correo` comprueba la forma básica de un correo.
- `validar_telefono` exige 9 dígitos numéricos.

Efectos secundarios:
- Emite `bus.socios_changed` tras cambios.
"""

import re
from datetime import date
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QHeaderView, QInputDialog, QFileDialog, QDialog
from PySide6.QtCore import Qt
from ui.socio_page_ui import Ui_SocioPage  # el generado por pyside6-uic
import services.socio_service as socio_service
from utils.events import bus
from models.orm_models import SocioEstado, ReservaEstado, PagoEstado, PagoTipo
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from ui.widgets.filtros_dialog import FiltrosSociosDialog, FiltrosReservasDialog, FiltrosPagosDialog
from utils.helpers import format_date, format_time


class SocioPage(QWidget, Ui_SocioPage):
    """Widget para administrar socios.

    Métodos públicos:
    - cargar_socios(): recarga la tabla.
    - insertar()/modificar(): crean o actualizan socios tras validación.
    - desactivar_socio()/activar_socio(): cambian estado y emiten `bus.socios_changed`.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Conectar botones
        self.btn_agregar.clicked.connect(self.insertar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_baja.clicked.connect(self.desactivar_socio)
        self.btn_activar.clicked.connect(self.activar_socio)
        self.btn_listar.clicked.connect(self.generar_listado)
        self.btn_listar_reservas.clicked.connect(self.generar_listado_reservas)
        self.btn_listar_pagos.clicked.connect(self.generar_listado_pagos)
        self.btn_limpiar.clicked.connect(self.vaciar_campos)

        # Conectar tabla para que actualice los campos al seleccionar fila
        self.tabla_socios.itemSelectionChanged.connect(self.actualizar_campos)
        self.tabla_socios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Conectar barra de búsqueda para filtrar en tiempo real
        self.txt_buscar.textChanged.connect(self.filtrar_tabla)

        # Guardar lista de socios original para filtrado
        self.socios_originales = []

        # Cargar tabla al inicio
        self.cargar_socios()
    
    def cargar_socios(self) -> None:
        """Recarga la tabla de socios desde el servicio.
        
        Obtiene todos los socios de la base de datos y actualiza la tabla con sus datos.
        Muestra el estado de forma legible (Activo/Inactivo).
        """
        socios = socio_service.listar_socios()
        self.socios_originales = socios  # Guardar para filtrado
        self.tabla_socios.setRowCount(len(socios))
        self.tabla_socios.setColumnCount(6)
        self.tabla_socios.setHorizontalHeaderLabels(
            ["Nombre", "Apellido1", "Apellido2", "Correo", "Teléfono", "Estado"]
        )

        for fila, socio in enumerate(socios):
            # Asumimos objetos ORM: acceder directamente a atributos
            # mostrar estado legible
            estado_display = socio.estado.name.capitalize() if hasattr(socio.estado, 'name') else str(socio.estado)
            values = [
                socio.nombre,
                socio.apellido1,
                socio.apellido2,
                socio.email,
                socio.telefono,
                estado_display,
            ]

            for col, dato in enumerate(values):
                item = QTableWidgetItem(str(dato))
                # Almacenar el ID del socio en el primer item como dato oculto
                if col == 0:
                    item.setData(Qt.UserRole, socio.id_socio)
                self.tabla_socios.setItem(fila, col, item)

    # Validaciones
    def validar_correo(self, correo: str) -> bool:
        """Valida que el correo tenga formato válido.
        
        Args:
            correo (str): Correo a validar.
        
        Returns:
            bool: True si el formato es válido, False en caso contrario.
        """
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(patron, correo)

    def validar_telefono(self, telefono: str) -> bool:
        """Valida que el teléfono tenga exactamente 9 dígitos numéricos.
        
        Args:
            telefono (str): Teléfono a validar.
        
        Returns:
            bool: True si tiene 9 dígitos, False en caso contrario.
        """
        patron = r'^\d{9}$'
        return re.match(patron, telefono)
    
    def validar_campos(self, correo_existente_id: int = None, telefono_existente_id: int = None) -> tuple:
        """Valida que los campos cumplan con los requisitos.
        
        Comprueba que nombre, correo y teléfono sean válidos y no existan duplicados.
        
        Args:
            correo_existente_id (int): ID del socio existente para permitir actualización sin duplicar correo.
            telefono_existente_id (int): ID del socio existente para permitir actualización sin duplicar teléfono.
        
        Returns:
            tuple: (bool, str) - Tupla con éxito de validación y mensaje de error si aplica.
        """
        nombre, apellido1, apellido2, correo, telefono = self.normalizar_campos()

        if not nombre or not apellido1:
            return False, "Nombre y primer apellido son obligatorios"
        if not correo:
            return False, "El correo es obligatorio"
        if not self.validar_correo(correo):
            return False, "Formato de correo inválido"
        if not telefono:
            return False,  "El teléfono es obligatorio"
        if not self.validar_telefono(telefono):
            return False, "Formato de teléfono inválido (9 dígitos)"
        if socio_service.existe_correo_id(correo, correo_existente_id):
            return False, "Este correo ya está registrado por otro socio"
        if socio_service.existe_telefono_id(telefono, telefono_existente_id):
            return False, "Este teléfono ya está registrado por otro socio"

        return True, ""
    
    # Campos
    def vaciar_campos(self) -> None:
        """Limpia todos los campos del formulario de socios.
        
        Borra el contenido de los campos de entrada de nombre, apellidos, correo y teléfono.
        """
        self.txt_nombre.clear()
        self.txt_apellido1.clear()
        self.txt_apellido2.clear()
        self.txt_email.clear()
        self.txt_telefono.clear()
        self.txt_buscar.clear()

    def filtrar_tabla(self) -> None:
        """Filtra la tabla de socios según el texto ingresado en la barra de búsqueda.
        
        Busca el texto en las columnas de nombre, apellidos, correo y teléfono.
        La búsqueda es case-insensitive.
        """
        texto_busqueda = self.txt_buscar.text().lower().strip()
        
        if not texto_busqueda:
            # Si el campo de búsqueda está vacío, mostrar todos los socios
            self.cargar_socios()
            return
        
        # Filtrar socios según el texto de búsqueda
        socios_filtrados = []
        for socio in self.socios_originales:
            # Convertir a strings para buscar
            nombre = socio.nombre.lower()
            apellido1 = socio.apellido1.lower()
            apellido2 = (socio.apellido2 or "").lower()
            email = socio.email.lower()
            telefono = socio.telefono.lower()
            
            # Buscar en cualquiera de los campos
            if (texto_busqueda in nombre or
                texto_busqueda in apellido1 or
                texto_busqueda in apellido2 or
                texto_busqueda in email or
                texto_busqueda in telefono):
                socios_filtrados.append(socio)
        
        # Actualizar tabla con socios filtrados
        self.tabla_socios.setRowCount(len(socios_filtrados))
        self.tabla_socios.setColumnCount(6)
        self.tabla_socios.setHorizontalHeaderLabels(
            ["Nombre", "Apellido1", "Apellido2", "Correo", "Teléfono", "Estado"]
        )

        for fila, socio in enumerate(socios_filtrados):
            estado_display = socio.estado.name.capitalize() if hasattr(socio.estado, 'name') else str(socio.estado)
            values = [
                socio.nombre,
                socio.apellido1,
                socio.apellido2,
                socio.email,
                socio.telefono,
                estado_display,
            ]

            for col, dato in enumerate(values):
                item = QTableWidgetItem(str(dato))
                # Almacenar el ID del socio en el primer item como dato oculto
                if col == 0:
                    item.setData(Qt.UserRole, socio.id_socio)
                self.tabla_socios.setItem(fila, col, item)

    def actualizar_campos(self) -> None:
        """Carga los datos de la fila seleccionada en los campos del formulario.
        
        Lee la fila actualmente seleccionada en la tabla y rellena los campos de entrada
        con los datos del socio seleccionado.
        """
        fila = self.tabla_socios.currentRow()
        if fila >= 0:
            self.txt_nombre.setText(self.tabla_socios.item(fila, 0).text())
            self.txt_apellido1.setText(self.tabla_socios.item(fila, 1).text())
            self.txt_apellido2.setText(self.tabla_socios.item(fila, 2).text())
            self.txt_email.setText(self.tabla_socios.item(fila, 3).text())
            self.txt_telefono.setText(self.tabla_socios.item(fila, 4).text())
    
    def normalizar_campos(self) -> tuple:
        """Normaliza el formato de los datos ingresados en los campos del formulario.
        
        Aplica transformaciones como trim de espacios, conversión a mayúsculas/minúsculas
        y extracción de solo dígitos en el teléfono.
        
        Returns:
            tuple: (nombre, apellido1, apellido2, correo, telefono) normalizados.
        """
        nombre = self.txt_nombre.text().strip().title()         # .strip() para eliminar espacios al inicio y al final 
        apellido1 = self.txt_apellido1.text().strip().title()   # .title() para poner la primera letra en mayúscula y el resto en minúscula
        apellido2 = self.txt_apellido2.text().strip().title()
        correo = self.txt_email.text().strip().lower()
        telefono = ''.join(filter(str.isdigit, self.txt_telefono.text().strip())) # dejar solo los números en el teléfono, eliminando guiones o espacios
        return nombre, apellido1, apellido2, correo, telefono

    # CRUD
    def insertar(self) -> None:
        """Inserta un nuevo socio en la base de datos.
        
        Valida los campos, normaliza los datos y crea un nuevo registro de socio.
        Emite la señal bus.socios_changed para actualizar otros widgets.
        """
        ok, mensaje = self.validar_campos()
        if not ok:
            QMessageBox.warning(self, "Error", mensaje)
            return

        nombre, apellido1, apellido2, correo, telefono = self.normalizar_campos()        
        socio_service.insertar_socio(nombre, apellido1, apellido2, correo, telefono)
        QMessageBox.information(self, "Éxito", "Socio insertado correctamente")
        self.vaciar_campos()
        self.cargar_socios()
        bus.socios_changed.emit()

    def modificar(self) -> None:
        """Actualiza los datos del socio seleccionado.
        
        Valida los campos, normaliza los datos y actualiza el registro del socio.
        Emite la señal bus.socios_changed para actualizar otros widgets.
        """
        fila = self.tabla_socios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un socio para modificar")
            return

        id_socio = int(self.tabla_socios.item(fila, 0).text())
        ok, mensaje = self.validar_campos(correo_existente_id=id_socio, telefono_existente_id=id_socio)
        if not ok:
            QMessageBox.warning(self, "Error", mensaje)
            return

        nombre, apellido1, apellido2, correo, telefono = self.normalizar_campos()
        socio_service.modificar_socio(id_socio, nombre, apellido1, apellido2, correo, telefono)
        QMessageBox.information(self, "Éxito", "Socio modificado correctamente")
        self.vaciar_campos()
        self.cargar_socios()
        bus.socios_changed.emit()

    def desactivar_socio(self) -> None:
        """Marca el socio seleccionado como inactivo (baja).
        
        Cambia el estado del socio a INACTIVO. Emite la señal bus.socios_changed
        para actualizar otros widgets.
        """
        fila = self.tabla_socios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un socio para darlo de baja")
            return

        id_socio = int(self.tabla_socios.item(fila, 0).text())
        socio_service.baja_socio(id_socio)
        QMessageBox.information(self, "Éxito", "Socio dado de baja correctamente")
        self.vaciar_campos()
        self.cargar_socios()
        bus.socios_changed.emit()

    def activar_socio(self) -> None:
        """Marca el socio seleccionado como activo (reactivación).
        
        Cambia el estado del socio a ACTIVO. Emite la señal bus.socios_changed
        para actualizar otros widgets.
        """
        fila = self.tabla_socios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un socio para activar")
            return

        id_socio = int(self.tabla_socios.item(fila, 0).text())
        socio_service.activa_socio(id_socio)
        QMessageBox.information(self, "Éxito", "Socio activado correctamente")
        self.vaciar_campos()
        self.cargar_socios()
        bus.socios_changed.emit()

    def generar_listado(self) -> None:
        """Genera un listado de socios en formato XLSX con filtros.
        
        Muestra un diálogo para seleccionar filtros (estado: Todos/Activos/Inactivos),
        solicita la ubicación del archivo y exporta los datos a Excel.
        """
        # Mostrar diálogo de filtros
        dialogo = FiltrosSociosDialog(self)
        if dialogo.exec() != QDialog.Accepted:
            return
        
        filtros = dialogo.get_filtros()
        estado = filtros['estado']
        
        # Verificar si hay datos con los filtros actuales
        socios = socio_service.listar_socios()
        if estado == "Activos":
            socios = [s for s in socios if s.estado == SocioEstado.ACTIVO]
        elif estado == "Inactivos":
            socios = [s for s in socios if s.estado == SocioEstado.INACTIVO]
        
        if not socios:
            QMessageBox.information(self, "Sin datos", f"No hay socios {estado.lower()} para listar.")
            return
        
        # Preguntar dónde guardar
        archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Listado de Socios",
            f"listado_socios_{estado.lower()}.xlsx",
            "Excel (*.xlsx)"
        )
        
        if not archivo:
            return  # Usuario canceló
        
        # Generar el archivo
        try:
            self._generar_xlsx(archivo, estado)
            QMessageBox.information(self, "Éxito", f"Listado guardado en:\n{archivo}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el listado:\n{e}")

    def _generar_xlsx(self, archivo: str, filtro_estado: str) -> None:
        """Genera el archivo XLSX con los datos de socios filtrados.
        
        Args:
            archivo (str): Ruta del archivo XLSX a crear.
            filtro_estado (str): Estado de filtro ('Todos', 'Activos' o 'Inactivos').
        """
        
        # Obtener socios según filtro
        socios = socio_service.listar_socios()
        if filtro_estado == "Activos":
            socios = [s for s in socios if s.estado == SocioEstado.ACTIVO]
        elif filtro_estado == "Inactivos":
            socios = [s for s in socios if s.estado == SocioEstado.INACTIVO]
        # Si es "Todos", no filtramos
        
        # Crear libro y hoja
        wb = Workbook()
        ws = wb.active
        ws.title = "Socios"
        
        # Cabecera con estilo
        cabecera = ["Nombre", "Apellido 1", "Apellido 2", "Email", "Teléfono", "Estado"]
        ws.append(cabecera)
        
        # Aplicar estilos a la cabecera
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Añadir datos
        for socio in socios:
            estado_display = socio.estado.name.capitalize() if hasattr(socio.estado, 'name') else str(socio.estado)
            fila = [
                socio.nombre,
                socio.apellido1,
                socio.apellido2,
                socio.email,
                socio.telefono,
                estado_display
            ]
            ws.append(fila)
        
        # Ajustar ancho de columnas
        from openpyxl.utils import get_column_letter
        anchos = [20, 20, 20, 30, 15, 12]
        for i, ancho in enumerate(anchos, start=1):
            ws.column_dimensions[get_column_letter(i)].width = ancho
        
        # Guardar archivo
        wb.save(archivo)

    def generar_listado_reservas(self) -> None:
        """Genera un listado de reservas del socio seleccionado en formato XLSX.
        
        Requiere que haya un socio seleccionado en la tabla. Muestra un diálogo
        de filtros (fechas y estado) y exporta las reservas a Excel.
        """
        # Verificar que hay un socio seleccionado
        fila = self.tabla_socios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un socio para listar sus reservas")
            return
        
        # Obtener el ID del socio del UserRole
        item0 = self.tabla_socios.item(fila, 0)
        if item0 is None:
            return
        id_socio = item0.data(Qt.UserRole)
        if id_socio is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID del socio")
            return
        
        nombre_socio = f"{self.tabla_socios.item(fila, 0).text()} {self.tabla_socios.item(fila, 1).text()}"
        
        # Mostrar diálogo de filtros
        dialogo = FiltrosReservasDialog(self)
        if dialogo.exec() != QDialog.Accepted:
            return
        
        filtros = dialogo.get_filtros()
        
        # Verificar si hay datos con los filtros actuales
        from services.reserva_service import listar_reservas
        reservas = listar_reservas(id_socio=id_socio)
        
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
            f"reservas_{nombre_socio.replace(' ', '_').lower()}.xlsx",
            "Excel (*.xlsx)"
        )
        
        if not archivo:
            return
        
        # Generar el archivo
        try:
            self._generar_xlsx_reservas(archivo, id_socio, nombre_socio, filtros)
            QMessageBox.information(self, "Éxito", f"Listado guardado en:\n{archivo}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el listado:\n{e}")

    def _generar_xlsx_reservas(self, archivo: str, id_socio: int, nombre_socio: str, filtros: dict) -> None:
        """Genera el archivo XLSX con las reservas del socio filtradas.
        
        Args:
            archivo (str): Ruta del archivo XLSX a crear.
            id_socio (int): ID del socio.
            nombre_socio (str): Nombre completo del socio para el título.
            filtros (dict): Diccionario con filtros (fecha_inicio, fecha_fin, estado).
        """
        from services.reserva_service import listar_reservas
        from services.pista_service import listar_pistas
        
        # Obtener todas las reservas del socio
        reservas = listar_reservas(id_socio=id_socio)
        
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
        
        # Crear mapa de pistas para evitar lazy loading
        pistas = listar_pistas()
        mapa_pistas = {p.id_pista: p.nombre for p in pistas}
        
        # Crear libro y hoja
        wb = Workbook()
        ws = wb.active
        ws.title = "Reservas"
        
        # Título
        ws.merge_cells('A1:E1')
        titulo = ws['A1']
        titulo.value = f"Reservas de {nombre_socio}"
        titulo.font = Font(bold=True, size=14)
        titulo.alignment = Alignment(horizontal="center", vertical="center")
        
        # Cabecera con estilo
        cabecera = ["Pista", "Fecha", "Hora Inicio", "Hora Fin", "Estado", "Duración (min)"]
        ws.append(cabecera)
        
        # Aplicar estilos a la cabecera
        for cell in ws[2]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Añadir datos
        for reserva in reservas:
            estado_display = reserva.estado.name.capitalize() if hasattr(reserva.estado, 'name') else str(reserva.estado)
            pista_nombre = mapa_pistas.get(reserva.id_pista, str(reserva.id_pista))
            
            # Calcular duración
            duracion_min = (reserva.hora_fin.hour * 60 + reserva.hora_fin.minute) - (reserva.hora_inicio.hour * 60 + reserva.hora_inicio.minute)
            
            fila = [
                pista_nombre,
                format_date(reserva.fecha),
                format_time(reserva.hora_inicio),
                format_time(reserva.hora_fin),
                estado_display,
                duracion_min
            ]
            ws.append(fila)
        
        # Ajustar ancho de columnas
        from openpyxl.utils import get_column_letter
        anchos = [20, 15, 15, 15, 12, 15]
        for i, ancho in enumerate(anchos, start=1):
            ws.column_dimensions[get_column_letter(i)].width = ancho
        
        # Guardar archivo
        wb.save(archivo)

    def generar_listado_pagos(self) -> None:
        """Genera un listado de pagos del socio seleccionado en formato XLSX.
        
        Requiere que haya un socio seleccionado en la tabla. Muestra un diálogo
        de filtros (tipo, fechas y estado) y exporta los pagos a Excel.
        """
        # Verificar que hay un socio seleccionado
        fila = self.tabla_socios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un socio para listar sus pagos")
            return
        
        # Obtener el ID del socio del UserRole
        item0 = self.tabla_socios.item(fila, 0)
        if item0 is None:
            return
        id_socio = item0.data(Qt.UserRole)
        if id_socio is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID del socio")
            return
        
        nombre_socio = f"{self.tabla_socios.item(fila, 0).text()} {self.tabla_socios.item(fila, 1).text()}"
        
        # Mostrar diálogo de filtros
        dialogo = FiltrosPagosDialog(self)
        if dialogo.exec() != QDialog.Accepted:
            return
        
        filtros = dialogo.get_filtros()
        
        # Verificar si hay datos con los filtros actuales
        from services.pago_service import listar_pagos
        pagos = listar_pagos()
        pagos = [p for p in pagos if p.id_socio == id_socio]
        
        # Aplicar filtros temporalmente para verificar
        if filtros['tipo'] == "Cuota":
            pagos_filtrados = [p for p in pagos if p.tipo == PagoTipo.CUOTA]
        elif filtros['tipo'] == "Reserva":
            pagos_filtrados = [p for p in pagos if p.tipo == PagoTipo.RESERVA]
        elif filtros['tipo'] == "Extra":
            pagos_filtrados = [p for p in pagos if p.tipo == PagoTipo.EXTRA]
        else:
            pagos_filtrados = pagos
        
        if filtros['fecha_inicio'] and filtros['fecha_fin']:
            pagos_filtrados = [p for p in pagos_filtrados if filtros['fecha_inicio'] <= p.fecha_pago <= filtros['fecha_fin']]
        elif filtros['fecha_inicio']:
            pagos_filtrados = [p for p in pagos_filtrados if p.fecha_pago >= filtros['fecha_inicio']]
        elif filtros['fecha_fin']:
            pagos_filtrados = [p for p in pagos_filtrados if p.fecha_pago <= filtros['fecha_fin']]
        
        if filtros['estado'] == "Pagados":
            pagos_filtrados = [p for p in pagos_filtrados if p.estado == PagoEstado.PAGADO]
        elif filtros['estado'] == "Anulados":
            pagos_filtrados = [p for p in pagos_filtrados if p.estado == PagoEstado.ANULADO]
        
        if not pagos_filtrados:
            QMessageBox.information(self, "Sin datos", "No hay pagos que cumplan los criterios de filtro.")
            return
        
        # Preguntar dónde guardar
        archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Listado de Pagos",
            f"pagos_{nombre_socio.replace(' ', '_').lower()}.xlsx",
            "Excel (*.xlsx)"
        )
        
        if not archivo:
            return
        
        # Generar el archivo
        try:
            self._generar_xlsx_pagos(archivo, id_socio, nombre_socio, filtros)
            QMessageBox.information(self, "Éxito", f"Listado guardado en:\n{archivo}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el listado:\n{e}")

    def _generar_xlsx_pagos(self, archivo: str, id_socio: int, nombre_socio: str, filtros: dict) -> None:
        """Genera el archivo XLSX con los pagos del socio filtrados.
        
        Args:
            archivo (str): Ruta del archivo XLSX a crear.
            id_socio (int): ID del socio.
            nombre_socio (str): Nombre completo del socio para el título.
            filtros (dict): Diccionario con filtros (tipo, fecha_inicio, fecha_fin, estado).
        """
        from services.pago_service import listar_pagos
        from models import orm
        
        # Obtener todos los pagos
        pagos = listar_pagos()
        # Filtrar por socio
        pagos = [p for p in pagos if p.id_socio == id_socio]
        
        # Filtrar por tipo
        if filtros['tipo'] == "Cuota":
            pagos = [p for p in pagos if p.tipo == PagoTipo.CUOTA]
        elif filtros['tipo'] == "Reserva":
            pagos = [p for p in pagos if p.tipo == PagoTipo.RESERVA]
        elif filtros['tipo'] == "Extra":
            pagos = [p for p in pagos if p.tipo == PagoTipo.EXTRA]
        
        # Filtrar por fechas si se especificaron
        if filtros['fecha_inicio'] and filtros['fecha_fin']:
            pagos = [p for p in pagos if filtros['fecha_inicio'] <= p.fecha_pago <= filtros['fecha_fin']]
        elif filtros['fecha_inicio']:
            pagos = [p for p in pagos if p.fecha_pago >= filtros['fecha_inicio']]
        elif filtros['fecha_fin']:
            pagos = [p for p in pagos if p.fecha_pago <= filtros['fecha_fin']]
        
        # Filtrar por estado
        if filtros['estado'] == "Pagados":
            pagos = [p for p in pagos if p.estado == PagoEstado.PAGADO]
        elif filtros['estado'] == "Anulados":
            pagos = [p for p in pagos if p.estado == PagoEstado.ANULADO]
        
        # Crear libro y hoja
        wb = Workbook()
        ws = wb.active
        ws.title = "Pagos"
        
        # Título
        ws.merge_cells('A1:E1')
        titulo = ws['A1']
        titulo.value = f"Pagos de {nombre_socio}"
        titulo.font = Font(bold=True, size=14)
        titulo.alignment = Alignment(horizontal="center", vertical="center")
        
        # Cabecera con estilo
        cabecera = ["Fecha", "Importe (€)", "Tipo", "Estado", "Concepto"]
        ws.append(cabecera)
        
        # Aplicar estilos a la cabecera
        for cell in ws[2]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Añadir datos
        total = 0.0
        for pago in pagos:
            tipo_display = pago.tipo.name.capitalize() if hasattr(pago.tipo, 'name') else str(pago.tipo)
            estado_display = pago.estado.name.capitalize() if hasattr(pago.estado, 'name') else str(pago.estado)
            
            # Obtener concepto según el tipo de pago
            concepto = ""
            if pago.tipo == PagoTipo.CUOTA:
                # Obtener período desde PagoCuota
                session = orm.SessionLocal()
                try:
                    from models.orm_models import PagoCuota
                    pago_cuota = session.query(PagoCuota).filter(PagoCuota.id_pago == pago.id_pago).first()
                    if pago_cuota:
                        concepto = pago_cuota.periodo
                finally:
                    session.close()
            elif pago.tipo == PagoTipo.EXTRA:
                # Obtener concepto desde PagoExtra
                session = orm.SessionLocal()
                try:
                    from models.orm_models import PagoExtra
                    pago_extra = session.query(PagoExtra).filter(PagoExtra.id_pago == pago.id_pago).first()
                    if pago_extra:
                        concepto = pago_extra.concepto
                finally:
                    session.close()
            elif pago.tipo == PagoTipo.RESERVA:
                concepto = ""  # Reserva se deja en blanco
            
            # Sumar solo pagos con estado PAGADO (no anulados)
            if pago.estado == PagoEstado.PAGADO:
                total += pago.importe
            
            fila = [
                format_date(pago.fecha_pago),
                f"{pago.importe:.2f}",
                tipo_display,
                estado_display,
                concepto
            ]
            ws.append(fila)
        
        # Añadir fila de total (separada por una línea en blanco)
        ws.append([])
        ws.append(["TOTAL PAGADO:", f"{total:.2f}"])
        fila_total = ws.max_row
        ws[f'A{fila_total}'].font = Font(bold=True)
        ws[f'B{fila_total}'].font = Font(bold=True)
        
        # Ajustar ancho de columnas
        from openpyxl.utils import get_column_letter
        anchos = [15, 15, 12, 12, 35]
        for i, ancho in enumerate(anchos, start=1):
            ws.column_dimensions[get_column_letter(i)].width = ancho
        
        # Guardar archivo
        wb.save(archivo)
