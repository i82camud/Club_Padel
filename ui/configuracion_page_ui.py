# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configuracion_page.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTimeEdit,
    QWidget)

class Ui_configuracion_page(object):
    def setupUi(self, configuracion_page):
        if not configuracion_page.objectName():
            configuracion_page.setObjectName(u"configuracion_page")
        configuracion_page.resize(1080, 756)
        self.label_configuracion = QLabel(configuracion_page)
        self.label_configuracion.setObjectName(u"label_configuracion")
        self.label_configuracion.setGeometry(QRect(20, 20, 221, 31))
        self.groupBox = QGroupBox(configuracion_page)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 60, 1041, 41))
        self.btn_guardar = QPushButton(self.groupBox)
        self.btn_guardar.setObjectName(u"btn_guardar")
        self.btn_guardar.setGeometry(QRect(0, 0, 141, 41))
        self.btn_clave = QPushButton(self.groupBox)
        self.btn_clave.setObjectName(u"btn_clave")
        self.btn_clave.setGeometry(QRect(170, 0, 141, 41))
        self.btn_copia = QPushButton(self.groupBox)
        self.btn_copia.setObjectName(u"btn_copia")
        self.btn_copia.setGeometry(QRect(340, 0, 141, 41))
        self.btn_restaurar = QPushButton(self.groupBox)
        self.btn_restaurar.setObjectName(u"btn_restaurar")
        self.btn_restaurar.setGeometry(QRect(510, 0, 141, 41))
        self.gridLayoutWidget = QWidget(configuracion_page)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(20, 110, 751, 131))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.timeApertura = QTimeEdit(self.gridLayoutWidget)
        self.timeApertura.setObjectName(u"timeApertura")

        self.gridLayout.addWidget(self.timeApertura, 0, 1, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 0, 2, 1, 1)

        self.timeCierre = QTimeEdit(self.gridLayoutWidget)
        self.timeCierre.setObjectName(u"timeCierre")

        self.gridLayout.addWidget(self.timeCierre, 0, 3, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.txt_reservas = QLineEdit(self.gridLayoutWidget)
        self.txt_reservas.setObjectName(u"txt_reservas")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txt_reservas.sizePolicy().hasHeightForWidth())
        self.txt_reservas.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.txt_reservas, 2, 1, 1, 1)

        self.label_9 = QLabel(self.gridLayoutWidget)
        self.label_9.setObjectName(u"label_9")
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_9, 2, 0, 1, 1)

        self.label_8 = QLabel(self.gridLayoutWidget)
        self.label_8.setObjectName(u"label_8")
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_8, 1, 0, 1, 1)

        self.timeReserva = QTimeEdit(self.gridLayoutWidget)
        self.timeReserva.setObjectName(u"timeReserva")
        self.timeReserva.setTime(QTime(1, 30, 0))

        self.gridLayout.addWidget(self.timeReserva, 1, 1, 1, 1)

        self.label_6 = QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)

        self.timeAntelacionMin = QTimeEdit(self.gridLayoutWidget)
        self.timeAntelacionMin.setObjectName(u"timeAntelacionMin")
        self.timeAntelacionMin.setTime(QTime(1, 0, 0))

        self.gridLayout.addWidget(self.timeAntelacionMin, 3, 1, 1, 1)

        self.label_7 = QLabel(self.gridLayoutWidget)
        self.label_7.setObjectName(u"label_7")
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_7, 3, 2, 1, 1)

        self.txt_antelacion_max = QLineEdit(self.gridLayoutWidget)
        self.txt_antelacion_max.setObjectName(u"txt_antelacion_max")
        sizePolicy1.setHeightForWidth(self.txt_antelacion_max.sizePolicy().hasHeightForWidth())
        self.txt_antelacion_max.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.txt_antelacion_max, 3, 3, 1, 1)


        self.retranslateUi(configuracion_page)

        QMetaObject.connectSlotsByName(configuracion_page)
    # setupUi

    def retranslateUi(self, configuracion_page):
        configuracion_page.setWindowTitle(QCoreApplication.translate("configuracion_page", u"Form", None))
        self.label_configuracion.setText(QCoreApplication.translate("configuracion_page", u"Configuraci\u00f3n", None))
        self.groupBox.setTitle("")
        self.btn_guardar.setText(QCoreApplication.translate("configuracion_page", u"Guardar Config.", None))
        self.btn_clave.setText(QCoreApplication.translate("configuracion_page", u"Cambiar Contrase\u00f1a", None))
        self.btn_copia.setText(QCoreApplication.translate("configuracion_page", u"Hacer Copia Seg.", None))
        self.btn_restaurar.setText(QCoreApplication.translate("configuracion_page", u"Restaurar Copia Seg.", None))
        self.timeApertura.setDisplayFormat(QCoreApplication.translate("configuracion_page", u"HH:mm", None))
        self.label_5.setText(QCoreApplication.translate("configuracion_page", u"Hora Cierre", None))
        self.timeCierre.setDisplayFormat(QCoreApplication.translate("configuracion_page", u"HH:mm", None))
        self.label_4.setText(QCoreApplication.translate("configuracion_page", u"Hora Apertura", None))
        self.label_9.setText(QCoreApplication.translate("configuracion_page", u"N\u00ba Reservas Simult\u00e1neas", None))
        self.label_8.setText(QCoreApplication.translate("configuracion_page", u"Duraci\u00f3n Reserva", None))
        self.timeReserva.setDisplayFormat(QCoreApplication.translate("configuracion_page", u"HH:mm", None))
        self.label_6.setText(QCoreApplication.translate("configuracion_page", u"Antelaci\u00f3n m\u00ednima", None))
        self.timeAntelacionMin.setDisplayFormat(QCoreApplication.translate("configuracion_page", u"HH:mm", None))
        self.label_7.setText(QCoreApplication.translate("configuracion_page", u"Antelaci\u00f3n m\u00e1xima", None))
    # retranslateUi

