"""Widget de gestión de Pagos.

Este módulo contiene la clase `PagoPage`, que implementa la interfaz de usuario
para listar, insertar y anular pagos. Usa los servicios del paquete `services`
para persistencia y `utils.helpers` para formateo de fechas/horas.

Responsabilidades principales:
- Mostrar la lista de pagos (`cargar_pagos`).
- Permitir insertar pagos (cuota, reserva, extra) con `insertar()`.
- Soportar prefilling desde una reserva con `cargar_para_reserva(id_reserva)`.
- Anular pagos (cambiar estado a ANULADO) con `anular()`.

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

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QCompleter, QHeaderView
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

        # cargar tabla
        self.cargar_pagos()

    def _cargar_socios(self):
        socios = listar_socios()
        self.mapa_socios = {f"{s.nombre} {s.apellido1} ({s.email})": s.id_socio for s in socios}
        completer = QCompleter(list(self.mapa_socios.keys()))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.activated.connect(self._on_completer_activated)
        self.txt_socio.setCompleter(completer)
        self.selected_socio_id = None

    def _on_completer_activated(self, text: str):
        self.selected_socio_id = self.mapa_socios.get(text)

    def cargar_para_reserva(self, id_reserva: int):
        """Prefill the payment form using a reservation id.

        - Busca la reserva y coloca el socio relacionado en el autocompleter y campo.
        - Rellena el concepto con el id de la reserva y selecciona el tipo 'Reserva'.
        - Ajusta la fecha al día de la reserva.
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

        # concepto: descripción legible de la reserva
        # intentar obtener nombre de pista y hora
        pistas = listar_pistas()
        mapa_pistas = {p.id_pista: p.nombre for p in pistas}
        pista_nombre = mapa_pistas.get(r.id_pista, str(r.id_pista))
        hora = ''
        try:
            hora = r.hora_inicio.strftime('%H:%M') if hasattr(r.hora_inicio, 'strftime') else ''
        except Exception:
            hora = ''
        descripcion = f"Reserva Pista {pista_nombre} — {r.fecha.isoformat()} {hora}"
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

    def _on_tipo_changed(self, idx: int):
        """Si el tipo deja de ser 'Reserva', limpiamos la vinculación."""
        try:
            tipo_text = self.comboBox.currentText().lower()
        except Exception:
            tipo_text = ''
        if tipo_text != 'reserva' and self._linked_reserva_id is not None:
            self._clear_linked_reserva()

    def _on_concepto_edited(self, text: str):
        """Si el usuario edita el concepto manualmente, limpiamos la vinculación."""
        if self._linked_reserva_id is not None:
            self._clear_linked_reserva()

    def _clear_linked_reserva(self):
        self._linked_reserva_id = None
        try:
            self.txt_concepto.setReadOnly(False)
        except Exception:
            pass

    def cargar_pagos(self):
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

    def insertar(self):
        # Validaciones mínimas
        try:
            importe = float(self.txt_importe.text())
        except Exception:
            QMessageBox.warning(self, "Error", "Importe inválido")
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
                    insertar_pago_reserva(pago.id_pago, id_reserva=self._linked_reserva_id, concepto=concepto)
                else:
                    # Intentar interpretar el concepto como id de reserva; si falla, crear sin enlace
                    try:
                        id_res = int(concepto)
                        insertar_pago_reserva(pago.id_pago, id_reserva=id_res, concepto=None)
                    except Exception:
                        # No hay id de reserva: creamos el pago sin enlace a reserva
                        pass
            elif tipo == 'extra':
                insertar_pago_extra(pago.id_pago, concepto_extra=concepto)

            QMessageBox.information(self, "Éxito", "Pago insertado")
            self.cargar_pagos()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def modificar(self):
        QMessageBox.information(self, "Info", "Modificar pagos no implementado")

    def anular(self):
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

__all__ = ['PagoPage']
