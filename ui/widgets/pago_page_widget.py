"""Widget de gestión de Pagos.

Este módulo contiene la clase `PagoPage`, que implementa la interfaz de usuario
para listar, insertar y anular pagos. Usa los servicios del paquete `services`
para persistencia y `utils.helpers` para formateo de fechas/horas.

Responsabilidades principales:
- Mostrar la lista de pagos (`cargar_pagos`).
- Permitir insertar pagos (cuota, reserva, extra) con `insertar()`.
- Soportar prefilling desde una reserva con `cargar_para_reserva(id_reserva)`.
- Anular pagos (cambiar estado a ANULADO) con `anular()`.
- Generar listado Excel de pagos con filtros `generar_listado()`.

Efectos secundarios:
- Emite/escucha la señal `bus.socios_changed` para recargar autocompletado de socios.
- Llama a funciones en `services.pago_service`, `services.socio_service`, etc.

Formato de fechas:
- Las fechas se muestran con `utils.helpers.format_date()` → DD/MM/YYYY.

Ejemplo de uso (desde MainWindow):
        main_win.pago_page.cargar_para_reserva(123)
        main_win.stackedWidget.setCurrentIndex(3)

Notas:
- Esta clase está diseñada para usarse dentro de la ventana principal generada
    por `main_window.py` y asume que los widgets (botones, combos) existen con
    los nombres generados por Qt Designer.
"""

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QCompleter, QHeaderView, QFileDialog
from PySide6.QtCore import Qt, QDate
from datetime import date
from utils.helpers import format_date

from ui.pago_page_ui import Ui_pago_page
from services.pago_service import (
    insertar_pago, insertar_pago_cuota, insertar_pago_reserva, insertar_pago_extra,
    listar_pagos, obtener_pago_por_id
)
from services.socio_service import listar_socios
from services.reserva_service import listar_reservas
from services.pista_service import listar_pistas
from utils.events import bus
from ui.widgets.filtros_dialog import FiltrosPagePagosDialog, _obtener_estilos_dialogo
from models.orm_models import PagoEstado, PagoTipo
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from models.orm import SessionLocal


