# Form implementation generated from reading ui file 'designer/ingredientinventorywidget.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1685, 1209)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.leftLayout = QtWidgets.QVBoxLayout()
        self.leftLayout.setObjectName("leftLayout")
        self.labelInventoryTitle = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.labelInventoryTitle.setFont(font)
        self.labelInventoryTitle.setObjectName("labelInventoryTitle")
        self.leftLayout.addWidget(self.labelInventoryTitle)
        self.inventoryList = QtWidgets.QListView(Form)
        self.inventoryList.setObjectName("inventoryList")
        self.leftLayout.addWidget(self.inventoryList)
        self.messageLayout_2 = QtWidgets.QHBoxLayout()
        self.messageLayout_2.setObjectName("messageLayout_2")
        self.labelMessage_2 = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelMessage_2.sizePolicy().hasHeightForWidth())
        self.labelMessage_2.setSizePolicy(sizePolicy)
        self.labelMessage_2.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.labelMessage_2.setObjectName("labelMessage_2")
        self.messageLayout_2.addWidget(self.labelMessage_2)
        self.closeMessageButton_2 = QtWidgets.QPushButton(Form)
        self.closeMessageButton_2.setMaximumSize(QtCore.QSize(128, 16777215))
        self.closeMessageButton_2.setStyleSheet("background-color:red; color:white;")
        self.closeMessageButton_2.setObjectName("closeMessageButton_2")
        self.messageLayout_2.addWidget(self.closeMessageButton_2)
        self.leftLayout.addLayout(self.messageLayout_2)
        self.groupBoxImport_2 = QtWidgets.QGroupBox(Form)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        self.groupBoxImport_2.setFont(font)
        self.groupBoxImport_2.setStyleSheet("")
        self.groupBoxImport_2.setTitle("")
        self.groupBoxImport_2.setObjectName("groupBoxImport_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBoxImport_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.idEdit_2 = QtWidgets.QLineEdit(self.groupBoxImport_2)
        self.idEdit_2.setMinimumSize(QtCore.QSize(8, 0))
        self.idEdit_2.setMaximumSize(QtCore.QSize(8, 16777215))
        self.idEdit_2.setObjectName("idEdit_2")
        self.horizontalLayout_12.addWidget(self.idEdit_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_quantity_2 = QtWidgets.QLabel(self.groupBoxImport_2)
        self.label_quantity_2.setObjectName("label_quantity_2")
        self.horizontalLayout_13.addWidget(self.label_quantity_2)
        self.quantityEdit_2 = QtWidgets.QLineEdit(self.groupBoxImport_2)
        self.quantityEdit_2.setMaximumSize(QtCore.QSize(64, 16777215))
        self.quantityEdit_2.setObjectName("quantityEdit_2")
        self.horizontalLayout_13.addWidget(self.quantityEdit_2)
        self.label_quantity_unit_2 = QtWidgets.QLabel(self.groupBoxImport_2)
        self.label_quantity_unit_2.setObjectName("label_quantity_unit_2")
        self.horizontalLayout_13.addWidget(self.label_quantity_unit_2)
        self.horizontalLayout_12.addLayout(self.horizontalLayout_13)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem1)
        self.checkBox = QtWidgets.QCheckBox(self.groupBoxImport_2)
        self.checkBox.setMinimumSize(QtCore.QSize(0, 0))
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_12.addWidget(self.checkBox)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem2)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_cost_2 = QtWidgets.QLabel(self.groupBoxImport_2)
        self.label_cost_2.setObjectName("label_cost_2")
        self.horizontalLayout_14.addWidget(self.label_cost_2)
        self.costEdit_2 = QtWidgets.QLineEdit(self.groupBoxImport_2)
        self.costEdit_2.setMaximumSize(QtCore.QSize(64, 16777215))
        self.costEdit_2.setObjectName("costEdit_2")
        self.horizontalLayout_14.addWidget(self.costEdit_2)
        self.label_cost_unit_2 = QtWidgets.QLabel(self.groupBoxImport_2)
        self.label_cost_unit_2.setObjectName("label_cost_unit_2")
        self.horizontalLayout_14.addWidget(self.label_cost_unit_2)
        self.horizontalLayout_12.addLayout(self.horizontalLayout_14)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem4)
        self.updateButton_2 = QtWidgets.QPushButton(self.groupBoxImport_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.updateButton_2.sizePolicy().hasHeightForWidth())
        self.updateButton_2.setSizePolicy(sizePolicy)
        self.updateButton_2.setMaximumSize(QtCore.QSize(160, 16777215))
        self.updateButton_2.setObjectName("updateButton_2")
        self.horizontalLayout_15.addWidget(self.updateButton_2)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem5)
        self.hideImportButton_2 = QtWidgets.QPushButton(self.groupBoxImport_2)
        self.hideImportButton_2.setObjectName("hideImportButton_2")
        self.horizontalLayout_15.addWidget(self.hideImportButton_2)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem6)
        self.verticalLayout_4.addLayout(self.horizontalLayout_15)
        self.leftLayout.addWidget(self.groupBoxImport_2)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem7)
        self.invDeleteButton = QtWidgets.QPushButton(Form)
        self.invDeleteButton.setObjectName("invDeleteButton")
        self.horizontalLayout_7.addWidget(self.invDeleteButton)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem8)
        self.invEditButton = QtWidgets.QPushButton(Form)
        self.invEditButton.setObjectName("invEditButton")
        self.horizontalLayout_7.addWidget(self.invEditButton)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem9)
        self.leftLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_16.addLayout(self.leftLayout)
        spacerItem10 = QtWidgets.QSpacerItem(55, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_16.addItem(spacerItem10)
        self.rightLayout = QtWidgets.QVBoxLayout()
        self.rightLayout.setObjectName("rightLayout")
        self.labelPublicTitle = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.labelPublicTitle.setFont(font)
        self.labelPublicTitle.setObjectName("labelPublicTitle")
        self.rightLayout.addWidget(self.labelPublicTitle)
        self.publicList = QtWidgets.QListView(Form)
        self.publicList.setObjectName("publicList")
        self.rightLayout.addWidget(self.publicList)
        self.messageLayout = QtWidgets.QHBoxLayout()
        self.messageLayout.setObjectName("messageLayout")
        self.labelMessage = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelMessage.sizePolicy().hasHeightForWidth())
        self.labelMessage.setSizePolicy(sizePolicy)
        self.labelMessage.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.labelMessage.setObjectName("labelMessage")
        self.messageLayout.addWidget(self.labelMessage)
        self.closeMessageButton = QtWidgets.QPushButton(Form)
        self.closeMessageButton.setMaximumSize(QtCore.QSize(128, 16777215))
        self.closeMessageButton.setStyleSheet("background-color:red; color:white;")
        self.closeMessageButton.setObjectName("closeMessageButton")
        self.messageLayout.addWidget(self.closeMessageButton)
        self.rightLayout.addLayout(self.messageLayout)
        self.groupBoxImport = QtWidgets.QGroupBox(Form)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        self.groupBoxImport.setFont(font)
        self.groupBoxImport.setStyleSheet("")
        self.groupBoxImport.setTitle("")
        self.groupBoxImport.setObjectName("groupBoxImport")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBoxImport)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem11)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_quantity = QtWidgets.QLabel(self.groupBoxImport)
        self.label_quantity.setObjectName("label_quantity")
        self.horizontalLayout_8.addWidget(self.label_quantity)
        self.quantityEdit = QtWidgets.QLineEdit(self.groupBoxImport)
        self.quantityEdit.setMaximumSize(QtCore.QSize(64, 16777215))
        self.quantityEdit.setObjectName("quantityEdit")
        self.horizontalLayout_8.addWidget(self.quantityEdit)
        self.label_quantity_unit = QtWidgets.QLabel(self.groupBoxImport)
        self.label_quantity_unit.setObjectName("label_quantity_unit")
        self.horizontalLayout_8.addWidget(self.label_quantity_unit)
        self.horizontalLayout_10.addLayout(self.horizontalLayout_8)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem12)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_cost = QtWidgets.QLabel(self.groupBoxImport)
        self.label_cost.setObjectName("label_cost")
        self.horizontalLayout_9.addWidget(self.label_cost)
        self.costEdit = QtWidgets.QLineEdit(self.groupBoxImport)
        self.costEdit.setMaximumSize(QtCore.QSize(64, 16777215))
        self.costEdit.setObjectName("costEdit")
        self.horizontalLayout_9.addWidget(self.costEdit)
        self.label_cost_unit = QtWidgets.QLabel(self.groupBoxImport)
        self.label_cost_unit.setObjectName("label_cost_unit")
        self.horizontalLayout_9.addWidget(self.label_cost_unit)
        self.horizontalLayout_10.addLayout(self.horizontalLayout_9)
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem13)
        self.label_date = QtWidgets.QLabel(self.groupBoxImport)
        self.label_date.setObjectName("label_date")
        self.horizontalLayout_10.addWidget(self.label_date)
        self.dateButton = QtWidgets.QPushButton(self.groupBoxImport)
        self.dateButton.setMaximumSize(QtCore.QSize(16, 16))
        self.dateButton.setStyleSheet("background-color:green")
        self.dateButton.setText("")
        self.dateButton.setObjectName("dateButton")
        self.horizontalLayout_10.addWidget(self.dateButton)
        self.importDateEdit = QtWidgets.QDateEdit(self.groupBoxImport)
        self.importDateEdit.setEnabled(False)
        self.importDateEdit.setStyleSheet("color:black;")
        self.importDateEdit.setWrapping(False)
        self.importDateEdit.setFrame(False)
        self.importDateEdit.setReadOnly(True)
        self.importDateEdit.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.importDateEdit.setCalendarPopup(True)
        self.importDateEdit.setObjectName("importDateEdit")
        self.horizontalLayout_10.addWidget(self.importDateEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        spacerItem14 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem14)
        self.confirmImportButton = QtWidgets.QPushButton(self.groupBoxImport)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.confirmImportButton.sizePolicy().hasHeightForWidth())
        self.confirmImportButton.setSizePolicy(sizePolicy)
        self.confirmImportButton.setMaximumSize(QtCore.QSize(160, 16777215))
        self.confirmImportButton.setObjectName("confirmImportButton")
        self.horizontalLayout_11.addWidget(self.confirmImportButton)
        spacerItem15 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem15)
        self.hideImportButton = QtWidgets.QPushButton(self.groupBoxImport)
        self.hideImportButton.setObjectName("hideImportButton")
        self.horizontalLayout_11.addWidget(self.hideImportButton)
        spacerItem16 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem16)
        self.verticalLayout_2.addLayout(self.horizontalLayout_11)
        self.rightLayout.addWidget(self.groupBoxImport)
        self.groupBoxNew = QtWidgets.QGroupBox(Form)
        self.groupBoxNew.setMaximumSize(QtCore.QSize(16777215, 300))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        self.groupBoxNew.setFont(font)
        self.groupBoxNew.setStyleSheet("")
        self.groupBoxNew.setTitle("")
        self.groupBoxNew.setObjectName("groupBoxNew")
        self.rightLayout.addWidget(self.groupBoxNew)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem17 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem17)
        self.importButton = QtWidgets.QPushButton(Form)
        self.importButton.setObjectName("importButton")
        self.horizontalLayout.addWidget(self.importButton)
        spacerItem18 = QtWidgets.QSpacerItem(98, 23, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem18)
        self.deleteButton = QtWidgets.QPushButton(Form)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout.addWidget(self.deleteButton)
        spacerItem19 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem19)
        self.editButton = QtWidgets.QPushButton(Form)
        self.editButton.setObjectName("editButton")
        self.horizontalLayout.addWidget(self.editButton)
        spacerItem20 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem20)
        self.newButton = QtWidgets.QPushButton(Form)
        self.newButton.setObjectName("newButton")
        self.horizontalLayout.addWidget(self.newButton)
        spacerItem21 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem21)
        self.rightLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_16.addLayout(self.rightLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.labelInventoryTitle.setText(_translate("Form", "Mon inventaire des fermentables"))
        self.labelMessage_2.setText(_translate("Form", "TextLabel"))
        self.closeMessageButton_2.setText(_translate("Form", "Close message"))
        self.label_quantity_2.setText(_translate("Form", "Quantité"))
        self.label_quantity_unit_2.setText(_translate("Form", "kg"))
        self.checkBox.setToolTip(_translate("Form", "Si cette case est cochée, une modification de la quantité provoque une modification proportionnelle du coût"))
        self.checkBox.setText(_translate("Form", "Lier"))
        self.label_cost_2.setText(_translate("Form", "Coût"))
        self.label_cost_unit_2.setText(_translate("Form", "€"))
        self.updateButton_2.setText(_translate("Form", "Mettre à jour"))
        self.hideImportButton_2.setText(_translate("Form", "Cacher le formulaire"))
        self.invDeleteButton.setText(_translate("Form", "Supprimer"))
        self.invEditButton.setText(_translate("Form", "Modifier"))
        self.labelPublicTitle.setText(_translate("Form", "Liste publique des fermentables"))
        self.labelMessage.setText(_translate("Form", "TextLabel"))
        self.closeMessageButton.setText(_translate("Form", "Close message"))
        self.label_quantity.setText(_translate("Form", "Quantité"))
        self.label_quantity_unit.setText(_translate("Form", "kg"))
        self.label_cost.setText(_translate("Form", "Coût"))
        self.label_cost_unit.setText(_translate("Form", "€"))
        self.label_date.setText(_translate("Form", "Date d\'achat"))
        self.importDateEdit.setDisplayFormat(_translate("Form", "dd MMMM yyyy"))
        self.confirmImportButton.setText(_translate("Form", "Confirmer l\'import"))
        self.hideImportButton.setText(_translate("Form", "Cacher le formulaire"))
        self.importButton.setText(_translate("Form", "Importer"))
        self.deleteButton.setText(_translate("Form", "Supprimer"))
        self.editButton.setText(_translate("Form", "Modifier"))
        self.newButton.setText(_translate("Form", "Nouveau"))