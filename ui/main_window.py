import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import QFile
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
        self.btn_inicio.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_socios.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btn_pistas.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.btn_pagos.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.btn_reservas.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(4))
        self.btn_configuracion.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(5))
        self.btn_salir.clicked.connect(QApplication.quit)

        # Configuración inicial
        self.stackedWidget.setCurrentIndex(0)
        self.lbl_bienvenido.setText("Bienvenido al Club de Pádel")
        self.lbl_imagen.setText("[Aquí podría ir una imagen]")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
