import datetime
import re
from PyQt6 import QtCore, QtGui,QtWidgets
from PyQt6.QtCore import QRegularExpression, Qt, QTimer
from PyQt6.QtGui import (QDoubleValidator, QIntValidator,
                         QRegularExpressionValidator)
from PyQt6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout, QWidget)
from CheckableComboBox import CheckableComboBox, MyStandardItem
from ConfirmationDialog import ConfirmationDialog
from database.commons.country import all_country, find_country_by_code
from database.hops.hop import (Hop, add_hop, all_hop, delete_hop,
                               find_hop_by_id, update_hop)
from database.hops.hop_suppliers import all_hsupplier
from database.hops.inventory_hop import (InventoryHop, add_inventory_hop,
                                         all_inventory_hop,
                                         delete_inventory_hop,
                                         update_inventory_hop)
from dateUtils import DateUtils
from datetime import date
#from ListModels import HopModel,InventoryHopModel
from HelpMessage import HelpMessage
from hop.HopInventoryWidgetBase import Ui_Form as hopInventoryWgt
from parameters import (get_hop_form_name, get_hop_purpose_name, hop_forms,
                        hop_purposes)
from pathlib import Path


class HopInventoryWidget(QWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =hopInventoryWgt()
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
        self.ui.importDateEdit.setDate(self.today)        
        
        self.source_selection=None
        self.destination_selection=None
        self.hide_main_mode_buttons()
        self.hide_inventory_mode_buttons()
        self.ui.newButton.setVisible(True)
        #for filters
        self.active_suppliers=[]
        self.active_forms=[]
        self.active_purposes=[]
        self.complete_gui()
        self.set_validators()
        self.set_connections()        

    def set_connections(self):
        #set the connections ------------------------------------------------------------------------------
        self.supplierFilterCombo.closedPopup.connect(self.on_supplier_closedPopup)
        self.supplier_checkbox.stateChanged.connect(self.toggle_supplier_filter)
        self.formFilterCombo.closedPopup.connect(self.on_form_closedPopup)
        self.form_checkbox.stateChanged.connect(self.toggle_form_filter)
        self.purposeFilterCombo.closedPopup.connect(self.on_purpose_closedPopup)
        self.purpose_checkbox.stateChanged.connect(self.toggle_purpose_filter)
        self.yearSearchEdit.editingFinished.connect(self.search_year)
        self.searchEdit.editingFinished.connect(self.search_in_name)

        self.ui.newButton.clicked.connect(lambda: self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.importButton.clicked.connect(lambda: self.show_group_box('import'))
        self.ui.invEditButton.clicked.connect(self.show_group_box_inv)
        self.ui.hideNewButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton.clicked.connect(self.hide_group_boxes)
        self.ui.invHideImportButton.clicked.connect(self.hide_group_box_inv)
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
        self.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
        self.ui.cropYearEdit.textChanged.connect(lambda :self.cleanEdit('crop_year'))
        self.ui.supplierCombo.currentIndexChanged.connect(lambda :self.cleanEdit('supplier')) 
        self.ui.countryCodeCombo.currentIndexChanged.connect(lambda :self.cleanEdit('country')) 
        self.ui.formCombo.currentIndexChanged.connect(lambda :self.cleanEdit('form')) 
        self.ui.purposeCombo.currentIndexChanged.connect(lambda :self.cleanEdit('purpose'))
        self.ui.alphaEdit.textChanged.connect(lambda: self.cleanEdit('alpha'))
        self.ui.invQuantityEdit.textChanged.connect(lambda :self.cleanEdit('quantity_2'))
        self.ui.invCostEdit.textChanged.connect(lambda :self.cleanEdit('cost_2'))
        self.searchHelpButton.clicked.connect(lambda: self.show_contextual_help('filter'))
            #------------------------------------------------------------------
    def show_contextual_help(self,what):
        helpPopup=HelpMessage()
        filename=(self.this_file_path/"../help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
        match what:
            case 'filter':
                helpPopup.set_title('À propos du filtrage et de la recherche')
                filename=(self.this_file_path/"../help/HopSearchHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
           
        helpPopup.exec()
    

    def complete_gui(self):
        self.ui.labelInventoryTitle.setStyleSheet(self.font_style_prefix+'font-weight:600')
        self.ui.labelPublicTitle.setStyleSheet(self.font_style_prefix+'font-weight:600')
        #initialize the various comboBox-----------------------------------------------------------------------------
        for h in hop_forms:
            self.ui.formCombo.addItem(h[1],h[0])
            
        for p in hop_purposes:
            self.ui.purposeCombo.addItem(p[1],p[0]) 

        self.countries=all_country()
        self.ui.countryCodeCombo.addItem('')
        for c in self.countries:
            self.ui.countryCodeCombo.addItem(c.name+' — '+c.country_code)
  
        suppliers= all_hsupplier() 
        self.ui.supplierCombo.addItem('',None)
        for s in suppliers:
            self.ui.supplierCombo.addItem(s.name)
        #Complete the GUI --------------------------------------------------------------------------------
       
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
        self.public_list=all_hop()
        self.public_list.sort(key=lambda x: (x.supplier,x.name,x.crop_year))  
        self.model = HopModel(hops=self.public_list)
        self.ui.publicList.setModel(self.model)

        self.inventory_list=all_inventory_hop()
        self.inventory_list.sort(key=lambda x: str(x.purchase_date)) 
        self.inventory_model=InventoryHopModel(inventory_hops=self.inventory_list)
        self.ui.inventoryList.setModel(self.inventory_model)
        self.mode_import='add'#the import button has two roles: adding to the inventory or replacing in inventory

        #set the filter of the public list
        #supplier
        self.filterLayout=QHBoxLayout()   
        self.supplierLayout=QVBoxLayout()
        self.supplierFilterCombo=CheckableComboBox()
        self.suppliers=all_hsupplier()
        for supplier in self.suppliers:
            item=MyStandardItem(supplier.name)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.supplierFilterCombo.model().appendRow(item)
        self.supplier_checkbox=QCheckBox('Filtrer fournisseurs')  
        self.supplierLayout.addWidget(self.supplier_checkbox)
        self.supplierLayout.addWidget(self.supplierFilterCombo)
        self.filterLayout.addLayout(self.supplierLayout)  
        #form  
        self.formLayout=QVBoxLayout()
        self.formFilterCombo=CheckableComboBox()
        self.forms=hop_forms#imported from parameters
        for form in self.forms:
            item=MyStandardItem(form[1],form[0])
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.formFilterCombo.model().appendRow(item)
        self.form_checkbox=QCheckBox('Filtrer formes')  
        self.formLayout.addWidget(self.form_checkbox)
        self.formLayout.addWidget(self.formFilterCombo)
        self.filterLayout.addLayout(self.formLayout) 
        self.ui.filterGroupBox.setLayout(self.filterLayout) 
        #purpose
        self.purposeLayout=QVBoxLayout()
        self.purposeFilterCombo=CheckableComboBox()
        self.purposes=hop_purposes#imported from parameters
        for purpose in self.purposes:
            item=MyStandardItem(purpose[1],purpose[0])
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.purposeFilterCombo.model().appendRow(item)
        self.purpose_checkbox=QCheckBox('Filtrer but')  
        self.purposeLayout.addWidget(self.purpose_checkbox)
        self.purposeLayout.addWidget(self.purposeFilterCombo)
        self.filterLayout.addLayout(self.purposeLayout) 
        
        #year
        self.yearLayout=QVBoxLayout()
        self.yearSearchLabel=QLabel('Année')
        self.yearSearchLabel.setFixedWidth(60)
        self.yearSearchEdit=QLineEdit()
        self.yearSearchEdit.setFixedWidth(60)
        self.yearSearchEdit.setPlaceholderText('? ')
        self.yearLayout.addWidget(self.yearSearchLabel)
        self.yearLayout.addWidget(self.yearSearchEdit)
        self.filterLayout.addLayout(self.yearLayout)

        #search
        self.nameLayout=QVBoxLayout()
        self.nameSearchLabel=QLabel('Chercher dans nom')
        self.searchEdit=QLineEdit()
        self.searchEdit.setPlaceholderText('? ')
        self.nameLayout.addWidget(self.nameSearchLabel)
        self.nameLayout.addWidget(self.searchEdit)
        self.filterLayout.addLayout(self.nameLayout)
        #help
        self.searchHelpButton=QPushButton('?')
        self.searchHelpButton.setFixedWidth(24)
        self.searchHelpButton.setStyleSheet('background-color:green; color:White')
        self.searchHelpButton.setToolTip("Obtenir de l'aide sur le filtrage et la recherche")
        self.filterLayout.addWidget(self.searchHelpButton)
        self.ui.filterGroupBox.setLayout(self.filterLayout) 
        self.ui.publicList.setStyleSheet("QListView{border: 2px solid green;}"\
                                         "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                            "QListView::item{border-bottom:2px solid gray}")
        self.ui.inventoryList.setStyleSheet("QListView{border: 2px solid green;}"\
                                            "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                                "QListView::item{border-bottom:2px solid gray}")


    #---------------------------------------------------------------------------
    QtCore.pyqtSlot()
    def on_supplier_closedPopup(self):
        self.active_suppliers=self.supplierFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.yearSearchEdit.setText('')
        self.filter_list()
    #----------------------------------------------
    def toggle_supplier_filter(self):
        if self.supplier_checkbox.isChecked():
            self.supplierFilterCombo.setVisible(True)
        else:
            self.supplierFilterCombo.setVisible(False)
           
        self.filter_list()

    #---------------------------------------------------------------------------
    QtCore.pyqtSlot()
    def on_form_closedPopup(self):
        self.active_forms=self.formFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.yearSearchEdit.setText('')
        self.filter_list()
    #----------------------------------------------
    def toggle_form_filter(self):
        if self.form_checkbox.isChecked():
            self.formFilterCombo.setVisible(True)
        else:
            self.formFilterCombo.setVisible(False)
            
        self.filter_list()
     
    #---------------------------------------------------------------------------
    QtCore.pyqtSlot()
    def on_purpose_closedPopup(self):
        self.active_purposes=self.purposeFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.yearSearchEdit.setText('')
        self.filter_list()
    #----------------------------------------------    
    def toggle_purpose_filter(self):
        if self.purpose_checkbox.isChecked():
            self.purposeFilterCombo.setVisible(True)
        else:
            self.purposeFilterCombo.setVisible(False)
            
        self.filter_list()
    #-----------------------------------------------------------------------------------------------
    def filter_list(self):
        items=self.public_list
        filtered=list(filter(lambda x:\
                                  (x.supplier in self.active_suppliers or not self.supplier_checkbox.isChecked()) and \
                                    (x.form in self.active_forms or not self.form_checkbox.isChecked()) and \
                                        (x.purpose in self.active_purposes or not self.purpose_checkbox.isChecked())\
                                            ,items ))
        
        filtered.sort(key=lambda x: (x.supplier,x.name,x.crop_year))
        self.model.hops=filtered 
        self.model.layoutChanged.emit()  
    #------------------------------------------------------------------------------------------------
    def search_in_name(self):
        self.yearSearchEdit.setText('')
        self.filter_list()#we start with the filtered list
        pattern=self.searchEdit.text()
        print('searching in name '+pattern)
        if pattern != '':
            items=self.model.hops #we search only in the filtered list
            sorted_array=list(filter(lambda x: re.search(pattern, x.name,re.IGNORECASE),items)) 
            self.model.hops=sorted_array
            self.model.layoutChanged.emit()
    
    #----------------------------------------------------------------------------------------------
    def search_year(self):
        self.searchEdit.setText('')
        self.filter_list()#we start with the filtered list
        pattern=self.yearSearchEdit.text()
        if pattern != '':
            items=self.model.hops #we search only in the filtered list
            sorted_array=list(filter(lambda x: re.search(pattern, x.crop_year,re.IGNORECASE),items)) 
            self.model.hops=sorted_array
            self.model.layoutChanged.emit()
       
    #----------------------------------------------------------------------------
    def set_validators(self):

        #set the validators-----------------------------------------------------------------------------------------
   
        locale=QtCore.QLocale('en')    
        self.alpha_validator = QDoubleValidator(0.0,20.0,1)
        self.alpha_validator.setLocale(locale)   
        self.alpha_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.alphaEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-1]?[0-9]{0,1}[\\.][0-9]")))
        
      
        self.quantity_validator=QDoubleValidator(0.0,1000.0,1)
        self.quantity_validator.setLocale(locale)
        self.quantity_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.quantityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}")))
        self.ui.invQuantityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}")))
        
        self.cost_validator=QDoubleValidator(0.0,500,2)
        self.cost_validator.setLocale(locale)
        self.cost_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.costEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-4]?[0-9]{0,2}[\\.][0-9]{0,2")))
        self.ui.invCostEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-4]?[0-9]{0,2}[\\.][0-9]{0,2")))
        
        accepted_chars_crop_year = QRegularExpressionValidator(QRegularExpression("20[0-9]{2}"))
        self.crop_year_validator=QIntValidator(2019,self.current_year) 
        self.crop_year_validator.setLocale(locale)
        self.ui.cropYearEdit.setValidator(accepted_chars_crop_year)
    #------------------------------------------------------------------------------------------------------
    def select_destination(self):
        #select an element in the destination list either for deletion, or update, or replacement
        old_selection=self.destination_selection
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            self.destination_selection=self.inventory_model.inventory_hops[index.row()]
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
            self.source_selection=self.model.hops[index.row()]
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
        self.inventory_model.inventory_hops=all_inventory_hop()
        self.inventory_model.layoutChanged.emit() 
        self.model.hops=all_hop()
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
            result= add_hop(data)
            if(result == 'OK'):
                self.cleanNewForm()
                self.set_message_public('success', 'Le houblon a été correctement enregistré')
                self.ui.labelMessage.setVisible(True)
                self.model.hops.append(data)
                self.public_list.sort(key=lambda x: (x.supplier,x.name,x.crop_year))
                self.model.layoutChanged.emit()
                self.hide_group_boxes()
            else:
                self.set_message_public('failure', result),
                self.ui.labelMessage.setVisible(True)  
        self.clear_selection('both') 
    #--------------------------------------------------------------------------           
    def update(self):
        #update an existing hop in the public list
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.model.hops[index.row()]
            read_item=self.read_new_form()
            if(read_item != False):
        #thi id has been set while loading form with selected item
                read_item.id=self.ui.idEdit.text()
                #attempt update in database
                result = update_hop(read_item)
                if(result == 'OK'):
                    self.cleanNewForm()
                    self.set_message_public('success', 'Le houblon a été correctement enregistré')
                    self.ui.labelMessage.setVisible(True)
                    selection=self.model.hops[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.supplier=read_item.supplier 
                    selection.crop_year=read_item.crop_year
                    selection.country_code=read_item.country_code
                    selection.form=read_item.form
                    selection.purpose=read_item.purpose
                    selection.aromas=read_item.aromas
                    selection.alternatives=read_item.alternatives
                    selection.alpha=read_item.alpha
                    selection.link=read_item.link
                    selection.notes=read_item.notes
                    self.public_list.sort(key=lambda x: (x.supplier,x.name,x.crop_year))
                    self.model.layoutChanged.emit()
                    #the update may affect the inventory hops
                    self.inventory_model.inventory_hops=all_inventory_hop()
                    self.inventory_model.layoutChanged.emit()
        self.clear_selection('both')     
        
    #------------------------------------------------------------------------------      
    def update_inventory(self):
        #update an ingredient in the inventory list
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.inventory_model.inventory_hops[index.row()]
            read_item=self.readUpdateInventoryForm()
            if(read_item != False):
                read_item.id=selection.id
                read_item.hop_id=selection.hop_id
                #update in database
                result =update_inventory_hop(read_item)
                if(result == 'OK'):
                    self.set_message_inventory('success', 'Le houblon d\'inventaire a été correctement enregistré')
                    self.ui.labelMessage_2.setVisible(True)
                    selection.quantity=read_item.quantity
                    selection.cost=read_item.cost
                    self.inventory_model.layoutChanged.emit()
                    self.hide_group_box_inv()
        
                else:
                    self.set_message_inventory('failure', result),
                    self.ui.labelMessage_2.setVisible(True) 
            else:
                self.set_message_inventory('failure','Vous devez sélectionner un houblon')                  
        self.clear_selection('both')                          
           
    #-------------------------------------------------------------------------------            
    def delete(self):
        #delete an ingredient from the public list       
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
                selected_item= self.model.hops[index.row()]
                #delete from database
                result=delete_hop(selected_item.id)
                if (result == 'OK'):
                    self.set_message_public('success', 'Le houblon a été correctement supprimé')
                    self.ui.labelMessage.setVisible(True)
                    # Remove the item and refresh.
                    del self.model.hops[index.row()]
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
        #delete an ingredient from the inventory list        
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
                selected_item=self.inventory_model.inventory_hops[index.row()]
                #delete from database
                result=delete_inventory_hop(selected_item.id)
                if (result == 'OK'):
                    self.set_message_inventory('success',"Le houblon d'inventaire a été correctement supprimé.")
                    self.ui.labelMessage_2.setVisible(True)
                    del self.inventory_model.inventory_hops[index.row()]
                    self.inventory_model.layoutChanged.emit()
                    self.ui.inventoryList.clearSelection()
                    self.hide_group_box_inv()
                else:
                    self.set_message_inventory('failure',result)
                    self.ui.labelMessage_2.setVisible(True)    
            else:
                self.set_message_inventory('failure','Vous devez sélectionner un houblon')        
            self.clear_selection('both') 
                   
 #------------------------------------------------------------------------------------            
    def importation(self,mode):
    #import a hop into the inventory
        #import form is for quantity and cost
        if mode =='replace':
            self.replacement()
            return
        read_item=self.readImportForm()
        if(read_item != False):
            result=add_inventory_hop(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success', 'Le houblon a été correctement importé')
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_hops.append(read_item) 
                self.inventory_list.sort(key=lambda x: str(x.purchase_date))
                self.inventory_model.layoutChanged.emit()
                self.hide_group_boxes()
            else:
                self.set_message_public('failure', result)
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
            selected_item=self.inventory_model.inventory_hops[index.row()]
            result=delete_inventory_hop(selected_item.id) 
            print('result of deletion is '+result)
            result=add_inventory_hop(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success', 'Le fermentable a été correctement importé')
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_hops.append(read_item) 
                del self.inventory_model.inventory_hops[index.row()]
                #self.ui.inventory_list=all_inventory_fermentable()
                self.inventory_list.sort(key=lambda x: str(x.purchase_date))
                self.inventory_model.layoutChanged.emit()
                self.hide_group_boxes()
            else:
                self.set_message_public('failure',result)
                self.ui.labelMessage.setVisible(True) 
        self.clear_selection('both')
       
    #-------------------------------------------------------------------------------------------    
    def load_hop(self):
        #load a hop's values in the new form after it has been selected in the public QListView
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.hops[index.row()]
            self.ui.idEdit.setText(str(selected_item.id))
            self.ui.nameEdit.setText(selected_item.name)
            self.ui.supplierCombo.setCurrentText(selected_item.supplier)
            self.ui.cropYearEdit.setText(selected_item.crop_year)
            country=find_country_by_code(selected_item.country_code)
            if country is not None:
                self.ui.countryCodeCombo.setCurrentText(country.name+' — '+country.country_code)
            self.ui.formCombo.setCurrentText(get_hop_form_name(selected_item.form))
            self.ui.purposeCombo.setCurrentText(get_hop_purpose_name(selected_item.purpose))
            self.ui.alphaEdit.setText(str(selected_item.alpha))
            self.ui.aromasEdit.setText(selected_item.aromas)
            self.ui.alternativesEdit.setText(selected_item.alternatives)
            self.ui.linkEdit.setText(selected_item.link)
            self.ui.notesEdit.setText(selected_item.notes)

    #---------------------------------------------------------------------------------------
    def set_message_public(self, style, text):
        self.ui.labelMessage.setText(text)
        if(style =='success'):
            self.ui.labelMessage.setStyleSheet('background-color:green; color: white;padding:10px')
            self.timer=QTimer()
            self.timer.timeout.connect(self.hide_message_public)
            self.timer.start(2000) 
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
            self.timer.start(2000) 
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

    #-----------------------------------------------------------------------------------------------        
    def load_inventory_hop(self):
        #load an inventory hop in the inventory form after it has been selected in the inventory QListView
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0] 
            selected_item=self.inventory_model.inventory_hops[index.row()]
            self.ui.idEdit_2.setText(str(selected_item.id))
            self.ui.invQuantityEdit.setText(str(selected_item.quantity))
            self.ui.invCostEdit.setText(str(selected_item.cost))
                 
    #-----------------------------------------------------------------------------------------------                    
    def read_new_form(self):
    #read the new hop form and check inputs are validated
    #returns False if not validated, returns new hop otherwise
        validated=True
        name=self.ui.nameEdit.text().upper()
        if(name == ''):
            self.ui.nameEdit.setStyleSheet('background-color: red; color:white;')
            validated = False
        supplier=self.ui.supplierCombo.currentText()
        if(supplier ==''):
            self.ui.supplierCombo.setStyleSheet('background-color: red; color:white;')
            validated=False
        crop_year=self.ui.cropYearEdit.text()
        r=self.crop_year_validator.validate(crop_year,0)
        if (r[0] != QtGui.QValidator.State.Acceptable): 
            self.ui.cropYearEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        country_code=self.ui.countryCodeCombo.currentText()[-2:]
        if (country_code == ''):
            self.ui.countryCodeCombo.setStyleSheet('background-color: red; color:white;')
            validated=False
        form=self.ui.formCombo.currentData()
        if(form == ''):
            self.ui.formCombo.setStyleSheet('background-color: red; color:white;')
            validated=False
        purpose=self.ui.purposeCombo.currentText()
        if(purpose==''):
            self.ui.purposeCombo.setStyleSheet('background-color: red; color:white;')
            validated=False

     
        alpha=self.ui.alphaEdit.text()
        r=self.alpha_validator.validate(alpha,0) 
        if( r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.alphaEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        aromas=self.ui.aromasEdit.text()
        alternatives=self.ui.alternativesEdit.text()
        link=self.ui.linkEdit.text() 
        notes=self.ui.notesEdit.toPlainText()
        if(validated == True):
            h=Hop (None,supplier,crop_year,country_code,name,form,purpose,alpha, aromas,alternatives,link,notes)  
            return h
        else:
            return False   

     #------------------------------------------------------------------------------------------------        
    def readImportForm(self):
    #read the import hop form and check inputs validated
    #returns Fals if not validated, returns a new inventory_hop otherwise
        validated=True
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.hops[index.row()]
            quantity=self.ui.quantityEdit.text()
            r=self.quantity_validator.validate(quantity,0)
            if(r[0] !=QtGui.QValidator.State.Acceptable):
                self.ui.quantityEdit.setStyleSheet('background-color: red; color:white;')
                validated=False
              
            cost=self.ui.costEdit.text()
            r=self.cost_validator.validate(cost,0)
            if(r[0] != QtGui.QValidator.State.Acceptable):
                self.ui.costEdit.setStyleSheet( 'background-color: red; color:white;')
                validated = False
            purchase_date=self.ui.importDateEdit.date()
            pd=date.fromisoformat(purchase_date.toString("yyyy-MM-dd"))#iso format

            if(validated == True):
                inventory_ferm=InventoryHop(None,selected_item.id,quantity,cost,pd,False) 
                return inventory_ferm
            else:
                return False
        else:
            self.set_message_public('failure','Vous devez sélectionner un houblon !')
            return False

    #---------------------------------------------------------------------------------------------       
    def readUpdateInventoryForm(self):
    #read the update inventory hop form and check inputs validated
    #returns Fals if not validated, returns a new inventory_hop otherwise
        validated=True
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.inventory_model.inventory_hops[index.row()]
            quantity=self.ui.invQuantityEdit.text()
            r=self.quantity_validator.validate(quantity,0)
            if(r[0] !=QtGui.QValidator.State.Acceptable):
                self.ui.invQuantityEdit.setStyleSheet('background-color: red; color:white;')
                validated=False
            cost=self.ui.invCostEdit.text()
            r=self.cost_validator.validate(cost,0)
            if(r[0] != QtGui.QValidator.State.Acceptable):
                self.ui.invCostEdit.setStyleSheet( 'background-color: red; color:white;')
                validated = False
            if(validated == True):
                inventory_ferm=InventoryHop(None,selected_item.id,quantity,cost,selected_item.purchase_date,selected_item.frozen) 
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
                self.ui.quantityEdit.setStyleSheet('background-color: white;color:black;')
            case 'cost':
                self.ui.costEdit.setStyleSheet('background-color: white;color:black;')
            case 'name':
                self.ui.nameEdit.setStyleSheet('background-color: white;color:black;')
            case 'crop_year':
                self.ui.cropYearEdit.setStyleSheet('background-color: white;color:black;')   
            case 'supplier':
                self.ui.supplierCombo.setStyleSheet('background-color: white;color:black;') 
            case 'country':
                self.ui.countryCodeCombo.setStyleSheet('background-color: white;color:black;') 
            case 'form':
                self.ui.formCombo.setStyleSheet('background-color: white;color:black;') 
            case 'purpose':
                self.ui.purposeCombo.setStyleSheet('background-color: white;color:black;') 
            case 'alpha':
                self.ui.alphaEdit.setStyleSheet('background-color: white;color:black;')
            case 'quantity_2':
                self.ui.invQuantityEdit.setStyleSheet('background-color: white;color:black;')
            
            case 'cost_2':
                self.ui.invCostEdit.setStyleSheet('background-color: white;color:black;')

    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        #clean the form for adding or updating a public ingredient
        self.ui.alphaEdit.setStyleSheet('background-color: white; color:black;')
        self.ui.nameEdit.setText('')
        self.ui.supplierCombo.setCurrentIndex(0)
        self.ui.alphaEdit.setText('')
        self.ui.formCombo.setCurrentIndex(0)
        self.ui.purposeCombo.setCurrentIndex(0) 
        self.ui.countryCodeCombo.setCurrentIndex(0)
        self.ui.aromasEdit.setText('')  
        self.ui.alternativesEdit.setText('')   
        self.ui.cropYearEdit.setText('')  
        self.ui.linkEdit.setText('') 
        self.ui.notesEdit.setText('')    

    #------------------------------------------------------------------------------------------    
    def cleanImportForm(self):
        #clean the importation form
        self.ui.quantityEdit.setStyleSheet('background-color: white; color:black;')
        self.ui.costEdit.setStyleSheet('background-color: white; color:black;')
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
            self.set_message_inventory('failure','Vous devez sélectionner un houblon')
        
    #------------------------------------------------------------------------------------------
    def hide_group_boxes(self):
        #hide the forms in the public side
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(False)
        self.ui.inventoryList.clearSelection()
        self.ui.publicList.clearSelection()
    #------------------------------------------------------------------------------------------
    def hide_group_box_inv(self):
        #hide the form in the inventory side
        self.ui.groupBoxImport_2.setVisible(False) 
        self.clear_selection('destination')  

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
                    self.load_hop()
                    self.showNewInputs(True)
                    self.ui.addButton.setVisible(False)
                    self.ui.updateButton.setVisible(True) 
                if(mode == 'import'):
                    self.showImportInputs()
            else:
                self.set_message_public('failure','Vous devez sélectionner un houblon')
        
    #--------------------------------------------------------------------------------------------
    def adjust_cost(self):
        #print('adjusting cost')
        if(self.ui.checkBox.isChecked()==False) :
            return 
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0] 
            selected_item=self.inventory_model.inventory_hops[index.row()]  
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
   
class HopModel(QtCore.QAbstractListModel):
    #a model for the public QListView
    def __init__(    self, *args, hops=None, **kwargs):
        super(HopModel,self).__init__(*args, **kwargs)
        self.hops = hops or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            h =self.hops[index.row()] 
            hname=self.str_normalize(h.name,15)
            hsupplier=self.str_normalize(str(h.supplier),20)
            form=get_hop_form_name(h.form)
            purpose=get_hop_purpose_name(h.purpose)
            return str(h.id)+' '+hname+' '+h.crop_year +' vendu par ' +hsupplier+'   '+'\n ('+form+', '+purpose+', '+str(h.alpha)+' %)'
        if (role == Qt.ItemDataRole.DecorationRole):
            h=self.hops[index.row()]
            filename='./w20/'+h.country_code+'.png'
            return QtGui.QImage(filename)
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.hops)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

###########################################################################################################
###########################################################################################################    
#     
class InventoryHopModel(QtCore.QAbstractListModel):
    #a model for the inventory QListView
    def __init__(    self, *args, inventory_hops=None, **kwargs):
        super(InventoryHopModel,self).__init__(*args, **kwargs)
        self.inventory_hops = inventory_hops or []
           
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            invh =self.inventory_hops[index.row()] 
            h=find_hop_by_id(invh.hop_id)
            hname=self.str_normalize(h.name,15)
            hsupplier=self.str_normalize(str(h.supplier),20)
            hid=self.str_normalize(str(h.id),3)
            form=get_hop_form_name(h.form)
            purpose=get_hop_purpose_name(h.purpose)
            return  hname+' '+str(h.crop_year) +' acheté chez ' +str(hsupplier)+'   '+'\n'+ \
            'QUANTITÉ : '+str(invh.quantity)+' g'+ ' COÛT : '+str(invh.cost) +' € — Id public : '+hid+ ' acheté le '+DateUtils.FrenchDate(invh.purchase_date)+\
            '\n ('+str(form)+', '+str(purpose)+', '+str(h.alpha)+' % )'
            #return '['+str(invf.id)+', '+f.name+' from '+f.brand+'], \n Quantity = '+str(invf.quantity)+' kg, '+'Cost = '+str(invf.cost)
        if (role == Qt.ItemDataRole.DecorationRole):
            invh =self.inventory_hops[index.row()] 
            h=find_hop_by_id(invh.hop_id)

            filename='./w20/'+h.country_code+'.png'
            return QtGui.QImage(filename)  
                
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       
                
    def rowCount(self,index):
        return len(self.inventory_hops)           
                     