from commons.CountryDialogBase import Ui_CountryDialog
from PyQt6.QtWidgets import QDialog
from PyQt6 import QtCore
from database.commons.country import Country, all_country, add_country,update_country,delete_country

from PyQt6.QtCore import Qt,QRegularExpression,QTimer
from parameters import fermentable_forms, raw_ingredients, fermentable_categories
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator
from PyQt6 import QtGui
import sys
from Themes import Themes

class CountryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =Ui_CountryDialog()
        self.ui.setupUi(self)
        self.parent=parent
      
        #colors
        pal=self.parent.palette()
        self.setPalette(pal)#use the MainWindow's palette
        additionalColors=Themes.get_additional_colors('brown')
#        self.ui.introTextEdit.setStyleSheet('color:'+additionalColors['intro']+';background-color: '+self.parent.WinBg+';')

      
        self.ui.addButton.clicked.connect(self.add_country)
        
        #setting the model for list view
        self.countries=all_country()
        self.countries.sort(key=lambda x: (x.name,x.country_code))
        self.model=CountryModel(countries=self.countries)
        self.ui.listView.setModel(self.model)
        
        self.ui.groupBox.setVisible(False)
        self.hideMessage()
        
        #set connection
   
        self.ui.newButton.clicked.connect(lambda  :self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.deleteButton.clicked.connect(self.delete_country)
        #selmodel =self.ui.listView.selectionModel()
        #selmodel.currentRowChanged.connect(self.load_brand)
        self.ui.listView.clicked.connect(self.load_country)
        self.ui.updateButton.clicked.connect(self.update_country)
   
    def delete_country(self):
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            index=indexes[0]
            country=self.model.countries[index.row()]
            delete_country(country.id) 
            self.model.countries=all_country()
            self.countries.sort(key=lambda x: (x.name,x.country_code))
            self.model.layoutChanged.emit()   

    def add_country(self):
        c=self.read_country()
        #adding to database
        result = add_country(c)
        if(result == 'OK'):
            self.clear_form()
            self.setMessage('success', 'Le pays a été correctement enregistrée')
            self.ui.labelMessage.setVisible(True)
            self.model.countries.append(c)
            self.countries.sort(key=lambda x: (x.name,x.country_code))
            self.model.layoutChanged.emit()
            
            
    def update_country(self):
        #read the country from form and 
        c=self.read_country()
        c.id=self.ui.idEdit.text()
        update_country(c)
        #as c from read_country is no longer related to the list
        #find the country into the list and update it
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            index=indexes[0]
            country=self.model.countries[index.row()]
            #update from form 
            country.name=c.name
            country.country_code=c.country_code
            self.countries.sort(key=lambda x: (x.name,x.country_code))
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
        
        
    def load_country(self):  
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            index=indexes[0]
            country=self.model.countries[index.row()]
            self.ui.idEdit.setText(str(country.id))
            self.ui.nameEdit.setText(country.name)
            self.ui.codeEdit.setText(country.country_code)
            return country   
        
    def read_country(self):
        name=self.ui.nameEdit.text()
        name=name.upper()  
        code=self.ui.codeEdit.text()
        code=code.lower()
        return Country(None,name,code)
        
    def clear_form(self):
        self.ui.nameEdit.setText('')
        self.ui.codeEdit.setText('')    
        
    def show_group_box(self,mode):
        
        if(mode == 'add'):
            self.ui.addButton.setVisible(True)
            self.ui.updateButton.setVisible(False)
            self.clear_form()
        if(mode == 'update'):
            self.ui.addButton.setVisible(False)
            self.ui.updateButton.setVisible(True)
            self.load_country()
        self.ui.groupBox.setVisible(True)    
     
    def hideMessage(self):
        self.ui.labelMessage.setVisible(False)   
        
class CountryModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, countries=None, **kwargs):
        super(CountryModel,self).__init__(*args, **kwargs)
        self.countries = countries or []  
        
    def data(self,index,role):
        c=self.countries[index.row()] 
        if (role ==Qt.ItemDataRole.DisplayRole):
            return c.name.strip()
        if (role == Qt.ItemDataRole.DecorationRole):
            filename='./w20/'+c.country_code+'.png'
            return QtGui.QImage(filename)
                
                      
    def rowCount(self,index):
        return len(self.countries)
        
    
