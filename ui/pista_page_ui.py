# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pista_page.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGridLayout,
    QGroupBox, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QWidget)

class Ui_PistaPage(object):
    def setupUi(self, PistaPage):
        if not PistaPage.objectName():
            PistaPage.setObjectName(u"PistaPage")
        PistaPage.resize(1080, 770)
        self.groupBox = QGroupBox(PistaPage)
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
        self.btn_activar = QPushButton(self.groupBox)
        self.btn_activar.setObjectName(u"btn_activar")
        self.btn_activar.setGeometry(QRect(450, 0, 121, 41))
        self.tabla_pistas = QTableWidget(PistaPage)
        self.tabla_pistas.setObjectName(u"tabla_pistas")
        self.tabla_pistas.setGeometry(QRect(20, 190, 1041, 561))
        self.tabla_pistas.setAlternatingRowColors(True)
        self.tabla_pistas.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.label_socios = QLabel(PistaPage)
        self.label_socios.setObjectName(u"label_socios")
        self.label_socios.setGeometry(QRect(20, 20, 221, 31))
        self.gridLayoutWidget_2 = QWidget(PistaPage)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(20, 110, 1041, 71))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.gridLayoutWidget_2)
        self.label_4.setObjectName(u"label_4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget_2)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_5, 0, 4, 1, 1)

        self.label_6 = QLabel(self.gridLayoutWidget_2)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_6, 0, 2, 1, 1)

        self.cmb_tipo = QComboBox(self.gridLayoutWidget_2)
        self.cmb_tipo.addItem("")
        self.cmb_tipo.addItem("")
        self.cmb_tipo.setObjectName(u"cmb_tipo")
        self.cmb_tipo.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_2.addWidget(self.cmb_tipo, 0, 5, 1, 1)

        self.cmb_pared = QComboBox(self.gridLayoutWidget_2)
        self.cmb_pared.addItem("")
        self.cmb_pared.addItem("")
        self.cmb_pared.setObjectName(u"cmb_pared")
        self.cmb_pared.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_2.addWidget(self.cmb_pared, 0, 3, 1, 1)

        self.txt_nombre = QLineEdit(self.gridLayoutWidget_2)
        self.txt_nombre.setObjectName(u"txt_nombre")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txt_nombre.sizePolicy().hasHeightForWidth())
        self.txt_nombre.setSizePolicy(sizePolicy1)
        self.txt_nombre.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_2.addWidget(self.txt_nombre, 0, 1, 1, 1)

        self.label_6.raise_()
        self.label_4.raise_()
        self.label_5.raise_()
        self.cmb_tipo.raise_()
        self.cmb_pared.raise_()
        self.txt_nombre.raise_()

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
        self.label_socios.setText(QCoreApplication.translate("PistaPage", u"Pistas", None))
        self.label_4.setText(QCoreApplication.translate("PistaPage", u"Nombre", None))
        self.label_5.setText(QCoreApplication.translate("PistaPage", u"Tipo", None))
        self.label_6.setText(QCoreApplication.translate("PistaPage", u"Pared", None))
        self.cmb_tipo.setItemText(0, QCoreApplication.translate("PistaPage", u"cubierta", None))
        self.cmb_tipo.setItemText(1, QCoreApplication.translate("PistaPage", u"descubierta", None))

        self.cmb_pared.setItemText(0, QCoreApplication.translate("PistaPage", u"cristal", None))
        self.cmb_pared.setItemText(1, QCoreApplication.translate("PistaPage", u"muro", None))

    # retranslateUi

