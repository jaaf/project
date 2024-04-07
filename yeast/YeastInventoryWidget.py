import datetime
import re
import sys

from PyQt6 import QtCore, QtGui,QtWidgets
from PyQt6.QtCore import QRegularExpression, Qt, QTimer
from PyQt6.QtGui import (QDoubleValidator, QIntValidator,
                         QRegularExpressionValidator)
from PyQt6.QtWidgets import (QCheckBox, QDialog, QHBoxLayout, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget)

from CheckableComboBox import CheckableComboBox, MyStandardItem
from ConfirmationDialog import ConfirmationDialog
from database.yeasts.yeast import (InventoryYeast, Yeast, add_inventory_yeast,
                                   add_yeast, all_inventory_yeast, all_ybrand,
                                   all_yeast, delete_inventory_yeast,
                                   delete_yeast, find_ybrand_by_name,
                                   find_yeast_by_id, update_inventory_yeast,
                                   update_yeast)
from dateUtils import DateUtils
from datetime import date
from HelpMessage import HelpMessage
from ListModels import InventoryYeastModel, YeastModel
from parameters import (yeast_floculation, yeast_form, yeast_pack_unit,
                        yeast_sedimentation, yeast_target)
from yeast.YeastInventoryWidgetBase import Ui_Form as yeastInventoryWgt
from pathlib import Path

