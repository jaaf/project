'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from PyQt6 import QtCore,QtWidgets
from IngredientInventoryWidgetBase import Ui_Form as ingredientWidget
from PyQt6.QtWidgets import QDialog,QLabel,QHBoxLayout,QVBoxLayout,QWidget,QFrame,QPushButton,QGroupBox,QListView,QTextEdit,QLayout
from PyQt6.QtWidgets import QDialog,QDateEdit
from PyQt6 import QtCore
from database.fermentables.fermentable_brand import all_fbrand, find_fbrand_by_name
from database.fermentables.fermentable import all_fermentable, update_fermentable,Fermentable, add_fermentable,delete_fermentable, find_fermentable_by_id
#from database.fermentables import Fermentable, add_fermentable,delete_fermentable,find_fermentable, find_fermentable_by_id
from database.fermentables.inventory_fermentable import all_inventory_fermentable, InventoryFermentable, add_inventory_fermentable, delete_inventory_fermentable, update_inventory_fermentable
from database.hops.hop_suppliers import all_hsupplier, find_hsupplier_by_name
from database.hops.hop import all_hop, update_hop,Hop, add_hop,delete_hop, find_hop_by_id
from database.hops.inventory_hop import all_inventory_hop, InventoryHop, add_inventory_hop, delete_inventory_hop, update_inventory_hop
from dateUtils import DateUtils
from PyQt6.QtCore import Qt,QRegularExpression,QTimer
from parameters import fermentable_forms, raw_ingredients, fermentable_categories,  hop_forms,hop_purposes
from database.commons.country import all_country,find_country_by_code
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator
from PyQt6 import QtGui
import sys,datetime
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator,QIntValidator
#from ListModels import FermentableModel,InventoryFermentableModel,HopModel,InventoryHopModel
#from fermentable.FermentableNewWidget import FermentableNewWidget
#from hop.HopNewWidget import HopNewWidget

