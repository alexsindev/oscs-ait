# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(460, 260)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.input_label = QLabel(self.centralwidget)
        self.input_label.setObjectName(u"input_label")
        self.input_label.setGeometry(QRect(20, 20, 50, 22))
        self.input_text = QLineEdit(self.centralwidget)
        self.input_text.setObjectName(u"input_text")
        self.input_text.setGeometry(QRect(75, 20, 365, 22))
        self.button_t = QPushButton(self.centralwidget)
        self.button_t.setObjectName(u"button_t")
        self.button_t.setGeometry(QRect(20, 55, 60, 30))
        self.button_f = QPushButton(self.centralwidget)
        self.button_f.setObjectName(u"button_f")
        self.button_f.setGeometry(QRect(90, 55, 60, 30))
        self.button_and = QPushButton(self.centralwidget)
        self.button_and.setObjectName(u"button_and")
        self.button_and.setGeometry(QRect(160, 55, 60, 30))
        self.button_imply = QPushButton(self.centralwidget)
        self.button_imply.setObjectName(u"button_imply")
        self.button_imply.setGeometry(QRect(230, 55, 60, 30))
        self.button_or = QPushButton(self.centralwidget)
        self.button_or.setObjectName(u"button_or")
        self.button_or.setGeometry(QRect(300, 55, 60, 30))
        self.button_clear = QPushButton(self.centralwidget)
        self.button_clear.setObjectName(u"button_clear")
        self.button_clear.setGeometry(QRect(370, 55, 60, 30))
        self.button_equal = QPushButton(self.centralwidget)
        self.button_equal.setObjectName(u"button_equal")
        self.button_equal.setGeometry(QRect(440, 55, 60, 30))
        self.separator = QFrame(self.centralwidget)
        self.separator.setObjectName(u"separator")
        self.separator.setGeometry(QRect(20, 100, 420, 2))
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.truth_key_label = QLabel(self.centralwidget)
        self.truth_key_label.setObjectName(u"truth_key_label")
        self.truth_key_label.setGeometry(QRect(20, 115, 100, 22))
        self.truth_label = QLabel(self.centralwidget)
        self.truth_label.setObjectName(u"truth_label")
        self.truth_label.setGeometry(QRect(125, 115, 315, 22))
        self.prefix_key_label = QLabel(self.centralwidget)
        self.prefix_key_label.setObjectName(u"prefix_key_label")
        self.prefix_key_label.setGeometry(QRect(20, 150, 100, 22))
        self.prefix_label = QLabel(self.centralwidget)
        self.prefix_label.setObjectName(u"prefix_label")
        self.prefix_label.setGeometry(QRect(125, 150, 315, 22))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 460, 30))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Propositional Logic Evaluator", None))
        self.input_label.setText(QCoreApplication.translate("MainWindow", u"Input:", None))
        self.input_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"e.g.  t \u2228 f and f", None))
        self.button_t.setText(QCoreApplication.translate("MainWindow", u"t", None))
        self.button_f.setText(QCoreApplication.translate("MainWindow", u"f", None))
        self.button_and.setText(QCoreApplication.translate("MainWindow", u"and", None))
        self.button_or.setText(QCoreApplication.translate("MainWindow", u"\u2228", None))
        self.button_imply.setText(QCoreApplication.translate("MainWindow", u"imply", None))
        self.button_clear.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.button_equal.setText(QCoreApplication.translate("MainWindow", u"=", None))
        self.truth_key_label.setText(QCoreApplication.translate("MainWindow", u"Truth Value:", None))
        self.truth_label.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.prefix_key_label.setText(QCoreApplication.translate("MainWindow", u"Prefix:", None))
        self.prefix_label.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
    # retranslateUi

