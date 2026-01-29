import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QSizePolicy, QHBoxLayout
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QPixmap
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
        pixmap = QPixmap("ui/icons/ImangenInicio.png")
        if not pixmap.isNull():
            # Escalar la imagen manteniendo la proporción
            scaled_pixmap = pixmap.scaledToHeight(600)
            self.lbl_imagen.setPixmap(scaled_pixmap)
            self.lbl_imagen.setAlignment(Qt.AlignCenter)
            self.lbl_imagen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        else:
            self.lbl_imagen.setText("[Imagen no encontrada]")
        
        # Configurar responsividad
        self._configurar_responsive()
    
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
        
        # Ancho lateral: ~12% del total (160px como mínimo)
        sidebar_width = max(160, int(width * 0.12))
        
        # Posicionar sidebar
        self.groupBox.setGeometry(10, 10, sidebar_width, height - 20)
        
        # Posicionar stackedWidget (resto del espacio disponible)
        stacked_x = sidebar_width + 20
        stacked_width = width - stacked_x - 10
        self.stackedWidget.setGeometry(stacked_x, 10, stacked_width, height - 20)
        
        # Mantener tamaño de botones fijo (131 x 31)
        btn_width = 131
        btn_height = 31
        
        # Centrar botones horizontalmente en el sidebar
        btn_x = (sidebar_width - btn_width) // 2
        
        # Posicionar botones de arriba hacia abajo
        y_pos = 20
        for btn in [self.btn_inicio, self.btn_socios, self.btn_pistas, 
                   self.btn_pagos, self.btn_reservas, self.btn_configuracion]:
            btn.setGeometry(btn_x, y_pos, btn_width, btn_height)
            y_pos += btn_height + 10
        
        # Botón salir al final, con el mismo espacio que el de inicio
        self.btn_salir.setGeometry(btn_x, height - btn_height - 30, btn_width, btn_height)

    def _cambiar_pagina(self, indice: int) -> None:
        """Cambia a la página indicada y limpia los campos de formularios.
        
        Args:
            indice (int): Índice de la página en el stackedWidget.
        """
        # Limpiar campos de la página anterior
        self._limpiar_pagina_actual()
        
        # Cambiar a la nueva página
        self.stackedWidget.setCurrentIndex(indice)

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
