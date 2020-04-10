# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'com_des.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1125, 543)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 6, 1310, 541))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.picture1 = QtWidgets.QLabel(self.layoutWidget)
        self.picture1.setMinimumSize(QtCore.QSize(650, 400))
        self.picture1.setObjectName("picture1")
        self.horizontalLayout_2.addWidget(self.picture1)
        self.picture2 = QtWidgets.QLabel(self.layoutWidget)
        self.picture2.setMinimumSize(QtCore.QSize(600, 400))
        self.picture2.setObjectName("picture2")
        self.horizontalLayout_2.addWidget(self.picture2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(800, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.ReadyBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.ReadyBtn.setMaximumSize(QtCore.QSize(150, 16777215))
        self.ReadyBtn.setObjectName("ReadyBtn")
        self.horizontalLayout.addWidget(self.ReadyBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.picture1.setText(_translate("Form", "p1"))
        self.picture2.setText(_translate("Form", "p2"))
        self.ReadyBtn.setText(_translate("Form", "Ready!"))

