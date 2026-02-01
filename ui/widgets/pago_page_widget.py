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
- Las fechas se muestran con `utils.helpers.formatear_fecha()` → DD/MM/YYYY.

Ejemplo de uso (desde MainWindow):
        main_win.pago_page.cargar_para_reserva(123)
        main_win.stackedWidget.setCurrentIndex(3)

Notas:
- Esta clase está diseñada para usarse dentro de la ventana principal generada
    por `main_window.py` y asume que los widgets (botones, combos) existen con
    los nombres generados por Qt Designer.
"""

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QCompleter, QHeaderView, QFileDialog, QPushButton, QLabel, QHBoxLayout, QComboBox
from PySide6.QtCore import Qt, QDate
from datetime import date
from utils.helpers import formatear_fecha
import calendar

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
    - utils.helpers.formatear_fecha para formatear fechas.
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
        
        # Mes y año actual para filtrado
        hoy = date.today()
        self.mes_actual = hoy.month
        self.anio_actual = hoy.year
        
        # Estado actual para filtrado
        self.estado_actual = None

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
        self.btn_limpiar.clicked.connect(self.vaciar_campos)
        
        # Conectar tabla para que actualice los campos al seleccionar fila
        self.tabla_pagos.itemSelectionChanged.connect(self.actualizar_campos)

        # Conectar barra de búsqueda para filtrar en tiempo real
        self.txt_buscar.textChanged.connect(self.filtrar_tabla)

        # Guardar lista de pagos original para filtrado
        self.pagos_originales = []
        
        # Crear controles de navegación de mes
        self._crear_controles_navegacion_mes()

        # cargar tabla
        self.cargar_pagos()

        # Conectar evento de resize para responsividad
        self.resizeEvent = self._on_redimensionar_pagina

    def _on_redimensionar_pagina(self, event) -> None:
        """Ajusta la geometría de widgets al redimensionar la página."""
        width = self.width()
        height = self.height()
        
        # Margen general
        margin = 20
        
        # Label "Pagos" (título)
        self.label_pagos.setGeometry(margin, margin, 200, 31)
        
        # GroupBox de botones: ancho completo, alto fijo
        gb_y = margin + 35
        gb_height = 41
        self.groupBox.setGeometry(margin, gb_y, width - 2*margin, gb_height)
        
        # GridLayoutWidget (campos de entrada): ancho completo, alto fijo
        grid_y = gb_y + gb_height + 10
        grid_height = 71
        if hasattr(self, 'gridLayoutWidget'):
            self.gridLayoutWidget.setGeometry(margin, grid_y, width - 2*margin, grid_height)
        
        # Botón Limpiar y GridLayoutWidget_2 (búsqueda)
        search_y = grid_y + grid_height + 10
        search_height = 35
        if hasattr(self, 'btn_limpiar'):
            self.btn_limpiar.setGeometry(margin, search_y, 71, search_height)
        if hasattr(self, 'gridLayoutWidget_2'):
            self.gridLayoutWidget_2.setGeometry(margin + 90, search_y, width - 2*margin - 90, search_height)
        
        # Controles de navegación de mes
        nav_y = search_y + search_height + 10
        nav_height = 35
        if hasattr(self, 'mes_nav_widget'):
            self.mes_nav_widget.setGeometry(margin, nav_y, width - 2*margin, nav_height)
        
        # Tabla (resto del espacio disponible)
        table_y = nav_y + nav_height + 10
        table_height = height - table_y - margin
        if hasattr(self, 'tabla_pagos'):
            self.tabla_pagos.setGeometry(margin, table_y, width - 2*margin, table_height)

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
    
    def _crear_controles_navegacion_mes(self) -> None:
        """Crea los controles de navegación de mes (botones anterior/siguiente y label)."""
        from PySide6.QtWidgets import QWidget
        
        # Widget contenedor para los controles
        self.mes_nav_widget = QWidget(self)
        layout = QHBoxLayout(self.mes_nav_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Botón mes anterior
        self.btn_mes_anterior = QPushButton("◀", self.mes_nav_widget)
        self.btn_mes_anterior.setFixedWidth(50)
        self.btn_mes_anterior.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.btn_mes_anterior.clicked.connect(self._mes_anterior)
        layout.addWidget(self.btn_mes_anterior)
        
        # Label con el mes y año actual
        self.lbl_mes_actual = QLabel(self.mes_nav_widget)
        self.lbl_mes_actual.setAlignment(Qt.AlignCenter)
        self.lbl_mes_actual.setStyleSheet("font-size: 14px; font-weight: bold;")
        self._actualizar_label_mes()
        layout.addWidget(self.lbl_mes_actual, 1)  # stretch=1 para que ocupe el espacio
        
        # Botón mes siguiente
        self.btn_mes_siguiente = QPushButton("▶", self.mes_nav_widget)
        self.btn_mes_siguiente.setFixedWidth(50)
        self.btn_mes_siguiente.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.btn_mes_siguiente.clicked.connect(self._mes_siguiente)
        layout.addWidget(self.btn_mes_siguiente)
        
        # Botón "Hoy" para volver al mes actual
        self.btn_hoy = QPushButton("Hoy", self.mes_nav_widget)
        self.btn_hoy.setFixedWidth(60)
        self.btn_hoy.clicked.connect(self._ir_a_hoy)
        layout.addWidget(self.btn_hoy)
        
        # Separador
        separador = QLabel("|", self.mes_nav_widget)
        separador.setStyleSheet("color: #888; margin: 0 5px;")
        layout.addWidget(separador)
        
        # Combo de estado
        self.cmb_estado = QComboBox(self.mes_nav_widget)
        self.cmb_estado.addItem("Todos", None)
        from models.orm_models import PagoEstado
        self.cmb_estado.addItem("Pagado", PagoEstado.PAGADO)
        self.cmb_estado.addItem("Anulado", PagoEstado.ANULADO)
        self.cmb_estado.setFixedWidth(120)
        self.cmb_estado.currentIndexChanged.connect(self._on_estado_changed)
        layout.addWidget(self.cmb_estado)
    
    def _actualizar_label_mes(self) -> None:
        """Actualiza el label con el nombre del mes y año actual."""
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        mes_nombre = meses[self.mes_actual - 1]
        self.lbl_mes_actual.setText(f"{mes_nombre} {self.anio_actual}")
    
    def _mes_anterior(self) -> None:
        """Navega al mes anterior."""
        if self.mes_actual == 1:
            self.mes_actual = 12
            self.anio_actual -= 1
        else:
            self.mes_actual -= 1
        self._actualizar_label_mes()
        self.cargar_pagos()
    
    def _mes_siguiente(self) -> None:
        """Navega al mes siguiente."""
        if self.mes_actual == 12:
            self.mes_actual = 1
            self.anio_actual += 1
        else:
            self.mes_actual += 1
        self._actualizar_label_mes()
        self.cargar_pagos()
    
    def _ir_a_hoy(self) -> None:
        """Vuelve al mes y año actuales."""
        hoy = date.today()
        self.mes_actual = hoy.month
        self.anio_actual = hoy.year
        self._actualizar_label_mes()
        self.cargar_pagos()
    
    def _on_estado_changed(self) -> None:
        """Recarga la tabla cuando cambia el estado seleccionado."""
        self.estado_actual = self.cmb_estado.currentData()
        self.cargar_pagos()

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
        descripcion = f"Reserva {pista_nombre} — {formatear_fecha(r.fecha)} {hora}"
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
        
        Obtiene los pagos del mes y año actuales de la base de datos y actualiza la tabla con sus datos.
        Utiliza mapeos internos para evitar acceso lazy loading a relaciones.
        """
        pagos = listar_pagos(mes=self.mes_actual, anio=self.anio_actual, estado=self.estado_actual)
        self.pagos_originales = pagos  # Guardar para filtrado
        self.tabla_pagos.setRowCount(len(pagos))
        self.tabla_pagos.setColumnCount(5)
        self.tabla_pagos.setHorizontalHeaderLabels(["Socio", "Importe", "Fecha", "Tipo", "Estado"])

        # crear mapa id->display para evitar lazy load
        socios = listar_socios()
        mapa = {s.id_socio: f"{s.nombre} {s.apellido1} ({s.email})" for s in socios}

        for fila, p in enumerate(pagos):
            tipo_display = p.tipo.name.capitalize() if hasattr(p.tipo, 'name') else str(p.tipo)
            estado_display = p.estado.name.capitalize() if hasattr(p.estado, 'name') else str(p.estado)
            values = [
                mapa.get(p.id_socio, str(p.id_socio)),
                f"{p.importe:.2f}",
                formatear_fecha(p.fecha_pago),
                tipo_display,
                estado_display,
            ]
            for col, dato in enumerate(values):
                item = QTableWidgetItem(str(dato))
                # Almacenar el ID del pago en el primer item como dato oculto
                if col == 0:
                    item.setData(Qt.UserRole, p.id_pago)
                self.tabla_pagos.setItem(fila, col, item)

        # ajustar tamaño de columnas
        header = self.tabla_pagos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5):
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
        
        # Obtener el ID del pago almacenado en el atributo del widget de la tabla
        item0 = self.tabla_pagos.item(fila, 0)
        if item0 is None:
            return
        
        # El ID está almacenado en los datos del item
        id_pago_data = item0.data(Qt.UserRole)
        if id_pago_data is None:
            return
        
        try:
            id_pago = int(id_pago_data)
            
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
                        concepto = f"Reserva {pista_nombre} — {formatear_fecha(reserva.fecha)} {hora}"
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
        
        # Obtener el ID del pago almacenado en Qt.UserRole
        id_pago_data = item0.data(Qt.UserRole)
        if id_pago_data is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID del pago")
            return
        id_pago = int(id_pago_data)
        
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
        # Obtener el ID del pago almacenado en Qt.UserRole
        id_pago_data = item0.data(Qt.UserRole)
        if id_pago_data is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID del pago")
            return
        id_pago = int(id_pago_data)
        confirm = QMessageBox.question(
            self,
            "Confirmar anulación",
            "¿Seguro que quieres anular este pago?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return
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
        cabecera = ["Socio", "Fecha", "Importe (€)", "Tipo", "Estado", "Concepto"]
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
                elif pago.tipo == PagoTipo.RESERVA:
                    # Para reserva: mostrar el mismo concepto que en cargar_para_reserva
                    pago_reserva = pago.pago_reserva
                    if pago_reserva:
                        reserva = pago_reserva.reserva if hasattr(pago_reserva, 'reserva') else None
                        if reserva:
                            pistas = listar_pistas()
                            mapa_pistas = {p.id_pista: p.nombre for p in pistas}
                            pista_nombre = mapa_pistas.get(reserva.id_pista, str(reserva.id_pista))
                            hora = ''
                            try:
                                hora = reserva.hora_inicio.strftime('%H:%M') if hasattr(reserva.hora_inicio, 'strftime') else ''
                            except Exception:
                                hora = ''
                            concepto = f"Reserva {pista_nombre} — {formatear_fecha(reserva.fecha)} {hora}"
                        else:
                            concepto = str(pago_reserva.id_reserva)
                elif pago.tipo == PagoTipo.EXTRA:
                    pago_extra = session.query(PagoExtra).filter_by(id_pago=pago.id_pago).first()
                    concepto = pago_extra.concepto if pago_extra else ""
                
                estado_display = pago.estado.name.capitalize() if hasattr(pago.estado, 'name') else str(pago.estado)
                tipo_display = pago.tipo.name.capitalize() if hasattr(pago.tipo, 'name') else str(pago.tipo)
                
                # Obtener nombre del socio
                socio = pago.socio
                nombre_socio = f"{socio.nombre} {socio.apellido1}" if socio else ""
                
                fila = [
                    nombre_socio,
                    formatear_fecha(pago.fecha_pago),
                    f"{pago.importe:.2f}",
                    tipo_display,
                    estado_display,
                    concepto
                ]
                ws.append(fila)
        finally:
            session.close()
        
        # Ajustar ancho de columnas
        anchos = [20, 12, 15, 12, 12, 35]
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
        self.txt_buscar.clear()

    def filtrar_tabla(self) -> None:
        """Filtra la tabla de pagos según el texto ingresado en la barra de búsqueda.
        
        Busca el texto en la columna de Socio (nombre completo y email).
        La búsqueda es case-insensitive.
        """
        texto_busqueda = self.txt_buscar.text().lower().strip()
        
        if not texto_busqueda:
            # Si el campo de búsqueda está vacío, mostrar todos los pagos
            self.cargar_pagos()
            return
        
        # Crear mapa de socios para búsqueda
        socios = listar_socios()
        mapa_socios = {s.id_socio: f"{s.nombre} {s.apellido1} ({s.email})".lower() for s in socios}
        
        # Filtrar pagos según el texto de búsqueda en la columna de socio
        pagos_filtrados = []
        for pago in self.pagos_originales:
            nombre_socio = mapa_socios.get(pago.id_socio, "").lower()
            
            # Buscar en el nombre del socio
            if texto_busqueda in nombre_socio:
                pagos_filtrados.append(pago)
        
        # Actualizar tabla con pagos filtrados
        self.tabla_pagos.setRowCount(len(pagos_filtrados))
        self.tabla_pagos.setColumnCount(5)
        self.tabla_pagos.setHorizontalHeaderLabels(["Socio", "Importe", "Fecha", "Tipo", "Estado"])

        # crear mapa id->display para evitar lazy load
        socios = listar_socios()
        mapa = {s.id_socio: f"{s.nombre} {s.apellido1} ({s.email})" for s in socios}

        for fila, p in enumerate(pagos_filtrados):
            tipo_display = p.tipo.name.capitalize() if hasattr(p.tipo, 'name') else str(p.tipo)
            estado_display = p.estado.name.capitalize() if hasattr(p.estado, 'name') else str(p.estado)
            values = [
                mapa.get(p.id_socio, str(p.id_socio)),
                f"{p.importe:.2f}",
                formatear_fecha(p.fecha_pago),
                tipo_display,
                estado_display,
            ]

            for col, dato in enumerate(values):
                item = QTableWidgetItem(str(dato))
                # Almacenar el ID del pago en el primer item como dato oculto
                if col == 0:
                    item.setData(Qt.UserRole, p.id_pago)
                self.tabla_pagos.setItem(fila, col, item)

        # ajustar tamaño de columnas
        header = self.tabla_pagos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
