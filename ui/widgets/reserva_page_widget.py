"""Widget de gestión de Reservas.

Contiene la clase `ReservaPage` que permite listar reservas, crear/editar
y cancelar reservas, y navegar al flujo de pagos para una reserva seleccionada.

Formatos:
- Fechas: `utils.helpers.format_date()` → DD/MM/YYYY
- Horas: `utils.helpers.format_time()` → HH:MM

Efectos secundarios:
- Se suscribe a `bus.socios_changed` y `bus.pistas_changed` para recargar autocompletados.
- Utiliza servicios en `services.reserva_service`, `services.socio_service` y `services.pista_service`.

API pública:
- cargar_reservas(): recarga la tabla de reservas.
- insertar()/modificar()/cancelar(): CRUD de reservas.
- ir_a_pagos(): navega a la página de pagos precargando la reserva.
"""

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QCompleter, QHeaderView, QFileDialog
from PySide6.QtCore import Qt, QDate, QTime
from datetime import date, time
from utils.helpers import format_date, format_time
from ui.reserva_page_ui import Ui_reserva_page
from services.reserva_service import insertar_reserva, listar_reservas, obtener_reserva_por_id, actualizar_reserva, cancelar_reserva
from services.pista_service import listar_pistas
from services.socio_service import listar_socios
from utils.events import bus
from models.orm_models import ReservaEstado
from models.orm import SessionLocal
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from ui.widgets.filtros_dialog import FiltrosReservasDialog


