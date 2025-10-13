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
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QHeaderView
from ui.socio_page_ui import Ui_SocioPage  # el generado por pyside6-uic
import services.socio_service as socio_service
from utils.events import bus


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

        # Conectar tabla para que actualice los campos al seleccionar fila
        self.tabla_socios.itemSelectionChanged.connect(self.actualizar_campos)
        self.tabla_socios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Cargar tabla al inicio
        self.cargar_socios()
    
    def cargar_socios(self):
        socios = socio_service.listar_socios()
        self.tabla_socios.setRowCount(len(socios))
        self.tabla_socios.setColumnCount(7)
        self.tabla_socios.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Apellido1", "Apellido2", "Correo", "Teléfono", "Estado"]
        )

        for fila, socio in enumerate(socios):
            # Asumimos objetos ORM: acceder directamente a atributos
            # mostrar estado legible
            estado_display = socio.estado.name.capitalize() if hasattr(socio.estado, 'name') else str(socio.estado)
            values = [
                socio.id_socio,
                socio.nombre,
                socio.apellido1,
                socio.apellido2,
                socio.email,
                socio.telefono,
                estado_display,
            ]

            for col, dato in enumerate(values):
                self.tabla_socios.setItem(fila, col, QTableWidgetItem(str(dato)))

    # Validaciones
    def validar_correo(self, correo):
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(patron, correo)

    def validar_telefono(self, telefono):
        patron = r'^\d{9}$'
        return re.match(patron, telefono)
    
    def validar_campos(self, correo_existente_id=None, telefono_existente_id=None):
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
    def vaciar_campos(self):
        self.txt_nombre.clear()
        self.txt_apellido1.clear()
        self.txt_apellido2.clear()
        self.txt_email.clear()
        self.txt_telefono.clear()

    def actualizar_campos(self):
        fila = self.tabla_socios.currentRow()
        if fila >= 0:
            self.txt_nombre.setText(self.tabla_socios.item(fila, 1).text())
            self.txt_apellido1.setText(self.tabla_socios.item(fila, 2).text())
            self.txt_apellido2.setText(self.tabla_socios.item(fila, 3).text())
            self.txt_email.setText(self.tabla_socios.item(fila, 4).text())
            self.txt_telefono.setText(self.tabla_socios.item(fila, 5).text())
    
    def normalizar_campos(self):
        nombre = self.txt_nombre.text().strip().title()         # .strip() para eliminar espacios al inicio y al final 
        apellido1 = self.txt_apellido1.text().strip().title()   # .title() para poner la primera letra en mayúscula y el resto en minúscula
        apellido2 = self.txt_apellido2.text().strip().title()
        correo = self.txt_email.text().strip().lower()
        telefono = ''.join(filter(str.isdigit, self.txt_telefono.text().strip())) # dejar solo los números en el teléfono, eliminando guiones o espacios
        return nombre, apellido1, apellido2, correo, telefono

    # CRUD
    def insertar(self):
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

    def modificar(self):
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

    def desactivar_socio(self):
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

    def activar_socio(self):
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
