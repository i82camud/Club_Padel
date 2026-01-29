# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pago_page.ui'
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
    QTableWidgetItem, QWidget)

class Ui_pago_page(object):
    def setupUi(self, pago_page):
        if not pago_page.objectName():
            pago_page.setObjectName(u"pago_page")
        pago_page.resize(1080, 770)
        self.label_pagos = QLabel(pago_page)
        self.label_pagos.setObjectName(u"label_pagos")
        self.label_pagos.setGeometry(QRect(20, 20, 221, 31))
        self.groupBox = QGroupBox(pago_page)
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
        self.btn_listar = QPushButton(self.groupBox)
        self.btn_listar.setObjectName(u"btn_listar")
        self.btn_listar.setGeometry(QRect(450, 0, 121, 41))
        self.gridLayoutWidget = QWidget(pago_page)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(20, 110, 1041, 71))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.txt_importe = QLineEdit(self.gridLayoutWidget)
        self.txt_importe.setObjectName(u"txt_importe")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txt_importe.sizePolicy().hasHeightForWidth())
        self.txt_importe.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.txt_importe, 0, 4, 1, 1)

        self.dateEdit = QDateEdit(self.gridLayoutWidget)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setCalendarPopup(True)

        self.gridLayout.addWidget(self.dateEdit, 0, 6, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 0, 5, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)

        self.comboBox = QComboBox(self.gridLayoutWidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayout.addWidget(self.comboBox, 1, 1, 1, 1)

        self.txt_socio = QLineEdit(self.gridLayoutWidget)
        self.txt_socio.setObjectName(u"txt_socio")
        sizePolicy.setHeightForWidth(self.txt_socio.sizePolicy().hasHeightForWidth())
        self.txt_socio.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.txt_socio, 0, 1, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 1, 3, 1, 1)

        self.txt_concepto = QLineEdit(self.gridLayoutWidget)
        self.txt_concepto.setObjectName(u"txt_concepto")
        sizePolicy.setHeightForWidth(self.txt_concepto.sizePolicy().hasHeightForWidth())
        self.txt_concepto.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.txt_concepto, 1, 4, 1, 1)

        self.label.raise_()
        self.label_2.raise_()
        self.label_3.raise_()
        self.label_4.raise_()
        self.dateEdit.raise_()
        self.txt_importe.raise_()
        self.comboBox.raise_()
        self.txt_socio.raise_()
        self.label_5.raise_()
        self.txt_concepto.raise_()
        self.tabla_pagos = QTableWidget(pago_page)
        self.tabla_pagos.setObjectName(u"tabla_pagos")
        self.tabla_pagos.setGeometry(QRect(20, 240, 1041, 511))
        self.tabla_pagos.setAlternatingRowColors(True)
        self.tabla_pagos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.btn_limpiar = QPushButton(pago_page)
        self.btn_limpiar.setObjectName(u"btn_limpiar")
        self.btn_limpiar.setGeometry(QRect(20, 200, 71, 31))
        self.gridLayoutWidget_2 = QWidget(pago_page)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(110, 190, 411, 51))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.gridLayoutWidget_2)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_6, 0, 0, 1, 1)

        self.txt_buscar = QLineEdit(self.gridLayoutWidget_2)
        self.txt_buscar.setObjectName(u"txt_buscar")

        self.gridLayout_2.addWidget(self.txt_buscar, 0, 1, 1, 1)


        self.retranslateUi(pago_page)

        QMetaObject.connectSlotsByName(pago_page)
    # setupUi

    def retranslateUi(self, pago_page):
        pago_page.setWindowTitle(QCoreApplication.translate("pago_page", u"Form", None))
        self.label_pagos.setText(QCoreApplication.translate("pago_page", u"Pagos", None))
        self.groupBox.setTitle("")
        self.btn_agregar.setText(QCoreApplication.translate("pago_page", u"Insertar", None))
        self.btn_modificar.setText(QCoreApplication.translate("pago_page", u"Modificar", None))
        self.btn_baja.setText(QCoreApplication.translate("pago_page", u"Anular", None))
        self.btn_listar.setText(QCoreApplication.translate("pago_page", u"Listar Pagos", None))
        self.label.setText(QCoreApplication.translate("pago_page", u"Socio", None))
        self.label_3.setText(QCoreApplication.translate("pago_page", u"Fecha", None))
        self.label_2.setText(QCoreApplication.translate("pago_page", u"Importe", None))
        self.label_4.setText(QCoreApplication.translate("pago_page", u"Tipo", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("pago_page", u"Cuota", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("pago_page", u"Reserva", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("pago_page", u"Extra", None))

        self.label_5.setText(QCoreApplication.translate("pago_page", u"Concepto", None))
        self.btn_limpiar.setText(QCoreApplication.translate("pago_page", u"Limpiar", None))
        self.label_6.setText(QCoreApplication.translate("pago_page", u"Buscar", None))
    # retranslateUi

