# Form implementation generated from reading ui file 'designer/diphitemwidget.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(949, 90)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(0, 90))
        Form.setMaximumSize(QtCore.QSize(16777215, 90))
        Form.setWindowTitle("")
        Form.setStyleSheet("")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setMinimumSize(QtCore.QSize(0, 75))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 75))
        self.frame.setStyleSheet("background-color: #148F77; border-radius: 12px")
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.nameLabel = QtWidgets.QLabel(self.frame)
        self.nameLabel.setMinimumSize(QtCore.QSize(250, 0))
        self.nameLabel.setMaximumSize(QtCore.QSize(250, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.nameLabel.setFont(font)
        self.nameLabel.setStyleSheet("color:white")
        self.nameLabel.setObjectName("nameLabel")
        self.horizontalLayout_2.addWidget(self.nameLabel)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.capacitySuggestedLabel = QtWidgets.QLabel(self.frame)
        self.capacitySuggestedLabel.setMinimumSize(QtCore.QSize(100, 0))
        self.capacitySuggestedLabel.setMaximumSize(QtCore.QSize(100, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.capacitySuggestedLabel.setFont(font)
        self.capacitySuggestedLabel.setStyleSheet("color: orange")
        self.capacitySuggestedLabel.setObjectName("capacitySuggestedLabel")
        self.gridLayout_2.addWidget(self.capacitySuggestedLabel, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setMaximumSize(QtCore.QSize(150, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setStyleSheet("color:orange")
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.capacityEdit = QtWidgets.QLineEdit(self.frame)
        self.capacityEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.capacityEdit.setMaximumSize(QtCore.QSize(100, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.capacityEdit.setFont(font)
        self.capacityEdit.setStyleSheet("color: white; background-color:darkgreen")
        self.capacityEdit.setObjectName("capacityEdit")
        self.gridLayout_2.addWidget(self.capacityEdit, 1, 2, 1, 1)
        self.diphSuggestedLabel = QtWidgets.QLabel(self.frame)
        self.diphSuggestedLabel.setMinimumSize(QtCore.QSize(100, 0))
        self.diphSuggestedLabel.setMaximumSize(QtCore.QSize(100, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.diphSuggestedLabel.setFont(font)
        self.diphSuggestedLabel.setStyleSheet("color:orange")
        self.diphSuggestedLabel.setObjectName("diphSuggestedLabel")
        self.gridLayout_2.addWidget(self.diphSuggestedLabel, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setMaximumSize(QtCore.QSize(150, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: white")
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.diphEdit = QtWidgets.QLineEdit(self.frame)
        self.diphEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.diphEdit.setMaximumSize(QtCore.QSize(100, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.diphEdit.setFont(font)
        self.diphEdit.setMouseTracking(False)
        self.diphEdit.setToolTip("")
        self.diphEdit.setStyleSheet("color: white; background-color:darkgreen")
        self.diphEdit.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.diphEdit.setObjectName("diphEdit")
        self.gridLayout_2.addWidget(self.diphEdit, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setMaximumSize(QtCore.QSize(32, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("color: white")
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 0, 3, 1, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        self.nameLabel.setText(_translate("Form", "TextLabel"))
        self.capacitySuggestedLabel.setText(_translate("Form", "TextLabel"))
        self.label.setText(_translate("Form", "Valeur suggérée"))
        self.diphSuggestedLabel.setText(_translate("Form", "TextLabel"))
        self.label_2.setText(_translate("Form", "Valeur retenue"))
        self.pushButton.setText(_translate("Form", "⬇"))