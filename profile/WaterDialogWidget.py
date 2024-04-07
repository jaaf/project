from profile.WaterDialogWidgetBase import Ui_WaterDialog as waterDlg
from PyQt6 import QtCore,QtWidgets
from PyQt6.QtWidgets import QDialog,QWidget
from PyQt6 import QtCore
from database.profiles.water import all_water, update_water,Water, add_water,delete_water, find_water_by_id
from dateUtils import DateUtils
from PyQt6.QtCore import Qt,QRegularExpression,QTimer
from database.commons.country import all_country,find_country_by_code
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator,QIntValidator
from PyQt6 import QtGui
import sys, datetime







class WaterDialogWidget(QWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =waterDlg()
        self.ui.setupUi(self)
        self.id=id
       
        self.parent=parent
        today=datetime.date.today()
        current_year=today.year
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
    
        

  
        
        #set the validators-----------------------------------------------------------------------------------------
        #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
        accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]"))
        locale=QtCore.QLocale('en')    
        self.first_validator = QDoubleValidator(0.0,2000.0,1)
        self.first_validator.setLocale(locale)   
        self.first_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.caEdit.setValidator(accepted_chars)
        self.ui.mgEdit.setValidator(accepted_chars)
        self.ui.naEdit.setValidator(accepted_chars)
        self.ui.clEdit.setValidator(accepted_chars)
        self.ui.so4Edit.setValidator(accepted_chars)
        self.ui.alcaEdit.setValidator(accepted_chars)
        self.ui.pHEdit.setValidator(accepted_chars)
        #Complete the GUI --------------------------------------------------------------------------------
        self.ui.labelTitle.setStyleSheet(self.font_style_prefix+'font-weight:600')
        self.ui.idEdit.setVisible(False)
        self.hide_message_public()
        #self.ui.groupBoxNew.setVisible(False)
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
        

        self.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
        self.ui.caEdit.textChanged.connect(lambda :self.cleanEdit('ca'))
        self.ui.mgEdit.textChanged.connect(lambda :self.cleanEdit('mg'))
        self.ui.naEdit.textChanged.connect(lambda :self.cleanEdit('na'))
        self.ui.clEdit.textChanged.connect(lambda :self.cleanEdit('cl'))
        self.ui.so4Edit.textChanged.connect(lambda :self.cleanEdit('so4'))
        self.ui.alcaEdit.textChanged.connect(lambda :self.cleanEdit('alca'))
        self.ui.pHEdit.textChanged.connect(lambda : self.cleanEdit('pH'))


        
    #-----------------------------------------------------------------------------
    def add(self):
        #add a new ingredient to the public list
        data=self.read_new_form()
        if(data != False):
            result= add_water(data)
            if(result == 'OK'):
                #print('success')
                self.cleanNewForm()
                self.set_message_public('success', 'Le profil a été correctement enregistré')
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
                    self.set_message_public('success', 'Le profil a été correctement enregistré')
                    self.ui.labelMessage.setVisible(True)
                    selection=self.model.waters[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.ca=read_item.ca
                    selection.mg=read_item.mg
                    selection.na=read_item.na
                    selection.cl=read_item.cl
                    selection.so4=read_item.so4
                    selection.alca=read_item.alca
                    selection.pH=read_item.pH
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
            self.ui.idEdit.setText(str(selected_item.id))
            self.ui.nameEdit.setText(selected_item.name)
            self.ui.caEdit.setText(str(selected_item.ca))
            self.ui.mgEdit.setText(str(selected_item.mg))
            self.ui.naEdit.setText(str(selected_item.na))
            self.ui.clEdit.setText(str(selected_item.cl))
            self.ui.so4Edit.setText(str(selected_item.so4))
            self.ui.alcaEdit.setText(str(selected_item.alca))
            
            self.ui.pHEdit.setText(str(selected_item.pH))
        
            
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
        name=self.ui.nameEdit.text().upper()
        if(name == ''):
            self.ui.nameEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated = False

        ca=self.ui.caEdit.text()
        r=self.first_validator.validate(ca,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.caEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        mg=self.ui.mgEdit.text()
        r=self.first_validator.validate(mg,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.mgEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        na=self.ui.naEdit.text()
        r=self.first_validator.validate(na,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.naEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        cl=self.ui.clEdit.text()
        r=self.first_validator.validate(cl,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.clEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        so4=self.ui.so4Edit.text()
        r=self.first_validator.validate(so4,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.so4Edit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        alca=self.ui.alcaEdit.text()
        r=self.first_validator.validate(alca,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.alcaEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        
        pH=self.ui.pHEdit.text()
        r=self.first_validator.validate(pH,0)
        if (r[0] !=QtGui.QValidator.State.Acceptable):
            self.ui.pHEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            validated=False
        

        if(validated == True):
            e=Water (None,name,ca,mg,na,cl, so4,alca,pH)  
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
                self.ui.nameEdit.setStyleSheet(self.font_style_prefix+'background-color: white;color:black;')  
   

  
  
    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        #clean the form for adding or updating a public ingredient
        self.ui.nameEdit.setText('')
        self.ui.caEdit.setText('')
        self.ui.mgEdit.setText('')
        self.ui.naEdit.setText('')
        self.ui.clEdit.setText('')
        self.ui.so4Edit.setText('')
        self.ui.alcaEdit.setText('')
        self.ui.pHEdit.setText('')
      


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

         
                     
