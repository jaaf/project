from misc.MiscSelectorBase import Ui_MiscSelector as msel
from PyQt6.QtWidgets import QDialog
from PyQt6 import QtCore
from database.miscs.misc import all_misc, update_misc,Misc, add_misc,delete_misc, find_misc_by_id
from database.miscs.misc import all_inventory_misc, InventoryMisc, add_inventory_misc, delete_inventory_misc, update_inventory_misc
from dateUtils import DateUtils
from PyQt6.QtCore import Qt,QRegularExpression,QTimer
from parameters import misc_category,misc_unit
from database.commons.country import all_country,find_country_by_code
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator,QIntValidator
from PyQt6 import QtGui
import sys, datetime


class MiscSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =msel()
        self.ui.setupUi(self)
   
        #print('----------------------------')
        self.px=self.parent().geometry().x()
        #print(self.px)
        self.py=self.parent().geometry().y()
        #print(self.py)
        self.w=self.parent().geometry().width()
        #print(self.w)

        self.h=self.parent().geometry().height()
        #print(self.h)  
        self.setGeometry(self.px,self.py+150,self.w,self.h-150)
        today=datetime.date.today()
        current_year=today.year
       
        #initialize the various comboBox-----------------------------------------------------------------------------
        for c in misc_category:
            self.ui.categoryCombo.addItem(c)
        
        for u in misc_unit:
            self.ui.unitCombo.addItem(u)
  
        
        #set the validators-----------------------------------------------------------------------------------------
        #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
      

        accepted_chars_quantity = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]{2}")) 
        locale=QtCore.QLocale('en')
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
        self.public_list=all_misc()
        self.inventory_list=all_inventory_misc()
        self.public_list.sort(key=lambda x: (x.brand,x.name))  
        self.inventory_list.sort(key=lambda x: str(x.purchase_date)) 
        self.model = MiscModel(miscs=self.public_list)
        self.ui.publicList.setModel(self.model)
        self.inventory_model=InventoryMiscModel(inventory_miscs=self.inventory_list)
        self.ui.inventoryList.setModel(self.inventory_model)
        
        #set the connections ------------------------------------------------------------------------------
        self.ui.newButton.clicked.connect(lambda: self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.importButton.clicked.connect(lambda: self.show_group_box('import'))
        self.ui.invEditButton.clicked.connect(self.show_group_box_inv)
        self.ui.hideNewButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton.clicked.connect(self.hide_group_boxes)
        self.ui.hideImportButton_2.clicked.connect(self.hide_group_box_inv)
        self.ui.publicList.clicked.connect(self.load_misc)
        self.ui.inventoryList.clicked.connect(self.load_inventory_misc)
        self.ui.addButton.clicked.connect(self.add)
        self.ui.updateButton.clicked.connect(self.update)
        self.ui.updateButton_2.clicked.connect(self.update_inventory)
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.invDeleteButton.clicked.connect(self.delete_inventory)
        self.ui.importButton.clicked.connect(self.showImportInputs)
        self.ui.confirmImportButton.clicked.connect(self.importation)
        self.ui.groupBoxNew.clicked.connect(self.hide_message_public)
        self.ui.closeMessageButton.clicked.connect(self.hide_message_public)
        self.ui.quantityEdit_2.textChanged.connect(self.adjust_cost)
            
        
        #set auto clean connection for reset of the controls-----------------------------------------------
        self.ui.quantityEdit.textChanged.connect(lambda :self.cleanEdit('quantity'))
        self.ui.costEdit.textChanged.connect(lambda :self.cleanEdit('cost'))
        
        self.ui.categoryCombo.currentIndexChanged.connect(lambda :self.cleanEdit('category'))
        self.ui.unitCombo.currentIndexChanged.connect(lambda :self.cleanEdit('unit'))
        self.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
        self.ui.brandEdit.textChanged.connect(lambda : self.cleanEdit('brand'))
       
        self.ui.quantityEdit_2.textChanged.connect(lambda :self.cleanEdit('quantity_2'))
        self.ui.costEdit_2.textChanged.connect(lambda :self.cleanEdit('cost_2'))
    
        
    #-----------------------------------------------------------------------------
    def add(self):
        #add a new ingredient to the public list
        data=self.read_new_form()
        if(data != False):
            result= add_misc(data)
            if(result == 'OK'):
                self.cleanNewForm()
                self.set_message_public('success', 'L\'ingrédient divers a été correctement enregistré')
                self.ui.labelMessage.setVisible(True)
                self.model.miscs.append(data)
                self.public_list.sort(key=lambda x: (x.name,x.brand))
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
                    self.set_message_public('success', 'L\'ingrédient divers a été correctement enregistré')
                    self.ui.labelMessage.setVisible(True)
                    selection=self.model.miscs[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.brand=read_item.brand
                    selection.category=read_item.category
                    selection.unit=read_item.unit
                    selection.notes=read_item.notes
                    self.public_list.sort(key=lambda x: (x.name,x.brand))
                    self.model.layoutChanged.emit()
                    #the update may affect the inventory miscs
                    self.inventory_model.inventory_miscs=all_inventory_misc()
                    self.inventory_model.layoutChanged.emit()

    #-------------------------------------------------------------------------------            
    def delete(self):
        #delete an ingredient from the public list
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            selected_item= self.model.miscs[index.row()]
            #delete from database
            result=delete_misc(selected_item.id)
            if (result == 'OK'):
                self.set_message_public('success', 'L\'ingrédient divers a été correctement supprimé')
                self.ui.labelMessage.setVisible(True)
                # Remove the item and refresh.
                del self.model.miscs[index.row()]
                self.model.layoutChanged.emit()
                # Clear the selection (as it is no longer valid).
                self.ui.publicList.clearSelection()
            else:
                self.set_message_public('failure', result)
                self.ui.labelMessage.setVisible(True)    

    #-------------------------------------------------------------------------------------------    
    def load_misc(self):
        #load a misc's values in the new form after it has been selected in the public QListView
        indexes = self.ui.publicList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.miscs[index.row()]
            self.ui.idEdit.setText(str(selected_item.id))
            self.ui.nameEdit.setText(selected_item.name)
            self.ui.brandEdit.setText(selected_item.brand)
            self.ui.categoryCombo.setCurrentText(selected_item.category)
            self.ui.unitCombo.setCurrentText(selected_item.unit)
            self.ui.notesEdit.setText(selected_item.notes)
              
    #------------------------------------------------------------------------------      
    def update_inventory(self):
        #update an ingredient in the inventory list
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.inventory_model.inventory_miscs[index.row()]
            read_item=self.readUpdateInventoryForm()
            if(read_item != False):
                read_item.id=self.ui.idEdit_2.text()
                read_item.misc_id=selection.misc_id
                #update in database
                result =update_inventory_misc(read_item)
                if(result == 'OK'):
                    self.set_message_inventory('success', 'L\'ingrédient divers d\'inventaire a été correctement enregistré')
                    self.ui.labelMessage_2.setVisible(True)
                    selection.quantity=read_item.quantity
                    selection.cost=read_item.cost
                    self.inventory_model.layoutChanged.emit()
        
                else:
                    self.set_message_inventory('failure', result),
                    self.ui.labelMessage_2.setVisible(True)       
                          
           
    #--------------------------------------------------------------------------------
    def delete_inventory(self):
        #delete an ingredient from the inventory list
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.inventory_model.inventory_miscs[index.row()]
            #delete from database
            result=delete_inventory_misc(selected_item.id)
            if (result == 'OK'):
                self.set_message_inventory('success',"L\'ingrédient divers d'inventaire a été correctement supprimé.")
                self.ui.labelMessage_2.setVisible(True)
                del self.inventory_model.inventory_miscs[index.row()]
                self.inventory_model.layoutChanged.emit()
                self.ui.inventoryList.clearSelection()
            else:
                self.set_message_inventory('failure',result)
                self.ui.labelMessage_2.setVisible(True)    
                
    #------------------------------------------------------------------------------------            
    def importation(self):
    #import a misc into the inventory
        #import form is for quantity and cost
        read_item=self.readImportForm()
        if(read_item != False):
            result=add_inventory_misc(read_item)
            if(result == 'OK'):
                self.cleanImportForm()
                self.set_message_public('success', 'Le houblon a été correctement importé')
                self.ui.labelMessage.setVisible(True)
                self.inventory_model.inventory_miscs.append(read_item) 
                self.inventory_list.sort(key=lambda x: str(x.purchase_date))
                self.inventory_model.layoutChanged.emit()
            else:
                self.set_message_public('failure', result)
                self.ui.labelMessage.setVisible(True)
        else:
            pass
   
    
    #---------------------------------------------------------------------------------------
    def set_message_public(self, style, text):
        #print('text is '+text)
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
    #-------------------------------------------------------------------------------------------    

    #------------------------------------------------------------------------------------------
 
    #-----------------------------------------------------------------------------------------------        
    def load_inventory_misc(self):
        #load an inventory misc in the inventory form after it has been selected in the inventory QListView
        indexes = self.ui.inventoryList.selectedIndexes()
        if indexes:
            index=indexes[0] 
            selected_item=self.inventory_model.inventory_miscs[index.row()]
            self.ui.idEdit_2.setText(str(selected_item.id))
            self.ui.quantityEdit_2.setText(str(selected_item.quantity))
            self.ui.costEdit_2.setText(str(selected_item.cost))
                 
    #-----------------------------------------------------------------------------------------------                    
    def read_new_form(self):
    #read the new misc form and check inputs are validated
    #returns False if not validated, returns new misc otherwise
        validated=True
        name=self.ui.nameEdit.text().upper()
        if(name == ''):
            self.ui.nameEdit.setStyleSheet('background-color: red; color:white;')
            validated = False
        brand=self.ui.brandEdit.text()
        if(brand ==''):
            self.ui.brandEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        category=self.ui.categoryCombo.currentText()
        if(category == ''):
            self.ui.categoryCombo.setStyleSheet('background-color: red; color:white;')
            validated=False 
        unit=self.ui.unitCombo.currentText()
        if(unit == ''):
            self.ui.unitCombo.setStyleSheet('background-color: red; color:white;')
            validated=False
    
        notes=self.ui.notesEdit.toPlainText()
        if(validated == True):
            m=Misc (None,name,brand,category,unit,notes)  
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
                self.ui.quantityEdit.setStyleSheet('background-color: red; color:white;')
                validated=False
              
            cost=self.ui.costEdit.text()
            r=self.cost_validator.validate(cost,0)
            if(r[0] != QtGui.QValidator.State.Acceptable):
                self.ui.costEdit.setStyleSheet( 'background-color: red; color:white;')
                validated = False
            purchase_date=self.ui.importDateEdit.date()
            pd=purchase_date.toString('yyyy-MM-dd')

            if(validated == True):
                inventory_ferm=InventoryMisc(None,selected_item.id,quantity,cost,pd,False) 
                return inventory_ferm
            else:
                return False
        else:
            self.set_message_public('failure','Vous devez sélectionner un item à importer')
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
                inventory_ferm=InventoryMisc(None,selected_item.id,quantity,cost,selected_item.frozen) 
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
            case 'brand':
                self.ui.brandEdit.setStyleSheet('background-color: white;color:black;') 
            case 'category':
                self.ui.categoryCombo.setStyleSheet('background-color: white;color:black;')  
            case 'unit':
                self.ui.unitCombo.setStyleSheet('background-color: white;color:black;') 
            
            case 'quantity_2':
                self.ui.quantityEdit_2.setStyleSheet('background-color: white;color:black;')
            
            case 'cost_2':
                self.ui.costEdit_2.setStyleSheet('background-color: white;color:black;')

    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        #clean the form for adding or updating a public ingredient
        self.ui.brandEdit.setText('')
        self.ui.nameEdit.setText('')
        self.ui.categoryCombo.setCurrentIndex(0)
        self.ui.unitCombo.setCurrentIndex(0)
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
        self.ui.importDateEdit.setDate(datetime.date.today())
        self.cleanNewForm() 
    
    #------------------------------------------------------------------------------------------
    def show_group_box_inv(self):
        #show the update inventory ingredient form (inventory side)
        self.ui.groupBoxImport_2.setVisible(True)
        self.ui.checkBox.setChecked(True)
        
    #------------------------------------------------------------------------------------------
    def hide_group_boxes(self):
        #hide the forms in the public side
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(False)
    
    #------------------------------------------------------------------------------------------
    def hide_group_box_inv(self):
        #hide the form in the inventory side
        self.ui.groupBoxImport_2.setVisible(False)   

    #------------------------------------------------------------------------------------------     
    def show_group_box(self,mode):
        #show the form for the selected (mode) operation (public side)
        if(mode == 'add'):
            self.showNewInputs()
            self.ui.addButton.setVisible(True)
            self.ui.updateButton.setVisible(False) 
        if(mode == 'update'):
            self.load_misc()
            self.showNewInputs(True)
            self.ui.addButton.setVisible(False)
            self.ui.updateButton.setVisible(True) 
        if(mode == 'import'):
            self.showImportInputs()

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
        if(selected_item.cost != '' and self.ui.invQuantityEdit.text() !=''  and selected_item.quantity != '' )   : 
            try:#to avoid crash in quantity and cost already at zero. Needs unbinding
                new_cost=float(selected_item.cost )* float(self.ui.quantityEdit_2.text())/float(selected_item.quantity)
                self.ui.costEdit_2.setText('{:0.2f}'.format(new_cost))
            except:
                pass
      
             
 ##############################################################################################################
 # ############################################################################################################     
   
class MiscModel(QtCore.QAbstractListModel):
    #a model for the public QListView
    def __init__(    self, *args, miscs=None, **kwargs):
        super(MiscModel,self).__init__(*args, **kwargs)
        self.miscs = miscs or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            m =self.miscs[index.row()] 
            mname=self.str_normalize(m.name,15)
            mbrand=self.str_normalize(str(m.brand),20)
            return str(m.id)+' '+mname+' '+' produit par ' +mbrand+' unité : '+m.unit
     
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.miscs)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

###########################################################################################################
###########################################################################################################    
#     
class InventoryMiscModel(QtCore.QAbstractListModel):
    #a model for the inventory QListView
    def __init__(    self, *args, inventory_miscs=None, **kwargs):
        super(InventoryMiscModel,self).__init__(*args, **kwargs)
        self.inventory_miscs = inventory_miscs or []
           
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            invy =self.inventory_miscs[index.row()] 
            y=find_misc_by_id(invy.misc_id)
            yname=self.str_normalize(y.name,15)
            ybrand=self.str_normalize(str(y.brand),20)
            yid=self.str_normalize(str(y.id),3)
            return  yname+' de ' +ybrand+'   '+'\n'+ \
            'QUANTITÉ : '+str(invy.quantity)+' '+y.unit+ ' COÛT : '+str(invy.cost) +' — Id public : '+yid+ ' acheté le '+DateUtils.FrenchDate(invy.purchase_date)
            #return '['+str(invf.id)+', '+f.name+' from '+f.brand+'], \n Quantity = '+str(invf.quantity)+' kg, '+'Cost = '+str(invf.cost)
        
                
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       
                
    def rowCount(self,index):
        return len(self.inventory_miscs)           
                     