class YeastInventoryWidget(QWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =yeastInventoryWgt()
        self.ui.setupUi(self)
        self.id=id
        self.parent=parent    
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
        self.current_year=self.today.year
        self.icon_path='base-data/icons/'
        self.source_selection=None
        self.destination_selection=None
        self.hide_main_mode_buttons()
        self.hide_inventory_mode_buttons()
        self.ui.newButton.setVisible(True)
        #for filters
        self.active_brands=[]
        self.active_forms=[]
        self.active_targets=[]
        self.ui.importDateEdit.setDate(self.today)
        self.complete_gui()
        self.set_validators()
        self.set_connections()    

    @QtCore.pyqtSlot()
    def on_brand_closedPopup(self):
        print('on closed popup')
        self.active_brands=self.brandFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.filter_list()  
    #----------------------------------------------
    def toggle_brand_filter(self):
        print('toggling brand filter')
        if self.brand_checkbox.isChecked():
            self.brandFilterCombo.setVisible(True)
        else:
            self.brandFilterCombo.setVisible(False)
            
        self.filter_list()
    #---------------------------------------------
    @QtCore.pyqtSlot()
    def on_form_closedPopup(self):
        self.active_forms=self.categoryFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.filter_list()       
    
    #----------------------------------------------
    def toggle_form_filter(self):
        print('toggling category filter')
        if self.form_checkbox.isChecked():
            self.formFilterCombo.setVisible(True)
        else:
            self.formFilterCombo.setVisible(False)
        
        self.filter_list()
        
    #---------------------------------------------
    @QtCore.pyqtSlot()
    def on_target_closedPopup(self):
        self.active_targets=self.targetFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.filter_list()       
    
    #----------------------------------------------
    def toggle_target_filter(self):
        print('toggling category filter')
        if self.target_checkbox.isChecked():
            self.targetFilterCombo.setVisible(True)
        else:
            self.targetFilterCombo.setVisible(False)

        self.filter_list()
          
    
    #-----------------------------------------------------------------------------------------------
    def filter_list(self):
        items=self.public_list
        filtered=list(filter(lambda x:\
                                  (x.brand in self.active_brands or not self.brand_checkbox.isChecked()) and \
                                    (x.form in self.active_forms or not self.form_checkbox.isChecked()) and \
                                        (x.target in self.active_targets or not self.target_checkbox.isChecked())\
                                            ,items ))
        
        filtered.sort(key=lambda x: (x.target,x.brand,x.name))
        self.model.yeasts=filtered 
        self.model.layoutChanged.emit()  

    #------------------------------------------------------------------------------------------------
    def search_in_name(self):
        self.filter_list()#we start with the filtered list
        pattern=self.searchEdit.text()
        print('searching in name '+pattern)
        if pattern != '':
            items=self.model.yeasts #we search only in the filtered list
            sorted_array=list(filter(lambda x: re.search(pattern, x.name,re.IGNORECASE),items)) 
            self.model.yeasts=sorted_array
            self.model.layoutChanged.emit()
    def complete_gui(self):
        #initialize the various comboBox-----------------------------------------------------------------------------
        for f in yeast_floculation:
            self.ui.floculationCombo.addItem(f)
        
        for f in yeast_form:
            self.ui.formCombo.addItem(f)

            
        for s in yeast_sedimentation:
            self.ui.sedimentationCombo.addItem(s)

        for t in yeast_target:
            self.ui.targetCombo.addItem(t)    

        for p in yeast_pack_unit:
            self.ui.packCombo.addItem(p)
        
        brands= all_ybrand() 
        self.ui.brandCombo.addItem('',None)
        for b in brands:
            self.ui.brandCombo.addItem(b.name)
  
        #Complete the GUI --------------------------------------------------------------------------------
        self.ui.labelInventoryTitle.setStyleSheet(self.font_style_prefix+'font-weight:600')
        self.ui.labelPublicTitle.setStyleSheet(self.font_style_prefix+'font-weight:600')
        self.ui.importDateEdit.setCalendarPopup(True)
        self.ui.manufactureDateEdit.setCalendarPopup(True)
        self.ui.expirationDateEdit.setCalendarPopup(True)
        self.ui.idEdit.setVisible(False)
        self.ui.idEdit_2.setVisible(False)

        self.hide_message_public()
        self.hide_message_inventory()
        self.hide_group_box_inv()
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(False)
        self.ui.publicList.setSpacing(6)
        self.ui.inventoryList.setSpacing(6)
        
        #set the models ---------------------------------------------------------------------------------
        #set the models ---------------------------------------------------------------------------------
        self.public_list=all_yeast()
        self.inventory_list=all_inventory_yeast()
        self.public_list.sort(key=lambda x: (x.brand,x.name))  
        self.inventory_list.sort(key=lambda x: str(x.purchase_date)) 
        self.model = YeastModel(yeasts=self.public_list)
        self.ui.publicList.setModel(self.model)
        self.inventory_model=InventoryYeastModel(inventory_yeasts=self.inventory_list)
        self.ui.inventoryList.setModel(self.inventory_model)
        self.mode_import='add' #the import button has two roles: adding to the inventory or replacing in inventory
        
        #set the filters of the public list
        self.filterLayout=QHBoxLayout()
        #brands
        self.brandLayout=QVBoxLayout()
        self.brandFilterCombo=CheckableComboBox()       
        self.brands=all_ybrand()
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
        
        #forms
        self.formLayout=QVBoxLayout()
        self.formFilterCombo=CheckableComboBox()       
        self.forms=yeast_form
        for form in self.forms:
            item = MyStandardItem(form)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.formFilterCombo.model().appendRow(item)     
        self.form_checkbox=QCheckBox('Filtrer les formes')
        self.formLayout.addWidget(self.form_checkbox)
        self.formLayout.addWidget(self.formFilterCombo)
        self.filterLayout.addLayout(self.formLayout)
        self.formFilterCombo.setVisible(False)
        #target
        self.targetLayout=QVBoxLayout()
        self.targetFilterCombo=CheckableComboBox()       
        self.targets=yeast_target#import from parameters
        for target in self.targets:
            item = MyStandardItem(target)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.targetFilterCombo.model().appendRow(item)   
        self.target_checkbox=   QCheckBox('Filtrer les cibles')   
        self.targetLayout.addWidget(self.target_checkbox)
        self.targetLayout.addWidget(self.targetFilterCombo)
        self.filterLayout.addLayout(self.targetLayout)
        self.targetFilterCombo.setVisible(False)

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
        self.ui.publicList.setStyleSheet("QListView{border: 2px solid green;}"\
                                         "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                            "QListView::item{border-bottom:2px solid gray}")
        self.ui.inventoryList.setStyleSheet("QListView{border: 2px solid green;}"\
                                            "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                                "QListView::item{border-bottom:2px solid gray}")



    def set_connections(self):
        #set the connections ------------------------------------------------------------------------------
        self.brandFilterCombo.closedPopup.connect(self.on_brand_closedPopup)
        self.brand_checkbox.stateChanged.connect(self.toggle_brand_filter)
        self.formFilterCombo.closedPopup.connect(self.on_form_closedPopup)
        self.form_checkbox.stateChanged.connect(self.toggle_form_filter)
        self.targetFilterCombo.closedPopup.connect(self.on_target_closedPopup)
        self.target_checkbox.stateChanged.connect(self.toggle_target_filter)
        self.searchEdit.editingFinished.connect(self.search_in_name)        
        self.searchHelpButton.clicked.connect(lambda: self.show_contextual_help('filter'))
        self.ui.newButton.clicked.connect(lambda: self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.importButton.clicked.connect(lambda: self.show_group_box('import'))
        self.ui.invEditButton.clicked.connect(self.show_group_box_inv)
        self.ui.hideNewButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton.clicked.connect(self.hide_group_boxes)
        self.ui.invHideButton.clicked.connect(self.hide_group_box_inv)
        self.ui.publicList.clicked.connect(self.select_source)
        self.ui.inventoryList.clicked.connect(self.select_destination)
        self.ui.addButton.clicked.connect(self.add)
        self.ui.updateButton.clicked.connect(self.update)
        self.ui.invUpdateButton.clicked.connect(self.update_inventory)
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.invDeleteButton.clicked.connect(self.delete_inventory)
        
        self.ui.confirmImportButton.clicked.connect(lambda: self.importation(self.mode_import))
        self.ui.groupBoxNew.clicked.connect(self.hide_message_public)
        self.ui.closeMessageButton.clicked.connect(self.hide_message_public)
        self.ui.closeMessageButton_2.clicked.connect(self.hide_message_inventory)
        self.ui.invQuantityEdit.textChanged.connect(self.adjust_cost)
        #set auto clean connection for reset of the controls-----------------------------------------------
        self.ui.quantityEdit.textChanged.connect(lambda :self.cleanEdit('quantity'))
        self.ui.costEdit.textChanged.connect(lambda :self.cleanEdit('cost'))

       #set auto clean connection for reset of the controls-----------------------------------------------
        self.ui.quantityEdit.textChanged.connect(lambda :self.cleanEdit('quantity'))
        self.ui.costEdit.textChanged.connect(lambda :self.cleanEdit('cost'))
        self.ui.cellsEdit.textChanged.connect(lambda :self.cleanEdit('cells'))
        self.ui.packCombo.currentIndexChanged.connect(lambda :self.cleanEdit('pack'))
        self.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
        self.ui.abvEdit.textChanged.connect(lambda :self.cleanEdit('abv'))
        self.ui.tempMinEdit.textChanged.connect(lambda :self.cleanEdit('temp_min'))
        self.ui.tempIdealMinEdit.textChanged.connect(lambda :self.cleanEdit('temp_ideal_min'))
        self.ui.tempIdealMaxEdit.textChanged.connect(lambda :self.cleanEdit('temp_ideal_max'))
        self.ui.tempMaxEdit.textChanged.connect(lambda :self.cleanEdit('temp_max'))
        self.ui.attenuationEdit.textChanged.connect(lambda : self.cleanEdit('attenuation'))
        self.ui.brandCombo.currentIndexChanged.connect(lambda : self.cleanEdit('brand'))
        self.ui.formCombo.currentIndexChanged.connect(lambda :self.cleanEdit('form')) 
       
        self.ui.invQuantityEdit.textChanged.connect(lambda :self.cleanEdit('quantity_2'))
        self.ui.invCostEdit.textChanged.connect(lambda :self.cleanEdit('cost_2'))
    
    #------------------------------------------------------------------
    def show_contextual_help(self,what):
        helpPopup=HelpMessage()
        filename=(self.this_file_path/"../help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
        match what:
            case 'filter':
                helpPopup.set_title('À propos du filtrage et de la recherche')
                filename=(self.this_file_path/"../help/YeastSearchHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
           
        helpPopup.exec() 



        

    def set_validators(self):

        #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
        temp_accepted_chars = QRegularExpressionValidator(QRegularExpression("[0-3]?[0-9][\\.][0-9]{1}"))
        locale=QtCore.QLocale('en')    
        self.temp_validator = QDoubleValidator(0.0,40.0,1)
        self.temp_validator.setLocale(locale)   
        self.temp_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.tempMinEdit.setValidator(temp_accepted_chars)
        self.ui.tempIdealMinEdit.setValidator(temp_accepted_chars)
        self.ui.tempIdealMaxEdit.setValidator(temp_accepted_chars)
        self.ui.tempMaxEdit.setValidator(temp_accepted_chars)
        
       
   
        self.attenuation_validator=QDoubleValidator(60.0, 100.0,1)
        self.attenuation_validator.setLocale(locale)
        self.attenuation_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.attenuationEdit.setValidator( QRegularExpressionValidator(QRegularExpression("[6-9][0-9]?[\\.][0-9]{1}")))

       
        self.abv_validator = QDoubleValidator(0.0,20.0,1)
        self.abv_validator.setLocale(locale)   
        self.abv_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.abvEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-1]?[0-9][\\.][0-9]{1}")))
        
       
        self.cells_validator = QDoubleValidator(0.0,1100.0,1)
        self.cells_validator.setLocale(locale)   
        self.cells_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.cellsEdit.setValidator( QRegularExpressionValidator(QRegularExpression("[0-9]{1,3}")))

        accepted_chars_quantity = QRegularExpressionValidator(QRegularExpression("[0-9]*[\\.]?[0-9]{2}"))
        self.quantity_validator=QDoubleValidator(0.0,1000.0,1)
        self.quantity_validator.setLocale(locale)
        self.quantity_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.quantityEdit.setValidator(accepted_chars_quantity)
        self.ui.invQuantityEdit.setValidator(accepted_chars_quantity)
        
        self.cost_validator=QDoubleValidator(0.0,500,2)
        self.cost_validator.setLocale(locale)
        self.cost_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.costEdit.setValidator( QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}[\\.]?[0-9]{2}")))
        self.ui.invCostEdit.setValidator( QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}[\\.]?[0-9]{2}")))
      
    #------------------------------------------------------------------------------------------------------
    def select_destination(self):
        #select an element in the destination list either for deletion, or update, or replacement
        old_selection=self.destination_selection
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            self.destination_selection=self.inventory_model.inventory_yeasts[index.row()]
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
            self.source_selection=self.model.yeasts[index.row()]
            if (old_selection==self.source_selection):  
                self.clear_selection('source')   
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
        self.inventory_model.inventory_yeasts=all_inventory_yeast()
        self.inventory_model.layoutChanged.emit()    
        self.model.yeasts=all_yeast() 
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

    #-----------------------------------------------------------------------------
    def add(self):
        #add a new ingredient to the public list
        data=self.read_new_form()
        if(data != False):
            result= add_yeast(data)
            if(result == 'OK'):
                self.cleanNewForm()
                self.set_message_public('success', 'Le houblon a été correctement enregistrée')
                self.ui.labelMessage.setVisible(True)
                self.model.yeasts.append(data)
                self.public_list.sort(key=lambda x: (x.supplier,x.name,x.crop_year))
                self.model.layoutChanged.emit()
            else:
                self.set_message_public('failure', result),
                self.ui.labelMessage.setVisible(True)  
     
    #--------------------------------------------------------------------------           
    def update(self):
        #update an existing ingredient in the public list
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.model.yeasts[index.row()]
            read_item=self.read_new_form()
            if(read_item != False):
        #thi id has been set while loading form with selected item
                read_item.id=self.ui.idEdit.text()
                #attempt update in database
                result = update_yeast(read_item)
                if(result == 'OK'):
                    self.cleanNewForm()
                    self.set_message_public('success', 'La levure a été correctement enregistrée')
                    self.ui.labelMessage.setVisible(True)
                    selection=self.model.yeasts[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.brand=read_item.brand
                    selection.manufacture_date=read_item.manufacture_date
                    selection.expiration_date=read_item.expiration_date
                    selection.pack_unit=read_item.pack_unit
                    selection.cell_per_pack=read_item.cells_per_pack
                    selection.form=read_item.form
                    selection.target=read_item.target
                    selection.floculation=read_item.floculation
                    selection.sedimentation=read_item.sedimentation
                    selection.abv_tolerance=read_item.abv_tolerance
                    selection.temp_min=read_item.temp_min
                    selection.temp_ideal_min=read_item.temp_ideal_min
                    selection.temp_ideal_max=read_item.temp_ideal_max
                    selection.temp_max=read_item.temp_max
                    selection.attenuation=read_item.attenuation
                    selection.link=read_item.link
                    selection.notes=read_item.notes
                    self.public_list.sort(key=lambda x: (x.supplier,x.name,x.crop_year))
                    self.model.layoutChanged.emit()
                    #the update may affect the inventory yeasts
                    self.inventory_model.inventory_yeasts=all_inventory_yeast()
                    self.inventory_model.layoutChanged.emit()
    #------------------------------------------------------------------------------      
    def update_inventory(self):
        #updating an inventoryYeast in the inventory list
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.inventory_model.inventory_yeasts[index.row()]
            read_item=self.readUpdateInventoryForm()
            if(read_item != False):
                read_item.id=selection.id
                read_item.yeast_id=selection.yeast_id
                #update in database
                result =update_inventory_yeast(read_item)
                if(result == 'OK'):
                    self.set_message_inventory('success', 'La levure d\'inventaire a été correctement enregistré')
                    self.ui.labelMessage_2.setVisible(True)
                    selection.quantity=read_item.quantity
                    selection.cost=read_item.cost
                    self.inventory_model.layoutChanged.emit()
                    self.hide_group_box_inv()
                else:
                    self.set_message_inventory('failure', result),
                    self.ui.labelMessage_2.setVisible(True)       
            else:
                self.set_message_inventory('failure','Vous devez sélectionner une levure')   
        self.clear_selection('both')            
    #----------------------------------
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
            #delete an ingredient from the public list
            indexes = self.ui.publicList.selectedIndexes()
            if indexes:
                # Indexes is a list of a single item in single-select mode.
                index = indexes[0]
                selected_item= self.model.yeasts[index.row()]
                #delete from database
                result=delete_yeast(selected_item.id)
                if (result == 'OK'):
                    self.set_message_public('success', 'La levure a été correctement supprimée')
                    self.ui.labelMessage.setVisible(True)
                    # Remove the item and refresh.
                    del self.model.yeasts[index.row()]
                    self.model.layoutChanged.emit()
                    # Clear the selection (as it is no longer valid).
                    self.ui.publicList.clearSelection()
                else:
                    self.set_message_public('failure', result)
                    self.ui.labelMessage.setVisible(True)    
            else:
                self.set_message_public('failure','Vous devez sélectionner un houblon') 
            self.clear_selection('both')

    #--------------------------------------------------------------------------------
    def delete_inventory(self):
        msgBox=ConfirmationDialog()
        msgBox.setTitle('Confirmer suppression')
        
        msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
        msgBox.setMessage('Vous êtes sur le point de supprimer un achat de levure de votre inventaire. Cette suppression sera définitive. \n Confirmez-vous la suppression ?') 
        msgBox.setCancelButtonText('Non. Ne pas supprimer')
        msgBox.setConfirmButtonText('Oui. Supprimer.')
        confirm=msgBox.exec()   
        if(confirm == 1):
            indexes = self.ui.inventoryList.selectedIndexes()
            if indexes:
                index=indexes[0]
                selected_item=self.inventory_model.inventory_yeasts[index.row()]
                #delete from database
                result=delete_inventory_yeast(selected_item.id)
                if (result == 'OK') :
                    self.set_message_inventory('success','La levure d\'inventaire a été correctement supprimée') 
                    self.ui.labelMessage_2.setVisible(True)
                    del self.inventory_model.inventory_yeasts[index.row()]
                    self.inventory_model.layoutChanged.emit()
                    self.ui.inventoryList.clearSelection()
                else:
                    self.set_message_inventory('failure',result)
                    self.ui.labelMessage_2.setVisible(True)    
            else:
                self.set_message_inventory('failure','Vous devez sélectionner une levure')      
            self.clear_selection('both')    

    #------------------------------------------------------------------------------------            
    def importation(self,mode):
        #import a fermentable into the inventory
        if mode =='replace':
            self.replacement()
            return
        
        read_item=self.readImportForm()
        if(read_item != False):
            result=add_inventory_yeast(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success', 'La levure a été correctement importée')
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_yeasts.append(read_item) 
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
            selected_item=self.inventory_model.inventory_yeasts[index.row()]
            result=delete_inventory_yeast(selected_item.id) 
            result=add_inventory_yeast(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success', 'Le fermentable a été correctement importé')
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_yeasts.append(read_item) 
                del self.inventory_model.inventory_yeasts[index.row()]
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
            self.timer.start(2000) 
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
            self.timer.start(2000) 
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

    #-------------------------------------------------------------------------------------------    
    def load_yeast(self):
        #load a yeast's values in the new form after it has been selected in the public QListView
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.yeasts[index.row()]
            self.ui.idEdit.setText(str(selected_item.id))
            self.ui.nameEdit.setText(selected_item.name)
            self.ui.brandCombo.setCurrentText(selected_item.brand)
            #print ('before loading')
            #print(selected_item.manufacture_date)
            self.ui.manufactureDateEdit.setDate(DateUtils.DateFromDbString(selected_item.manufacture_date))
            self.ui.expirationDateEdit.setDate(DateUtils.DateFromDbString(selected_item.expiration_date))
            self.ui.packCombo.setCurrentText(selected_item.pack_unit)
            self.ui.cellsEdit.setText(str(selected_item.cells_per_pack))
            self.ui.formCombo.setCurrentText(selected_item.form)
            self.ui.targetCombo.setCurrentText(selected_item.target)
            self.ui.floculationCombo.setCurrentText(selected_item.floculation)
            self.ui.sedimentationCombo.setCurrentText(selected_item.sedimentation)
            self.ui.abvEdit.setText(str(selected_item.abv_tolerance))
            self.ui.tempMinEdit.setText(str(selected_item.temp_min))
            self.ui.tempIdealMinEdit.setText(str(selected_item.temp_ideal_min))
            self.ui.tempIdealMaxEdit.setText(str(selected_item.temp_ideal_max))
            self.ui.tempMaxEdit.setText(str(selected_item.temp_max))
            self.ui.attenuationEdit.setText(str(selected_item.attenuation))
            self.ui.linkEdit.setText(selected_item.link)
            self.ui.notesEdit.setText(selected_item.notes)
                   
    #-----------------------------------------------------------------------------------------------        
    def load_inventory_yeast(self):
        #load an inventory yeast in the inventory form after it has been selected in the inventory QListView
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0] 
            selected_item=self.inventory_model.inventory_yeasts[index.row()]
            self.ui.idEdit_2.setText(str(selected_item.id))
            self.ui.invQuantityEdit.setText(str(selected_item.quantity))
            self.ui.invCostEdit.setText(str(selected_item.cost))
                 
    #-----------------------------------------------------------------------------------------------                    
    def read_new_form(self):
    #read the new yeast form and check inputs are validated
    #returns False if not validated, returns new yeast otherwise
        validated=True
        name=self.ui.nameEdit.text().upper()
        if(name == ''):
            self.ui.nameEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated = False
        brand=self.ui.brandCombo.currentText()
        if(brand ==''):
            self.ui.brandCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        form=self.ui.formCombo.currentText()
        if(form == ''):
            self.ui.formCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        floculation=self.ui.floculationCombo.currentText()
        sedimentation=self.ui.sedimentationCombo.currentText()
        target=self.ui.targetCombo.currentText()
        abv_tolerance=self.ui.abvEdit.text()
        r=self.abv_validator.validate(abv_tolerance,0)
        if( r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.abvEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        m_date=self.ui.manufactureDateEdit.date()
        manufacture_date=m_date.toString('yyyy-MM-dd')
        p_date=self.ui.expirationDateEdit.date()
        expiration_date=p_date.toString('yyyy-MM-dd')
        pack_unit=self.ui.packCombo.currentText()
        if(pack_unit == ''):
            self.ui.packCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        cells_per_pack=self.ui.cellsEdit.text()
        r=self.cells_validator.validate(cells_per_pack,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.cellsEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
       
        temp_min=self.ui.tempMinEdit.text()
        r=self.temp_validator.validate(temp_min,0)
        if( r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.tempMinEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False

        temp_ideal_min=self.ui.tempIdealMinEdit.text()
        r=self.temp_validator.validate(temp_ideal_min,0)
        if( r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.tempIdealMinEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
    
        temp_ideal_max=self.ui.tempIdealMaxEdit.text()
        r=self.temp_validator.validate(temp_ideal_max,0)
        if( r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.tempIdealMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False

        temp_max=self.ui.tempMaxEdit.text()
        r=self.temp_validator.validate(temp_max,0)
        if( r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.tempMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False

       

        if(temp_min>temp_ideal_min):
            self.ui.tempMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;') 
            self.ui.tempMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False
        if(temp_min>temp_ideal_min):
            self.ui.tempMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;') 
            self.ui.tempIdealMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False
        if(temp_min>temp_max): 
            self.ui.tempMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;') 
            self.ui.tempMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False
        if(temp_ideal_min>temp_ideal_max):
            self.ui.tempIdealMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;') 
            self.ui.tempIdealMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False
        if(temp_ideal_min>temp_max):
            self.ui.tempIdelaMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;') 
            self.ui.tempMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False
        if(temp_ideal_max>temp_max) :
            self.ui.tempIdealMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;') 
            self.ui.tempMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False

        attenuation=self.ui.attenuationEdit.text() 
        r=self.attenuation_validator.validate(attenuation,0)
        if( r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.attenuationEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False 

        link=self.ui.linkEdit.text() 
        notes=self.ui.notesEdit.toPlainText()
        if(validated == True):
            y=Yeast (None,brand,name, manufacture_date,expiration_date,pack_unit,cells_per_pack,form,target,floculation,sedimentation,abv_tolerance,temp_min,temp_ideal_min,temp_ideal_max,temp_max,attenuation,link,notes)  
            return y
        else:
            return False  

     #------------------------------------------------------------------------------------------------        
    def readImportForm(self):
    #read the import yeast form and check inputs validated
    #returns Fals if not validated, returns a new inventory_yeast otherwise
        validated=True
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.yeasts[index.row()]
            quantity=self.ui.quantityEdit.text()
            r=self.quantity_validator.validate(quantity,0)
            if(r[0] !=QtGui.QValidator.State.Acceptable):
                self.ui.quantityEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
                validated=False
              
            cost=self.ui.costEdit.text()
            r=self.cost_validator.validate(cost,0)
            if(r[0] != QtGui.QValidator.State.Acceptable):
                self.ui.costEdit.setStyleSheet(self.font_style_prefix+ 'background-color: red; color:white;')
                validated = False
            purchase_date=self.ui.importDateEdit.date()
            pd=date.fromisoformat(purchase_date.toString("yyyy-MM-dd"))

            if(validated == True):
                inventory_ferm=InventoryYeast(None,selected_item.id,quantity,cost,pd,False) 
                return inventory_ferm
            else:
                return False
        else:
            self.set_message_public('failure','Vous devez sélectionner une levure !')
            return False

    #---------------------------------------------------------------------------------------------       
    def readUpdateInventoryForm(self):
    #read the update inventory yeast form and check inputs validated
    #returns Fals if not validated, returns a new inventory_yeast otherwise
        validated=True
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.inventory_model.inventory_yeasts[index.row()]
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
                inventory_ferm=InventoryYeast(None,selected_item.id,quantity,cost,selected_item.purchase_date,selected_item.frozen) 
                return inventory_ferm
            else:
                return False
        else:
            return False   
    
    #-----------------------------------------------------------------------------------------------
    def cleanEdit(self, what):
        #auto clean a QLineEdit or a QComboBox after it has been marqued wrong when using it again
        match what:
            case 'quantity':
                self.ui.quantityEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'cost':
                self.ui.costEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'name':
                self.ui.nameEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
            case 'brand':
                self.ui.brandCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;') 
            case 'form':
                self.ui.formCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
            case 'pack':
                self.ui.packCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;') 
            case 'cells':
                self.ui.cellsEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;') 
            case 'temp_min':
                self.ui.tempMinEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'temp_ideal_min':
                self.ui.tempIdealMinEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;') 
            case 'temp_ideal_max':
                self.ui.tempIdealMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
            case 'temp_max':
                self.ui.tempMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;') 
            case 'attenuation':
                self.ui.attenuationEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;') 
            case 'abv':
                self.ui.abvEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'quantity_2':
                self.ui.invQuantityEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            
            case 'cost_2':
                self.ui.invCostEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')


    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        #clean the form for adding or updating a public ingredient
        self.ui.brandCombo.setCurrentIndex(0)
        self.ui.nameEdit.setText('')
        self.ui.manufactureDateEdit.setDate(datetime.date.today())
        self.ui.expirationDateEdit.setDate(datetime.date.today())
        self.ui.packCombo.setCurrentText('')
        self.ui.cellsEdit.setText('')
        self.ui.formCombo.setCurrentIndex(0)
        self.ui.targetCombo.setCurrentIndex(0)
        self.ui.sedimentationCombo.setCurrentIndex(0) 
        self.ui.floculationCombo.setCurrentIndex(0)
        self.ui.abvEdit.setText('')  
        self.ui.tempMinEdit.setText('')   
        self.ui.tempIdealMinEdit.setText('')
        self.ui.tempIdealMaxEdit.setText('') 
        self.ui.tempMaxEdit.setText('') 
        self.ui.attenuationEdit.setText('')
        self.ui.linkEdit.setText('') 
        self.ui.notesEdit.setText('')   

    #------------------------------------------------------------------------------------------    
    def cleanImportForm(self):
        #clean the importation form
        self.ui.quantityEdit.setStyleSheet(self.font_style_prefix+'background-color: white; color:black;')
        self.ui.costEdit.setStyleSheet(self.font_style_prefix+'background-color: white; color:black;')
        self.ui.quantityEdit.setText('')
        self.ui.costEdit.setText('')   
    
    #------------------------------------------------------------------------------------------  
    def showNewInputs(self,keep=False):
        #show the add or update form and hide the importation form
        self.ui.groupBoxNew.setVisible(True)
        self.ui.groupBoxImport.setVisible(False) 
        self.cleanImportForm()
        if(keep == False):
            self.cleanNewForm()

    #------------------------------------------------------------------------------------------  
    def showImportInputs(self):
        #show the importation form and hide the add or update form (public side)
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(True)   
        self.cleanNewForm() 
    
    #------------------------------------------------------------------------------------------
    def show_group_box_inv(self):
        #show the update inventory ingredient form (inventory side)
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            self.ui.groupBoxImport_2.setVisible(True)
            self.ui.checkBox.setChecked(True)
        else:
            self.set_message_inventory('failure','Vous devez sélectionner une levure')
        
    #------------------------------------------------------------------------------------------
    def hide_group_boxes(self):
        #hide the forms in the public side
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(False)
        self.ui.inventoryList.clearSelection()
        self.ui.publicList.clearSelection() 
        self.ui.newButton.setVisible(True)
    #------------------------------------------------------------------------------------------
    def hide_group_box_inv(self):
        #hide the form in the inventory side
        self.ui.groupBoxImport_2.setVisible(False) 
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


    #------------------------------------------------------------------------------------------     
    def show_group_box(self,mode):
        #show the form for the selected (mode) operation (public side)
        if(mode == 'add'):
            self.showNewInputs()
            self.ui.addButton.setVisible(True)
            self.ui.updateButton.setVisible(False) 
        else:
            indexes=self.ui.publicList.selectedIndexes() 
            if indexes:
                if(mode == 'update'):
                    self.load_yeast()
                    self.showNewInputs(True)
                    self.ui.addButton.setVisible(False)
                    self.ui.updateButton.setVisible(True) 
                if(mode == 'import'):
                    self.showImportInputs()
            else:
                self.set_message_public('failure','Vous devez sélectionner une levure')
        
    #--------------------------------------------------------------------------------------------
    def adjust_cost(self):
        #print('adjusting cost')
        if(self.ui.checkBox.isChecked()==False) :
            return 
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0] 
            selected_item=self.inventory_model.inventory_yeasts[index.row()]  
        else: 
            return
        if(selected_item.cost != '' and self.ui.invQuantityEdit.text() !=''  and selected_item.quantity != '' )   : 
            try:#to avoid crash if quantity and cost already at zero
                new_cost=float(selected_item.cost )* float(self.ui.invQuantityEdit.text())/float(selected_item.quantity)
                self.ui.invCostEdit.setText('{:0.2f}'.format(new_cost))
            except:
                pass
                

