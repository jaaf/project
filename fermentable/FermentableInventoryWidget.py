import datetime
import re
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QRegularExpression, Qt, QTimer
from PyQt6.QtGui import QDoubleValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import (QCheckBox, QHBoxLayout, QLineEdit, QPushButton,QListView,
                             QVBoxLayout, QWidget)
from CheckableComboBox import CheckableComboBox, MyStandardItem
from ConfirmationDialog import ConfirmationDialog
from database.fermentables.fermentable import (Fermentable, add_fermentable,
                                               all_fermentable,
                                               delete_fermentable,
                                               find_fermentable_by_id,
                                               update_fermentable)
from database.fermentables.fermentable_brand import (all_fbrand,
                                                     find_fbrand_by_name)
#from database.fermentables import Fermentable, add_fermentable,delete_fermentable,find_fermentable, find_fermentable_by_id
from database.fermentables.inventory_fermentable import (
    InventoryFermentable, add_inventory_fermentable, all_inventory_fermentable,
    delete_inventory_fermentable, update_inventory_fermentable)
from dateUtils import DateUtils
from datetime import date
from fermentable.FermentableInventoryWidgetBase import \
    Ui_Form as fermentableInventoryWgt
from HelpMessage import HelpMessage
from parameters import (fermentable_categories, fermentable_forms,
                        get_fermentable_category_name, raw_ingredients)
from pathlib import Path


