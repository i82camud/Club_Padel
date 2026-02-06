# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGroupBox, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QStackedWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.ApplicationModal)
        MainWindow.resize(1280, 800)
        MainWindow.setContextMenuPolicy(Qt.NoContextMenu)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 10, 150, 771))
        self.lbl_logo = QLabel(self.groupBox)
        self.lbl_logo.setObjectName(u"lbl_logo")
        self.lbl_logo.setGeometry(QRect(25, 20, 100, 100))
        self.lbl_logo.setAlignment(Qt.AlignCenter)
        self.lbl_logo.setScaledContents(True)
        self.btn_inicio = QPushButton(self.groupBox)
        self.btn_inicio.setObjectName(u"btn_inicio")
        self.btn_inicio.setGeometry(QRect(10, 130, 131, 31))
        self.btn_inicio.setIconSize(QSize(16, 16))
        self.btn_inicio.setFlat(False)
        self.btn_socios = QPushButton(self.groupBox)
        self.btn_socios.setObjectName(u"btn_socios")
        self.btn_socios.setGeometry(QRect(10, 170, 131, 31))
        self.btn_pistas = QPushButton(self.groupBox)
        self.btn_pistas.setObjectName(u"btn_pistas")
        self.btn_pistas.setGeometry(QRect(10, 210, 131, 31))
        self.btn_pagos = QPushButton(self.groupBox)
        self.btn_pagos.setObjectName(u"btn_pagos")
        self.btn_pagos.setGeometry(QRect(10, 250, 131, 31))
        self.btn_reservas = QPushButton(self.groupBox)
        self.btn_reservas.setObjectName(u"btn_reservas")
        self.btn_reservas.setGeometry(QRect(10, 290, 131, 31))
        self.btn_salir = QPushButton(self.groupBox)
        self.btn_salir.setObjectName(u"btn_salir")
        self.btn_salir.setGeometry(QRect(10, 720, 131, 31))
        self.btn_salir.setIconSize(QSize(24, 24))
        self.btn_configuracion = QPushButton(self.groupBox)
        self.btn_configuracion.setObjectName(u"btn_configuracion")
        self.btn_configuracion.setGeometry(QRect(10, 680, 131, 31))
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(180, 10, 1080, 770))
        self.page_inicio = QWidget()
        self.page_inicio.setObjectName(u"page_inicio")
        self.verticalLayout = QVBoxLayout(self.page_inicio)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(54, 30, 30, 30)
        self.lbl_bienvenido = QLabel(self.page_inicio)
        self.lbl_bienvenido.setObjectName(u"lbl_bienvenido")

        self.verticalLayout.addWidget(self.lbl_bienvenido)

        self.lbl_imagen = QLabel(self.page_inicio)
        self.lbl_imagen.setObjectName(u"lbl_imagen")
        self.lbl_imagen.setScaledContents(False)
        self.lbl_imagen.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.lbl_imagen)

        self.stackedWidget.addWidget(self.page_inicio)
        self.page_socios = QWidget()
        self.page_socios.setObjectName(u"page_socios")
        self.stackedWidget.addWidget(self.page_socios)
        self.page_pistas = QWidget()
        self.page_pistas.setObjectName(u"page_pistas")
        self.stackedWidget.addWidget(self.page_pistas)
        self.page_pagos = QWidget()
        self.page_pagos.setObjectName(u"page_pagos")
        self.stackedWidget.addWidget(self.page_pagos)
        self.page_reservas = QWidget()
        self.page_reservas.setObjectName(u"page_reservas")
        self.stackedWidget.addWidget(self.page_reservas)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Club de P\u00e1del", None))
        self.groupBox.setTitle("")
        self.btn_inicio.setText(QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.btn_socios.setText(QCoreApplication.translate("MainWindow", u"Socios", None))
        self.btn_pistas.setText(QCoreApplication.translate("MainWindow", u"Pistas", None))
        self.btn_pagos.setText(QCoreApplication.translate("MainWindow", u"Pagos", None))
        self.btn_reservas.setText(QCoreApplication.translate("MainWindow", u"Reservas", None))
        self.btn_salir.setText(QCoreApplication.translate("MainWindow", u"Salir", None))
        self.btn_configuracion.setText(QCoreApplication.translate("MainWindow", u"Configuraci\u00f3n", None))
        self.lbl_bienvenido.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_imagen.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

