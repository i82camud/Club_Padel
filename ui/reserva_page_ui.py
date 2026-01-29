# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'reserva_page.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDateEdit,
    QGridLayout, QGroupBox, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QTimeEdit, QWidget)

class Ui_reserva_page(object):
    def setupUi(self, reserva_page):
        if not reserva_page.objectName():
            reserva_page.setObjectName(u"reserva_page")
        reserva_page.resize(1080, 770)
        self.label_pistas = QLabel(reserva_page)
        self.label_pistas.setObjectName(u"label_pistas")
        self.label_pistas.setGeometry(QRect(20, 20, 221, 31))
        self.groupBox = QGroupBox(reserva_page)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 60, 1041, 41))
        self.btn_agregar = QPushButton(self.groupBox)
        self.btn_agregar.setObjectName(u"btn_agregar")
        self.btn_agregar.setGeometry(QRect(0, 0, 121, 41))
        self.btn_modificar = QPushButton(self.groupBox)
        self.btn_modificar.setObjectName(u"btn_modificar")
        self.btn_modificar.setGeometry(QRect(150, 0, 121, 41))
        self.btn_baja = QPushButton(self.groupBox)
        self.btn_baja.setObjectName(u"btn_baja")
        self.btn_baja.setGeometry(QRect(300, 0, 121, 41))
        self.btn_pagar = QPushButton(self.groupBox)
        self.btn_pagar.setObjectName(u"btn_pagar")
        self.btn_pagar.setGeometry(QRect(450, 0, 121, 41))
        self.btn_listar = QPushButton(self.groupBox)
        self.btn_listar.setObjectName(u"btn_listar")
        self.btn_listar.setGeometry(QRect(600, 0, 121, 41))
        self.gridLayoutWidget = QWidget(reserva_page)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(20, 110, 1041, 71))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)

        self.dateEdit = QDateEdit(self.gridLayoutWidget)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setCalendarPopup(True)

        self.gridLayout.addWidget(self.dateEdit, 0, 1, 1, 1)

        self.timeEdit_2 = QTimeEdit(self.gridLayoutWidget)
        self.timeEdit_2.setObjectName(u"timeEdit_2")

        self.gridLayout.addWidget(self.timeEdit_2, 0, 5, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 0, 4, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 1, 2, 1, 1)

        self.cmb_pista = QComboBox(self.gridLayoutWidget)
        self.cmb_pista.setObjectName(u"cmb_pista")

        self.gridLayout.addWidget(self.cmb_pista, 1, 3, 1, 1)

        self.timeEdit = QTimeEdit(self.gridLayoutWidget)
        self.timeEdit.setObjectName(u"timeEdit")

        self.gridLayout.addWidget(self.timeEdit, 0, 3, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.txt_socio = QLineEdit(self.gridLayoutWidget)
        self.txt_socio.setObjectName(u"txt_socio")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txt_socio.sizePolicy().hasHeightForWidth())
        self.txt_socio.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.txt_socio, 1, 1, 1, 1)

        self.tabla_reservas = QTableWidget(reserva_page)
        self.tabla_reservas.setObjectName(u"tabla_reservas")
        self.tabla_reservas.setGeometry(QRect(20, 240, 1041, 511))
        self.tabla_reservas.setAlternatingRowColors(True)
        self.tabla_reservas.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.btn_limpiar = QPushButton(reserva_page)
        self.btn_limpiar.setObjectName(u"btn_limpiar")
        self.btn_limpiar.setGeometry(QRect(20, 200, 71, 31))
        self.gridLayoutWidget_2 = QWidget(reserva_page)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(110, 190, 411, 51))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.gridLayoutWidget_2)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_6, 0, 0, 1, 1)

        self.txt_buscar = QLineEdit(self.gridLayoutWidget_2)
        self.txt_buscar.setObjectName(u"txt_buscar")

        self.gridLayout_2.addWidget(self.txt_buscar, 0, 1, 1, 1)


        self.retranslateUi(reserva_page)

        QMetaObject.connectSlotsByName(reserva_page)
    # setupUi

    def retranslateUi(self, reserva_page):
        reserva_page.setWindowTitle(QCoreApplication.translate("reserva_page", u"Form", None))
        self.label_pistas.setText(QCoreApplication.translate("reserva_page", u"Reservas", None))
        self.groupBox.setTitle("")
        self.btn_agregar.setText(QCoreApplication.translate("reserva_page", u"Insertar", None))
        self.btn_modificar.setText(QCoreApplication.translate("reserva_page", u"Modificar", None))
        self.btn_baja.setText(QCoreApplication.translate("reserva_page", u"Cancelar", None))
        self.btn_pagar.setText(QCoreApplication.translate("reserva_page", u"Pagar", None))
        self.btn_listar.setText(QCoreApplication.translate("reserva_page", u"Listar Reservas", None))
        self.label_3.setText(QCoreApplication.translate("reserva_page", u"Fecha", None))
        self.timeEdit_2.setDisplayFormat(QCoreApplication.translate("reserva_page", u"HH:mm", None))
        self.label_5.setText(QCoreApplication.translate("reserva_page", u"Hora Fin", None))
        self.label_2.setText(QCoreApplication.translate("reserva_page", u"Pista", None))
        self.timeEdit.setDisplayFormat(QCoreApplication.translate("reserva_page", u"HH:mm", None))
        self.label_4.setText(QCoreApplication.translate("reserva_page", u"Hora Inicio", None))
        self.label.setText(QCoreApplication.translate("reserva_page", u"Socio", None))
        self.btn_limpiar.setText(QCoreApplication.translate("reserva_page", u"Limpiar", None))
        self.label_6.setText(QCoreApplication.translate("reserva_page", u"Buscar", None))
    # retranslateUi

