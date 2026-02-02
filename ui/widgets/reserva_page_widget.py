"""Widget de gestión de Reservas.

Contiene la clase `ReservaPage` que permite listar reservas, crear/editar
y cancelar reservas, y navegar al flujo de pagos para una reserva seleccionada.

Formatos:
- Fechas: `utils.helpers.formatear_fecha()` → DD/MM/YYYY
- Horas: `utils.helpers.formatear_hora()` → HH:MM

Efectos secundarios:
- Se suscribe a `bus.socios_changed` y `bus.pistas_changed` para recargar autocompletados.
- Utiliza servicios en `services.reserva_service`, `services.socio_service` y `services.pista_service`.

API pública:
- cargar_reservas(): recarga la tabla de reservas.
- insertar()/modificar()/cancelar(): CRUD de reservas.
- ir_a_pagos(): navega a la página de pagos precargando la reserva.
"""

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QCompleter, QHeaderView, QFileDialog, QPushButton, QLabel, QHBoxLayout, QComboBox, QStyledItemDelegate, QStyleOptionViewItem, QAbstractItemView
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QColor, QPainter, QPalette
from datetime import date, time, datetime, timedelta
from utils.helpers import formatear_fecha, formatear_hora
import calendar
from ui.reserva_page_ui import Ui_reserva_page
from services.reserva_service import insertar_reserva, listar_reservas, obtener_reserva_por_id, actualizar_reserva, cancelar_reserva, hay_solapamiento
from services.pista_service import listar_pistas
from services.socio_service import listar_socios
from utils.events import bus
from models.orm_models import ReservaEstado
from models.orm import SessionLocal
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from ui.widgets.filtros_dialog import FiltrosReservasDialog


