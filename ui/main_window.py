"""Ventana principal de la aplicación Club de Pádel.

Gestiona la navegación entre las diferentes páginas (Socios, Pistas,
Reservas, Pagos, Configuración) y proporciona un diseño responsive
que se ajusta dinámicamente al tamaño de la ventana.
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QSizePolicy, QHBoxLayout
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QPixmap, QIcon
from ui.main_window_ui import Ui_MainWindow
from ui.widgets.configuracion_page_widget import ConfiguracionPage
from ui.widgets.socio_page_widget import SocioPage
from ui.widgets.pista_page_widget import PistaPage
from ui.widgets.reserva_page_widget import ReservaPage
from ui.widgets.pago_page_widget import PagoPage
import recursos_rc



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Cargar y aplicar hoja de estilos
        style_file = QFile("ui/styles/style.qss")
        if style_file.open(QFile.ReadOnly):
            self.setStyleSheet(str(style_file.readAll(), encoding="utf-8"))

        # Cargar y establecer icono de la aplicación
        self.setWindowIcon(QIcon("ui/icons/aplicacion.ico"))
        
        # Cargar logo en el menú lateral
        logo_pixmap = QPixmap("ui/icons/aplicacion.ico")
        if not logo_pixmap.isNull():
            self.lbl_logo.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.lbl_logo.setText("[Logo]")

        # Conectar widgets a páginas del QStackedWidget
        self.socio_page = SocioPage()
        self.stackedWidget.insertWidget(1, self.socio_page)
        self.pista_page = PistaPage()
        self.stackedWidget.insertWidget(2, self.pista_page)
        self.pago_page = PagoPage()
        self.stackedWidget.insertWidget(3, self.pago_page)
        self.reserva_page = ReservaPage()
        self.stackedWidget.insertWidget(4, self.reserva_page) 
        self.configuracion_page = ConfiguracionPage()
        self.stackedWidget.insertWidget(5, self.configuracion_page)         

        # Conectar botones a páginas del QStackedWidget
        self.btn_inicio.clicked.connect(lambda: self._cambiar_pagina(0))
        self.btn_socios.clicked.connect(lambda: self._cambiar_pagina(1))
        self.btn_pistas.clicked.connect(lambda: self._cambiar_pagina(2))
        self.btn_pagos.clicked.connect(lambda: self._cambiar_pagina(3))
        self.btn_reservas.clicked.connect(lambda: self._cambiar_pagina(4))
        self.btn_configuracion.clicked.connect(lambda: self._cambiar_pagina(5))
        self.btn_salir.clicked.connect(QApplication.quit)

        # Configuración inicial
        self.stackedWidget.setCurrentIndex(0)
        self.lbl_bienvenido.setText("Bienvenido al Club de Pádel")
        
        # Cargar imagen de inicio
        self.pixmap_original = QPixmap("ui/icons/ImagenInicio.png")
        self.ultimo_ancho_imagen = 0  # Para controlar rescalados
        if not self.pixmap_original.isNull():
            self.lbl_imagen.setScaledContents(False)
            self.lbl_imagen.setAlignment(Qt.AlignCenter)
        else:
            self.lbl_imagen.setText("[Imagen no encontrada]")
        
        # Configurar responsividad
        self._configurar_responsive()
        
        # Ajustar imagen después de que se configure la UI
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._ajustar_imagen_inicio)
    
    def _configurar_responsive(self) -> None:
        """Configura la ventana y sus widgets para ser responsive."""
        # Iniciar maximizado
        self.showMaximized()
        
        # Configurar sizePolicy para que se expandan
        self.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stackedWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.groupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        # Conectar evento de resize para ajustar geometría dinámicamente
        self.resizeEvent = self._on_window_resized
    
    def _on_window_resized(self, event) -> None:
        """Ajusta la geometría de widgets al redimensionar la ventana."""
        if not hasattr(self, 'centralwidget'):
            return
        
        width = self.centralwidget.width()
        height = self.centralwidget.height()
        
        # Ancho lateral: 160px
        sidebar_width = 160
        
        # Posicionar sidebar (solo escala verticalmente)
        self.groupBox.setGeometry(10, 10, sidebar_width, height - 20)
        
        # Posicionar stackedWidget (escala horizontalmente - ocupa todo el espacio restante)
        stacked_x = sidebar_width + 20
        stacked_width = width - stacked_x - 10
        self.stackedWidget.setGeometry(stacked_x, 10, stacked_width, height - 20)
        
        # Mantener tamaño de botones (131 x 31)
        btn_width = 131
        btn_height = 31
        
        # Centrar botones horizontalmente en el sidebar
        btn_x = (sidebar_width - btn_width) // 2
        
        # Posicionar botones principales de arriba hacia abajo
        y_pos = 117
        for btn in [self.btn_inicio, self.btn_socios, self.btn_pistas, 
                   self.btn_pagos, self.btn_reservas]:
            btn.setGeometry(btn_x, y_pos, btn_width, btn_height)
            y_pos += btn_height + 10
        
        # Botón configuración encima de salir
        self.btn_configuracion.setGeometry(btn_x, height - 2 * btn_height - 40, btn_width, btn_height)
        
        # Botón salir al final
        self.btn_salir.setGeometry(btn_x, height - btn_height - 30, btn_width, btn_height)
        
        # Si estamos en la página de inicio, ajustar la imagen
        if self.stackedWidget.currentIndex() == 0:
            self._ajustar_imagen_inicio()

    def _actualizar_boton_activo(self, indice: int) -> None:
        """Actualiza el estilo del botón activo según la página actual.
        
        Args:
            indice (int): Índice de la página en el stackedWidget.
        """
        # Lista de botones y sus índices
        botones = {
            0: self.btn_inicio,
            1: self.btn_socios,
            2: self.btn_pistas,
            3: self.btn_pagos,
            4: self.btn_reservas,
            5: self.btn_configuracion
        }
        
        # Limpiar el atributo active de todos los botones
        for btn in botones.values():
            btn.setProperty("active", False)
        
        # Establecer el botón actual como activo
        if indice in botones:
            botones[indice].setProperty("active", True)
        
        # Forzar actualización de estilos
        for btn in botones.values():
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    
    def _cambiar_pagina(self, indice: int) -> None:
        """Cambia a la página indicada y limpia los campos de formularios.
        
        Args:
            indice (int): Índice de la página en el stackedWidget.
        """
        # Limpiar campos de la página anterior
        self._limpiar_pagina_actual()
        
        # Cambiar a la nueva página
        self.stackedWidget.setCurrentIndex(indice)
        
        # Actualizar botones activos
        self._actualizar_boton_activo(indice)
        
        # Si vamos a la página de inicio, escalar la imagen para que no tenga zoom
        if indice == 0 and hasattr(self, 'pixmap_original'):
            self._ajustar_imagen_inicio()

    def _ajustar_imagen_inicio(self) -> None:
        """Escala la imagen dinámicamente según el tamaño disponible."""
        if not hasattr(self, 'pixmap_original') or self.pixmap_original.isNull():
            return
        
        # Obtener tamaño disponible del stackedWidget
        stacked_width = self.stackedWidget.width()
        stacked_height = self.stackedWidget.height()
        
        # Evitar rescalar si el tamaño no ha cambiado significativamente
        if abs(stacked_width - self.ultimo_ancho_imagen) < 10:
            return
        
        self.ultimo_ancho_imagen = stacked_width
        
        # Dejar margen
        max_width = stacked_width - 80
        max_height = stacked_height - 80
        
        if max_width <= 0 or max_height <= 0:
            return
        
        # Obtener dimensiones originales
        orig_width = self.pixmap_original.width()
        orig_height = self.pixmap_original.height()
        
        # Calcular factor de escala
        scale_w = max_width / orig_width
        scale_h = max_height / orig_height
        
        # Usar el menor para que encaje completamente
        scale = min(scale_w, scale_h)
        
        # Nunca amplificar (máximo 1.0)
        scale = min(scale, 1.0)
        
        if scale < 0.1:
            return
        
        # Calcular nuevas dimensiones
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)
        
        # Escalar la imagen
        scaled_pixmap = self.pixmap_original.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.lbl_imagen.setPixmap(scaled_pixmap)

    def _limpiar_pagina_actual(self) -> None:
        """Limpia los campos de la página actual si tiene un método vaciar_campos."""
        indice_actual = self.stackedWidget.currentIndex()
        
        if indice_actual == 1:  # Página de Socios
            self.socio_page.vaciar_campos()
        elif indice_actual == 2:  # Página de Pistas
            self.pista_page.vaciar_campos()
        elif indice_actual == 3:  # Página de Pagos
            self.pago_page.vaciar_campos()
        elif indice_actual == 4:  # Página de Reservas
            self.reserva_page.vaciar_campos()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