class PagoPage(QWidget, Ui_pago_page):
    """Widget de Pagos.

    API pública y comportamiento relevante:
    - cargar_pagos(): recarga la tabla de pagos desde la base de datos.
    - cargar_para_reserva(id_reserva): precarga campos para crear un pago vinculado a una reserva.
    - insertar(): lee los campos del formulario y crea un pago (y entradas relacionadas).
    - modificar(): actualmente no implementado, muestra un mensaje.
    - anular(): marca un pago como anulado en la base de datos.

    Excepciones:
    - `cargar_para_reserva` lanza ValueError si la reserva no existe.

    Dependencias externas importantes:
    - services.pago_service: funciones de inserción y consulta de pagos.
    - services.socio_service, services.reserva_service, services.pista_service.
    - utils.helpers.format_date para formatear fechas.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # fecha por defecto
        self.dateEdit.setDate(QDate.currentDate())

        # autocompletado socios
        self._cargar_socios()

        # internal linked reservation id when opened from a reserva
        self._linked_reserva_id = None

        # si el usuario cambia el tipo o edita el concepto, rompemos la vinculación
        self.comboBox.currentIndexChanged.connect(self._on_tipo_changed)
        try:
            # QLineEdit.textEdited se dispara cuando el usuario modifica manualmente
            self.txt_concepto.textEdited.connect(self._on_concepto_edited)
        except Exception:
            pass

        # Suscribir recarga automática cuando cambien los socios
        bus.socios_changed.connect(self._cargar_socios)

        # conectar botones
        self.btn_agregar.clicked.connect(self.insertar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_baja.clicked.connect(self.anular)
        self.btn_listar.clicked.connect(self.generar_listado)
        
        # Conectar tabla para que actualice los campos al seleccionar fila
        self.tabla_pagos.itemSelectionChanged.connect(self.actualizar_campos)

        # cargar tabla
        self.cargar_pagos()

    def _cargar_socios(self) -> None:
        """Carga el autocompletado de socios desde el servicio.
        
        Obtiene todos los socios del servicio y configura un completer con autocompletado
        case-insensitive para el campo de socio. Crea mapeos internos para acceso rápido.
        """
        socios = listar_socios()
        self.mapa_socios = {f"{s.nombre} {s.apellido1} ({s.email})": s.id_socio for s in socios}
        completer = QCompleter(list(self.mapa_socios.keys()))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.activated.connect(self._on_completer_activated)
        self.txt_socio.setCompleter(completer)
        self.selected_socio_id = None

    def _on_completer_activated(self, text: str) -> None:
        """Handler llamado cuando el usuario selecciona un elemento del completer.
        
        Args:
            text (str): Texto del elemento seleccionado del completer.
        """
        self.selected_socio_id = self.mapa_socios.get(text)

    def cargar_para_reserva(self, id_reserva: int) -> None:
        """Prefill the payment form using a reservation id.

        - Busca la reserva y coloca el socio relacionado en el autocompleter y campo.
        - Rellena el concepto con el id de la reserva y selecciona el tipo 'Reserva'.
        - Ajusta la fecha al día de la reserva.
        
        Args:
            id_reserva (int): ID de la reserva para precarga.
        
        Raises:
            ValueError: Si la reserva no se encuentra en la base de datos.
        """
        from services.reserva_service import obtener_reserva_por_id

        r = obtener_reserva_por_id(id_reserva)
        if r is None:
            raise ValueError("Reserva no encontrada")

        # establecer socio en el campo (intentar mostrar el texto del mapa)
        socios = listar_socios()
        mapa = {f"{s.nombre} {s.apellido1} ({s.email})": s.id_socio for s in socios}
        # buscar key por id
        display = None
        for k, v in mapa.items():
            if v == r.id_socio:
                display = k
                break

        if display:
            self.txt_socio.setText(display)
            self.selected_socio_id = r.id_socio
        else:
            self.txt_socio.setText(str(r.id_socio))
            self.selected_socio_id = r.id_socio

    # concepto: descripción legible de la reserva (no se almacena en Pago_Reserva)
        # intentar obtener nombre de pista y hora
        pistas = listar_pistas()
        mapa_pistas = {p.id_pista: p.nombre for p in pistas}
        pista_nombre = mapa_pistas.get(r.id_pista, str(r.id_pista))
        hora = ''
        try:
            hora = r.hora_inicio.strftime('%H:%M') if hasattr(r.hora_inicio, 'strftime') else ''
        except Exception:
            hora = ''
        descripcion = f"Reserva {pista_nombre} — {format_date(r.fecha)} {hora}"
        self.txt_concepto.setText(descripcion)
        # guardar la referencia interna y bloquear edición del concepto
        self._linked_reserva_id = id_reserva
        try:
            self.txt_concepto.setReadOnly(True)
        except Exception:
            pass
        # seleccionar tipo 'Reserva' en combo (segundo elemento)
        idx = self.comboBox.findText('Reserva', Qt.MatchFixedString)
        if idx >= 0:
            self.comboBox.setCurrentIndex(idx)

        # fecha del pago: por defecto fecha de la reserva
        try:
            if hasattr(r.fecha, 'year'):
                self.dateEdit.setDate(r.fecha)
        except Exception:
            pass

    def _on_tipo_changed(self, idx: int) -> None:
        """Si el tipo deja de ser 'Reserva', limpiamos la vinculación.
        
        Args:
            idx (int): Índice del item seleccionado en el combo.
        """
        try:
            tipo_text = self.comboBox.currentText().lower()
        except Exception:
            tipo_text = ''
        if tipo_text != 'reserva' and self._linked_reserva_id is not None:
            self._clear_linked_reserva()

    def _on_concepto_edited(self, text: str) -> None:
        """Si el usuario edita el concepto manualmente, limpiamos la vinculación.
        
        Args:
            text (str): Nuevo texto del campo concepto.
        """
        if self._linked_reserva_id is not None:
            self._clear_linked_reserva()

    def _clear_linked_reserva(self) -> None:
        """Limpia la vinculación a una reserva precargada."""
        self._linked_reserva_id = None
        try:
            self.txt_concepto.setReadOnly(False)
        except Exception:
            pass

    def cargar_pagos(self) -> None:
        """Recarga la tabla de pagos desde el servicio.
        
        Obtiene todos los pagos de la base de datos y actualiza la tabla con sus datos.
        Utiliza mapeos internos para evitar acceso lazy loading a relaciones.
        """
        pagos = listar_pagos()
        self.tabla_pagos.setRowCount(len(pagos))
        self.tabla_pagos.setColumnCount(6)
        self.tabla_pagos.setHorizontalHeaderLabels(["ID", "Socio", "Importe", "Fecha", "Tipo", "Estado"])

        # crear mapa id->display para evitar lazy load
        socios = listar_socios()
        mapa = {s.id_socio: f"{s.nombre} {s.apellido1} ({s.email})" for s in socios}

        for fila, p in enumerate(pagos):
            tipo_display = p.tipo.name.capitalize() if hasattr(p.tipo, 'name') else str(p.tipo)
            estado_display = p.estado.name.capitalize() if hasattr(p.estado, 'name') else str(p.estado)
            values = [
                p.id_pago,
                mapa.get(p.id_socio, str(p.id_socio)),
                f"{p.importe:.2f}",
                format_date(p.fecha_pago),
                tipo_display,
                estado_display,
            ]
            for col, dato in enumerate(values):
                self.tabla_pagos.setItem(fila, col, QTableWidgetItem(str(dato)))

        # ajustar tamaño de columnas
        header = self.tabla_pagos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.tabla_pagos.setColumnWidth(0, 60)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        for col in range(2, 5):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
            self.tabla_pagos.setColumnWidth(col, 120) 

    def actualizar_campos(self) -> None:
        """Carga los datos de la fila seleccionada en los campos del formulario.
        
        Lee la fila actualmente seleccionada en la tabla y rellena los campos de entrada
        con los datos del pago seleccionado.
        """
        fila = self.tabla_pagos.currentRow()
        if fila < 0:
            return
        
        # Obtener el id del pago de la primera columna
        item0 = self.tabla_pagos.item(fila, 0)
        if item0 is None:
            return
        
        try:
            id_pago = int(item0.text())
            
            # Usar sesión para cargar relaciones lazy
            from models import orm
            from models.orm_models import Pago
            session = orm.SessionLocal()
            try:
                pago = session.query(Pago).filter(Pago.id_pago == id_pago).first()
                if pago is None:
                    return
                
                # Rellenar los campos con los datos del pago
                # Socio: mostrar nombre y apellido con email
                socios = listar_socios()
                mapa_socios = {s.id_socio: f"{s.nombre} {s.apellido1} ({s.email})" for s in socios}
                self.txt_socio.setText(mapa_socios.get(pago.id_socio, str(pago.id_socio)))
                
                # Importe
                self.txt_importe.setText(f"{pago.importe:.2f}")
                
                # Fecha
                if hasattr(pago.fecha_pago, 'year'):
                    self.dateEdit.setDate(pago.fecha_pago)
                
                # Tipo de pago
                tipo_text = pago.tipo.name.capitalize() if hasattr(pago.tipo, 'name') else str(pago.tipo)
                idx = self.comboBox.findText(tipo_text, Qt.MatchFixedString)
                if idx >= 0:
                    self.comboBox.setCurrentIndex(idx)
                
                # Concepto (depende del tipo de pago)
                concepto = ""
                if pago.pago_cuota:
                    concepto = pago.pago_cuota.periodo
                elif pago.pago_reserva:
                    # Para reserva: mostrar el mismo concepto que en cargar_para_reserva
                    reserva = pago.pago_reserva.reserva if hasattr(pago.pago_reserva, 'reserva') else None
                    if reserva:
                        pistas = listar_pistas()
                        mapa_pistas = {p.id_pista: p.nombre for p in pistas}
                        pista_nombre = mapa_pistas.get(reserva.id_pista, str(reserva.id_pista))
                        hora = ''
                        try:
                            hora = reserva.hora_inicio.strftime('%H:%M') if hasattr(reserva.hora_inicio, 'strftime') else ''
                        except Exception:
                            hora = ''
                        concepto = f"Reserva {pista_nombre} — {format_date(reserva.fecha)} {hora}"
                    else:
                        concepto = str(pago.pago_reserva.id_reserva)
                elif pago.pago_extra:
                    concepto = pago.pago_extra.concepto
                self.txt_concepto.setText(concepto)
            finally:
                session.close()
            
        except Exception:
            pass

    def insertar(self) -> None:
        """Inserta un nuevo pago en la base de datos.
        
        Valida los campos, lee los valores del formulario y crea un nuevo registro de pago
        con sus correspondientes entradas vinculadas (PagoCuota, PagoReserva o PagoExtra).
        Luego recarga la tabla de pagos.
        """
        # Validaciones mínimas
        try:
            importe = float(self.txt_importe.text())
        except Exception:
            QMessageBox.warning(self, "Error", "Importe inválido")
            return
        
        # Validar que el importe no sea negativo
        if importe < 0:
            QMessageBox.warning(self, "Error", "El importe no puede ser negativo")
            return

        fecha_q = self.dateEdit.date()
        fecha_py = date(fecha_q.year(), fecha_q.month(), fecha_q.day())

        # resolver socio
        socio_text = self.txt_socio.text().strip()
        sid = self.selected_socio_id if self.selected_socio_id and socio_text in self.mapa_socios else self.mapa_socios.get(socio_text)
        if not sid:
            QMessageBox.warning(self, "Error", "Selecciona un socio válido")
            return

        tipo = self.comboBox.currentText().lower()
        concepto = self.txt_concepto.text().strip()

        try:
            from models.orm_models import PagoTipo
            # mapear tipo string del combo a PagoTipo
            tipo_enum = PagoTipo.CUOTA if tipo == 'cuota' else (PagoTipo.RESERVA if tipo == 'reserva' else PagoTipo.EXTRA)
            pago = insertar_pago(id_socio=sid, importe=importe, fecha_pago=fecha_py, tipo=tipo_enum)
            # crear entradas específicas
            if tipo == 'cuota':
                insertar_pago_cuota(pago.id_pago, periodo=concepto)
            elif tipo == 'reserva':
                # Si venimos de una reserva vinculada, usamos ese id.
                if getattr(self, '_linked_reserva_id', None):
                    insertar_pago_reserva(pago.id_pago, id_reserva=self._linked_reserva_id)
                else:
                    # Intentar interpretar el texto del campo como id de reserva; si falla, no vinculamos
                    try:
                        id_res = int(concepto)
                        insertar_pago_reserva(pago.id_pago, id_reserva=id_res)
                    except Exception:
                        # No hay id de reserva: no se crea enlace
                        pass
            elif tipo == 'extra':
                insertar_pago_extra(pago.id_pago, concepto=concepto)

            QMessageBox.information(self, "Éxito", "Pago insertado")
            # limpiar formulario y recargar tabla
            try:
                self.vaciar_campos()
            except Exception:
                pass
            self.cargar_pagos()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def modificar(self) -> None:
        """Modifica los datos del pago seleccionado en la base de datos.
        
        Valida los campos, lee los valores del formulario y actualiza el registro del pago.
        Luego recarga la tabla de pagos.
        """
        fila = self.tabla_pagos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un pago para modificar")
            return
        
        item0 = self.tabla_pagos.item(fila, 0)
        if item0 is None:
            QMessageBox.warning(self, "Error", "Fila inválida")
            return
        
        id_pago = int(item0.text())
        
        # Validaciones mínimas
        try:
            importe = float(self.txt_importe.text())
        except Exception:
            QMessageBox.warning(self, "Error", "Importe inválido")
            return
        
        # Validar que el importe no sea negativo
        if importe < 0:
            QMessageBox.warning(self, "Error", "El importe no puede ser negativo")
            return
        
        fecha_q = self.dateEdit.date()
        fecha_py = date(fecha_q.year(), fecha_q.month(), fecha_q.day())
        
        # resolver socio
        socio_text = self.txt_socio.text().strip()
        sid = self.selected_socio_id if self.selected_socio_id and socio_text in self.mapa_socios else self.mapa_socios.get(socio_text)
        if not sid:
            QMessageBox.warning(self, "Error", "Selecciona un socio válido")
            return
        
        try:
            from services.pago_service import modificar_pago
            modificar_pago(id_pago=id_pago, id_socio=sid, importe=importe, fecha_pago=fecha_py)
            QMessageBox.information(self, "Éxito", "Pago modificado correctamente")
            self.vaciar_campos()
            self.cargar_pagos()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def anular(self) -> None:
        """Marca el pago seleccionado como anulado.
        
        Cambia el estado del pago a ANULADO. Luego recarga la tabla de pagos.
        """
        fila = self.tabla_pagos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un pago para anular")
            return
        item0 = self.tabla_pagos.item(fila, 0)
        if item0 is None:
            QMessageBox.warning(self, "Error", "Fila inválida")
            return
        id_pago = int(item0.text())
        # recuperar y cambiar estado
        p = obtener_pago_por_id(id_pago)
        if p is None:
            QMessageBox.warning(self, "Error", "Pago no encontrado")
            return
        # anular -> cambiar estado
        from models import orm
        session = orm.SessionLocal()
        try:
            pago_obj = session.get(type(p), p.id_pago)
            if pago_obj is None:
                QMessageBox.warning(self, "Error", "Pago no encontrado en sesión")
                return
            from models.orm_models import PagoEstado
            pago_obj.estado = PagoEstado.ANULADO
            session.commit()
        finally:
            session.close()
        QMessageBox.information(self, "Éxito", "Pago anulado")
        self.cargar_pagos()

    def generar_listado(self) -> None:
        """Genera un listado de pagos en formato XLSX con filtros.
        
        Muestra un diálogo para seleccionar filtros (tipo, fechas y estado),
        solicita la ubicación del archivo y exporta los datos a Excel.
        """
        from PySide6.QtWidgets import QDialog
        # Mostrar diálogo de filtros
        dlg = FiltrosPagePagosDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        
        filtros = dlg.get_filtros()
        
        # Obtener todos los pagos
        pagos = listar_pagos()
        
        # Filtrar por tipo
        if filtros['tipo'] != "Todos":
            tipo_mapa = {"Cuota": PagoTipo.CUOTA, "Reserva": PagoTipo.RESERVA, "Extra": PagoTipo.EXTRA}
            tipo_enum = tipo_mapa.get(filtros['tipo'])
            if tipo_enum:
                pagos = [p for p in pagos if p.tipo == tipo_enum]
        
        # Filtrar por fechas
        if filtros['fecha_inicio']:
            pagos = [p for p in pagos if p.fecha_pago >= filtros['fecha_inicio']]
        if filtros['fecha_fin']:
            pagos = [p for p in pagos if p.fecha_pago <= filtros['fecha_fin']]
        
        # Filtrar por estado
        if filtros['estado'] == "Pagados":
            pagos = [p for p in pagos if p.estado == PagoEstado.PAGADO]
        elif filtros['estado'] == "Anulados":
            pagos = [p for p in pagos if p.estado == PagoEstado.ANULADO]
        
        # Validar que hay datos
        if not pagos:
            QMessageBox.information(self, "Sin datos", "No hay pagos que coincidan con los criterios de filtro.")
            return
        
        # Mostrar diálogo para guardar
        tipo_filtro = filtros['tipo'].lower()
        estado_filtro = filtros['estado'].lower()
        archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Listado de Pagos",
            f"listado_pagos_{tipo_filtro}_{estado_filtro}.xlsx",
            "Excel (*.xlsx)"
        )
        
        if not archivo:
            return
        
        # Generar Excel
        self._generar_xlsx_pagos(archivo, pagos)
        QMessageBox.information(self, "Éxito", f"Listado guardado en:\n{archivo}")

    def _generar_xlsx_pagos(self, archivo: str, pagos: list) -> None:
        """Genera un archivo Excel con el listado de pagos.
        
        Args:
            archivo (str): Ruta del archivo XLSX a crear.
            pagos (list): Lista de objetos pago a exportar.
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Pagos"
        
        # Cabecera con estilo
        cabecera = ["ID", "Socio", "Fecha", "Importe (€)", "Tipo", "Estado", "Concepto"]
        ws.append(cabecera)
        
        # Aplicar estilos a la cabecera
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Sesión para lazy-loaded relationships
        session = SessionLocal()
        try:
            from models.orm_models import PagoCuota, PagoExtra, Socio
            
            # Obtener IDs de pagos para re-consultar dentro de la sesión
            pago_ids = [p.id_pago for p in pagos]
            pagos_sesion = session.query(__import__('models.orm_models', fromlist=['Pago']).Pago).filter(
                __import__('models.orm_models', fromlist=['Pago']).Pago.id_pago.in_(pago_ids)
            ).all()
            
            # Añadir datos
            for pago in pagos_sesion:
                # Obtener concepto según tipo
                concepto = ""
                if pago.tipo == PagoTipo.CUOTA:
                    pago_cuota = session.query(PagoCuota).filter_by(id_pago=pago.id_pago).first()
                    concepto = pago_cuota.periodo if pago_cuota else ""
                elif pago.tipo == PagoTipo.EXTRA:
                    pago_extra = session.query(PagoExtra).filter_by(id_pago=pago.id_pago).first()
                    concepto = pago_extra.concepto if pago_extra else ""
                # RESERVA no tiene concepto adicional
                
                estado_display = pago.estado.name.capitalize() if hasattr(pago.estado, 'name') else str(pago.estado)
                tipo_display = pago.tipo.name.capitalize() if hasattr(pago.tipo, 'name') else str(pago.tipo)
                
                # Obtener nombre del socio
                socio = pago.socio
                nombre_socio = f"{socio.nombre} {socio.apellido1}" if socio else ""
                
                fila = [
                    pago.id_pago,
                    nombre_socio,
                    format_date(pago.fecha_pago),
                    f"{pago.importe:.2f}",
                    tipo_display,
                    estado_display,
                    concepto
                ]
                ws.append(fila)
        finally:
            session.close()
        
        # Ajustar ancho de columnas
        anchos = [10, 20, 12, 15, 12, 12, 35]
        for i, ancho in enumerate(anchos, start=1):
            col_letter = get_column_letter(i)
            ws.column_dimensions[col_letter].width = ancho
        
        wb.save(archivo)

    def vaciar_campos(self) -> None:
        """Restablece los campos del formulario de pago al estado por defecto.
        
        Limpia todos los campos de entrada y resetea los valores de control internos.
        """
        self.txt_importe.clear()
        self.txt_socio.clear()
        self.selected_socio_id = None
        self.comboBox.setCurrentIndex(0)
        self.txt_concepto.clear()
        self._linked_reserva_id = None
        self.txt_concepto.setReadOnly(False)
        self.dateEdit.setDate(QDate.currentDate())

__all__ = ['PagoPage']
