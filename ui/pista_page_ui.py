# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pista_page.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QWidget)

class Ui_PistaPage(object):
    def setupUi(self, PistaPage):
        if not PistaPage.objectName():
            PistaPage.setObjectName(u"PistaPage")
        PistaPage.resize(900, 680)
        self.groupBox = QGroupBox(PistaPage)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 10, 861, 61))
        self.btn_agregar = QPushButton(self.groupBox)
        self.btn_agregar.setObjectName(u"btn_agregar")
        self.btn_agregar.setGeometry(QRect(10, 10, 121, 41))
        self.btn_modificar = QPushButton(self.groupBox)
        self.btn_modificar.setObjectName(u"btn_modificar")
        self.btn_modificar.setGeometry(QRect(160, 10, 121, 41))
        self.btn_baja = QPushButton(self.groupBox)
        self.btn_baja.setObjectName(u"btn_baja")
        self.btn_baja.setGeometry(QRect(310, 10, 121, 41))
        self.btn_activar = QPushButton(self.groupBox)
        self.btn_activar.setObjectName(u"btn_activar")
        self.btn_activar.setGeometry(QRect(460, 10, 121, 41))
        self.gridLayoutWidget = QWidget(PistaPage)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(20, 80, 861, 41))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.cmb_pared = QComboBox(self.gridLayoutWidget)
        self.cmb_pared.addItem("")
        self.cmb_pared.addItem("")
        self.cmb_pared.setObjectName(u"cmb_pared")
        self.cmb_pared.setMaximumSize(QSize(140, 16777215))

        self.gridLayout.addWidget(self.cmb_pared, 0, 3, 1, 1)

        self.cmb_tipo = QComboBox(self.gridLayoutWidget)
        self.cmb_tipo.addItem("")
        self.cmb_tipo.addItem("")
        self.cmb_tipo.setObjectName(u"cmb_tipo")
        self.cmb_tipo.setMaximumSize(QSize(140, 16777215))

        self.gridLayout.addWidget(self.cmb_tipo, 0, 7, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(60, 16777215))

        self.gridLayout.addWidget(self.label_3, 0, 4, 1, 1)

        self.txt_nombre = QLineEdit(self.gridLayoutWidget)
        self.txt_nombre.setObjectName(u"txt_nombre")
        self.txt_nombre.setMaximumSize(QSize(140, 16777215))

        self.gridLayout.addWidget(self.txt_nombre, 0, 1, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(60, 16777215))

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(60, 16777215))

        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)

        self.tabla_pistas = QTableWidget(PistaPage)
        self.tabla_pistas.setObjectName(u"tabla_pistas")
        self.tabla_pistas.setGeometry(QRect(20, 140, 861, 531))

        self.retranslateUi(PistaPage)

        QMetaObject.connectSlotsByName(PistaPage)
    # setupUi

    def retranslateUi(self, PistaPage):
        PistaPage.setWindowTitle(QCoreApplication.translate("PistaPage", u"Form", None))
        self.groupBox.setTitle("")
        self.btn_agregar.setText(QCoreApplication.translate("PistaPage", u"Insertar", None))
        self.btn_modificar.setText(QCoreApplication.translate("PistaPage", u"Modificar", None))
        self.btn_baja.setText(QCoreApplication.translate("PistaPage", u"Desactivar", None))
        self.btn_activar.setText(QCoreApplication.translate("PistaPage", u"Activar", None))
        self.cmb_pared.setItemText(0, QCoreApplication.translate("PistaPage", u"cristal", None))
        self.cmb_pared.setItemText(1, QCoreApplication.translate("PistaPage", u"muro", None))

        self.cmb_tipo.setItemText(0, QCoreApplication.translate("PistaPage", u"cubierta", None))
        self.cmb_tipo.setItemText(1, QCoreApplication.translate("PistaPage", u"descubierta", None))

        self.label_3.setText(QCoreApplication.translate("PistaPage", u"Tipo", None))
        self.label.setText(QCoreApplication.translate("PistaPage", u"Nombre", None))
        self.label_2.setText(QCoreApplication.translate("PistaPage", u"Pared", None))
    # retranslateUi