class FermentableInventoryWidget(QWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =fermentableInventoryWgt()
        self.ui.setupUi(self)
        self.id=id
        self.this_file_path=Path(__file__).parent

        #propage app font
        app = QtWidgets.QApplication.instance()
        #as use of setStyleSheet prevents correct font propagation. Prepend all style with this prefix to fix this issue
        self.font_style_prefix='font:'+str(app.font().pointSize())+'pt '+app.font().family()+';'
        self.setFont(app.font())
        mylist=self.findChildren(QWidget)
        app_font=app.font()
        for item in mylist:
            item.setFont(app_font)

        self.today=datetime.date.today()
        self.icon_path='base-data/icons/'
        self.ui.importDateEdit.setDate(self.today)
        self.source_selection=None
        self.destination_selection=None
        self.hide_main_mode_buttons()
        self.hide_inventory_mode_buttons()
        self.ui.newButton.setVisible(True)
        #initialize the various ComboBoxes
        for f in fermentable_forms:
            #self.ui.formCombo.addItem(f[1],f[0])
            self.ui.formCombo.addItem(f)
            
        for c in fermentable_categories:
            #self.ui.categoryCombo.addItem(c[1],c[0])    #text, data
            self.ui.categoryCombo.addItem(c)    #text, data
            
        self.brands= all_fbrand() 
        self.ui.brandCombo.addItem('',None)
        for b in self.brands:
            self.ui.brandCombo.addItem(b.name,b.id)
        
        for ri in raw_ingredients:
            #self.ui.rawIngredientCombo.addItem(ri[1],ri[0]) # text , data
            self.ui.rawIngredientCombo.addItem(ri)
        #for filters
        self.active_brands=[]
        self.active_categories=[]
        self.active_ingredients=[]
        self.set_validators()
        self.complete_gui()
        self.set_connections()

    #-------------------------------------------------------------------------
    @QtCore.pyqtSlot()
    def on_brand_closedPopup(self):
        self.active_brands=self.brandFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.filter_list()  
    
    #----------------------------------------------
    def toggle_brand_filter(self):
        if self.brand_checkbox.isChecked():
            self.brandFilterCombo.setVisible(True)
        else:
            self.brandFilterCombo.setVisible(False)
        self.filter_list()
    
    #---------------------------------------------
    @QtCore.pyqtSlot()
    def on_category_closedPopup(self):
        self.active_categories=self.categoryFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.filter_list()       
    
    #----------------------------------------------
    def toggle_category_filter(self):
        if self.category_checkbox.isChecked():
            self.categoryFilterCombo.setVisible(True)
        else:
            self.categoryFilterCombo.setVisible(False)
        self.filter_list()
        
    #---------------------------------------------
    @QtCore.pyqtSlot()
    def on_ingredient_closedPopup(self):
        self.active_ingredients=self.ingredientFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.filter_list()       
    
    #----------------------------------------------
    def toggle_ingredient_filter(self):
        if self.ingredient_checkbox.isChecked():
            self.ingredientFilterCombo.setVisible(True)
        else:
            self.ingredientFilterCombo.setVisible(False)
        self.filter_list()
          
    
    #-----------------------------------------------------------------------------------------------
    def filter_list(self):
        items=self.public_list
        filtered=list(filter(lambda x:\
                                  (x.brand in self.active_brands or not self.brand_checkbox.isChecked()) and \
                                    (x.category in self.active_categories or not self.category_checkbox.isChecked()) and \
                                        (x.raw_ingredient in self.active_ingredients or not self.ingredient_checkbox.isChecked())\
                                            ,items ))
        
        filtered.sort(key=lambda x: (x.brand,x.name,x.version))
        self.model.fermentables=filtered 
        self.model.layoutChanged.emit()  

    #------------------------------------------------------------------------------------------------
    def search_in_name(self):
        self.filter_list()#we start with the filtered list
        pattern=self.searchEdit.text()
        print('searching in name '+pattern)
        if pattern != '':
            items=self.model.fermentables #we search only in the filtered list
            sorted_array=list(filter(lambda x: re.search(pattern, x.name,re.IGNORECASE),items)) 
            self.model.fermentables=sorted_array
            self.model.layoutChanged.emit()
           
    #--------------------------------------------------------------------------------------------------
    def complete_gui(self):
        self.hide_message_public()
        self.hide_message_inventory()
        self.hide_group_box_inv()
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(False)
        self.ui.idEdit.setVisible(False)
        self.ui.idEdit_2.setVisible(False)
        self.ui.publicList.setSpacing(6)
        self.ui.inventoryList.setSpacing(6)
        
        #set the models
        self.public_list=all_fermentable()
        self.public_list.sort(key=lambda x: (x.brand,x.name,x.version)) 
        self.model = FermentableModel(fermentables=self.public_list)
        self.ui.publicList.setModel(self.model)

        self.inventory_list=all_inventory_fermentable()
        self.inventory_list.sort(key=lambda x: str(x.purchase_date))
        self.inventory_model=InventoryFermentableModel(inventory_fermentables=self.inventory_list)
        self.ui.inventoryList.setModel(self.inventory_model)
        self.mode_import='add' #the import button has two roles: adding to the inventory or replacing in inventory

        #set the filters of the public list
        self.filterLayout=QHBoxLayout()
        self.brandLayout=QVBoxLayout()
        self.brandFilterCombo=CheckableComboBox()       
        self.brands=all_fbrand()
        for brand in self.brands:
            item = MyStandardItem(brand.name)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.brandFilterCombo.model().appendRow(item) 
        self.brand_checkbox=QCheckBox('Filtrer les marques')
        self.brandLayout.addWidget(self.brand_checkbox)
        self.brandLayout.addWidget(self.brandFilterCombo)
        self.filterLayout.addLayout(self.brandLayout)
        self.brandFilterCombo.setVisible(False)
        

        self.categoryLayout=QVBoxLayout()
        self.categoryFilterCombo=CheckableComboBox()       
        self.categories=fermentable_categories
        for category in self.categories:
            #item = MyStandardItem(category[1],category[0])
            item = MyStandardItem(category)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.categoryFilterCombo.model().appendRow(item)     
        self.category_checkbox=QCheckBox('Filtrer les catégories')
        self.categoryLayout.addWidget(self.category_checkbox)
        self.categoryLayout.addWidget(self.categoryFilterCombo)
        self.filterLayout.addLayout(self.categoryLayout)
        self.categoryFilterCombo.setVisible(False)

        self.ingredientLayout=QVBoxLayout()
        self.ingredientFilterCombo=CheckableComboBox()       
        self.ingredients=raw_ingredients#import from parameters
        for ingredient in self.ingredients:
            item = MyStandardItem(ingredient)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.ingredientFilterCombo.model().appendRow(item)   
        self.ingredient_checkbox=   QCheckBox('Filtrer les ingrédients')   
        self.ingredientLayout.addWidget(self.ingredient_checkbox)
        self.ingredientLayout.addWidget(self.ingredientFilterCombo)
        self.filterLayout.addLayout(self.ingredientLayout)
        self.ingredientFilterCombo.setVisible(False)

        self.searchEdit=QLineEdit()
        self.searchEdit.setPlaceholderText('🔍Entrée en fin de saisie')
        self.filterLayout.addWidget(self.searchEdit)
        self.searchHelpButton=QPushButton('?')
        self.searchHelpButton.setFixedWidth(24)
        self.searchHelpButton.setStyleSheet(self.font_style_prefix+'background-color:green; color:White')
        self.searchHelpButton.setToolTip("Obtenir de l'aide sur le filtrage et la recherche")
        self.filterLayout.addWidget(self.searchHelpButton)
        #self.filterLayout.addStretch()
        self.ui.filterGroupBox.setLayout(self.filterLayout)
        self.ui.labelInventoryTitle.setStyleSheet(self.font_style_prefix+"font-weight: 600; ") 
        self.ui.labelPublicTitle.setStyleSheet(self.font_style_prefix+"font-weight: 600; ")
        self.ui.publicList.setStyleSheet("QListView{border: 2px solid green;}"\
                                         "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                            "QListView::item{border-bottom:2px solid gray}")
        self.ui.inventoryList.setStyleSheet("QListView{border: 2px solid green;}"\
                                            "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                                "QListView::item{border-bottom:2px solid gray}")



    def set_connections(self) :
        #set the commections
        self.brandFilterCombo.closedPopup.connect(self.on_brand_closedPopup)
        self.brand_checkbox.stateChanged.connect(self.toggle_brand_filter)
        self.categoryFilterCombo.closedPopup.connect(self.on_category_closedPopup)
        self.category_checkbox.stateChanged.connect(self.toggle_category_filter)
        self.ingredientFilterCombo.closedPopup.connect(self.on_ingredient_closedPopup)
        self.ingredient_checkbox.stateChanged.connect(self.toggle_ingredient_filter)
        self.searchEdit.editingFinished.connect(self.search_in_name)

        self.ui.newButton.clicked.connect(lambda: self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.importButton.clicked.connect(lambda: self.show_group_box('import'))
        self.ui.invEditButton.clicked.connect(self.show_group_box_inv)
        self.ui.hideNewButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton_2.clicked.connect(self.hide_group_box_inv)
        self.ui.publicList.clicked.connect(self.select_source)
        self.ui.inventoryList.clicked.connect(self.select_destination)
        self.ui.addButton.clicked.connect(self.add)
        self.ui.updateButton.clicked.connect(self.update)#public
        self.ui.updateButton_2.clicked.connect(self.update_inventory)#inventory
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.invDeleteButton.clicked.connect(self.delete_inventory)
        self.ui.confirmImportButton.clicked.connect(lambda: self.importation(self.mode_import))
        self.ui.groupBoxNew.clicked.connect(self.hide_message_public)
        self.ui.closeMessageButton.clicked.connect(self.hide_message_public)#public
        self.ui.closeMessageButton_2.clicked.connect(self.hide_message_inventory)#inventory
        self.ui.invQuantityEdit.textChanged.connect(self.adjust_cost)
       
        self.ui.quantityEdit.textChanged.connect(lambda :self.cleanEdit('quantity'))
        self.ui.costEdit.textChanged.connect(lambda :self.cleanEdit('cost'))
        self.ui.potentialEdit.textChanged.connect(lambda: self.cleanEdit('potential'))
        self.ui.colorEdit.textChanged.connect(lambda: self.cleanEdit('color'))
        self.ui.invQuantityEdit.textChanged.connect(lambda :self.cleanEdit('quantity_2'))
        self.ui.invCostEdit.textChanged.connect(lambda :self.cleanEdit('cost_2'))
        self.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
        self.ui.formCombo.currentIndexChanged.connect(lambda :self.cleanEdit('form')) 
        self.ui.brandCombo.currentIndexChanged.connect(lambda :self.cleanEdit('brand')) 
        self.ui.categoryCombo.currentIndexChanged.connect(lambda :self.cleanEdit('category')) 
        self.ui.rawIngredientCombo.currentIndexChanged.connect(lambda :self.cleanEdit('ingredient'))
        self.ui.versionEdit.textChanged.connect(lambda :self.cleanEdit('version'))
        self.searchHelpButton.clicked.connect(lambda: self.show_contextual_help('filter'))
    
    #------------------------------------------------------------------
    def show_contextual_help(self,what):
        helpPopup=HelpMessage() 
        filename=(self.this_file_path/"../help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
        match what:
            case 'filter':
                helpPopup.set_title('À propos du filtrage et de la recherche')
                filename=(self.this_file_path/"../help/FermentableSearchHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
           
        helpPopup.exec()
    #------------------------------------------------------------------------------------------
    def set_validators(self):
     
        locale=QtCore.QLocale('en')    
        self.potential_validator = QDoubleValidator(0.0,100.0,1)
        self.potential_validator.setLocale(locale)   
        self.potential_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.potentialEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,2}[\\.][0-9]{0,1}")))
        
        self.color_validator = QDoubleValidator(0.0,1500.0,1)
        self.color_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)   
        self.color_validator.setLocale(locale)   
        self.ui.colorEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,4}[\\.][0-9]{0,1}")))   
         
       
        self.quantity_validator=QDoubleValidator(0.0,100.0,2)
        self.quantity_validator.setLocale(locale)
        self.quantity_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.quantityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,2}[\\.][0-9]{0,3}")))
        self.ui.invQuantityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,2}[\\.][0-9]{0,3}")))
        
        self.cost_validator=QDoubleValidator(0.0,500.0,2)
        self.cost_validator.setLocale(locale)
        self.cost_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.costEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-4]?[0-9]{0,2}[\\.][0-9]{0,2}")))
        self.ui.invCostEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-4]?[0-9]{0,2}[\\.][0-9]{0,2}")))
    #------------------------------------------------------------------------------------------------------
    def select_destination(self):
        #select an element in the destination list either for deletion, or update, or replacement
        old_selection=self.destination_selection
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            self.destination_selection=self.inventory_model.inventory_fermentables[index.row()]
            if (old_selection==self.destination_selection):  
                self.clear_selection('destination')
        else:
            self.clear_selection('destination') 
            #self.reset_form()
        self.adapt_form()    

    #------------------------------------------------------------------------------
    def select_source(self):
        #select an item in the source (public) list for addition to the destination list
        old_selection=self.source_selection
        indexes =self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0] 
            self.source_selection=self.model.fermentables[index.row()]
            if (old_selection==self.source_selection):  
                self.clear_selection('source')   
            self.load_fermentable()
        else:
            self.clear_selection('source') 
        self.adapt_form()        
    #----------------------------------------------------------------------------------------
    def clear_selection(self,what):
        #used when clicking on an already selected item
        match what:
            case 'source':
                self.source_selection=None
                self.ui.publicList.clearSelection() 
                #self.reset_form()
                #to delete the inverted highlight background on the last selected item
                self.ui.publicList.clearFocus()
            case 'destination':
                self.destination_selection=None
                self.ui.inventoryList.clearSelection()
                #to delete the inverted highlight background on the last selected item
                self.ui.inventoryList.clearFocus()
            case 'both':
                self.ui.inventoryList.clearSelection()
                self.destination_selection=None  
                self.ui.inventoryList.clearFocus()
                self.ui.publicList.clearSelection() 
                self.source_selection=None
                self.ui.publicList.clearFocus()          
                #-----------------------------------------------------------------------------------------
    def adapt_form(self):
        #adapt the form for additional values depending on the operation to perform
    
        if(self.source_selection and self.destination_selection):
            self.prepare_form_for_replace()
        if(self.source_selection and not(self.destination_selection)):
            self.prepare_form_for_add()
        if(not self.source_selection and self.destination_selection):
            self.prepare_form_for_update()
        if( not self.source_selection and not self.destination_selection):
            self.hide_all_controls()
            self.ui.newButton.setVisible(True)
    #---------------------
    def hide_all_controls(self):
        self.hide_group_boxes()
        self.ui.importButton.setVisible(False)
        self.ui.deleteButton.setVisible(False)
        self.ui.editButton.setVisible(False)
        self.ui.newButton.setVisible(False)
        self.ui.invDeleteButton.setVisible(False)
        self.ui.invEditButton.setVisible(False)

    #------------------------------------------------------------------------------------------------
    def showEvent(self,event): 
        self.inventory_model.inventory_fermentables=all_inventory_fermentable()
        self.inventory_model.layoutChanged.emit()     
        self.model.fermentables=all_fermentable()
        self.model.layoutChanged.emit() 
    #------------------------------------------------------------------------------------------------    
    def prepare_form_for_replace(self):
        self.ui.importButton.setText('Remplacer')
        self.ui.confirmImportButton.setText('Confirmer le remplacement')
        self.ui.importButton.setVisible(True)
        self.ui.deleteButton.setVisible(False)
        self.ui.quantityEdit.setVisible(True)
        self.ui.quantityLabel.setVisible(True)
        self.ui.quantityUnitLabel.setVisible(True) 
        self.ui.quantityEdit.setText(str(round(float(self.destination_selection.quantity),3)))
        self.ui.costEdit.setText(str(round(float(self.destination_selection.cost),2)))
        self.hide_inventory_mode_buttons()
        self.mode_import='replace'
    #---------------------------------------------------------------------------------------------
    def prepare_form_for_add(self):
        #prepare the form for additional values when adding an item from source list to destination list
        self.ui.importButton.setText("Ajouter à l’inventaire")
        self.ui.confirmImportButton.setText("Confirmer l'importation")
        self.ui.importButton.setVisible(True)
        self.ui.deleteButton.setVisible(True)
        self.ui.editButton.setVisible(True)
        self.ui.quantityEdit.setText('')  
        self.ui.quantityLabel.setVisible(True)
        self.ui.quantityUnitLabel.setVisible(True)
        self.ui.importDateEdit.setVisible(True)
        self.ui.dateLabel.setVisible(True)
        self.ui.costEdit.setText('')
        self.mode_import='add'
    #--------------------------------------------------------------------------------------------
    def prepare_form_for_update(self):
        #prepare update or deletion in inventory list
        self.ui.invEditButton.setVisible(True)
        self.ui.invDeleteButton.setVisible(True)
        self.ui.importButton.setVisible(False)
        self.ui.invQuantityEdit.setVisible(True)
        self.ui.invQuantityEdit.setText(str(round(float(self.destination_selection.quantity),3)))  
        self.ui.quantityUnitLabel.setVisible(True)
        self.ui.invCostEdit.setVisible(True)
        self.ui.invCostEdit.setText(str(round(float(self.destination_selection.cost),2)))
        self.ui.invCostLabel.setVisible(True)

    #--------------------------------------------------------------------------------------------
    def add(self):
        #adding a new fermentable in the public list
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
        self.clear_selection('both') 
    #--------------------------------------------------------------------------           
    def update(self):
        #updating a fermentable in the public list
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
        self.clear_selection('both')         
    #------------------------------------------------------------------------------      
    def update_inventory(self):
        #updating an inventoryFermentable in the inventory list
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.inventory_model.inventory_fermentables[index.row()]
            read_item=self.readUpdateInventoryForm()
            if(read_item != False):
                read_item.id=selection.id
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
            else:
                self.set_message_inventory('failure','Vous devez sélectionner un fermentable')   
        self.clear_selection('both')       
             
    #-------------------------------------------------------------------------------           
    def delete(self):
        msgBox=ConfirmationDialog()
        msgBox.setTitle('Confirmer suppression')
        msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
        msgBox.setMessage('Vous êtes sur le point de supprimer un fermentable de la liste publique. Cette suppression sera définitive. \n Confirmez-vous la suppression ?') 
        msgBox.setCancelButtonText('Non. Ne pas supprimer')
        msgBox.setConfirmButtonText('Oui. Supprimer.')
        confirm=msgBox.exec()   
        if(confirm == 1):
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
            else:
                self.set_message_public('failure','Vous devez sélectionner un fermentable')               
            self.clear_selection('both')    
    
    #--------------------------------------------------------------------------------
    def delete_inventory(self,message):
        msgBox=ConfirmationDialog()
        msgBox.setTitle('Confirmer suppression')
        
        msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
        msgBox.setMessage('Vous êtes sur le point de supprimer un achat de fermentable de votre inventaire. Cette suppression sera définitive. \n Confirmez-vous la suppression ?') 
        msgBox.setCancelButtonText('Non. Ne pas supprimer')
        msgBox.setConfirmButtonText('Oui. Supprimer.')
        confirm=msgBox.exec()   
        if(confirm == 1):
            indexes = self.ui.inventoryList.selectedIndexes()
            if indexes:
                index=indexes[0]
                selected_item=self.inventory_model.inventory_fermentables[index.row()]
                #delete from database
                result=delete_inventory_fermentable(selected_item.id)
                if (result == 'OK') :
                    self.set_message_inventory('success','Le fermentable d\'inventaire a été correctement supprimé') 
                    self.ui.labelMessage_2.setVisible(True)
                    del self.inventory_model.inventory_fermentables[index.row()]
                    self.inventory_model.layoutChanged.emit()
                    self.ui.inventoryList.clearSelection()
                else:
                    self.set_message_inventory('failure',result)
                    self.ui.labelMessage_2.setVisible(True)    
            else:
                self.set_message_inventory('failure','Vous devez sélectionner un fermentable')      
            self.clear_selection('both')      
    
    #------------------------------------------------------------------------------------            
    def importation(self,mode):
        #import a fermentable into the inventory
        if mode =='replace':
            self.replacement()
            return
        
        read_item=self.readImportForm()
        if(read_item != False):
            result=add_inventory_fermentable(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success', 'Le fermentable a été correctement importé')
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_fermentables.append(read_item) 
                #self.ui.inventory_list=all_inventory_fermentable()
                self.inventory_list.sort(key=lambda x: str(x.purchase_date))
                self.inventory_model.layoutChanged.emit()
                self.hide_group_boxes()
            else:
                self.set_message_public('failure',result)
                self.ui.labelMessage.setVisible(True) 
        self.clear_selection('both')
    #------------------------------------------------------------------------------------            
    def replacement(self):
        #replace an inventory fermentable
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
        
        read_item=self.readImportForm()
        if(read_item != False):
            selected_item=self.inventory_model.inventory_fermentables[index.row()]
            result=delete_inventory_fermentable(selected_item.id) 
            result=add_inventory_fermentable(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success', 'Le fermentable a été correctement importé')
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_fermentables.append(read_item) 
                del self.inventory_model.inventory_fermentables[index.row()]
                #self.ui.inventory_list=all_inventory_fermentable()
                self.inventory_list.sort(key=lambda x: str(x.purchase_date))
                self.inventory_model.layoutChanged.emit()
                self.hide_group_boxes()
            else:
                self.set_message_public('failure',result)
                self.ui.labelMessage.setVisible(True) 
        self.clear_selection('source')
        self.clear_selection('destination')
    
    #---------------------------------------------------------------------------------------
    def set_message_public(self, style, text):
        self.ui.labelMessage.setText(text)
        if(style =='success'):
            self.ui.labelMessage.setStyleSheet(self.font_style_prefix+'background-color:green; color: white;padding:10px')
            self.timer=QTimer()
            self.timer.timeout.connect(self.hide_message_public)
            self.timer.start(3000) 
        if(style == 'failure'):
                self.ui.labelMessage.setStyleSheet(self.font_style_prefix+'background-color:red; color: white;padding:10px')
                self.ui.closeMessageButton.setVisible(True)
        self.ui.labelMessage.setVisible(True)
    
    #----------------------------------------------------------------------------------------           
    def set_message_inventory(self, style, text):
        self.ui.labelMessage_2.setText(text)
        if(style =='success'):
            self.ui.labelMessage_2.setStyleSheet(self.font_style_prefix+'background-color:green; color: white;padding:10px')
            self.timer=QTimer()
            self.timer.timeout.connect(self.hide_message_inventory)
            self.timer.start(3000) 
        if(style == 'failure'):
                self.ui.labelMessage_2.setStyleSheet(self.font_style_prefix+'background-color:red; color: white;padding:10px')
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
            #self.ui.formCombo.setCurrentText(get_fermentable_form_name(selected_item.form))
            self.ui.formCombo.setCurrentText(selected_item.form)
            self.ui.categoryCombo.setCurrentText(get_fermentable_category_name(selected_item.category))
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
            self.ui.invQuantityEdit.setText(str(selected_item.quantity))
            self.ui.invCostEdit.setText(str(selected_item.cost))
            print('id on loaded inventoryFermentable is '+str(selected_item.id))
                 
    #-----------------------------------------------------------------------------------------------                    
    def read_new_form(self):
    #read the new fermentable form and check inputs validates
    #returns False if not validated, returns new fermentable otherwise
        validated=True
        name=self.ui.nameEdit.text().upper()
        if(name ==''):
            self.ui.nameEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        brand=self.ui.brandCombo.currentText()
        if(brand == ''):
            self.ui.brandCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        form=self.ui.formCombo.currentText()
        if(form == ''):
            self.ui.formCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        category=self.ui.categoryCombo.currentText()
        if(category ==''):
            self.ui.categoryCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        color=self.ui.colorEdit.text()
        color=color.replace(',','.')
        r=self.color_validator.validate(color,0)
        if(r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.colorEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        potential=self.ui.potentialEdit.text()
        r=self.potential_validator.validate(potential,0) 
        if( r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.potentialEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        raw_ingredient=self.ui.rawIngredientCombo.currentText()
        if(raw_ingredient==''):
            self.ui.rawIngredientCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        version=self.ui.versionEdit.text()
        if(version ==''):
            self.ui.versionEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        link=self.ui.linkEdit.text() 
        notes=self.ui.notesEdit.toPlainText()
        if(validated == True):
            f=Fermentable (None,brand,name,form,category,color,potential,raw_ingredient,version,link,notes)  
            print(f)
            return f
        else:
            return False   

     #------------------------------------------------------------------------------------------------        
    def readImportForm(self):
    #read the import fermentable form and check inputs validated
    #returns False if not validated, returns a new inventory_fermentable otherwise
        validated=True
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.fermentables[index.row()]
            quantity=self.ui.quantityEdit.text()
            r=self.quantity_validator.validate(quantity,0)
            if(r[0] !=QtGui.QValidator.State.Acceptable):
                self.ui.quantityEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
                validated=False
                #print('bad quantity')
            cost=self.ui.costEdit.text()
            r=self.cost_validator.validate(cost,0)
            if(r[0] != QtGui.QValidator.State.Acceptable):
                self.ui.costEdit.setStyleSheet(self.font_style_prefix+ 'background-color: red; color:white;')
                validated = False
                #print('bat cost')
            purchase_date=self.ui.importDateEdit.date()
            pd=date.fromisoformat(purchase_date.toString("yyyy-MM-dd"))
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
    #returns False if not validated, returns a new inventory_fermentable otherwise
        validated=True
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.inventory_model.inventory_fermentables[index.row()]
            quantity=self.ui.invQuantityEdit.text()
            r=self.quantity_validator.validate(quantity,0)
            if(r[0] !=QtGui.QValidator.State.Acceptable):
                self.ui.invQuantityEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
                validated=False
            cost=self.ui.invCostEdit.text()
            r=self.cost_validator.validate(cost,0)
            if(r[0] != QtGui.QValidator.State.Acceptable):
                self.ui.invCostEdit.setStyleSheet(self.font_style_prefix+ 'background-color: red; color:white;')
                validated = False
            if(validated == True):
                inventory_ferm=InventoryFermentable(selected_item.id,selected_item.fermentable_id,quantity,cost,selected_item.purchase_date,selected_item.frozen) 
                return inventory_ferm
            else:
                return False
        else:
            return False   
    
    #-----------------------------------------------------------------------------------------------
    def cleanEdit(self, what):
        #restore initial state of inputs after a mistake has been fixed
        match what:
            case 'quantity':
                self.ui.quantityEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'cost':
                self.ui.costEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'name':
                self.ui.nameEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;') 
            case 'brand':
                self.ui.brandCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;') 
            case 'category':
                self.ui.categoryCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'form':
                self.ui.formCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'potential':
                self.ui.potentialEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'color':
                self.ui.colorEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'ingredient':
                self.ui.rawIngredientCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'form':
                self.ui.formCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')    
            case 'quantity_2':
                self.ui.invQuantityEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'version':
                self.ui.versionEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            
            case 'cost_2':
                self.ui.invCostEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')

    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        self.ui.colorEdit.setStyleSheet(self.font_style_prefix+'background-color: white; color:black;')
        self.ui.potentialEdit.setStyleSheet(self.font_style_prefix+'background-color: white; color:black;')
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

    #--------------------------------------------------------------------------------------------    
    def cleanImportForm(self):
        self.ui.quantityEdit.setStyleSheet(self.font_style_prefix+'background-color: white; color:black;')
        self.ui.costEdit.setStyleSheet(self.font_style_prefix+'background-color: white; color:black;')
        self.ui.quantityEdit.setText('')
        self.ui.costEdit.setText('')   
    #-------------------------------------------------------------------------------------------   
    def showNewInputs(self,keep=False):
        self.ui.groupBoxNew.setVisible(True)
        self.ui.groupBoxImport.setVisible(False) 
        self.cleanImportForm()
        if(keep == False):
            self.cleanNewForm()

    #--------------------------------------------------------------------------------------------   
    def showImportInputs(self):
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(True)   
        self.cleanNewForm() 

    #-------------------------------------------------------------------------------------------- 
    def show_group_box_inv(self):
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            self.ui.groupBoxImport_2.setVisible(True)
            self.ui.checkBox.setChecked(True)
            self.hide_inventory_mode_buttons()
        else:
            self.set_message_inventory('failure','Vous devez sélectionner un fermentable') 

    #--------------------------------------------------------------------------------------------     
    def hide_group_boxes(self):
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(False)
        #self.ui.inventoryList.clearSelection()
        #self.ui.publicList.clearSelection()
        
        self.ui.newButton.setVisible(True)

    #-------------------------------------------------------------------------------------------- 
    def hide_group_box_inv(self):
        self.ui.groupBoxImport_2.setVisible(False)   
        #self.ui.inventoryList.clearSelection()
        self.clear_selection('destination')

    #--------------------------------------------------------------------------------------------  
    def hide_main_mode_buttons(self):
        self.ui.importButton.setVisible(False)
        self.ui.deleteButton.setVisible(False)
        self.ui.editButton.setVisible(False)
        self.ui.newButton.setVisible(False)    
    
    #--------------------------------------------------------------------------------------------  
    def hide_inventory_mode_buttons(self):
        self.ui.invDeleteButton.setVisible(False)
        self.ui.invEditButton.setVisible(False)

    #--------------------------------------------------------------------------------------------  
    def show_group_box(self,mode):
        if(mode == 'add'):
            self.showNewInputs()
            self.ui.addButton.setVisible(True)
            self.ui.updateButton.setVisible(False) 
            self.hide_main_mode_buttons()
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
                self.hide_main_mode_buttons()
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
            selected_item=self.inventory_model.inventory_fermentables[index.row()]  
        else: 
            return
        if(selected_item.cost != '' and self.ui.invQuantityEdit.text() !='' and selected_item.quantity != '' )   : 
            try:#to avoid crash in quantity and cost already at zero. Needs unbinding
                new_cost=float(selected_item.cost )* float(self.ui.invQuantityEdit.text())/float(selected_item.quantity)
                self.ui.invCostEdit.setText('{:0.2f}'.format(new_cost))
            except:
                pass

        
 ##############################################################################################################
 # ############################################################################################################       
class FermentableModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, fermentables=None, **kwargs):
        super(FermentableModel,self).__init__(*args, **kwargs)
        self.fermentables = fermentables or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        
        if (role ==Qt.ItemDataRole.DisplayRole):
            f =self.fermentables[index.row()] 
            form=f.form
            category=get_fermentable_category_name(f.category)
            raw_ingredient=f.raw_ingredient
            fname=self.str_normalize(f.name,15)
            fbrand=self.str_normalize(str(f.brand),20)
            #we use str for security as some fieds may be None type
            return str(f.id)+' '+str(fname)+' '+str(f.version) +' [' +str(fbrand)+' ]  '+'\n ('+str(form)+', '+str(category)+', '+str(f.color)+' EBC, '+str(f.potential)+'%, '+str(raw_ingredient)+')'
        
        if (role == Qt.ItemDataRole.DecorationRole):
            f=self.fermentables[index.row()]
            #print(f)
            #print('fbrand is '+str(f.brand))
            fb=find_fbrand_by_name(f.brand)
            filename='./w20/'+fb.country_code+'.png'
            return QtGui.QImage(filename)
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.fermentables)


    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

###########################################################################################################
# #########################################################################################################        
class InventoryFermentableModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, inventory_fermentables=None, **kwargs):
        super(InventoryFermentableModel,self).__init__(*args, **kwargs)
        self.inventory_fermentables = inventory_fermentables or []
           
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            invf =self.inventory_fermentables[index.row()] 
            f=find_fermentable_by_id(invf.fermentable_id)
            #form=get_fermentable_form_name(f.form)
            form=f.form
            category=get_fermentable_category_name(f.category)
            raw_ingredient=f.raw_ingredient
            fname=self.str_normalize(f.name,15)
            fbrand=self.str_normalize(str(f.brand),20)
            
            return fname+' '+str(f.version) +' produit par ' +str(fbrand)+'  '+'\n'+ \
            'QUANTITÉ : '+str(invf.quantity)+' kg'+ ' COÛT : '+str(invf.cost) + ' € — Id public: '+str(invf.fermentable_id)+ ' acheté le '+DateUtils.FrenchDate(invf.purchase_date)+' '\
            '\n ('+str(form)+', '+str(category)+', '+str(f.color)+' EBC, '+str(f.potential)+'%, '+str(raw_ingredient)+')'
            #return '['+str(invf.id)+', '+f.name+' from '+f.brand+'], \n Quantity = '+str(invf.quantity)+' kg, '+'Cost = '+str(invf.cost)
        
        if (role == Qt.ItemDataRole.DecorationRole):
            invf =self.inventory_fermentables[index.row()] 
            f=find_fermentable_by_id(invf.fermentable_id)
            fb=find_fbrand_by_name(f.brand)
            filename='./w20/'+fb.country_code+'.png'
            return QtGui.QImage(filename) 

                
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       
                
    def rowCount(self,index):
        return len(self.inventory_fermentables)           
                     
    def FrenchDate(self,date_from_db) :
        adate=  adate=QtCore.QDate.fromString(str(date_from_db),'yyyy-MM-dd')   
        loc=QtCore.QLocale("fr_FR")
        return loc.toString(adate,'dd MMMM yyyy')     
