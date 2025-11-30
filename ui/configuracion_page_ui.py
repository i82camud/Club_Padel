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
from PySide6.QtWidgets import (QApplication, QGroupBox, QLabel, QPushButton,
    QSizePolicy, QWidget)

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
        self.btn_clave = QPushButton(self.groupBox)
        self.btn_clave.setObjectName(u"btn_clave")
        self.btn_clave.setGeometry(QRect(0, 0, 141, 41))

        self.retranslateUi(configuracion_page)

        QMetaObject.connectSlotsByName(configuracion_page)
    # setupUi

    def retranslateUi(self, configuracion_page):
        configuracion_page.setWindowTitle(QCoreApplication.translate("configuracion_page", u"Form", None))
        self.label_configuracion.setText(QCoreApplication.translate("configuracion_page", u"Configuraci\u00f3n", None))
        self.groupBox.setTitle("")
        self.btn_clave.setText(QCoreApplication.translate("configuracion_page", u"Cambiar Contrase\u00f1a", None))
    # retranslateUi

