from yeast.YBrandDialogBase import Ui_BrandDialog
from PyQt6.QtWidgets import QDialog
from PyQt6 import QtCore
from database.yeasts.yeast import YBrand, all_ybrand, add_ybrand, find_ybrand_by_id,find_ybrand_by_name,update_ybrand

from PyQt6.QtCore import Qt,QRegularExpression,QTimer
from parameters import fermentable_forms, raw_ingredients, fermentable_categories
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator
from PyQt6 import QtGui
import sys
from database.commons.country import all_country, find_country_by_code
from Themes import Themes

class YBrandDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =Ui_BrandDialog()
        self.ui.setupUi(self) 
        self.parent=parent
        
        #colors
        pal=self.parent.palette()
        self.setPalette(pal)#use the MainWindow's palette
        additionalColors=Themes.get_additional_colors('brown')
        self.ui.introTextEdit.setStyleSheet('color:'+additionalColors['intro']+';background-color: white;')

        self.ui.addButton.clicked.connect(self.add_brand)
        self.ui.idEdit.setVisible(False)
        
        countries=all_country()
        self.ui.codeCombo.addItem('')
        for c in countries:
            self.ui.codeCombo.addItem(c.name+' — '+c.country_code)
        #setting the model for list view
        self.ybrands=all_ybrand()
        self.ybrands.sort(key=lambda x: (x.country_code,x.name))
        self.model=BrandModel(ybrands=self.ybrands)
        self.ui.listView.setModel(self.model)
        
        self.ui.groupBox.setVisible(False)
        self.hideMessage()
        
        #set connection
   
        self.ui.newButton.clicked.connect(lambda  :self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        selmodel =self.ui.listView.selectionModel()
        #selmodel.currentRowChanged.connect(self.load_brand)
        self.ui.listView.clicked.connect(self.load_brand)
        self.ui.updateButton.clicked.connect(self.update_brand)
   
        
    def add_brand(self):
        br=self.read_brand()
        #adding to database
        result = add_ybrand(br)
        if(result == 'OK'):
            self.clear_form()
            self.setMessage('success', 'La marque a été correctement enregistrée')
            self.ui.labelMessage.setVisible(True)
            self.model.ybrands.append(br)
            self.ybrands.sort(key=lambda x: (x.country_code,x.name))
            self.model.layoutChanged.emit()
            
            
    def update_brand(self):
        #read the brand from form and 
        br=self.read_brand()
        br.id=self.ui.idEdit.text()
        #print(br)
        update_ybrand(br)
        #as br from read_brand is no longer related to the list
        #find the brand into the list and update it
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            index=indexes[0]
            brand=self.model.ybrands[index.row()]
            #update from form 
            brand.name=br.name
            brand.country_code=br.country_code
            self.ybrands.sort(key=lambda x: (x.country_code,x.name))
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
        
        
    def load_brand(self):  
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            index=indexes[0]
            brand=self.model.ybrands[index.row()]
            #print(brand)
            self.ui.idEdit.setText(str(brand.id))
            self.ui.nameEdit.setText(brand.name)
            country=find_country_by_code(brand.country_code)
            self.ui.codeCombo.setCurrentText(country.name+ ' — '+country.country_code)
        return brand    
        
    def read_brand(self):
        name=self.ui.nameEdit.text()
        name=name.upper()  
        ##print(name)
        code=self.ui.codeCombo.currentText()[-2:]
        code=code.lower()
        return YBrand(None,name,code)
        
    def clear_form(self):
        self.ui.nameEdit.setText('')
        self.ui.codeCombo.setCurrentText('')    
        
    def show_group_box(self,mode):
        
        #print (str(mode))
        if(mode == 'add'):
            self.ui.addButton.setVisible(True)
            self.ui.updateButton.setVisible(False)
            self.ui.nameEdit.setStyleSheet('background-color:honeydew')
            self.ui.codeCombo.setStyleSheet('background-color:honeydew')
            
            self.clear_form()
        if(mode == 'update'):
            self.ui.addButton.setVisible(False)
            self.ui.updateButton.setVisible(True)
            self.ui.nameEdit.setStyleSheet('background-color:lightgray')
            self.ui.codeCombo.setStyleSheet('background-color:lightgray')
            self.load_brand()
        self.ui.groupBox.setVisible(True)    
     
    def hideMessage(self):
        self.ui.labelMessage.setVisible(False)   
        
class BrandModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, ybrands=None, **kwargs):
        super(BrandModel,self).__init__(*args, **kwargs)
        self.ybrands = ybrands or []  
        #print ('#printing ybrands')
        #print (self.ybrands )
        
    def data(self,index,role):
        fb =self.ybrands[index.row()] 
        if (role ==Qt.ItemDataRole.DisplayRole):
            return fb.name
        if (role == Qt.ItemDataRole.DecorationRole):
            filename='./w20/'+fb.country_code+'.png'
            return QtGui.QImage(filename)
                
                      
    def rowCount(self,index):
        return len(self.ybrands)
        
    