class ColoredComboBoxDelegate(QStyledItemDelegate):
    """Delegado personalizado para mostrar colores en items de QComboBox.
    
    Necesario en macOS donde el estilo nativo puede ignorar los colores
    establecidos con setItemData(Qt.ForegroundRole).
    """
    def paint(self, painter, option, index):
        """Pinta el item del combo con el color personalizado si está definido."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        color = index.data(Qt.ForegroundRole)
        if color and isinstance(color, QColor):
            opt.palette.setColor(QPalette.Text, color)
            opt.palette.setColor(QPalette.HighlightedText, color)

        super().paint(painter, opt, index)


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
        
        # Mes y año actual para filtrado
        hoy = date.today()
        self.mes_actual = hoy.month
        self.anio_actual = hoy.year
        
        # Estado actual para filtrado
        self.estado_actual = None
        
        # cuando se cambia la hora de inicio, ajustar hora fin
        self.timeEdit.timeChanged.connect(self.suma_tiempo)
        # actualizar disponibilidad de pistas al cambiar fecha u horas
        self.dateEdit.dateChanged.connect(self.actualizar_disponibilidad_pistas)
        self.timeEdit.timeChanged.connect(self.actualizar_disponibilidad_pistas)
        self.timeEdit_2.timeChanged.connect(self.actualizar_disponibilidad_pistas)
        # refrescar cuadrante al cambiar fecha
        self.dateEdit.dateChanged.connect(self._refrescar_cuadrante)

        # Conectar botones
        self.btn_agregar.clicked.connect(self.insertar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_baja.clicked.connect(self.cancelar)
        self.btn_pagar.clicked.connect(self.ir_a_pagos)
        self.btn_listar.clicked.connect(self.generar_listado)
        self.btn_limpiar.clicked.connect(self.vaciar_campos)

        # Conectar tabla
        self.tabla_reservas.itemSelectionChanged.connect(self.actualizar_campos)
        
        # Deshabilitar edición directa en la tabla
        self.tabla_reservas.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Configurar cuadrante de disponibilidad
        if hasattr(self, 'tabla_cuadrante'):
            self.tabla_cuadrante.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tabla_cuadrante.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.tabla_cuadrante.setSelectionMode(QAbstractItemView.SingleSelection)
            self.tabla_cuadrante.itemSelectionChanged.connect(self._on_cuadrante_seleccion)
            header_h = self.tabla_cuadrante.horizontalHeader()
            header_h.setSectionResizeMode(QHeaderView.Fixed)
            header_h.setDefaultSectionSize(80)
            header_v = self.tabla_cuadrante.verticalHeader()
            header_v.setSectionResizeMode(QHeaderView.Fixed)
            header_v.setDefaultSectionSize(24)

        # Avisar si se selecciona una pista ocupada
        self.cmb_pista.currentIndexChanged.connect(self._avisar_si_pista_ocupada)

        # Conectar barra de búsqueda para filtrar en tiempo real
        self.txt_buscar.textChanged.connect(self.filtrar_tabla)

        # Guardar lista de reservas original para filtrado
        self.reservas_originales = []
        # Mapa de disponibilidad de pistas (id_pista -> bool)
        self.pistas_disponibilidad = {}

        # Establecer delegado personalizado para el combo de pistas (colores en macOS)
        self.cmb_pista.setItemDelegate(ColoredComboBoxDelegate(self.cmb_pista))

        # Inicializar campos
        self.cargar_pistas()
        self.cargar_socios()
        
        # Crear controles de navegación de mes
        self._crear_controles_navegacion_mes()
        
        # Crear controles de navegación de cuadrante
        self._crear_controles_navegacion_cuadrante()
        
        self.cargar_reservas()

        # Pintar disponibilidad inicial
        self.actualizar_disponibilidad_pistas()
        # Pintar cuadrante inicial
        self._refrescar_cuadrante()

        # Suscribirse a cambios globales para mantener autocompleters/combos actualizados
        bus.socios_changed.connect(self.cargar_socios)
        bus.pistas_changed.connect(self.cargar_pistas)

        # Conectar evento de resize para responsividad
        self.resizeEvent = self._on_redimensionar_pagina

    def _on_redimensionar_pagina(self, event) -> None:
        """Ajusta la geometría de widgets al redimensionar la página."""
        width = self.width()
        height = self.height()
        
        # Margen general
        margin = 20
        
        # Label "Reservas" (título)
        self.label_pistas.setGeometry(margin, margin, 200, 31)
        
        # GroupBox de botones: ancho completo, alto fijo
        gb_y = margin + 35
        gb_height = 41
        self.groupBox.setGeometry(margin, gb_y, width - 2*margin, gb_height)

        # Botones de acciones: calcular anchos para que no se corte el texto
        if hasattr(self, "btn_agregar"):
            botones = [
                self.btn_agregar,
                self.btn_modificar,
                self.btn_baja,
                self.btn_pagar,
                self.btn_listar,
            ]
            spacing = 8
            min_width = 130
            padding = 28
            fm = self.btn_agregar.fontMetrics()
            max_text = max(fm.horizontalAdvance(b.text()) for b in botones)
            preferred = max(min_width, max_text + padding)
            available = self.groupBox.width()
            max_width = max(1, (available - spacing * (len(botones) - 1)) // len(botones))
            button_width = min(preferred, max_width)
            x = 0
            for btn in botones:
                btn.setGeometry(x, 0, button_width, gb_height)
                x += button_width + spacing
        
        # GridLayoutWidget (campos de entrada): ancho completo, alto fijo
        grid_y = gb_y + gb_height + 10
        grid_height = 71
        if hasattr(self, 'gridLayoutWidget'):
            self.gridLayoutWidget.setGeometry(margin, grid_y, width - 2*margin, grid_height)
        
        # Botón Limpiar y GridLayoutWidget_2 (búsqueda)
        search_y = grid_y + grid_height + 10
        search_height = 35
        if hasattr(self, 'btn_limpiar'):
            limpiar_width = max(100, self.btn_limpiar.fontMetrics().horizontalAdvance(self.btn_limpiar.text()) + 24)
            self.btn_limpiar.setGeometry(margin, search_y, limpiar_width, search_height)
        if hasattr(self, 'gridLayoutWidget_2'):
            gap = 10
            search_x = margin + limpiar_width + gap
            search_w = width - 2*margin - limpiar_width - gap
            self.gridLayoutWidget_2.setGeometry(search_x, search_y, max(0, search_w), search_height)
        
        # Controles de navegación de mes
        nav_y = search_y + search_height + 10
        nav_height = 35

        # Anchos de tablas (reservas + cuadrante)
        total_width = width - 2 * margin
        gap = 10
        cuadrante_width = max(320, int(total_width * 0.33))
        reservas_width = max(300, total_width - cuadrante_width - gap)

        if hasattr(self, 'mes_nav_widget'):
            self.mes_nav_widget.setGeometry(margin, nav_y, reservas_width, nav_height)

        # Controles de navegación del cuadrante en el hueco superior
        if hasattr(self, 'cuadrante_nav_widget'):
            label_x = margin + reservas_width + gap
            label_y = nav_y
            self.cuadrante_nav_widget.setGeometry(label_x, label_y, cuadrante_width, nav_height)
            self._actualizar_label_cuadrante()

        # Tablas (reservas + cuadrante)
        table_y = nav_y + nav_height + 10
        # Ajustar posición y altura de tablas
        table_height = height - table_y - margin
        cuadrante_y = table_y
        cuadrante_height = table_height

        self.tabla_reservas.setGeometry(margin, table_y, reservas_width, table_height)
        if hasattr(self, 'tabla_cuadrante'):
            cuadrante_x = margin + reservas_width + gap
            self.tabla_cuadrante.setGeometry(cuadrante_x, cuadrante_y, cuadrante_width, cuadrante_height)

    def cargar_pistas(self) -> None:
        """Recarga la lista de pistas en el combo y crea mapeos internos.
        
        Obtiene todas las pistas activas del servicio, carga el combo de pistas y
        crea un mapa interno para acceso rápido sin lazy loading.
        """
        from models.orm_models import PistaEstado
        pistas = listar_pistas(estado=PistaEstado.ACTIVA)
        self.cmb_pista.clear()
        for p in pistas:
            # mostrar nombre, almacenar id en data
            self.cmb_pista.addItem(p.nombre, p.id_pista)
        # no seleccionar ninguna pista por defecto
        self.cmb_pista.setCurrentIndex(-1)
        # mapa id -> nombre para usar en la tabla sin lazy-loading
        # Incluir todas las pistas para mostrar en la tabla aunque sean inactivas
        todas_pistas = listar_pistas()
        self.mapa_pistas = {p.id_pista: p.nombre for p in todas_pistas}

        # Refrescar colores de disponibilidad
        self.actualizar_disponibilidad_pistas()
        # Refrescar cuadrante
        self._refrescar_cuadrante()

    def actualizar_disponibilidad_pistas(self) -> None:
        """Actualiza el color de las pistas según disponibilidad.

        Verde si está disponible, rojo si está ocupada para la franja seleccionada.
        """
        fecha_qdate = self.dateEdit.date()
        fecha_py = date(fecha_qdate.year(), fecha_qdate.month(), fecha_qdate.day())

        hi_q = self.timeEdit.time()
        hf_q = self.timeEdit_2.time()
        hi_py = time(hi_q.hour(), hi_q.minute())
        hf_py = time(hf_q.hour(), hf_q.minute())

        # Si no hay rango válido, limpiar colores
        if hf_py <= hi_py:
            for i in range(self.cmb_pista.count()):
                self.cmb_pista.setItemData(i, None, Qt.ForegroundRole)
            self.pistas_disponibilidad = {}
            return

        # Validar horario de apertura del club
        from utils.settings import get_horario_apertura
        apertura, cierre = get_horario_apertura()
        fuera_horario = hi_py < apertura or hf_py > cierre

        self.pistas_disponibilidad = {}
        for i in range(self.cmb_pista.count()):
            id_pista = self.cmb_pista.itemData(i)
            if id_pista is None:
                continue
            ocupada = fuera_horario or hay_solapamiento(id_pista, fecha_py, hi_py, hf_py)
            disponible = not ocupada
            self.pistas_disponibilidad[id_pista] = disponible
            color = QColor("#2E7D32") if disponible else QColor("#C62828")
            self.cmb_pista.setItemData(i, color, Qt.ForegroundRole)

    def _construir_slots_cuadrante(self) -> list[tuple[time, time]]:
        """Construye las franjas horarias para el cuadrante según configuración."""
        from utils.settings import get_horario_apertura, get_duracion_reserva

        apertura, cierre = get_horario_apertura()
        dur_min = get_duracion_reserva()
        slots: list[tuple[time, time]] = []

        cur = datetime(2000, 1, 1, apertura.hour, apertura.minute)
        end = datetime(2000, 1, 1, cierre.hour, cierre.minute)
        delta = timedelta(minutes=dur_min)
        while cur + delta <= end:
            hi = cur.time()
            hf = (cur + delta).time()
            slots.append((hi, hf))
            cur += delta

        return slots

    def _refrescar_cuadrante(self) -> None:
        """Rellena el cuadrante con disponibilidad por pista y franja."""
        if not hasattr(self, 'tabla_cuadrante'):
            return

        from models.orm_models import PistaEstado

        pistas = listar_pistas(estado=PistaEstado.ACTIVA)
        slots = self._construir_slots_cuadrante()

        self.tabla_cuadrante.clear()
        self.tabla_cuadrante.setRowCount(len(slots))
        self.tabla_cuadrante.setColumnCount(len(pistas))

        self.tabla_cuadrante.setHorizontalHeaderLabels([p.nombre for p in pistas])
        self.tabla_cuadrante.setVerticalHeaderLabels([
            f"{h1.strftime('%H:%M')}-{h2.strftime('%H:%M')}" for h1, h2 in slots
        ])

        fecha_qdate = self.dateEdit.date()
        fecha_py = date(fecha_qdate.year(), fecha_qdate.month(), fecha_qdate.day())
        
        # Actualizar label del cuadrante
        self._actualizar_label_cuadrante()

        for row, (hi, hf) in enumerate(slots):
            for col, pista in enumerate(pistas):
                ocupada = hay_solapamiento(pista.id_pista, fecha_py, hi, hf)
                texto = "Ocupada" if ocupada else ""
                item = QTableWidgetItem(texto)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setData(Qt.UserRole, (pista.id_pista, hi, hf))
                item.setData(Qt.UserRole + 1, not ocupada)
                if ocupada:
                    # Mostrar texto "Ocupada" en rojo
                    from PySide6.QtGui import QBrush
                    item.setForeground(QBrush(QColor("#D32F2F")))
                    # Negrita para mayor visibilidad
                    from PySide6.QtGui import QFont
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_cuadrante.setItem(row, col, item)

    def _on_cuadrante_seleccion(self) -> None:
        """Sincroniza selección del cuadrante con pista y horario."""
        if not hasattr(self, 'tabla_cuadrante'):
            return

        item = self.tabla_cuadrante.currentItem()
        if item is None:
            return

        data = item.data(Qt.UserRole)
        disponible = item.data(Qt.UserRole + 1)
        if not data:
            return

        id_pista, hi, hf = data
        if disponible is False:
            QMessageBox.warning(self, "Aviso", "La franja seleccionada está ocupada.")
            return

        idx = self.cmb_pista.findData(id_pista)
        if idx >= 0:
            was_blocked = self.cmb_pista.blockSignals(True)
            self.cmb_pista.setCurrentIndex(idx)
            self.cmb_pista.blockSignals(was_blocked)

        self.timeEdit.setTime(QTime(hi.hour, hi.minute))
        self.timeEdit_2.setTime(QTime(hf.hour, hf.minute))
        self.txt_socio.clear()
        self.actualizar_disponibilidad_pistas()

    def _avisar_si_pista_ocupada(self) -> None:
        """Muestra aviso si el usuario selecciona una pista ocupada."""
        id_pista = self.cmb_pista.currentData()
        if id_pista is None:
            return
        disponible = self.pistas_disponibilidad.get(id_pista)
        if disponible is False:
            QMessageBox.warning(self, "Aviso", "La pista seleccionada está ocupada en ese horario.")

    def cargar_socios(self) -> None:
        """Recarga la lista de socios y configura el autocompletado.
        
        Obtiene solo los socios activos del servicio y configura un completer con autocompletado
        case-insensitive para el campo de socio. Crea mapeos internos para acceso rápido.
        """
        from models.orm_models import SocioEstado
        
        # Filtrar solo socios activos para el autocompletado
        socios_activos = [s for s in listar_socios() if s.estado == SocioEstado.ACTIVO]
        # Creamos un diccionario para mapear texto mostrado → id_socio
        self.mapa_socios = {
            f"{s.nombre} {s.apellido1} ({s.email})": s.id_socio for s in socios_activos
        }

        completer = QCompleter(list(self.mapa_socios.keys()))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)  # busca en cualquier parte del texto
        # cuando el usuario seleccione un elemento del completer guardamos el id
        completer.activated.connect(self._on_completer_activated)
        self.txt_socio.setCompleter(completer)

        # crear mapa inverso id -> display para buscar rápidamente
        # Incluir todos los socios para mostrar en la tabla aunque sean inactivos
        todos_socios = listar_socios()
        self.mapa_socios_id_to_display = {s.id_socio: f"{s.nombre} {s.apellido1} ({s.email})" for s in todos_socios}
    
    def _crear_controles_navegacion_cuadrante(self) -> None:
        """Crea los controles de navegación de día para el cuadrante."""
        from PySide6.QtWidgets import QWidget
        
        # Widget contenedor para los controles
        self.cuadrante_nav_widget = QWidget(self)
        layout = QHBoxLayout(self.cuadrante_nav_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Botón día anterior
        self.btn_dia_anterior = QPushButton("◀", self.cuadrante_nav_widget)
        self.btn_dia_anterior.setFixedWidth(50)
        self.btn_dia_anterior.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.btn_dia_anterior.clicked.connect(self._dia_anterior)
        layout.addWidget(self.btn_dia_anterior)
        
        # Label con la fecha del cuadrante
        self.lbl_cuadrante = QLabel(self.cuadrante_nav_widget)
        self.lbl_cuadrante.setAlignment(Qt.AlignCenter)
        self.lbl_cuadrante.setStyleSheet("font-size: 14px; font-weight: bold;")
        self._actualizar_label_cuadrante()
        layout.addWidget(self.lbl_cuadrante, 1)  # stretch=1 para que ocupe el espacio
        
        # Botón día siguiente
        self.btn_dia_siguiente = QPushButton("▶", self.cuadrante_nav_widget)
        self.btn_dia_siguiente.setFixedWidth(50)
        self.btn_dia_siguiente.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.btn_dia_siguiente.clicked.connect(self._dia_siguiente)
        layout.addWidget(self.btn_dia_siguiente)
    
    def _actualizar_label_cuadrante(self) -> None:
        """Actualiza el label del cuadrante con la fecha actual."""
        if hasattr(self, 'lbl_cuadrante'):
            fecha_qdate = self.dateEdit.date()
            fecha_py = date(fecha_qdate.year(), fecha_qdate.month(), fecha_qdate.day())
            self.lbl_cuadrante.setText(f"Cuadrante de disponibilidad - {formatear_fecha(fecha_py)}")
    
    def _dia_anterior(self) -> None:
        """Navega al día anterior."""
        fecha_actual = self.dateEdit.date()
        nueva_fecha = fecha_actual.addDays(-1)
        self.dateEdit.setDate(nueva_fecha)
        self._actualizar_label_cuadrante()
        self._refrescar_cuadrante()
    
    def _dia_siguiente(self) -> None:
        """Navega al día siguiente."""
        fecha_actual = self.dateEdit.date()
        nueva_fecha = fecha_actual.addDays(1)
        self.dateEdit.setDate(nueva_fecha)
        self._actualizar_label_cuadrante()
        self._refrescar_cuadrante()
    
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
        from models.orm_models import ReservaEstado
        self.cmb_estado.addItem("Activa", ReservaEstado.ACTIVA)
        self.cmb_estado.addItem("Cancelada", ReservaEstado.CANCELADA)
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
        self.cargar_reservas()
    
    def _mes_siguiente(self) -> None:
        """Navega al mes siguiente."""
        if self.mes_actual == 12:
            self.mes_actual = 1
            self.anio_actual += 1
        else:
            self.mes_actual += 1
        self._actualizar_label_mes()
        self.cargar_reservas()
    
    def _ir_a_hoy(self) -> None:
        """Vuelve al mes y año actuales."""
        hoy = date.today()
        self.mes_actual = hoy.month
        self.anio_actual = hoy.year
        self._actualizar_label_mes()
        self.cargar_reservas()
    
    def _on_estado_changed(self) -> None:
        """Recarga la tabla cuando cambia el estado seleccionado."""
        self.estado_actual = self.cmb_estado.currentData()
        self.cargar_reservas()

    def cargar_reservas(self) -> None:
        """Recarga la tabla de reservas desde el servicio.
        
        Obtiene las reservas del mes y año actuales de la base de datos y actualiza la tabla con sus datos.
        Utiliza mapeos internos para evitar acceso lazy loading a relaciones.
        """
        reservas = listar_reservas(mes=self.mes_actual, anio=self.anio_actual, estado=self.estado_actual)
        self.reservas_originales = reservas
        self.tabla_reservas.setRowCount(len(reservas))
        # Definir siempre las columnas y las cabeceras para que se muestren aun sin filas
        self.tabla_reservas.setColumnCount(6)
        self.tabla_reservas.setHorizontalHeaderLabels(["Socio", "Pista", "Fecha", "Hora Inicio", "Hora Fin", "Estado"])

        for fila, r in enumerate(reservas):
            values = [
                # usar mapas para evitar lazy load: mostrar texto del socio (nombre + email)
                self.mapa_socios_id_to_display.get(r.id_socio, str(r.id_socio)),
                self.mapa_pistas.get(r.id_pista, str(r.id_pista)),
                # Mostrar fecha y horas con helpers centralizados
                formatear_fecha(r.fecha),
                formatear_hora(r.hora_inicio),
                formatear_hora(r.hora_fin),
                (r.estado.name.capitalize() if hasattr(r.estado, 'name') else str(r.estado))
            ]

            for col, dato in enumerate(values):
                item = QTableWidgetItem(str(dato))
                # Almacenar el ID de la reserva en el primer item como dato oculto
                if col == 0:
                    item.setData(Qt.UserRole, r.id_reserva)
                self.tabla_reservas.setItem(fila, col, item)

        # ajustar tamaño de columnas
        header = self.tabla_reservas.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in range(1, 6):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        
        # Refrescar cuadrante con los datos actuales
        self._refrescar_cuadrante()
    
    def actualizar_campos(self) -> None:
        """Carga los datos de la fila seleccionada en los campos del formulario.
        
        Lee la fila actualmente seleccionada en la tabla y rellena los campos de entrada
        con los datos de la reserva seleccionada.
        """
        fila = self.tabla_reservas.currentRow()
        if fila < 0:
            return

        # Obtener el ID de la reserva almacenado en el atributo del widget de la tabla
        item0 = self.tabla_reservas.item(fila, 0)
        if item0 is None:
            return
        # El ID está almacenado en los datos del item
        id_reserva_data = item0.data(Qt.UserRole)
        if id_reserva_data is not None:
            id_reserva = int(id_reserva_data)
        else:
            # Si no está en UserRole, intentar obtenerlo de otra forma
            return
        
        r = obtener_reserva_por_id(id_reserva)
        if r is None:
            return

        # Seleccionar pista en cmb_pista por id
        idx = self.cmb_pista.findData(r.id_pista)
        if idx >= 0:
            # Evitar aviso al cambiar selección desde la tabla
            was_blocked = self.cmb_pista.blockSignals(True)
            self.cmb_pista.setCurrentIndex(idx)
            self.cmb_pista.blockSignals(was_blocked)

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

    def validar_campos(self) -> tuple:
        """Valida que los campos del formulario cumplan con los requisitos.
        
        Verifica que haya una pista seleccionada, que exista un socio válido,
        y que la hora inicio sea anterior a la hora fin.
        
        Returns:
            tuple: (bool, str) - Tupla con éxito de validación y mensaje de error si aplica.
        """
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

    def _on_completer_activated(self, text: str) -> None:
        """Handler llamado cuando el usuario selecciona un elemento del completer.
        
        Args:
            text (str): Texto del elemento seleccionado del completer.
        """
        sid = self.mapa_socios.get(text)
        if sid:
            self.selected_socio_id = sid

    def _resolve_socio_id(self, text: str) -> int:
        """Resuelve el id del socio a partir del texto del campo.

        - Si el usuario seleccionó via completer, `self.selected_socio_id` estará fijado.
        - Si el texto coincide con una clave del mapa, devolvemos su id.
        - Si el texto es un entero (id), lo devolvemos.
        - En cualquier otro caso devolvemos None.
        
        Args:
            text (str): Texto del campo de socio.
        
        Returns:
            int: ID del socio si se resuelve, None en caso contrario.
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

    def suma_tiempo(self, qtime: QTime) -> None:
        """Al cambiar la hora de inicio, actualizar la hora fin según duración configurada.
        
        Args:
            qtime (QTime): Nueva hora de inicio seleccionada.
        """
        try:
            from utils.settings import get_duracion_reserva
            duracion_minutos = get_duracion_reserva()
            new_qt = qtime.addSecs(duracion_minutos * 60)
            # establecer la hora fin sin disparar loops (no desconectamos señales porque no hay handling recíproco)
            self.timeEdit_2.setTime(new_qt)
        except Exception:
            # no queremos que un fallo de UI rompa la app
            pass

    def vaciar_campos(self) -> None:
        """Restablece los campos del formulario de reserva al estado por defecto.

        - Limpia el campo de socio y resetea el id seleccionado.
        - Selecciona la primera pista del combo si existe.
        - Pone la fecha a hoy y las horas a valores por defecto.
        """
        self.txt_socio.clear()
        self.selected_socio_id = None
        # no seleccionar pista por defecto
        self.cmb_pista.setCurrentIndex(-1)
        # Fecha a hoy
        self.dateEdit.setDate(QDate.currentDate())
        # Horas a 00:00
        self.timeEdit.setTime(QTime(0, 0))
        self.timeEdit_2.setTime(QTime(0, 0))
        self.txt_buscar.clear()

    def filtrar_tabla(self) -> None:
        """Filtra la tabla de reservas según el texto del campo de búsqueda.
        
        Busca en la columna Socio (nombre + apellido + email) de forma case-insensitive.
        Si el campo está vacío, muestra todas las reservas.
        """
        texto_busqueda = self.txt_buscar.text().strip().lower()
        
        if not texto_busqueda:
            # Si no hay búsqueda, mostrar todas las reservas
            self.cargar_reservas()
            return
        
        # Filtrar reservas por el texto de búsqueda en la columna Socio
        reservas_filtradas = [
            r for r in self.reservas_originales
            if texto_busqueda in self.mapa_socios_id_to_display.get(r.id_socio, "").lower()
        ]
        
        # Actualizar tabla con resultados filtrados
        self.tabla_reservas.setRowCount(len(reservas_filtradas))
        self.tabla_reservas.setColumnCount(6)
        self.tabla_reservas.setHorizontalHeaderLabels(["Socio", "Pista", "Fecha", "Hora Inicio", "Hora Fin", "Estado"])
        
        for fila, r in enumerate(reservas_filtradas):
            values = [
                self.mapa_socios_id_to_display.get(r.id_socio, str(r.id_socio)),
                self.mapa_pistas.get(r.id_pista, str(r.id_pista)),
                formatear_fecha(r.fecha),
                formatear_hora(r.hora_inicio),
                formatear_hora(r.hora_fin),
                (r.estado.name.capitalize() if hasattr(r.estado, 'name') else str(r.estado))
            ]
            
            for col, dato in enumerate(values):
                item = QTableWidgetItem(str(dato))
                if col == 0:
                    item.setData(Qt.UserRole, r.id_reserva)
                self.tabla_reservas.setItem(fila, col, item)
        
        # ajustar tamaño de columnas
        header = self.tabla_reservas.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 6):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
            self.tabla_reservas.setColumnWidth(col, 120)

    def insertar(self) -> None:
        """Inserta una nueva reserva en la base de datos.
        
        Valida los campos, normaliza los datos y crea un nuevo registro de reserva.
        Luego recarga la tabla de reservas.
        """
        ok, msg = self.validar_campos()
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return

        id_pista = self.cmb_pista.currentData()
        
        # Validar que la pista esté activa
        from services.pista_service import obtener_pista_por_id
        from models.orm_models import PistaEstado
        pista = obtener_pista_por_id(id_pista)
        if pista is None or pista.estado != PistaEstado.ACTIVA:
            QMessageBox.warning(self, "Error", "La pista seleccionada no está activa")
            return
        
        # Para simplicidad usamos el texto de socio; servicio espera id_socio, pero
        # en este widget no resolvemos id desde nombre: se asume que el flujo de UI
        # usará ids. Aquí intentaremos interpretar un entero si se introdujo.
        socio_text = self.txt_socio.text().strip()
        id_socio = self._resolve_socio_id(socio_text)
        if id_socio is None:
            QMessageBox.warning(self, "Error", "Selecciona un socio válido del autocompletado")
            return
        
        # Validar que el socio esté activo
        from services.socio_service import obtener_socio_por_id
        from models.orm_models import SocioEstado
        socio = obtener_socio_por_id(id_socio)
        if socio is None or socio.estado != SocioEstado.ACTIVO:
            QMessageBox.warning(self, "Error", "El socio seleccionado no está activo")
            return

        fecha_qdate = self.dateEdit.date()
        fecha_py = date(fecha_qdate.year(), fecha_qdate.month(), fecha_qdate.day())
        
        hi_q = self.timeEdit.time()
        hf_q = self.timeEdit_2.time()
        hi_py = time(hi_q.hour(), hi_q.minute())
        hf_py = time(hf_q.hour(), hf_q.minute())
        
        # Validar que la fecha y hora no sean anteriores a ahora
        from datetime import datetime
        ahora = datetime.now()
        fecha_hora_reserva = datetime.combine(fecha_py, hi_py)
        if fecha_hora_reserva < ahora:
            QMessageBox.warning(self, "Error", "La reserva no puede ser anterior a la fecha y hora actual")
            return

        try:
            insertar_reserva(id_socio=id_socio, id_pista=id_pista, fecha=fecha_py, hora_inicio=hi_py, hora_fin=hf_py)
            QMessageBox.information(self, "Éxito", "Reserva insertada correctamente")
            self.vaciar_campos()
            self.cargar_reservas()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def modificar(self) -> None:
        """Actualiza los datos de la reserva seleccionada.
        
        Valida los campos, normaliza los datos y actualiza el registro de la reserva.
        Luego recarga la tabla de reservas.
        """
        fila = self.tabla_reservas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona una reserva para modificar")
            return
        item0 = self.tabla_reservas.item(fila, 0)
        if item0 is None:
            QMessageBox.warning(self, "Error", "Fila seleccionada inválida")
            return
        # Obtener el ID de la reserva almacenado en Qt.UserRole
        id_reserva_data = item0.data(Qt.UserRole)
        if id_reserva_data is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la reserva")
            return
        id_reserva = int(id_reserva_data)
        ok, msg = self.validar_campos()
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return

        id_pista = self.cmb_pista.currentData()
        
        # Validar que la pista esté activa
        from services.pista_service import obtener_pista_por_id
        from models.orm_models import PistaEstado
        pista = obtener_pista_por_id(id_pista)
        if pista is None or pista.estado != PistaEstado.ACTIVA:
            QMessageBox.warning(self, "Error", "La pista seleccionada no está activa")
            return
        
        socio_text = self.txt_socio.text().strip()
        id_socio = self._resolve_socio_id(socio_text)
        if id_socio is None:
            QMessageBox.warning(self, "Error", "Selecciona un socio válido del autocompletado")
            return
        
        # Validar que el socio esté activo
        from services.socio_service import obtener_socio_por_id
        from models.orm_models import SocioEstado
        socio = obtener_socio_por_id(id_socio)
        if socio is None or socio.estado != SocioEstado.ACTIVO:
            QMessageBox.warning(self, "Error", "El socio seleccionado no está activo")
            return

        fecha_qdate = self.dateEdit.date()
        fecha_py = date(fecha_qdate.year(), fecha_qdate.month(), fecha_qdate.day())
        
        hi_q = self.timeEdit.time()
        hf_q = self.timeEdit_2.time()
        hi_py = time(hi_q.hour(), hi_q.minute())
        hf_py = time(hf_q.hour(), hf_q.minute())
        
        # Validar que la fecha y hora no sean anteriores a ahora
        from datetime import datetime
        ahora = datetime.now()
        fecha_hora_reserva = datetime.combine(fecha_py, hi_py)
        if fecha_hora_reserva < ahora:
            QMessageBox.warning(self, "Error", "La reserva no puede ser anterior a la fecha y hora actual")
            return

        try:
            actualizar_reserva(id_reserva=id_reserva, id_socio=id_socio, id_pista=id_pista, fecha=fecha_py, hora_inicio=hi_py, hora_fin=hf_py)
            QMessageBox.information(self, "Éxito", "Reserva modificada correctamente")
            self.vaciar_campos()
            self.cargar_reservas()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def cancelar(self) -> None:
        """Marca la reserva seleccionada como cancelada.
        
        Cambia el estado de la reserva a CANCELADA. Luego recarga la tabla de reservas.
        """
        fila = self.tabla_reservas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona una reserva para cancelar")
            return
        item0 = self.tabla_reservas.item(fila, 0)
        if item0 is None:
            QMessageBox.warning(self, "Error", "Fila seleccionada inválida")
            return
        # Obtener el ID de la reserva almacenado en Qt.UserRole
        id_reserva_data = item0.data(Qt.UserRole)
        if id_reserva_data is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la reserva")
            return
        id_reserva = int(id_reserva_data)
        reserva = obtener_reserva_por_id(id_reserva)
        if reserva is None:
            QMessageBox.warning(self, "Error", "Reserva no encontrada")
            return
        if reserva.estado == ReservaEstado.CANCELADA:
            QMessageBox.information(self, "Aviso", "La reserva ya está cancelada")
            return
        confirm = QMessageBox.question(
            self,
            "Confirmar cancelación",
            "¿Seguro que quieres cancelar esta reserva?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return
        cancelar_reserva(id_reserva)
        QMessageBox.information(self, "Éxito", "Reserva cancelada")
        self.cargar_reservas()

    def ir_a_pagos(self) -> None:
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
        
        # Obtener el ID de la reserva almacenado en Qt.UserRole
        id_reserva_data = item0.data(Qt.UserRole)
        if id_reserva_data is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la reserva")
            return
        id_reserva = int(id_reserva_data)
        
        r = obtener_reserva_por_id(id_reserva)
        if r is None:
            QMessageBox.warning(self, "Error", "Reserva no encontrada")
            return
        
        # Validar que la reserva no esté cancelada
        from models.orm_models import ReservaEstado
        if r.estado == ReservaEstado.CANCELADA:
            QMessageBox.warning(self, "Error", "No se puede pagar una reserva cancelada")
            return
        
        # Validar que la reserva no esté ya pagada
        from models import orm
        session = orm.SessionLocal()
        try:
            from models.orm_models import PagoReserva, Pago, PagoEstado
            pago_reserva = session.query(PagoReserva).filter(PagoReserva.id_reserva == id_reserva).first()
            if pago_reserva is not None:
                # Verificar el estado del pago
                pago = session.query(Pago).filter(Pago.id_pago == pago_reserva.id_pago).first()
                if pago is not None and pago.estado == PagoEstado.PAGADO:
                    QMessageBox.information(self, "Información", "Esta reserva ya está pagada")
                    return
        finally:
            session.close()

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
            if hasattr(main_win, "_cambiar_pagina"):
                main_win._cambiar_pagina(3)
            else:
                main_win.stackedWidget.setCurrentIndex(3)
        except Exception:
            # fallback: intentar buscar método público
            pass

    def generar_listado(self) -> None:
        """Genera un listado de reservas en formato XLSX con filtros.
        
        Muestra un diálogo para seleccionar filtros (fechas y estado),
        solicita la ubicación del archivo y exporta los datos a Excel.
        """
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

    def _generar_xlsx_reservas(self, archivo: str, reservas: list) -> None:
        """Genera un archivo Excel con el listado de reservas con nombres de socio y pista.
        
        Args:
            archivo (str): Ruta del archivo XLSX a crear.
            reservas (list): Lista de objetos reserva a exportar.
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Reservas"
        
        # Definir encabezados
        headers = ["Socio", "Pista", "Fecha", "Hora Inicio", "Hora Fin", "Estado"]
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
                ws.cell(row=fila, column=1, value=f"{r.socio.nombre} {r.socio.apellido1}")
                ws.cell(row=fila, column=2, value=r.pista.nombre)
                ws.cell(row=fila, column=3, value=formatear_fecha(r.fecha))
                ws.cell(row=fila, column=4, value=formatear_hora(r.hora_inicio))
                ws.cell(row=fila, column=5, value=formatear_hora(r.hora_fin))
                ws.cell(row=fila, column=6, value=r.estado.name.capitalize())
                
                # Centrar celdas
                for col in range(1, 7):
                    ws.cell(row=fila, column=col).alignment = Alignment(horizontal="center", vertical="center")
        finally:
            session.close()
        
        # Ajustar ancho de columnas
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 12
        ws.column_dimensions['F'].width = 12
        
        wb.save(archivo)