class IngredientInventoryWidget(QWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self, what,parent=None):
        super().__init__(parent)
        self.ui =ingredientWidget()
        self.ui.setupUi(self)
        
        self.what=what
       
        self.parent=parent
        self.newFermentableForm=FermentableNewWidget()
        self.newHopForm=HopNewWidget()
        self.today=datetime.date.today()
        self.current_year=self.today.year
        self.ui.importDateEdit.setDate(self.today)
        #self.set_specific(self.what)

        self.set_validators(self.what)
        
        self.complete_gui()
        self.set_models(self.what)
        self.set_connections(self.what)
          
    
    def set_specific(self,what):
        match what:

            case 'fermentable':
                #print('match fermentable dans specific')
                #initialize the various ComboBoxes
                for f in fermentable_forms:
                    self.ui.formCombo.addItem(f)
                    
                for c in fermentable_categories:
                    self.ui.categoryCombo.addItem(c)    
                    
                brands= all_fbrand() 
                self.ui.brandCombo.addItem('',None)
                for b in brands:
                    self.ui.brandCombo.addItem(b.name,b.id)
                
                for ri in raw_ingredients:
                    self.ui.rawIngredientCombo.addItem(ri)
                
                newFermentableLayout=QVBoxLayout()
                newFermentableLayout.addWidget(self.newFermentableForm)  
                self.ui.groupBoxNew.setLayout(newFermentableLayout)  
            case 'hop':
                #print('match hop dans specific')
                for h in hop_forms:
                    self.newHopForm.ui.formCombo.addItem(h)
                
                for p in hop_purposes:
                    self.newHopForm.ui.purposeCombo.addItem(p) 

                self.countries=all_country()
                self.newHopForm.ui.countryCodeCombo.addItem('')
                for c in self.countries:
                    self.newHopForm.ui.countryCodeCombo.addItem(c.name+' — '+c.country_code)
        
                suppliers= all_hsupplier() 
                self.newHopForm.ui.supplierCombo.addItem('',None)
                for s in suppliers:
                    self.newHopForm.ui.supplierCombo.addItem(s.name) 
                
                self.newHopLayout=QVBoxLayout()
                self.newHopLayout.addWidget(self.newHopForm)  
                self.ui.groupBoxNew.setLayout(self.newHopLayout)            
            

    def complete_gui(self):
        self.hide_message_public()
        self.hide_message_inventory()
        self.hide_group_box_inv()
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(False)
        self.newHopForm.ui.idEdit.setVisible(False)
        self.ui.idEdit_2.setVisible(False)
        self.ui.publicList.setSpacing(6)
        self.ui.inventoryList.setSpacing(6)

    def set_models(self,what):  
        #set the models
        match what:
            case 'fermentable':
                self.public_list=all_fermentable()
                
                self.public_list.sort(key=lambda x: (x.brand,x.name,x.version)) 
                self.model = FermentableModel(fermentables=self.public_list)
                self.ui.publicList.setModel(self.model)

                self.inventory_list=all_inventory_fermentable()
                self.inventory_list.sort(key=lambda x: str(x.purchase_date))
                self.inventory_model=InventoryFermentableModel(inventory_fermentables=self.inventory_list)
                self.ui.inventoryList.setModel(self.inventory_model)
            case 'hop':
                self.public_list=all_hop()
                self.inventory_list=all_inventory_hop()
                self.public_list.sort(key=lambda x: (x.supplier,x.name,x.crop_year))  
                self.inventory_list.sort(key=lambda x: str(x.purchase_date)) 
                self.model = HopModel(hops=self.public_list)
                self.ui.publicList.setModel(self.model)
                self.inventory_model=InventoryHopModel(inventory_hops=self.inventory_list)
                self.ui.inventoryList.setModel(self.inventory_model)    

    def set_connections(self,what) :
        #set the commections
        self.ui.newButton.clicked.connect(lambda: self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.importButton.clicked.connect(lambda: self.show_group_box('import'))
        self.ui.invEditButton.clicked.connect(self.show_group_box_inv)
        self.newHopForm.ui.hideNewButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton_2.clicked.connect(self.hide_group_box_inv)
        self.ui.publicList.clicked.connect(self.load_fermentable)
        self.ui.inventoryList.clicked.connect(self.load_inventory_fermentable)
        self.newHopForm.ui.addButton.clicked.connect(self.add)
        self.newHopForm.ui.updateButton.clicked.connect(self.update)#public
        self.newHopForm.ui.updateButton_2.clicked.connect(self.update_inventory)#inventory
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.invDeleteButton.clicked.connect(self.delete_inventory)
        #self.ui.importButton.clicked.connect(self.showImportInputs)
        self.ui.confirmImportButton.clicked.connect(self.importation)
        self.ui.groupBoxNew.clicked.connect(self.hide_message_public)
        self.ui.closeMessageButton.clicked.connect(self.hide_message_public)#public
        self.ui.closeMessageButton_2.clicked.connect(self.hide_message_inventory)#inventory
        self.ui.quantityEdit_2.textChanged.connect(self.adjust_cost)
       
        self.ui.dateButton.clicked.connect(self.toggle_calendar)

        self.ui.quantityEdit.textChanged.connect(lambda :self.cleanEdit('quantity'))
        self.ui.costEdit.textChanged.connect(lambda :self.cleanEdit('cost'))
        
        self.ui.quantityEdit_2.textChanged.connect(lambda :self.cleanEdit('quantity_2'))
        self.ui.costEdit_2.textChanged.connect(lambda :self.cleanEdit('cost_2'))

        match what:
            case 'fermentable':        
                self.newHopForm.ui.formCombo.currentIndexChanged.connect(lambda :self.cleanEdit('form')) 
                self.newHopForm.ui.brandCombo.currentIndexChanged.connect(lambda :self.cleanEdit('brand')) 
                self.newHopForm.ui.categoryCombo.currentIndexChanged.connect(lambda :self.cleanEdit('category')) 
                self.newHopForm.ui.rawIngredientCombo.currentIndexChanged.connect(lambda :self.cleanEdit('ingredient'))
                self.newHopForm.ui.versionEdit.textChanged.connect(lambda :self.cleanEdit('version'))
                self.newHopForm.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
                self.newHopForm.ui.potentialEdit.textChanged.connect(lambda: self.cleanEdit('potential'))
                self.newHopForm.ui.colorEdit.textChanged.connect(lambda: self.cleanEdit('color'))
            case 'hop':
                self.newHopForm.ui.countryCodeCombo.currentIndexChanged.connect(lambda :self.cleanEdit('country')) 
                self.newHopForm.ui.formCombo.currentIndexChanged.connect(lambda :self.cleanEdit('form')) 
                self.newHopForm.ui.purposeCombo.currentIndexChanged.connect(lambda :self.cleanEdit('purpose'))
                self.newHopForm.ui.supplierCombo.currentIndexChanged.connect(lambda :self.cleanEdit('supplier')) 
                self.newHopForm.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
                self.newHopForm.ui.cropYearEdit.textChanged.connect(lambda :self.cleanEdit('crop_year'))
                self.newHopForm.ui.supplierCombo.currentIndexChanged.connect(lambda :self.cleanEdit('supplier')) 
                self.ui.alphaEdit.textChanged.connect(lambda: self.cleanEdit('alpha'))

    def set_validators(self,what):
        match what:
            case 'fermentable':
                accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
                accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]"))
                locale=QtCore.QLocale('en')    
                self.potential_validator = QDoubleValidator(0.0,100.0,1)
                self.potential_validator.setLocale(locale)   
                self.potential_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
                self.ui.potentialEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}[\\.][0-9]{0,1}")))
                
                self.color_validator = QDoubleValidator(0.0,1500.0,1)
                self.color_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)   
                self.color_validator.setLocale(locale)   
                self.ui.colorEdit.setValidator(accepted_chars)   
                
                accepted_chars_quantity = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]{2}"))
                self.quantity_validator=QDoubleValidator(0.0,100.0,2)
                self.quantity_validator.setLocale(locale)
                self.quantity_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
                self.ui.quantityEdit.setValidator(accepted_chars_quantity)
                self.ui.quantityEdit_2.setValidator(accepted_chars_quantity)
                
                self.cost_validator=QDoubleValidator(0.0,500,2)
                self.cost_validator.setLocale(locale)
                self.cost_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
                self.ui.costEdit.setValidator(accepted_chars_quantity)
                self.ui.costEdit_2.setValidator(accepted_chars_quantity)
            case 'hop':
                
                #set the validators-----------------------------------------------------------------------------------------
                #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
                accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]"))
                locale=QtCore.QLocale('en')    
                self.alpha_validator = QDoubleValidator(0.0,20.0,1)
                self.alpha_validator.setLocale(locale)   
                self.alpha_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
                #self.ui.alphaEdit.setValidator(accepted_chars)
                
                accepted_chars_quantity = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]{2}"))
                self.quantity_validator=QDoubleValidator(0.0,1000.0,1)
                self.quantity_validator.setLocale(locale)
                self.quantity_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
                self.ui.quantityEdit.setValidator(accepted_chars_quantity)
                self.ui.quantityEdit_2.setValidator(accepted_chars_quantity)
                
                self.cost_validator=QDoubleValidator(0.0,500,2)
                self.cost_validator.setLocale(locale)
                self.cost_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
                self.ui.costEdit.setValidator(accepted_chars_quantity)
                self.ui.costEdit_2.setValidator(accepted_chars_quantity)
                
                accepted_chars_crop_year = QRegularExpressionValidator(QRegularExpression("20[0-9]{2}"))
                self.crop_year_validator=QIntValidator(2019,self.current_year) 
                self.crop_year_validator.setLocale(locale)
                self.newHopForm.ui.cropYearEdit.setValidator(accepted_chars_crop_year)    
                
                pass
    #------------------------------------------------------------------------------------------------    
    def add(self):
        data=self.read_new_form()
        if(data != False):
            result= add_fermentable(data)
            if(result == 'OK'):
                self.cleanNewForm()
                self.set_message_public('success', 'Le fermentable a été correctement enregistré')
                self.ui.labelMessage.setVisible(True)
                self.model.fermentables.append(data)
                self.public_list.sort(key=lambda x: (x.brand,x.name,x.version))
                self.model.layoutChanged.emit()
                self.hide_group_boxes()
            else:
                self.set_message_public('failure', result),
                self.ui.labelMessage.setVisible(True)  
     
    #--------------------------------------------------------------------------           
    def update(self):
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.model.fermentables[index.row()]
            read_item=self.read_new_form()
            if(read_item !=False):
        #thi id has been set while loading form with selected item
                read_item.id=self.ui.idEdit.text()
                #attempt update in database
                result = update_fermentable(read_item)
                if(result == 'OK'):
                    self.cleanNewForm()
                    self.set_message_public('success', 'Le fermentable a été correctement enregistré')
                    self.ui.labelMessage.setVisible(True)
        
                    selection=self.model.fermentables[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.brand=read_item.brand
                    selection.form=read_item.form
                    selection.category=read_item.category
                    selection.color=read_item.color
                    selection.potential=read_item.potential
                    selection.raw_ingredient=read_item.raw_ingredient
                    selection.version=read_item.version
                    selection.link=read_item.link
                    selection.notes=read_item.notes
                    self.public_list.sort(key=lambda x: (x.brand,x.name,x.version))
                    self.model.layoutChanged.emit()
                    #the update may affect the inventory fermentables
                    self.inventory_model.inventory_fermentables=all_inventory_fermentable()
                    self.inventory_model.layoutChanged.emit()
                
    #------------------------------------------------------------------------------      
    def update_inventory(self):
        
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.inventory_model.inventory_fermentables[index.row()]
            read_item=self.readUpdateInventoryForm()
            if(read_item != False):
                read_item.id=self.ui.idEdit_2.text()
                read_item.fermentable_id=selection.fermentable_id
                #update in database
                result =update_inventory_fermentable(read_item)
                if(result == 'OK'):
                    self.set_message_inventory('success', 'Le fermentable d\'inventaire a été correctement enregistré')
                    self.ui.labelMessage_2.setVisible(True)
                    selection.quantity=read_item.quantity
                    selection.cost=read_item.cost
                    self.inventory_model.layoutChanged.emit()
                    self.hide_group_box_inv()
        
                else:
                    self.set_message_inventory('failure', result),
                    self.ui.labelMessage_2.setVisible(True)       
                          
    #-------------------------------------------------------------------------------            
    def delete(self):
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            selected_item= self.model.fermentables[index.row()]
            #delete from database
            result=delete_fermentable(selected_item.id)
            if (result == 'OK'):
                self.set_message_public('success', 'Le fermentable a été correctement supprimé')
                self.ui.labelMessage.setVisible(True)
                # Remove the item and refresh.
                del self.model.fermentables[index.row()]
                self.model.layoutChanged.emit()
                # Clear the selection (as it is no longer valid).
                self.ui.publicList.clearSelection()
            else:
                self.set_message_public('failure', result)
                self.ui.labelMessage.setVisible(True)    
                
    #--------------------------------------------------------------------------------
    def delete_inventory(self):
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.inventory_model.inventory_fermentables[index.row()]
            #delete from database
            result=delete_inventory_fermentable(selected_item.id)
            if (result == 'OK'):
                self.set_message_inventory('success','Le fermentable d\'inventaire a été correctement supprimé') 
                self.ui.labelMessage_2.setVisible(True)
                del self.inventory_model.inventory_fermentables[index.row()]
                self.inventory_model.layoutChanged.emit()
                self.ui.inventoryList.clearSelection()
            else:
                self.set_message_inventory('failure',result)
                self.ui.labelMessage_2.setVisible(True)    
                
    #------------------------------------------------------------------------------------            
    def importation(self):
    #import a fermentable into the inventory
        #import form is for quantity and cost
        #print('importing inventory fermentable')
        read_item=self.readImportForm()
        if(read_item != False):
            #print('read_item good')
            #print(read_item)
            result=add_inventory_fermentable(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success', 'Le fermentable a été correctement importé')
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_fermentables.append(read_item) 
                #self.inventory_list=all_inventory_fermentable()
                self.inventory_list.sort(key=lambda x: str(x.purchase_date))
                self.inventory_model.layoutChanged.emit()
                self.hide_group_boxes()
            else:
                self.set_message_public('failure',result)
                self.ui.labelMessage.setVisible(True) 
        else:
            pass
    
    #---------------------------------------------------------------------------------------
    def set_message_public(self, style, text):
        self.ui.labelMessage.setText(text)
        if(style =='success'):
            self.ui.labelMessage.setStyleSheet('background-color:green; color: white;padding:10px')
            self.timer=QTimer()
            self.timer.timeout.connect(self.hide_message_public)
            self.timer.start(3000) 
        if(style == 'failure'):
                self.ui.labelMessage.setStyleSheet('background-color:red; color: white;padding:10px')
                self.ui.closeMessageButton.setVisible(True)
        self.ui.labelMessage.setVisible(True)
    #----------------------------------------------------------------------------------------           
    def set_message_inventory(self, style, text):
        self.ui.labelMessage_2.setText(text)
        if(style =='success'):
            self.ui.labelMessage_2.setStyleSheet('background-color:green; color: white;padding:10px')
            self.timer=QTimer()
            self.timer.timeout.connect(self.hide_message_inventory)
            self.timer.start(3000) 
        if(style == 'failure'):
                self.ui.labelMessage_2.setStyleSheet('background-color:red; color: white;padding:10px')
                self.ui.closeMessageButton_2.setVisible(True)        
        self.ui.labelMessage_2.setVisible(True)
    #-----------------------------------------------------------------------------------------          
    def   hide_message_public(self):
        self.ui.labelMessage.setVisible(False)  
        self.ui.closeMessageButton.setVisible(False) 
      
    #------------------------------------------------------------------------------------------           
    def   hide_message_inventory(self):
        self.ui.labelMessage_2.setVisible(False)  
        self.ui.closeMessageButton_2.setVisible(False)      
    
    #-------------------------------------------------------------------------------------------    
    def toggle_calendar(self):
        if(self.ui.calendarWidget.isVisible()==False):
            self.ui.calendarWidget.setVisible(True)
            self.ui.dateButton.setStyleSheet('background-color:red;color:white')
            self.ui.dateButton.setText('X')
            self.ui.calendarWidget.setSelectedDate(self.ui.importDateEdit.date())
        else:
            date=self.ui.calendarWidget.selectedDate()
            self.ui.importDateEdit.setDate(date)
            self.ui.calendarWidget.setVisible(False)
            self.ui.dateButton.setStyleSheet('background-color:green;color:white')
            self.ui.dateButton.setText('')
            self.ui.calendarWidget.setSelectedDate(self.ui.importDateEdit.date())
    #------------------------------------------------------------------------------------------

    #------------------------------------------------)
    def load_fermentable(self):
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.fermentables[index.row()]
            self.ui.idEdit.setText(str(selected_item.id))
            self.ui.nameEdit.setText(selected_item.name)
            self.ui.brandCombo.setCurrentText(selected_item.brand)
            self.ui.versionEdit.setText(selected_item.version)
            self.ui.formCombo.setCurrentText(selected_item.form)
            self.ui.categoryCombo.setCurrentText(selected_item.category)
            self.ui.potentialEdit.setText(str(selected_item.potential))
            self.ui.colorEdit.setText(str(selected_item.color))
            self.ui.rawIngredientCombo.setCurrentText(selected_item.raw_ingredient)
            self.ui.linkEdit.setText(selected_item.link)
            self.ui.notesEdit.setText(selected_item.notes)
     
    #-----------------------------------------------------------------------------------------------        
    def load_inventory_fermentable(self):
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0] 
            selected_item=self.inventory_model.inventory_fermentables[index.row()]
            self.ui.idEdit_2.setText(str(selected_item.id))
            self.ui.quantityEdit_2.setText(str(selected_item.quantity))
            self.ui.costEdit_2.setText(str(selected_item.cost))
                 
    #-----------------------------------------------------------------------------------------------                    
    def read_new_form(self):
    #read the new fermentable form and check inputs validates
    #returns False if not validated, returns new fermentable otherwise
        validated=True
        name=self.ui.nameEdit.text().upper()
        if(name ==''):
            self.ui.nameEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        brand=self.ui.brandCombo.currentText()
        if(brand == ''):
            self.ui.brandCombo.setStyleSheet('background-color: red; color:white;')
            validated=False
        form=self.ui.formCombo.currentText()
        if(form == ''):
            self.ui.formCombo.setStyleSheet('background-color: red; color:white;')
            validated=False
        category=self.ui.categoryCombo.currentText()
        if(category ==''):
            self.ui.categoryCombo.setStyleSheet('background-color: red; color:white;')
            validated=FermentableSelector
        color=self.ui.colorEdit.text()
        color=color.replace(',','.')
        r=self.color_validator.validate(color,0)
        if(r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.colorEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        potential=self.ui.potentialEdit.text()
        r=self.potential_validator.validate(potential,0) 
        if( r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.potentialEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        raw_ingredient=self.ui.rawIngredientCombo.currentText()
        if(raw_ingredient==''):
            self.ui.rawIngredientCombo.setStyleSheet('background-color: red; color:white;')
            validated=False
        version=self.ui.versionEdit.text()
        if(version ==''):
            self.ui.versionEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        link=self.ui.linkEdit.text() 
        notes=self.ui.notesEdit.toPlainText()
        if(validated == True):
            f=Fermentable (None,brand,name,form,category,color,potential,raw_ingredient,version,link,notes)  
            return f
        else:
            return False   

     #------------------------------------------------------------------------------------------------        
    def readImportForm(self):
    #read the import fermentable form and check inputs validated
    #returns Fals if not validated, returns a new inventory_fermentable otherwise
        validated=True
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.fermentables[index.row()]
            quantity=self.ui.quantityEdit.text()
            r=self.quantity_validator.validate(quantity,0)
            if(r[0] !=QtGui.QValidator.State.Acceptable):
                self.ui.quantityEdit.setStyleSheet('background-color: red; color:white;')
                validated=False
                #print('bad quantity')
            cost=self.ui.costEdit.text()
            r=self.cost_validator.validate(cost,0)
            if(r[0] != QtGui.QValidator.State.Acceptable):
                self.ui.costEdit.setStyleSheet( 'background-color: red; color:white;')
                validated = False
                #print('bat cost')
            purchase_date=self.ui.importDateEdit.date()
            pd=purchase_date.toString('yyyy-MM-dd')
            #print(pd)   
            if(validated == True):
                #print('validated is True')
                inventory_ferm=InventoryFermentable(None,selected_item.id,quantity,cost,pd,False) 
                return inventory_ferm
            else:
                return False
        else:
            self.set_message_public('failure','Vous devez sélectionner un fermentable !')
            return False

    #---------------------------------------------------------------------------------------------       
    def readUpdateInventoryForm(self):
    #read the import fermentable form and check inputs validated
    #returns Fals if not validated, returns a new inventory_fermentable otherwise
        validated=True
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.inventory_model.inventory_fermentables[index.row()]
            quantity=self.ui.quantityEdit_2.text()
            r=self.quantity_validator.validate(quantity,0)
            if(r[0] !=QtGui.QValidator.State.Acceptable):
                self.ui.quantityEdit_2.setStyleSheet('background-color: red; color:white;')
                validated=False
            cost=self.ui.costEdit_2.text()
            r=self.cost_validator.validate(cost,0)
            if(r[0] != QtGui.QValidator.State.Acceptable):
                self.ui.costEdit_2.setStyleSheet( 'background-color: red; color:white;')
                validated = False
            if(validated == True):
                inventory_ferm=InventoryFermentable(None,selected_item.id,quantity,cost,selected_item.frozen) 
                return inventory_ferm
            else:
                return False
        else:
            return False   
    
    #-----------------------------------------------------------------------------------------------
    def cleanEdit(self, what):
        match what:
            case 'quantity':
                self.ui.quantityEdit.setStyleSheet('background-color: white;color:black;')
            case 'cost':
                self.ui.costEdit.setStyleSheet('background-color: white;color:black;')
            case 'name':
                self.ui.nameEdit.setStyleSheet('background-color: white;color:black;') 
            case 'brand':
                self.ui.brandCombo.setStyleSheet('background-color: white;color:black;') 
            case 'category':
                self.ui.categoryCombo.setStyleSheet('background-color: white;color:black;')
            case 'form':
                self.ui.formCombo.setStyleSheet('background-color: white;color:black;')
            case 'potential':
                self.ui.potentialEdit.setStyleSheet('background-color: white;color:black;')
            case 'color':
                self.ui.colorEdit.setStyleSheet('background-color: white;color:black;')
            case 'ingredient':
                self.ui.rawIngredientCombo.setStyleSheet('background-color: white;color:black;')
            case 'form':
                self.ui.formCombo.setStyleSheet('background-color: white;color:black;')    
            case 'quantity_2':
                self.ui.quantityEdit_2.setStyleSheet('background-color: white;color:black;')
            case 'version':
                self.ui.versionEdit.setStyleSheet('background-color: white;color:black;')
            
            case 'cost_2':
                self.ui.costEdit_2.setStyleSheet('background-color: white;color:black;')

    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        self.ui.colorEdit.setStyleSheet('background-color: white; color:black;')
        self.ui.potentialEdit.setStyleSheet('background-color: white; color:black;')
        self.ui.nameEdit.setText('')
        self.ui.brandCombo.setCurrentIndex(0)
        self.ui.formCombo.setCurrentIndex(0)
        self.ui.categoryCombo.setCurrentIndex(0) 
        self.ui.rawIngredientCombo.setCurrentIndex(0)
        self.ui.colorEdit.setText('')  
        self.ui.potentialEdit.setText('')   
        self.ui.versionEdit.setText('')  
        self.ui.linkEdit.setText('') 
        self.ui.notesEdit.setText('')    
        
    def cleanImportForm(self):
        self.ui.quantityEdit.setStyleSheet('background-color: white; color:black;')
        self.ui.costEdit.setStyleSheet('background-color: white; color:black;')
        self.ui.quantityEdit.setText('')
        self.ui.costEdit.setText('')   
        
    def showNewInputs(self,keep=False):
        self.ui.groupBoxNew.setVisible(True)
        self.ui.groupBoxImport.setVisible(False) 
        self.cleanImportForm()
        if(keep == False):
            self.cleanNewForm()
        
    def showImportInputs(self):
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(True)   
        self.cleanNewForm() 
    
    def show_group_box_inv(self):
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:

            self.ui.groupBoxImport_2.setVisible(True)
            self.ui.checkBox.setChecked(True)
        else:
            self.set_message_inventory('failure','Vous devez sélectionner un fermentable')    
        
    def hide_group_boxes(self):
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(False)
        self.ui.inventoryList.clearSelection()
        self.ui.publicList.clearSelection()
    
    def hide_group_box_inv(self):
        self.ui.groupBoxImport_2.setVisible(False)   
        self.ui.inventoryList.clearSelection()
         
    def show_group_box(self,mode):
        if(mode == 'add'):
            self.showNewInputs()
            self.ui.addButton.setVisible(True)
            self.ui.updateButton.setVisible(False) 
        else:

            indexes=self.ui.publicList.selectedIndexes()
            if indexes:
                if(mode == 'update'):
                    self.load_fermentable()
                    self.showNewInputs(True)
                    self.ui.addButton.setVisible(False)
                    self.ui.updateButton.setVisible(True) 
                if(mode == 'import'):
                    self.showImportInputs()
            else:
                self.set_message_public('failure','Vous devez sélectionner un fermentable')        


         #--------------------------------------------------------------------------------------------
def adjust_cost(self):
        #print('adjusting cost')
        if(self.ui.checkBox.isChecked()==False) :
            return 
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0] 
            selected_item=self.inventory_model.inventory_miscs[index.row()]  
        else: 
            return
        if(selected_item.cost != '' and self.ui.invQuantityEdit.text() !='' and selected_item.quantity != '' )   : 
            try:#to avoid crash in quantity and cost already at zero. Needs unbinding
                new_cost=float(selected_item.cost )* float(self.ui.invQuantityEdit.text())/float(selected_item.quantity)
                self.ui.invCostEdit.setText('{:0.2f}'.format(new_cost))
            except:
                pass

        
