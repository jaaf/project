import datetime
from profile.WaterTargetDialogWidgetBase import Ui_WaterDialog as waterDlg
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QRegularExpression, Qt, QTimer
from PyQt6.QtGui import (QDoubleValidator, QIntValidator,QRegularExpressionValidator)
from PyQt6.QtWidgets import  QWidget
from database.profiles.watertarget import (WaterTarget, add_water, all_water,delete_water, find_water_by_id,update_water)

from database.profiles.style import Style,all_style
import time
class WaterTargetDialogWidget(QWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =waterDlg()
        self.ui.setupUi(self)
        self.id=id
        self.parent=parent

        app = QtWidgets.QApplication.instance()
        #as use of setStyleSheet prevents correct font propagation. Prepend all style with this prefix to fix this issue
        self.font_style_prefix='font:'+str(app.font().pointSize())+'pt '+app.font().family()+';'
        #don't understand why font is not correctly propagated though is is for hop and yeasts
        self.setFont(app.font())
        mylist=self.findChildren(QWidget)
        app_font=app.font()
        for item in mylist:
            item.setFont(app_font)
       
        #initialize the various comboBox-----------------------------------------------------------------------------
    
        self.styles=all_style()
        self.reset_name_combo(self.styles)
 

  
        
        #set the validators-----------------------------------------------------------------------------------------
        #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
        accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]"))
        locale=QtCore.QLocale('en')    
        self.first_validator = QDoubleValidator(0.0,2000.0,1)
        self.first_validator.setLocale(locale)   
        self.first_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.caMinEdit.setValidator(accepted_chars)
        self.ui.mgMinEdit.setValidator(accepted_chars)
        self.ui.naMinEdit.setValidator(accepted_chars)
        self.ui.clMinEdit.setValidator(accepted_chars)
        self.ui.so4MinEdit.setValidator(accepted_chars)
        self.ui.alcaMinEdit.setValidator(accepted_chars)
        self.ui.caMaxEdit.setValidator(accepted_chars)
        self.ui.mgMaxEdit.setValidator(accepted_chars)
        self.ui.naMaxEdit.setValidator(accepted_chars)
        self.ui.clMaxEdit.setValidator(accepted_chars)
        self.ui.so4MaxEdit.setValidator(accepted_chars)
        self.ui.alcaMaxEdit.setValidator(accepted_chars)

        #Complete the GUI --------------------------------------------------------------------------------
        self.ui.labelTitle.setStyleSheet(self.font_style_prefix+'font-weight:600')
        self.ui.idEdit.setVisible(False)
        self.hide_message_public()
        self.ui.groupBoxNew.setVisible(False)
        self.ui.waterList.setSpacing(6)
        
        #set the models ---------------------------------------------------------------------------------
        self.water_list=all_water()
        self.water_list.sort(key=lambda x: x.name)  
        self.model = WaterModel(waters=self.water_list)
        self.ui.waterList.setModel(self.model)
        
        #set the connections ------------------------------------------------------------------------------
        self.ui.newButton.clicked.connect(lambda: self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.waterList.clicked.connect(self.load_water)
        self.ui.addButton.clicked.connect(self.add)
        self.ui.updateButton.clicked.connect(self.update)
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.groupBoxNew.clicked.connect(self.hide_message_public)
        self.ui.closeMessageButton.clicked.connect(self.hide_message_public)
            
        
        #set auto clean connection for reset of the controls-----------------------------------------------
        

        self.ui.styleNameCombo.currentTextChanged.connect(lambda :self.cleanEdit('name'))
        self.ui.caMinEdit.textChanged.connect(lambda :self.cleanEdit('ca_min'))
        self.ui.mgMinEdit.textChanged.connect(lambda :self.cleanEdit('mg_min'))
        self.ui.naMinEdit.textChanged.connect(lambda :self.cleanEdit('na_min'))
        self.ui.clMinEdit.textChanged.connect(lambda :self.cleanEdit('cl_min'))
        self.ui.so4MinEdit.textChanged.connect(lambda :self.cleanEdit('so4_min'))
        self.ui.alcaMinEdit.textChanged.connect(lambda :self.cleanEdit('alca_min'))
        self.ui.caMaxEdit.textChanged.connect(lambda :self.cleanEdit('ca_max'))
        self.ui.mgMaxEdit.textChanged.connect(lambda :self.cleanEdit('mg_max'))
        self.ui.naMaxEdit.textChanged.connect(lambda :self.cleanEdit('na_max'))
        self.ui.clMaxEdit.textChanged.connect(lambda :self.cleanEdit('cl_max'))
        self.ui.so4MaxEdit.textChanged.connect(lambda :self.cleanEdit('so4_max'))
        self.ui.alcaMaxEdit.textChanged.connect(lambda :self.cleanEdit('alca_max'))

    #----------------------------------------------------------------------------
    def reset_name_combo(self, list):
        self.ui.styleNameCombo.clear()
        self.ui.styleNameCombo.addItem('')
        self.ui.styleNameCombo.addItem('')
        for style in list:
            self.ui.styleNameCombo.addItem(style.name) 
    #------------------------------------------------------------------------------
    def clean_all_edit(self):
        self.cleanEdit('ca_min')
        self.cleanEdit('mg_min')
        self.cleanEdit('na_min')
        self.cleanEdit('cl_min')
        self.cleanEdit('so4_min')
        self.cleanEdit('alca_min')
        self.cleanEdit('ca_max')
        self.cleanEdit('mg_max')
        self.cleanEdit('na_max')
        self.cleanEdit('cl_max')
        self.cleanEdit('so4_max')
        self.cleanEdit('alca_max')

    def refresh(self):
        print('showing up WaterTargetDialog')
        
        self.styles=all_style()
        self.reset_name_combo(self.styles)
        self.water_list=all_water()   
        self.water_list.sort(key=lambda x: x.name)  
        self.model.waters=self.water_list
        self.model.layoutChanged.emit()
    
    #-----------------------------------------------------------------------------
    def add(self):
        #add a new ingredient to the public list
        data=self.read_new_form()
        if(data != False):
            result= add_water(data)
            if(result == 'OK'):
                #print('success')
                self.cleanNewForm()
                self.set_message_public('success', "Le profil d'eau cible a été correctement enregistré")
                self.ui.labelMessage.setVisible(True)
                self.model.waters.append(data)
                self.water_list.sort(key=lambda x: x.name)
                self.model.layoutChanged.emit()
            else:
                #print('failure')
                self.set_message_public('failure', result),
                self.ui.labelMessage.setVisible(True)  
     
    #--------------------------------------------------------------------------           
    def update(self):
        #update an existing ingredient in the public list
        indexes = self.ui.waterList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.model.waters[index.row()]
            read_item=self.read_new_form()
            if(read_item != False):
        #thi id has been set while loading form with selected item
                read_item.id=self.ui.idEdit.text()
                #attempt update in database
                result = update_water(read_item)
                if(result == 'OK'):
                    self.cleanNewForm()
                    self.set_message_public('success', 'L\'équipement a été correctement enregistré')
                    self.ui.labelMessage.setVisible(True)
                    selection=self.model.waters[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.ca_min=read_item.ca_min
                    selection.mg_min=read_item.mg_min
                    selection.na_min=read_item.na_min
                    selection.cl_min=read_item.cl_min
                    selection.so4_min=read_item.so4_min
                    selection.alca_min=read_item.alca_min
                    selection.ca_max=read_item.ca_max
                    selection.mg_max=read_item.mg_max
                    selection.na_max=read_item.na_max
                    selection.cl_max=read_item.cl_max
                    selection.so4_max=read_item.so4_max
                    selection.alca_max=read_item.alca_max
                    self.water_list.sort(key=lambda x: x.name)
                    self.model.layoutChanged.emit()
                
                

    #-------------------------------------------------------------------------------            
    def delete(self):
        #delete an ingredient from the public list
        indexes = self.ui.waterList.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            selected_item= self.model.waters[index.row()]
            #delete from database
            result=delete_water(selected_item.id)
            if (result == 'OK'):
                self.set_message_public('success', 'Le profil d\'eau a été correctement supprimé')
                self.ui.labelMessage.setVisible(True)
                # Remove the item and refresh.
                del self.model.waters[index.row()]
                self.model.layoutChanged.emit()
                # Clear the selection (as it is no longer valid).
                self.ui.waterList.clearSelection()
            else:
                self.set_message_public('failure', result)
                self.ui.labelMessage.setVisible(True)    

    #-------------------------------------------------------------------------------------------    
    def load_water(self):
        #load a water's values in the new form after it has been selected in the public QListView
        indexes = self.ui.waterList.selectedIndexes()
        if indexes:
            index=indexes[0]
           
            selected_item=self.model.waters[index.row()] 
            print(selected_item)
            print(str(selected_item.id))
            self.ui.idEdit.setText(str(selected_item.id))
            print(selected_item.name)
            self.ui.styleNameCombo.setCurrentText(str(selected_item.name))
            #time.sleep(5)
            self.ui.caMinEdit.setText(str(selected_item.ca_min))
            self.ui.mgMinEdit.setText(str(selected_item.mg_min))
            self.ui.naMinEdit.setText(str(selected_item.na_min))
            self.ui.clMinEdit.setText(str(selected_item.cl_min))
            self.ui.so4MinEdit.setText(str(selected_item.so4_min))
            self.ui.alcaMinEdit.setText(str(selected_item.alca_min))
            self.ui.caMaxEdit.setText(str(selected_item.ca_max))
            self.ui.mgMaxEdit.setText(str(selected_item.mg_max))
            self.ui.naMaxEdit.setText(str(selected_item.na_max))
            self.ui.clMaxEdit.setText(str(selected_item.cl_max))
            self.ui.so4MaxEdit.setText(str(selected_item.so4_max))
            self.ui.alcaMaxEdit.setText(str(selected_item.alca_max))
    #---------------------------------------------------------------------------------------
    def set_message_public(self, style, text):
        self.ui.labelMessage.setText(text)
        if(style =='success'):
            #print('message success')
            self.ui.labelMessage.setStyleSheet(self.font_style_prefix+'background-color:green; color: white;padding:10px')
            self.timer=QTimer()
            self.timer.timeout.connect(self.hide_message_public)
            self.timer.start(2000) 
        if(style == 'failure'):
                #print('message failure')
                self.ui.labelMessage.setStyleSheet(self.font_style_prefix+'background-color:red; color: white;padding:10px')
                self.ui.closeMessageButton.setVisible(True)
    
   
    #-----------------------------------------------------------------------------------------          
    def   hide_message_public(self):
        self.ui.labelMessage.setVisible(False)  
        self.ui.closeMessageButton.setVisible(False) 
      
    #------------------------------------------------------------------------------------    

    #------------------------------------------------------------------------------------------
 
      
    #-----------------------------------------------------------------------------------------------                    
    def read_new_form(self):
    #read the new water form and check inputs are validated
    #returns False if not validated, returns new water otherwise
        validated=True
        name=self.ui.styleNameCombo.currentText()
        if(name == ''):
            self.ui.styleNameCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated = False

        ca_min=self.ui.caMinEdit.text()
        r=self.first_validator.validate(ca_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.caMinEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        mg_min=self.ui.mgMinEdit.text()
        r=self.first_validator.validate(mg_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.mgMinEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        na_min=self.ui.naMinEdit.text()
        r=self.first_validator.validate(na_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.naMinEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        cl_min=self.ui.clMinEdit.text()
        r=self.first_validator.validate(cl_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.clMinEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        so4_min=self.ui.so4MinEdit.text()
        r=self.first_validator.validate(so4_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.so4MinEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        alca_min=self.ui.alcaMinEdit.text()
        r=self.first_validator.validate(alca_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.alcaMinEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        

        ca_max=self.ui.caMaxEdit.text()
        r=self.first_validator.validate(ca_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.caMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        if ca_min>ca_max:
            self.ui.caMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            self.ui.caMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False

        mg_max=self.ui.mgMaxEdit.text()
        r=self.first_validator.validate(mg_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.mgMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False       
        if mg_min>mg_max:
            self.ui.mgMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            self.ui.mgMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False

        na_max=self.ui.naMaxEdit.text()
        r=self.first_validator.validate(na_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.naMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        if na_min>na_max:
            self.ui.naMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            self.ui.naMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False

        cl_max=self.ui.clMaxEdit.text()
        r=self.first_validator.validate(cl_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.clMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        if cl_min>cl_max:
            self.ui.clMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            self.ui.clMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False

        so4_max=self.ui.so4MaxEdit.text()
        r=self.first_validator.validate(so4_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.so4MaxEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        if so4_min>so4_max:
            self.ui.so4MinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            self.ui.so4MaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False

        alca_max=self.ui.alcaMaxEdit.text()
        r=self.first_validator.validate(alca_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.alcaMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False  
        if alca_min>alca_max:
            self.ui.alcaMinEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            self.ui.alcaMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: orange; color:white;')
            validated=False              

        if(validated == True):
            e=WaterTarget (None,name,ca_min,mg_min,na_min,cl_min, so4_min,alca_min,ca_max,mg_max,na_max,cl_max,so4_max,alca_max)  
            #print(e)
            return e
        else:
            #print('not validated water')
            return False   


  
    #-----------------------------------------------------------------------------------------------
    def cleanEdit(self, what):
        #auto clean a QLineEdit or a QComboBox after it has been marqued wrong when using it again
        match what:
           
            case 'name':
                self.ui.styleNameCombo.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
            case 'ca_min':
                self.ui.caMinEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
            case 'mg_min':
                self.ui.mgMinEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'na_min':
                self.ui.naMinEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
            case 'so4_min':
                self.ui.so4MinEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'cl_min':
                self.ui.clMinEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'alca_min':
                self.ui.alcaMinEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')

            case 'ca_max':
                self.ui.caMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
            case 'mg_max':
                self.ui.mgMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'na_max':
                self.ui.naMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
            case 'so4_max':
                self.ui.so4MaxEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'cl_max':
                self.ui.clMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')
            case 'alca_max':
                self.ui.alcaMaxEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')

  
  
    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        #clean the form for adding or updating a public ingredient
        self.clean_all_edit()
        self.ui.styleNameCombo.setCurrentText('')
        self.ui.caMinEdit.setText('')
        self.ui.mgMinEdit.setText('')
        self.ui.naMinEdit.setText('')
        self.ui.clMinEdit.setText('')
        self.ui.so4MinEdit.setText('')
        self.ui.alcaMinEdit.setText('')
        self.ui.caMaxEdit.setText('')
        self.ui.mgMaxEdit.setText('')
        self.ui.naMaxEdit.setText('')
        self.ui.clMaxEdit.setText('')
        self.ui.so4MaxEdit.setText('')
        self.ui.alcaMaxEdit.setText('')
      


    #------------------------------------------------------------------------------------------  
    def showNewInputs(self,keep=False):
        #show the add or update form and hide the importation form
        self.ui.groupBoxNew.setVisible(True)
        if(keep == False):
            self.cleanNewForm()

    

    #------------------------------------------------------------------------------------------
    def hide_group_boxes(self):
        #hide the forms in the public side
        self.ui.groupBoxNew.setVisible(False)
        self.ui.groupBoxImport.setVisible(False)
    
    
    #------------------------------------------------------------------------------------------     
    def show_group_box(self,mode):
        #show the form for the selected (mode) operation (public side)
        if(mode == 'add'):
            self.showNewInputs()
            self.ui.addButton.setVisible(True)
            self.ui.updateButton.setVisible(False) 
        if(mode == 'update'):
            self.load_water()
            self.showNewInputs(True)
            self.ui.addButton.setVisible(False)
            self.ui.updateButton.setVisible(True) 
       

        

             
 ##############################################################################################################
 # ############################################################################################################     
   
class WaterModel(QtCore.QAbstractListModel):
    #a model for the public QListView
    def __init__(    self, *args, waters=None, **kwargs):
        super(WaterModel,self).__init__(*args, **kwargs)
        self.waters = waters or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            w =self.waters[index.row()] 
            wname=self.str_normalize(w.name,15)
            return wname
     
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.waters)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

         
                     