class ReservaPage(QWidget, Ui_reserva_page):
    """Widget para administrar reservas.

    Métodos públicos:
    - cargar_reservas(): re-lee reservas y actualiza la tabla.
    - insertar()/modificar()/cancelar(): acciones sobre reservas.
    - ir_a_pagos(): envía al usuario a la página de pagos con la reserva seleccionada.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.selected_socio_id = None
        # fecha por defecto: hoy
        self.dateEdit.setDate(QDate.currentDate())
        # cuando se cambia la hora de inicio, ajustar hora fin
        self.timeEdit.timeChanged.connect(self.suma_tiempo)

        # Conectar botones
        self.btn_agregar.clicked.connect(self.insertar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_baja.clicked.connect(self.cancelar)
        self.btn_pagar.clicked.connect(self.ir_a_pagos)
        self.btn_listar.clicked.connect(self.generar_listado)

        # Conectar tabla
        self.tabla_reservas.itemSelectionChanged.connect(self.actualizar_campos)

        # Inicializar campos
        self.cargar_pistas()
        self.cargar_socios()
        self.cargar_reservas()

        # Suscribirse a cambios globales para mantener autocompleters/combos actualizados
        bus.socios_changed.connect(self.cargar_socios)
        bus.pistas_changed.connect(self.cargar_pistas)

    def cargar_pistas(self):
        pistas = listar_pistas()
        self.cmb_pista.clear()
        for p in pistas:
            # mostrar nombre, almacenar id en data
            self.cmb_pista.addItem(p.nombre, p.id_pista)
        # mapa id -> nombre para usar en la tabla sin lazy-loading
        self.mapa_pistas = {p.id_pista: p.nombre for p in pistas}

    def cargar_socios(self):
        socios = listar_socios()
        # Creamos un diccionario para mapear texto mostrado → id_socio
        self.mapa_socios = {
            f"{s.nombre} {s.apellido1} ({s.email})": s.id_socio for s in socios
        }

        completer = QCompleter(list(self.mapa_socios.keys()))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)  # busca en cualquier parte del texto
        # cuando el usuario seleccione un elemento del completer guardamos el id
        completer.activated.connect(self._on_completer_activated)
        self.txt_socio.setCompleter(completer)

        # crear mapa inverso id -> display para buscar rápidamente
        self.mapa_socios_id_to_display = {v: k for k, v in self.mapa_socios.items()}

    def cargar_reservas(self):
        reservas = listar_reservas()
        self.tabla_reservas.setRowCount(len(reservas))
        # Definir siempre las columnas y las cabeceras para que se muestren aun sin filas
        self.tabla_reservas.setColumnCount(7)
        self.tabla_reservas.setHorizontalHeaderLabels(["ID", "Socio", "Pista", "Fecha", "Hora Inicio", "Hora Fin", "Estado"])

        for fila, r in enumerate(reservas):
            values = [
                r.id_reserva,
                # usar mapas para evitar lazy load: mostrar texto del socio (nombre + email)
                self.mapa_socios_id_to_display.get(r.id_socio, str(r.id_socio)),
                self.mapa_pistas.get(r.id_pista, str(r.id_pista)),
                # Mostrar fecha y horas con helpers centralizados
                format_date(r.fecha),
                format_time(r.hora_inicio),
                format_time(r.hora_fin),
                (r.estado.name.capitalize() if hasattr(r.estado, 'name') else str(r.estado))
            ]

            for col, dato in enumerate(values):
                self.tabla_reservas.setItem(fila, col, QTableWidgetItem(str(dato)))

        # ajustar tamaño de columnas
        header = self.tabla_reservas.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.tabla_reservas.setColumnWidth(0, 60)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        for col in range(2, 7):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
            self.tabla_reservas.setColumnWidth(col, 120)    
    
    def actualizar_campos(self):
        fila = self.tabla_reservas.currentRow()
        if fila < 0:
            return

        # rellenar campos desde la fila seleccionada
        item0 = self.tabla_reservas.item(fila, 0)
        if item0 is None:
            return
        id_reserva = int(item0.text())
        r = obtener_reserva_por_id(id_reserva)
        if r is None:
            return

        # Seleccionar pista en cmb_pista por id
        idx = self.cmb_pista.findData(r.id_pista)
        if idx >= 0:
            self.cmb_pista.setCurrentIndex(idx)

        # Socio: mostrar el string del mapa (Nombre Apellido (email)) si lo tenemos
        display = self.mapa_socios_id_to_display.get(r.id_socio)
        if display:
            self.txt_socio.setText(display)
            self.selected_socio_id = r.id_socio
        else:
            # fallback: mostrar id (no accedemos a relaciones en instancia desconectada)
            self.txt_socio.setText(str(r.id_socio))
            self.selected_socio_id = r.id_socio

        # Fecha y horas
        if hasattr(r.fecha, 'year'):
            self.dateEdit.setDate(r.fecha)
        if hasattr(r.hora_inicio, 'hour'):
            self.timeEdit.setTime(r.hora_inicio)
        if hasattr(r.hora_fin, 'hour'):
            self.timeEdit_2.setTime(r.hora_fin)

    def validar_campos(self):
        # Validar que exista pista seleccionada y que horas sean coherentes
        if self.cmb_pista.currentIndex() < 0:
            return False, "Selecciona una pista"
        if not self.txt_socio.text().strip():
            return False, "Introduce el nombre del socio"

        hi = self.timeEdit.time()
        hf = self.timeEdit_2.time()
        if hi >= hf:
            return False, "Hora inicio debe ser anterior a hora fin"

        return True, ""

    def _on_completer_activated(self, text: str):
        """Handler llamado cuando el usuario selecciona un elemento del completer."""
        sid = self.mapa_socios.get(text)
        if sid:
            self.selected_socio_id = sid

    def _resolve_socio_id(self, text: str):
        """Resuelve el id del socio a partir del texto del campo.

        - Si el usuario seleccionó via completer, `self.selected_socio_id` estará fijado.
        - Si el texto coincide con una clave del mapa, devolvemos su id.
        - Si el texto es un entero (id), lo devolvemos.
        - En cualquier otro caso devolvemos None.
        """
        if self.selected_socio_id is not None and self.txt_socio.text().strip() in self.mapa_socios:
            # usuario seleccionó algo y el texto coincide
            return self.selected_socio_id

        text = text.strip()
        if not text:
            return None

        # comprobar coincidencia exacta en el mapa
        sid = self.mapa_socios.get(text)
        if sid:
            return sid

        # intentar como entero id
        try:
            return int(text)
        except Exception:
            return None

    def suma_tiempo(self, qtime: QTime):
        """Al cambiar la hora de inicio, actualizar la hora fin según duración configurada."""
        try:
            from utils.settings import get_reservation_duration
            duracion_minutos = get_reservation_duration()
            new_qt = qtime.addSecs(duracion_minutos * 60)
            # establecer la hora fin sin disparar loops (no desconectamos señales porque no hay handling recíproco)
            self.timeEdit_2.setTime(new_qt)
        except Exception:
            # no queremos que un fallo de UI rompa la app
            pass

    def vaciar_campos(self):
        """Restablece los campos del formulario de reserva al estado por defecto.

        - Limpia el campo de socio y resetea el id seleccionado.
        - Selecciona la primera pista del combo si existe.
        - Pone la fecha a hoy y las horas a valores por defecto.
        """
        self.txt_socio.clear()
        self.selected_socio_id = None
        self.cmb_pista.setCurrentIndex(0)
        # Fecha a hoy
        self.dateEdit.setDate(QDate.currentDate())
        # Horas a 00:00
        self.timeEdit.setTime(QTime(0, 0))
        self.timeEdit_2.setTime(QTime(0, 0))

    def insertar(self):
        ok, msg = self.validar_campos()
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return

        id_pista = self.cmb_pista.currentData()
        # Para simplicidad usamos el texto de socio; servicio espera id_socio, pero
        # en este widget no resolvemos id desde nombre: se asume que el flujo de UI
        # usará ids. Aquí intentaremos interpretar un entero si se introdujo.
        socio_text = self.txt_socio.text().strip()
        id_socio = self._resolve_socio_id(socio_text)
        if id_socio is None:
            QMessageBox.warning(self, "Error", "Selecciona un socio válido del autocompletado")
            return

        fecha_qdate = self.dateEdit.date()
        fecha_py = date(fecha_qdate.year(), fecha_qdate.month(), fecha_qdate.day())
        hi_q = self.timeEdit.time()
        hf_q = self.timeEdit_2.time()
        hi_py = time(hi_q.hour(), hi_q.minute())
        hf_py = time(hf_q.hour(), hf_q.minute())

        try:
            insertar_reserva(id_socio=id_socio, id_pista=id_pista, fecha=fecha_py, hora_inicio=hi_py, hora_fin=hf_py)
            QMessageBox.information(self, "Éxito", "Reserva insertada correctamente")
            self.vaciar_campos()
            self.cargar_reservas()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def modificar(self):
        fila = self.tabla_reservas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona una reserva para modificar")
            return
        item0 = self.tabla_reservas.item(fila, 0)
        if item0 is None:
            QMessageBox.warning(self, "Error", "Fila seleccionada inválida")
            return
        id_reserva = int(item0.text())
        ok, msg = self.validar_campos()
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return

        id_pista = self.cmb_pista.currentData()
        socio_text = self.txt_socio.text().strip()
        id_socio = self._resolve_socio_id(socio_text)
        if id_socio is None:
            QMessageBox.warning(self, "Error", "Selecciona un socio válido del autocompletado")
            return

        fecha_qdate = self.dateEdit.date()
        fecha_py = date(fecha_qdate.year(), fecha_qdate.month(), fecha_qdate.day())
        hi_q = self.timeEdit.time()
        hf_q = self.timeEdit_2.time()
        hi_py = time(hi_q.hour(), hi_q.minute())
        hf_py = time(hf_q.hour(), hf_q.minute())

        try:
            actualizar_reserva(id_reserva=id_reserva, id_socio=id_socio, id_pista=id_pista, fecha=fecha_py, hora_inicio=hi_py, hora_fin=hf_py)
            QMessageBox.information(self, "Éxito", "Reserva modificada correctamente")
            self.vaciar_campos()
            self.cargar_reservas()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def cancelar(self):
        fila = self.tabla_reservas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona una reserva para cancelar")
            return
        item0 = self.tabla_reservas.item(fila, 0)
        if item0 is None:
            QMessageBox.warning(self, "Error", "Fila seleccionada inválida")
            return
        id_reserva = int(item0.text())
        cancelar_reserva(id_reserva)
        QMessageBox.information(self, "Éxito", "Reserva cancelada")
        self.cargar_reservas()

    def ir_a_pagos(self):
        """Navega a la página de Pagos y carga los datos de la reserva seleccionada.

        - Verifica que hay una reserva seleccionada en la tabla.
        - Obtiene la reserva y delega en la página de Pagos para rellenar el formulario.
        - Cambia el stackedWidget del MainWindow a la página de Pagos.
        """
        fila = self.tabla_reservas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona una reserva para pagar")
            return
        item0 = self.tabla_reservas.item(fila, 0)
        if item0 is None:
            QMessageBox.warning(self, "Error", "Fila seleccionada inválida")
            return
        id_reserva = int(item0.text())
        r = obtener_reserva_por_id(id_reserva)
        if r is None:
            QMessageBox.warning(self, "Error", "Reserva no encontrada")
            return

        # Obtener la ventana principal y la página de pagos
        main_win = self.window()
        if not hasattr(main_win, 'pago_page') or not hasattr(main_win, 'stackedWidget'):
            QMessageBox.warning(self, "Error", "No se puede abrir la página de pagos")
            return

        try:
            # pedir a la página de pagos que cargue los datos necesarios
            main_win.pago_page.cargar_para_reserva(id_reserva)
        except Exception as e:
            # no queremos que un fallo aquí rompa la app, mostrar mensaje
            QMessageBox.warning(self, "Error", f"No se pudo preparar la página de pagos: {e}")
            return

        # Cambiar a la página de pagos (índice 3 según MainWindow)
        try:
            main_win.stackedWidget.setCurrentIndex(3)
        except Exception:
            # fallback: intentar buscar método público
            pass

    def generar_listado(self):
        """Genera un listado de reservas en Excel con filtros por fecha y estado."""
        from PySide6.QtWidgets import QDialog
        dlg = FiltrosReservasDialog(self)
        if dlg.exec() == QDialog.Accepted:
            filtros = dlg.get_filtros()
            
            # Obtener todas las reservas y filtrar
            session = SessionLocal()
            try:
                reservas = session.query(
                    __import__('models.orm_models', fromlist=['Reserva']).Reserva
                ).all()
                
                # Filtrar por fecha
                fecha_inicio = filtros['fecha_inicio']
                fecha_fin = filtros['fecha_fin']
                reservas = [r for r in reservas if fecha_inicio <= r.fecha <= fecha_fin]
                
                # Filtrar por estado
                estado_filter = filtros['estado']
                if estado_filter != 'Todas':
                    if estado_filter == 'Activas':
                        reservas = [r for r in reservas if r.estado == ReservaEstado.ACTIVA]
                    elif estado_filter == 'Canceladas':
                        reservas = [r for r in reservas if r.estado == ReservaEstado.CANCELADA]
                
                if not reservas:
                    QMessageBox.information(self, "Sin datos", "No hay reservas que coincidan con los filtros seleccionados")
                    return
                
                # Generar nombre del archivo por defecto
                estado_name = estado_filter.lower().replace('á', 'a')
                archivo_default = f"listado_reservas_{estado_name}.xlsx"
                
                # Abrir diálogo de guardado
                archivo, _ = QFileDialog.getSaveFileName(
                    self,
                    "Guardar listado de reservas",
                    archivo_default,
                    "Excel Files (*.xlsx);;All Files (*)"
                )
                
                if not archivo:
                    return
                
                self._generar_xlsx_reservas(archivo, reservas)
                QMessageBox.information(self, "Éxito", f"Listado guardado en:\n{archivo}")
            finally:
                session.close()

    def _generar_xlsx_reservas(self, archivo: str, reservas: list):
        """Genera un archivo Excel con el listado de reservas con nombres de socio y pista."""
        wb = Workbook()
        ws = wb.active
        ws.title = "Reservas"
        
        # Definir encabezados
        headers = ["ID", "Socio", "Pista", "Fecha", "Hora Inicio", "Hora Fin", "Estado"]
        ws.append(headers)
        
        # Estilos para encabezado
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Sesión para cargar relaciones
        session = SessionLocal()
        try:
            # Re-queryear reservas dentro de la sesión para acceder a relaciones
            from models.orm_models import Reserva
            ids_reservas = [r.id_reserva for r in reservas]
            reservas_session = session.query(Reserva).filter(Reserva.id_reserva.in_(ids_reservas)).all()
            
            # Agregar datos
            for fila, r in enumerate(reservas_session, 2):
                ws.cell(row=fila, column=1, value=r.id_reserva)
                ws.cell(row=fila, column=2, value=f"{r.socio.nombre} {r.socio.apellido1}")
                ws.cell(row=fila, column=3, value=r.pista.nombre)
                ws.cell(row=fila, column=4, value=format_date(r.fecha))
                ws.cell(row=fila, column=5, value=format_time(r.hora_inicio))
                ws.cell(row=fila, column=6, value=format_time(r.hora_fin))
                ws.cell(row=fila, column=7, value=r.estado.name.capitalize())
                
                # Centrar celdas
                for col in range(1, 8):
                    ws.cell(row=fila, column=col).alignment = Alignment(horizontal="center", vertical="center")
        finally:
            session.close()
        
        # Ajustar ancho de columnas
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 12
        ws.column_dimensions['F'].width = 12
        ws.column_dimensions['G'].width = 12
        
        wb.save(archivo)
