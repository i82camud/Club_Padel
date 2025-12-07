# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'socio_page.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QGroupBox,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QWidget)

class Ui_SocioPage(object):
    def setupUi(self, SocioPage):
        if not SocioPage.objectName():
            SocioPage.setObjectName(u"SocioPage")
        SocioPage.resize(1080, 770)
        self.tabla_socios = QTableWidget(SocioPage)
        self.tabla_socios.setObjectName(u"tabla_socios")
        self.tabla_socios.setGeometry(QRect(20, 190, 1041, 561))
        self.tabla_socios.setAlternatingRowColors(True)
        self.tabla_socios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.groupBox = QGroupBox(SocioPage)
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
        self.btn_listar = QPushButton(self.groupBox)
        self.btn_listar.setObjectName(u"btn_listar")
        self.btn_listar.setGeometry(QRect(600, 0, 121, 41))
        self.btn_listar_reservas = QPushButton(self.groupBox)
        self.btn_listar_reservas.setObjectName(u"btn_listar_reservas")
        self.btn_listar_reservas.setGeometry(QRect(750, 0, 121, 41))
        self.btn_listar_pagos = QPushButton(self.groupBox)
        self.btn_listar_pagos.setObjectName(u"btn_listar_pagos")
        self.btn_listar_pagos.setGeometry(QRect(900, 0, 121, 41))
        self.gridLayoutWidget = QWidget(SocioPage)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(20, 110, 1041, 71))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.txt_nombre = QLineEdit(self.gridLayoutWidget)
        self.txt_nombre.setObjectName(u"txt_nombre")

        self.gridLayout.addWidget(self.txt_nombre, 0, 1, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.txt_apellido1 = QLineEdit(self.gridLayoutWidget)
        self.txt_apellido1.setObjectName(u"txt_apellido1")

        self.gridLayout.addWidget(self.txt_apellido1, 0, 3, 1, 1)

        self.txt_email = QLineEdit(self.gridLayoutWidget)
        self.txt_email.setObjectName(u"txt_email")

        self.gridLayout.addWidget(self.txt_email, 1, 1, 1, 1)

        self.txt_apellido2 = QLineEdit(self.gridLayoutWidget)
        self.txt_apellido2.setObjectName(u"txt_apellido2")

        self.gridLayout.addWidget(self.txt_apellido2, 0, 5, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 1, 2, 1, 1)

        self.txt_telefono = QLineEdit(self.gridLayoutWidget)
        self.txt_telefono.setObjectName(u"txt_telefono")

        self.gridLayout.addWidget(self.txt_telefono, 1, 3, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 0, 4, 1, 1)

        self.txt_nombre.raise_()
        self.label.raise_()
        self.label_2.raise_()
        self.label_3.raise_()
        self.txt_apellido2.raise_()
        self.label_4.raise_()
        self.txt_email.raise_()
        self.label_5.raise_()
        self.txt_telefono.raise_()
        self.txt_apellido1.raise_()
        self.label_socios = QLabel(SocioPage)
        self.label_socios.setObjectName(u"label_socios")
        self.label_socios.setGeometry(QRect(20, 20, 221, 31))

        self.retranslateUi(SocioPage)

        QMetaObject.connectSlotsByName(SocioPage)
    # setupUi

    def retranslateUi(self, SocioPage):
        SocioPage.setWindowTitle(QCoreApplication.translate("SocioPage", u"Form", None))
        self.groupBox.setTitle("")
        self.btn_agregar.setText(QCoreApplication.translate("SocioPage", u"Insertar", None))
        self.btn_modificar.setText(QCoreApplication.translate("SocioPage", u"Modificar", None))
        self.btn_baja.setText(QCoreApplication.translate("SocioPage", u"Dar de Baja", None))
        self.btn_activar.setText(QCoreApplication.translate("SocioPage", u"Activar", None))
        self.btn_listar.setText(QCoreApplication.translate("SocioPage", u"Listar Socios", None))
        self.btn_listar_reservas.setText(QCoreApplication.translate("SocioPage", u"Listar Reservas", None))
        self.btn_listar_pagos.setText(QCoreApplication.translate("SocioPage", u"Listar Pagos", None))
        self.label_2.setText(QCoreApplication.translate("SocioPage", u"1\u00ba Apellido", None))
        self.label.setText(QCoreApplication.translate("SocioPage", u"Nombre", None))
        self.label_4.setText(QCoreApplication.translate("SocioPage", u"Correo", None))
        self.label_5.setText(QCoreApplication.translate("SocioPage", u"Tel\u00e9fono", None))
        self.label_3.setText(QCoreApplication.translate("SocioPage", u"2\u00ba Apellido", None))
        self.label_socios.setText(QCoreApplication.translate("SocioPage", u"Socios", None))
    # retranslateUi

