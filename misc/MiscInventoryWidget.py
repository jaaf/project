import datetime
import re

from PyQt6 import QtCore, QtGui,QtWidgets
from PyQt6.QtCore import QRegularExpression, Qt, QTimer
from PyQt6.QtGui import (QDoubleValidator,
                         QRegularExpressionValidator)
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLineEdit, QPushButton,
                             QWidget)

from database.miscs.misc import (InventoryMisc, add_inventory_misc,
                                           all_inventory_misc,
                                           delete_inventory_misc,
                                           update_inventory_misc)
from database.miscs.misc import (Misc, add_misc, all_misc, delete_misc,
                                 find_misc_by_id, update_misc)
from dateUtils import DateUtils
from datetime import date
from ConfirmationDialog import ConfirmationDialog
from ListModels import InventoryMiscModel, MiscModel
from misc.MiscInventoryWidgetBase import Ui_Form as miscInventoryWgt
from parameters import misc_category, misc_unit


class MiscInventoryWidget(QWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =miscInventoryWgt()
        self.ui.setupUi(self)
        self.id=id
        self.parent=parent

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
        self.ui.importDateEdit.setDate(self.today)
        self.icon_path='base-data/icons/'        
        self.source_selection=None
        self.destination_selection=None
        self.hide_main_mode_buttons()
        self.hide_inventory_mode_buttons()
        self.ui.newButton.setVisible(True)
        self.complete_gui()
        self.set_validators()
        self.set_connections()        

    def set_connections(self):
        #set the connections ------------------------------------------------------------------------------
        self.searchEdit.editingFinished.connect(self.search_in_name)
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
        
        self.ui.categoryCombo.currentIndexChanged.connect(lambda :self.cleanEdit('category'))
        self.ui.unitCombo.currentIndexChanged.connect(lambda :self.cleanEdit('unit'))
        self.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
       
        self.ui.invQuantityEdit.textChanged.connect(lambda :self.cleanEdit('quantity_2'))
        self.ui.invCostEdit.textChanged.connect(lambda :self.cleanEdit('cost_2'))
    
    #------------------------------------------------------------------------------------------------
    def search_in_name(self):
        #self.filter_list()#we start with the filtered list
        self.model.miscs=self.public_list
        pattern=self.searchEdit.text()
        print('searching in name '+pattern)
        if pattern != '':
            items=self.model.miscs #we search only in the filtered list
            sorted_array=list(filter(lambda x: re.search(pattern, x.name,re.IGNORECASE),items)) 
            self.model.miscs=sorted_array
        self.model.layoutChanged.emit()

    def complete_gui(self):
        self.ui.labelInventoryTitle.setStyleSheet(self.font_style_prefix+'font-weight:600')
        self.ui.labelPublicTitle.setStyleSheet(self.font_style_prefix+'font-weight:600')
       #initialize the various comboBox-----------------------------------------------------------------------------
        for c in misc_category:
            self.ui.categoryCombo.addItem(c)
        
        for u in misc_unit:
            self.ui.unitCombo.addItem(u)
  
        #Complete the GUI --------------------------------------------------------------------------------
       
        self.ui.importDateEdit.setCalendarPopup(True)
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
        self.public_list=all_misc()
        self.inventory_list=all_inventory_misc()
        self.public_list.sort(key=lambda x: (x.name))  
        self.inventory_list.sort(key=lambda x: str(x.purchase_date)) 
        self.model = MiscModel(miscs=self.public_list)
        self.ui.publicList.setModel(self.model)
        self.inventory_model=InventoryMiscModel(inventory_miscs=self.inventory_list)
        self.ui.inventoryList.setModel(self.inventory_model)
        self.mode_import='add' #the import button has two roles: adding to the inventory or replacing in inventory
        #filters
        self.filterLayout=QHBoxLayout()
        self.searchEdit=QLineEdit()
        self.searchEdit.setPlaceholderText('🔍Entrée en fin de saisie')
        self.filterLayout.addWidget(self.searchEdit)
        self.searchHelpButton=QPushButton('?')
        self.searchHelpButton.setFixedWidth(24)
        self.searchHelpButton.setStyleSheet(self.font_style_prefix+'background-color:green; color:White')
        self.searchHelpButton.setToolTip("Obtenir de l'aide sur le filtrage et la recherche")
        self.filterLayout.addWidget(self.searchHelpButton)   
        self.ui.filterGroupBox.setLayout(self.filterLayout)    

        self.ui.publicList.setStyleSheet("QListView{border: 2px solid green;}"\
                                         "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                            "QListView::item{border-bottom:2px solid gray}")
        self.ui.inventoryList.setStyleSheet("QListView{border: 2px solid green;}"\
                                            "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                                "QListView::item{border-bottom:2px solid gray}")

    def set_validators(self):

        #set the validators-----------------------------------------------------------------------------------------
        #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
      

        accepted_chars_quantity = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]{2}")) 
        locale=QtCore.QLocale('en')
        self.quantity_validator=QDoubleValidator(0.0,1000.0,1)
        self.quantity_validator.setLocale(locale)
        self.quantity_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.quantityEdit.setValidator(accepted_chars_quantity)
        self.ui.invQuantityEdit.setValidator(accepted_chars_quantity)
        
        self.cost_validator=QDoubleValidator(0.0,500,2)
        self.cost_validator.setLocale(locale)
        self.cost_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.costEdit.setValidator(accepted_chars_quantity)
        self.ui.invCostEdit.setValidator(accepted_chars_quantity)

    #------------------------------------------------------------------------------------------------------
    def select_destination(self):
        #select an element in the destination list either for deletion, or update, or replacement
        old_selection=self.destination_selection
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            self.destination_selection=self.inventory_model.inventory_miscs[index.row()]
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
            self.source_selection=self.model.miscs[index.row()]
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
        self.inventory_model.inventory_miscs=all_inventory_misc()
        self.inventory_model.layoutChanged.emit()  
        self.model.miscs=all_misc()  
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
            result= add_misc(data)
            if(result == 'OK'):
                self.cleanNewForm()
                self.set_message_public('success', 'L\'ingrédient a été correctement enregistré')
                self.ui.labelMessage.setVisible(True)
                self.model.miscs.append(data)
                self.public_list.sort(key=lambda x: (x.name))
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
            selection=self.model.miscs[index.row()]
            read_item=self.read_new_form()
            if(read_item != False):
        #thi id has been set while loading form with selected item
                read_item.id=self.ui.idEdit.text()
                #attempt update in database
                result = update_misc(read_item)
                if(result == 'OK'):
                    self.cleanNewForm()
                    self.set_message_public('success', 'L\'ingrédient a été correctement enregistré')
                    self.ui.labelMessage.setVisible(True)
                    selection=self.model.miscs[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.category=read_item.category
                    selection.unit=read_item.unit
                    selection.notes=read_item.notes
                    self.public_list.sort(key=lambda x: (x.supplier,x.name,x.crop_year))
                    self.model.layoutChanged.emit()
                    #the update may affect the inventory miscs
                    self.inventory_model.inventory_miscs=all_inventory_misc()
                    self.inventory_model.layoutChanged.emit()
        self.clear_selection('both') 
        
     #------------------------------------------------------------------------------      
    def update_inventory(self):
        #update an ingredient in the inventory list
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.inventory_model.inventory_miscs[index.row()]
            read_item=self.readUpdateInventoryForm()
            if(read_item != False):
                read_item.id=selection.id
                read_item.misc_id=selection.misc_id
                #update in database
                result =update_inventory_misc(read_item)
                if(result == 'OK'):
                    self.set_message_inventory('success', 'L\'ingrédient d\'inventaire a été correctement enregistré')
                    self.ui.labelMessage_2.setVisible(True)
                    selection.quantity=read_item.quantity
                    selection.cost=read_item.cost
                    self.inventory_model.layoutChanged.emit()
                    self.hide_group_box_inv()
        
                else:
                    self.set_message_inventory('failure', result),
                    self.ui.labelMessage_2.setVisible(True) 
        else:
            self.set_message_inventory('failure','Vous devez sélectionner un ingrédient')                  
                        
        self.clear_selection('both')        

    #-------------------------------------------------------------------------------            
    def delete(self):
        #delete an ingredient from the public list
        msgBox=ConfirmationDialog()
        msgBox.setTitle('Confirmer suppression')
        msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
        msgBox.setMessage('Vous êtes sur le point de supprimer un ingrédient divers de la liste publique. Cette suppression sera définitive. \n Confirmez-vous la suppression ?') 
        msgBox.setCancelButtonText('Non. Ne pas supprimer')
        msgBox.setConfirmButtonText('Oui. Supprimer.')
        confirm=msgBox.exec()   
        if(confirm == 1):
            indexes = self.ui.publicList.selectedIndexes()
            if indexes:
                # Indexes is a list of a single item in single-select mode.
                index = indexes[0]
                selected_item= self.model.miscs[index.row()]
                #delete from database
                result=delete_misc(selected_item.id)
                if (result == 'OK'):
                    self.set_message_public('success', 'L\'ingrédient a été correctement supprimé')
                    self.ui.labelMessage.setVisible(True)
                    # Remove the item and refresh.
                    del self.model.miscs[index.row()]
                    self.model.layoutChanged.emit()
                    # Clear the selection (as it is no longer valid).
                    self.ui.publicList.clearSelection()
                else:
                    self.set_message_public('failure', result)
                    self.ui.labelMessage.setVisible(True)    
            else:
                self.set_message_public('failure','Vous devez sélectionner un ingrédient') 
            self.clear_selection('both')
    
    #--------------------------------------------------------------------------------
    def delete_inventory(self):
        #delete an ingredient from the inventory list
        msgBox=ConfirmationDialog()
        msgBox.setTitle('Confirmer suppression')
        msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
        msgBox.setMessage('Vous êtes sur le point de supprimer un achat d\'ingrédient divers de votre inventaire. Cette suppression sera définitive. \n Confirmez-vous la suppression ?') 
        msgBox.setCancelButtonText('Non. Ne pas supprimer')
        msgBox.setConfirmButtonText('Oui. Supprimer.')
        confirm=msgBox.exec()   
        if(confirm == 1):
            indexes = self.ui.inventoryList.selectedIndexes()
            if indexes:
                index=indexes[0]
                selected_item=self.inventory_model.inventory_miscs[index.row()]
                #delete from database
                result=delete_inventory_misc(selected_item.id)
                if (result == 'OK'):
                    self.set_message_inventory('success',"L'ingrédient d'inventaire a été correctement supprimé.")
                    self.ui.labelMessage_2.setVisible(True)
                    del self.inventory_model.inventory_miscs[index.row()]
                    self.inventory_model.layoutChanged.emit()
                    self.ui.inventoryList.clearSelection()
                    self.hide_group_box_inv()
                else:
                    self.set_message_inventory('failure',result)
                    self.ui.labelMessage_2.setVisible(True)    
            else:
                self.set_message_inventory('failure','Vous devez sélectionner un ingrédient')  
            self.clear_selection('both')   

    #------------------------------------------------------------------------------------            
    def importation(self,mode):
    #import a misc into the inventory
        #import form is for quantity and cost
        if mode =='replace':
            self.replacement()
            return
        

        read_item=self.readImportForm()
        if(read_item != False):
            result=add_inventory_misc(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success', 'L\'ingrédient  a été correctement importé')
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_miscs.append(read_item) 
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
            selected_item=self.inventory_model.inventory_miscs[index.row()]
            result=delete_inventory_misc(selected_item.id) 
            result=add_inventory_misc(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success'," L'ingrédient divers a été correctement importé")
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_miscs.append(read_item) 
                del self.inventory_model.inventory_miscs[index.row()]
                #self.ui.inventory_list=all_inventory_fermentable()
                self.inventory_list.sort(key=lambda x: str(x.purchase_date))
                self.inventory_model.layoutChanged.emit()
                self.hide_group_boxes()
            else:
                self.set_message_public('failure',result)
                self.ui.labelMessage.setVisible(True) 
        self.clear_selection('source')
        self.clear_selection('destination')
      
                                       
    #-------------------------------------------------------------------------------------------    
    def load_misc(self):
        #load a misc's values in the new form after it has been selected in the public QListView
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.miscs[index.row()]
            self.ui.idEdit.setText(str(selected_item.id))
            self.ui.nameEdit.setText(selected_item.name)
            self.ui.categoryCombo.setCurrentText(selected_item.category)
            self.ui.unitCombo.setCurrentText(selected_item.unit)
            self.ui.notesEdit.setText(selected_item.notes)
                   

    

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
    
    #-----------------------------------------------------------------------------------------------        
    def load_inventory_misc(self):
        #load an inventory misc in the inventory form after it has been selected in the inventory QListView
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0] 
            selected_item=self.inventory_model.inventory_miscs[index.row()]
            self.ui.idEdit_2.setText(str(selected_item.id))
            self.ui.invQuantityEdit.setText(str(selected_item.quantity))
            self.ui.invCostEdit.setText(str(selected_item.cost))
                 
    #-----------------------------------------------------------------------------------------------                    
    def read_new_form(self):
    #read the new misc form and check inputs are validated
    #returns False if not validated, returns new misc otherwise
        validated=True
        name=self.ui.nameEdit.text().upper()
        if(name == ''):
            self.ui.nameEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated = False

        category=self.ui.categoryCombo.currentText()
        if(category == ''):
            self.ui.categoryCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False 
        unit=self.ui.unitCombo.currentText()
        if(unit == ''):
            self.ui.unitCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
    
        notes=self.ui.notesEdit.toPlainText()
        if(validated == True):
            m=Misc (None,name,category,unit,notes)  
            return m
        else:
            return False  

     #------------------------------------------------------------------------------------------------        
    def readImportForm(self):
    #read the import misc form and check inputs validated
    #returns Fals if not validated, returns a new inventory_misc otherwise
        validated=True
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.miscs[index.row()]
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
                inventory_ferm=InventoryMisc(None,selected_item.id,quantity,cost,pd,False) 
                return inventory_ferm
            else:
                return False
        else:
            self.set_message_public('failure','Vous devez sélectionner un ingrédient !')
            return False

    #---------------------------------------------------------------------------------------------       
    def readUpdateInventoryForm(self):
    #read the update inventory misc form and check inputs validated
    #returns Fals if not validated, returns a new inventory_misc otherwise
        validated=True
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.inventory_model.inventory_miscs[index.row()]
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
                inventory_ferm=InventoryMisc(None,selected_item.id,quantity,cost,selected_item.purchase_date,selected_item.frozen) 
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
            case 'category':
                self.ui.categoryCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
            case 'unit':
                self.ui.unitCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;') 
            
            case 'quantity_2':
                self.ui.invQuantityEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            
            case 'cost_2':
                self.ui.invCostEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')


    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        #clean the form for adding or updating a public ingredient
        self.ui.nameEdit.setText('')
        self.ui.categoryCombo.setCurrentIndex(0)
        self.ui.unitCombo.setCurrentIndex(0)
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
            self.set_message_inventory('failure','Vous devez sélectionner un ingrédient')
        
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
                    self.load_misc()
                    self.showNewInputs(True)
                    self.ui.addButton.setVisible(False)
                    self.ui.updateButton.setVisible(True) 
                if(mode == 'import'):
                    self.showImportInputs()
            else:
                self.set_message_public('failure','Vous devez sélectionner un ingrédient')
        
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
            try:# to avoid crash when quantity and cost already at zero. Needs unbinding
                new_cost=float(selected_item.cost )* float(self.ui.invQuantityEdit.text())/float(selected_item.quantity)
                self.ui.invCostEdit.setText('{:0.2f}'.format(new_cost))
            except:
                pass
                

