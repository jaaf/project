from hop.SupplierDialogBase import Ui_SupplierDialog
from PyQt6.QtWidgets import QDialog
from PyQt6 import QtCore
from database.hops.hop_suppliers import HSupplier, all_hsupplier, add_hsupplier,find_hsupplier_by_id,find_hsupplier_by_name,update_hsupplier

from PyQt6.QtCore import Qt,QRegularExpression,QTimer
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator
from PyQt6 import QtGui
import sys
from Themes import Themes

class SupplierDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent
        self.ui =Ui_SupplierDialog()
        self.ui.setupUi(self)
        self.ui.addButton.clicked.connect(self.add_supplier)
        self.ui.idEdit.setVisible(False)
        #colors
        pal=self.parent.palette()
        self.setPalette(pal)#use the MainWindow's palette
        additionalColors=Themes.get_additional_colors('brown')
        #self.ui.introTextEdit.setStyleSheet('color:'+additionalColors['intro']+';background-color: '+self.parent.WinBg+';')

        
        #setting the model for list view
        self.hsuppliers=all_hsupplier()
        self.hsuppliers.sort(key=lambda x: x.name)
        self.model=SupplierModel(hsuppliers=self.hsuppliers)
        self.ui.listView.setModel(self.model)
        
        self.ui.groupBox.setVisible(False)
        self.hideMessage()
        
        #set connection
   
        self.ui.newButton.clicked.connect(lambda  :self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        selmodel =self.ui.listView.selectionModel()
        #selmodel.currentRowChanged.connect(self.load_brand)
        self.ui.listView.clicked.connect(self.load_supplier)
        self.ui.updateButton.clicked.connect(self.update_supplier)
   
        
    def add_supplier(self):
        sup=self.read_supplier()
        #adding to database
        result = add_hsupplier(sup)
        if(result == 'OK'):
            self.clear_form()
            self.setMessage('success', 'Le fournisseur a été correctement enregistré')
            self.ui.labelMessage.setVisible(True)
            self.model.hsuppliers.append(sup)
            self.hsuppliers.sort(key=lambda x: x.name)
            self.model.layoutChanged.emit()
            
            
    def update_supplier(self):
        #read the supplier from form and 
        sup=self.read_supplier()
        sup.id=self.ui.idEdit.text()
        #print(sup)
        update_hsupplier(sup)
        #as sup from read_supplier is no longer related to the list
        #find the supplier into the list and update it
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            index=indexes[0]
            supplier=self.model.hsuppliers[index.row()]
            #update from form 
            supplier.name=sup.name
            self.hsuppliers.sort(key=lambda x: x.name)
            self.model.layoutChanged.emit()    
        
    def setMessage(self, style, text):
        self.ui.labelMessage.setText(text)
        if(style =='success'):
            self.ui.labelMessage.setStyleSheet('background-color:green; color: white;padding:10px')
            self.timer=QTimer()
            self.timer.timeout.connect(self.hideMessage)
            self.timer.start(1500) 
        if(style == 'failure'):
                self.ui.labelMessage.setStyleSheet('background-color:red; color: white;padding:10px')
                self.ui.closeMessageButton.setVisible(True)        
        
        
    def load_supplier(self):  
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            index=indexes[0]
            supplier=self.model.hsuppliers[index.row()]
            #print(supplier)
            self.ui.idEdit.setText(str(supplier.id))
            self.ui.nameEdit.setText(supplier.name)
        return supplier   
        
    def read_supplier(self):
        name=self.ui.nameEdit.text()
        name=name.upper()  
      
        return HSupplier(None,name)
        
    def clear_form(self):
        self.ui.nameEdit.setText('')    
        
    def show_group_box(self,mode):
        
        #print (str(mode))
        if(mode == 'add'):
            self.ui.addButton.setVisible(True)
            self.ui.updateButton.setVisible(False)
            self.clear_form()
        if(mode == 'update'):
            self.ui.addButton.setVisible(False)
            self.ui.updateButton.setVisible(True)
            self.load_supplier()
        self.ui.groupBox.setVisible(True)    
     
    def hideMessage(self):
        self.ui.labelMessage.setVisible(False)   
        
class SupplierModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, hsuppliers=None, **kwargs):
        super(SupplierModel,self).__init__(*args, **kwargs)
        self.hsuppliers = hsuppliers or []  
        
    def data(self,index,role):
        hs =self.hsuppliers[index.row()] 
        if (role ==Qt.ItemDataRole.DisplayRole):
            return hs.name
                
                      
    def rowCount(self,index):
        return len(self.hsuppliers)
        
    
