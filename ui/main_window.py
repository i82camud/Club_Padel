import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui.main_window_ui import Ui_MainWindow
from ui.widgets.socio_page_widget import SocioPage
from ui.widgets.pista_page_widget import PistaPage


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Conectar widgets a páginas del QStackedWidget
        self.socio_page = SocioPage()
        self.stackedWidget.insertWidget(1, self.socio_page)
        self.pista_page = PistaPage()
        self.stackedWidget.insertWidget(2, self.pista_page)

        # Conectar botones a páginas del QStackedWidget
        self.btn_inicio.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_socios.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btn_pistas.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.btn_pagos.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.btn_reservas.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(4))
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
