# Form implementation generated from reading ui file 'designer/miscinventorywidget.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1668, 753)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.labelInventoryTitle = QtWidgets.QLabel(parent=Form)
        self.labelInventoryTitle.setObjectName("labelInventoryTitle")
        self.verticalLayout_6.addWidget(self.labelInventoryTitle)
        self.inventoryList = QtWidgets.QListView(parent=Form)
        self.inventoryList.setMinimumSize(QtCore.QSize(500, 0))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.inventoryList.setFont(font)
        self.inventoryList.setObjectName("inventoryList")
        self.verticalLayout_6.addWidget(self.inventoryList)
        self.messageLayout_2 = QtWidgets.QHBoxLayout()
        self.messageLayout_2.setObjectName("messageLayout_2")
        self.labelMessage_2 = QtWidgets.QLabel(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelMessage_2.sizePolicy().hasHeightForWidth())
        self.labelMessage_2.setSizePolicy(sizePolicy)
        self.labelMessage_2.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.labelMessage_2.setObjectName("labelMessage_2")
        self.messageLayout_2.addWidget(self.labelMessage_2)
        self.closeMessageButton_2 = QtWidgets.QPushButton(parent=Form)
        self.closeMessageButton_2.setMaximumSize(QtCore.QSize(128, 16777215))
        self.closeMessageButton_2.setStyleSheet("background-color:red; color:white;")
        self.closeMessageButton_2.setObjectName("closeMessageButton_2")
        self.messageLayout_2.addWidget(self.closeMessageButton_2)
        self.verticalLayout_6.addLayout(self.messageLayout_2)
        self.groupBoxImport_2 = QtWidgets.QGroupBox(parent=Form)
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
        self.idEdit_2 = QtWidgets.QLineEdit(parent=self.groupBoxImport_2)
        self.idEdit_2.setMinimumSize(QtCore.QSize(8, 0))
        self.idEdit_2.setMaximumSize(QtCore.QSize(8, 16777215))
        self.idEdit_2.setObjectName("idEdit_2")
        self.horizontalLayout_12.addWidget(self.idEdit_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.invQuantityLabel = QtWidgets.QLabel(parent=self.groupBoxImport_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.invQuantityLabel.setFont(font)
        self.invQuantityLabel.setObjectName("invQuantityLabel")
        self.horizontalLayout_13.addWidget(self.invQuantityLabel)
        self.invQuantityEdit = QtWidgets.QLineEdit(parent=self.groupBoxImport_2)
        self.invQuantityEdit.setMaximumSize(QtCore.QSize(64, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.invQuantityEdit.setFont(font)
        self.invQuantityEdit.setObjectName("invQuantityEdit")
        self.horizontalLayout_13.addWidget(self.invQuantityEdit)
        self.invQuantityUnitLabel = QtWidgets.QLabel(parent=self.groupBoxImport_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.invQuantityUnitLabel.setFont(font)
        self.invQuantityUnitLabel.setObjectName("invQuantityUnitLabel")
        self.horizontalLayout_13.addWidget(self.invQuantityUnitLabel)
        self.horizontalLayout_12.addLayout(self.horizontalLayout_13)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem1)
        self.checkBox = QtWidgets.QCheckBox(parent=self.groupBoxImport_2)
        self.checkBox.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.checkBox.setFont(font)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_12.addWidget(self.checkBox)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem2)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.invCostLabel = QtWidgets.QLabel(parent=self.groupBoxImport_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.invCostLabel.setFont(font)
        self.invCostLabel.setObjectName("invCostLabel")
        self.horizontalLayout_14.addWidget(self.invCostLabel)
        self.invCostEdit = QtWidgets.QLineEdit(parent=self.groupBoxImport_2)
        self.invCostEdit.setMaximumSize(QtCore.QSize(64, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.invCostEdit.setFont(font)
        self.invCostEdit.setObjectName("invCostEdit")
        self.horizontalLayout_14.addWidget(self.invCostEdit)
        self.invCostUnitLabel = QtWidgets.QLabel(parent=self.groupBoxImport_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.invCostUnitLabel.setFont(font)
        self.invCostUnitLabel.setObjectName("invCostUnitLabel")
        self.horizontalLayout_14.addWidget(self.invCostUnitLabel)
        self.horizontalLayout_12.addLayout(self.horizontalLayout_14)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem4)
        self.invUpdateButton = QtWidgets.QPushButton(parent=self.groupBoxImport_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.invUpdateButton.sizePolicy().hasHeightForWidth())
        self.invUpdateButton.setSizePolicy(sizePolicy)
        self.invUpdateButton.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.invUpdateButton.setFont(font)
        self.invUpdateButton.setObjectName("invUpdateButton")
        self.horizontalLayout_15.addWidget(self.invUpdateButton)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem5)
        self.invHideButton = QtWidgets.QPushButton(parent=self.groupBoxImport_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.invHideButton.setFont(font)
        self.invHideButton.setObjectName("invHideButton")
        self.horizontalLayout_15.addWidget(self.invHideButton)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem6)
        self.verticalLayout_4.addLayout(self.horizontalLayout_15)
        self.verticalLayout_6.addWidget(self.groupBoxImport_2)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem7)
        self.invDeleteButton = QtWidgets.QPushButton(parent=Form)
        self.invDeleteButton.setObjectName("invDeleteButton")
        self.horizontalLayout_7.addWidget(self.invDeleteButton)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem8)
        self.invEditButton = QtWidgets.QPushButton(parent=Form)
        self.invEditButton.setObjectName("invEditButton")
        self.horizontalLayout_7.addWidget(self.invEditButton)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem9)
        self.verticalLayout_6.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_3.addLayout(self.verticalLayout_6)
        spacerItem10 = QtWidgets.QSpacerItem(55, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem10)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.labelPublicTitle = QtWidgets.QLabel(parent=Form)
        self.labelPublicTitle.setObjectName("labelPublicTitle")
        self.verticalLayout_3.addWidget(self.labelPublicTitle)
        self.publicList = QtWidgets.QListView(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.publicList.sizePolicy().hasHeightForWidth())
        self.publicList.setSizePolicy(sizePolicy)
        self.publicList.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.publicList.setFont(font)
        self.publicList.setObjectName("publicList")
        self.verticalLayout_3.addWidget(self.publicList)
        self.filterGroupBox = QtWidgets.QGroupBox(parent=Form)
        self.filterGroupBox.setMaximumSize(QtCore.QSize(16777215, 80))
        self.filterGroupBox.setStyleSheet("background-color:#D5F5E3")
        self.filterGroupBox.setTitle("")
        self.filterGroupBox.setObjectName("filterGroupBox")
        self.verticalLayout_3.addWidget(self.filterGroupBox)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.labelMessage = QtWidgets.QLabel(parent=Form)
        self.labelMessage.setObjectName("labelMessage")
        self.horizontalLayout_11.addWidget(self.labelMessage)
        self.closeMessageButton = QtWidgets.QPushButton(parent=Form)
        self.closeMessageButton.setMaximumSize(QtCore.QSize(128, 16777215))
        self.closeMessageButton.setStyleSheet("background-color:red; color:white;")
        self.closeMessageButton.setObjectName("closeMessageButton")
        self.horizontalLayout_11.addWidget(self.closeMessageButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_11)
        self.groupBoxImport = QtWidgets.QGroupBox(parent=Form)
        self.groupBoxImport.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        self.groupBoxImport.setFont(font)
        self.groupBoxImport.setStyleSheet("")
        self.groupBoxImport.setTitle("")
        self.groupBoxImport.setObjectName("groupBoxImport")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBoxImport)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem11)
        self.quantityLabel = QtWidgets.QLabel(parent=self.groupBoxImport)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.quantityLabel.setFont(font)
        self.quantityLabel.setObjectName("quantityLabel")
        self.horizontalLayout_9.addWidget(self.quantityLabel)
        self.quantityEdit = QtWidgets.QLineEdit(parent=self.groupBoxImport)
        self.quantityEdit.setMaximumSize(QtCore.QSize(64, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.quantityEdit.setFont(font)
        self.quantityEdit.setObjectName("quantityEdit")
        self.horizontalLayout_9.addWidget(self.quantityEdit)
        self.quantityUnitLabel = QtWidgets.QLabel(parent=self.groupBoxImport)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.quantityUnitLabel.setFont(font)
        self.quantityUnitLabel.setObjectName("quantityUnitLabel")
        self.horizontalLayout_9.addWidget(self.quantityUnitLabel)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem12)
        self.costLabel = QtWidgets.QLabel(parent=self.groupBoxImport)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.costLabel.setFont(font)
        self.costLabel.setObjectName("costLabel")
        self.horizontalLayout_9.addWidget(self.costLabel)
        self.costEdit = QtWidgets.QLineEdit(parent=self.groupBoxImport)
        self.costEdit.setMaximumSize(QtCore.QSize(64, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.costEdit.setFont(font)
        self.costEdit.setObjectName("costEdit")
        self.horizontalLayout_9.addWidget(self.costEdit)
        self.costUnitLabel = QtWidgets.QLabel(parent=self.groupBoxImport)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.costUnitLabel.setFont(font)
        self.costUnitLabel.setObjectName("costUnitLabel")
        self.horizontalLayout_9.addWidget(self.costUnitLabel)
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem13)
        self.dateLabel = QtWidgets.QLabel(parent=self.groupBoxImport)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.dateLabel.setFont(font)
        self.dateLabel.setObjectName("dateLabel")
        self.horizontalLayout_9.addWidget(self.dateLabel)
        self.importDateEdit = QtWidgets.QDateEdit(parent=self.groupBoxImport)
        self.importDateEdit.setMaximumSize(QtCore.QSize(16777207, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.importDateEdit.setFont(font)
        self.importDateEdit.setObjectName("importDateEdit")
        self.horizontalLayout_9.addWidget(self.importDateEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        spacerItem14 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem14)
        self.confirmImportButton = QtWidgets.QPushButton(parent=self.groupBoxImport)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.confirmImportButton.sizePolicy().hasHeightForWidth())
        self.confirmImportButton.setSizePolicy(sizePolicy)
        self.confirmImportButton.setMaximumSize(QtCore.QSize(250, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.confirmImportButton.setFont(font)
        self.confirmImportButton.setStyleSheet("background-color:lightgray")
        self.confirmImportButton.setObjectName("confirmImportButton")
        self.horizontalLayout_10.addWidget(self.confirmImportButton)
        spacerItem15 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem15)
        self.hideImportButton = QtWidgets.QPushButton(parent=self.groupBoxImport)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.hideImportButton.setFont(font)
        self.hideImportButton.setStyleSheet("background-color:lightgray")
        self.hideImportButton.setObjectName("hideImportButton")
        self.horizontalLayout_10.addWidget(self.hideImportButton)
        spacerItem16 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem16)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.verticalLayout_3.addWidget(self.groupBoxImport)
        self.groupBoxNew = QtWidgets.QGroupBox(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxNew.sizePolicy().hasHeightForWidth())
        self.groupBoxNew.setSizePolicy(sizePolicy)
        self.groupBoxNew.setMaximumSize(QtCore.QSize(16777215, 200))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        self.groupBoxNew.setFont(font)
        self.groupBoxNew.setStyleSheet("")
        self.groupBoxNew.setTitle("")
        self.groupBoxNew.setObjectName("groupBoxNew")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBoxNew)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.idEdit = QtWidgets.QLineEdit(parent=self.groupBoxNew)
        self.idEdit.setMaximumSize(QtCore.QSize(24, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.idEdit.setFont(font)
        self.idEdit.setObjectName("idEdit")
        self.horizontalLayout_6.addWidget(self.idEdit)
        self.nameLabel = QtWidgets.QLabel(parent=self.groupBoxNew)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.nameLabel.setFont(font)
        self.nameLabel.setObjectName("nameLabel")
        self.horizontalLayout_6.addWidget(self.nameLabel)
        self.nameEdit = QtWidgets.QLineEdit(parent=self.groupBoxNew)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nameEdit.sizePolicy().hasHeightForWidth())
        self.nameEdit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.nameEdit.setFont(font)
        self.nameEdit.setObjectName("nameEdit")
        self.horizontalLayout_6.addWidget(self.nameEdit)
        spacerItem17 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem17)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.categoryLabel = QtWidgets.QLabel(parent=self.groupBoxNew)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.categoryLabel.setFont(font)
        self.categoryLabel.setObjectName("categoryLabel")
        self.horizontalLayout_5.addWidget(self.categoryLabel)
        self.categoryCombo = QtWidgets.QComboBox(parent=self.groupBoxNew)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.categoryCombo.setFont(font)
        self.categoryCombo.setObjectName("categoryCombo")
        self.horizontalLayout_5.addWidget(self.categoryCombo)
        spacerItem18 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem18)
        self.unitLabel = QtWidgets.QLabel(parent=self.groupBoxNew)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.unitLabel.setFont(font)
        self.unitLabel.setObjectName("unitLabel")
        self.horizontalLayout_5.addWidget(self.unitLabel)
        self.unitCombo = QtWidgets.QComboBox(parent=self.groupBoxNew)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.unitCombo.setFont(font)
        self.unitCombo.setObjectName("unitCombo")
        self.horizontalLayout_5.addWidget(self.unitCombo)
        spacerItem19 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem19)
        self.abvUnitLabel = QtWidgets.QLabel(parent=self.groupBoxNew)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.abvUnitLabel.setFont(font)
        self.abvUnitLabel.setObjectName("abvUnitLabel")
        self.horizontalLayout_5.addWidget(self.abvUnitLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.label_notes = QtWidgets.QLabel(parent=self.groupBoxNew)
        self.label_notes.setObjectName("label_notes")
        self.verticalLayout.addWidget(self.label_notes)
        self.notesEdit = QtWidgets.QTextEdit(parent=self.groupBoxNew)
        self.notesEdit.setMaximumSize(QtCore.QSize(16777215, 50))
        self.notesEdit.setObjectName("notesEdit")
        self.verticalLayout.addWidget(self.notesEdit)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem20 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem20)
        self.addButton = QtWidgets.QPushButton(parent=self.groupBoxNew)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.addButton.setFont(font)
        self.addButton.setStyleSheet("background-color:lightgray")
        self.addButton.setObjectName("addButton")
        self.horizontalLayout_2.addWidget(self.addButton)
        spacerItem21 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem21)
        self.updateButton = QtWidgets.QPushButton(parent=self.groupBoxNew)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.updateButton.setFont(font)
        self.updateButton.setStyleSheet("background-color:lightgray")
        self.updateButton.setObjectName("updateButton")
        self.horizontalLayout_2.addWidget(self.updateButton)
        spacerItem22 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem22)
        self.hideNewButton = QtWidgets.QPushButton(parent=self.groupBoxNew)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.hideNewButton.setFont(font)
        self.hideNewButton.setStyleSheet("background-color:lightgray")
        self.hideNewButton.setObjectName("hideNewButton")
        self.horizontalLayout_2.addWidget(self.hideNewButton)
        spacerItem23 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem23)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addWidget(self.groupBoxNew)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem24 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem24)
        self.importButton = QtWidgets.QPushButton(parent=Form)
        self.importButton.setObjectName("importButton")
        self.horizontalLayout.addWidget(self.importButton)
        spacerItem25 = QtWidgets.QSpacerItem(98, 23, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem25)
        self.deleteButton = QtWidgets.QPushButton(parent=Form)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout.addWidget(self.deleteButton)
        spacerItem26 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem26)
        self.editButton = QtWidgets.QPushButton(parent=Form)
        self.editButton.setObjectName("editButton")
        self.horizontalLayout.addWidget(self.editButton)
        spacerItem27 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem27)
        self.newButton = QtWidgets.QPushButton(parent=Form)
        self.newButton.setObjectName("newButton")
        self.horizontalLayout.addWidget(self.newButton)
        spacerItem28 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem28)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.labelInventoryTitle.setText(_translate("Form", "Mon inventaire des ingrédients divers"))
        self.labelMessage_2.setText(_translate("Form", "TextLabel"))
        self.closeMessageButton_2.setText(_translate("Form", "Close message"))
        self.invQuantityLabel.setText(_translate("Form", "Quantité"))
        self.invQuantityUnitLabel.setText(_translate("Form", "unité(s)"))
        self.checkBox.setText(_translate("Form", "Lier"))
        self.invCostLabel.setText(_translate("Form", "Coût"))
        self.invCostUnitLabel.setText(_translate("Form", "€"))
        self.invUpdateButton.setText(_translate("Form", "Mettre à jour"))
        self.invHideButton.setText(_translate("Form", "Cacher le formulaire"))
        self.invDeleteButton.setText(_translate("Form", "Supprimer"))
        self.invEditButton.setText(_translate("Form", "Modifier"))
        self.labelPublicTitle.setText(_translate("Form", "Liste publique des ingrédients divers"))
        self.labelMessage.setText(_translate("Form", "TextLabel"))
        self.closeMessageButton.setText(_translate("Form", "Close message"))
        self.quantityLabel.setText(_translate("Form", "Quantité"))
        self.quantityEdit.setToolTip(_translate("Form", "Maximum 1000 g"))
        self.quantityUnitLabel.setText(_translate("Form", "unité(s)"))
        self.costLabel.setText(_translate("Form", "Coût"))
        self.costEdit.setToolTip(_translate("Form", "Maximum 100 € "))
        self.costUnitLabel.setText(_translate("Form", "€"))
        self.dateLabel.setText(_translate("Form", "Date d\'achat"))
        self.confirmImportButton.setText(_translate("Form", "Confirmer l\'import"))
        self.hideImportButton.setText(_translate("Form", "Cacher le formulaire"))
        self.nameLabel.setText(_translate("Form", "Nom*"))
        self.categoryLabel.setText(_translate("Form", "Catégorie"))
        self.categoryCombo.setToolTip(_translate("Form", "obligatoire, ne peut être vide"))
        self.unitLabel.setText(_translate("Form", "Unité"))
        self.abvUnitLabel.setText(_translate("Form", "%"))
        self.label_notes.setText(_translate("Form", "Notes"))
        self.notesEdit.setToolTip(_translate("Form", "facultatif"))
        self.addButton.setText(_translate("Form", "Ajouter "))
        self.updateButton.setText(_translate("Form", "Mettre à jour"))
        self.hideNewButton.setText(_translate("Form", "Cacher le formulaire"))
        self.importButton.setText(_translate("Form", "Importer"))
        self.deleteButton.setText(_translate("Form", "Supprimer"))
        self.editButton.setText(_translate("Form", "Modifier"))
        self.newButton.setText(_translate("Form", "Nouveau"))
