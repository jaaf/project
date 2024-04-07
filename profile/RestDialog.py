from profile.RestDialogBase import Ui_RestDialog as wsel
from PyQt6.QtWidgets import QDialog
from PyQt6 import QtCore
from database.profiles.rest import all_rest, update_rest,Rest, add_rest,delete_rest, find_rest_by_id
from PyQt6.QtCore import Qt,QRegularExpression,QTimer

from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator,QIntValidator
from PyQt6 import QtGui
from PyQt6.QtGui import QPalette,QColor
import sys, datetime
from Themes import Themes


class RestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =wsel()
        self.ui.setupUi(self)
        self.parent=parent
      
        #colors
        pal=self.parent.palette()
        self.setPalette(pal)#use the MainWindow's palette
        additionalColors=Themes.get_additional_colors('brown')
#        self.ui.introTextEdit.setStyleSheet('color:'+additionalColors['intro']+';background-color: '+self.parent.WinBg+';')

      
        today=datetime.date.today()
        current_year=today.year
       
        
        
        #set the validators-----------------------------------------------------------------------------------------
        #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
        accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]"))
        locale=QtCore.QLocale('en')    
        self.first_validator = QDoubleValidator(0.0,2000.0,1)
        self.first_validator.setLocale(locale)   
        self.first_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.tempEdit.setValidator(accepted_chars)
        self.ui.durationEdit.setValidator(accepted_chars)
      

        #Complete the GUI --------------------------------------------------------------------------------
       
        self.ui.idEdit.setVisible(False)
        self.hide_message_public()
        self.ui.groupBoxNew.setVisible(False)
        self.ui.restList.setSpacing(6)
        
        #set the models ---------------------------------------------------------------------------------
        self.rest_list=all_rest()
        self.rest_list.sort(key=lambda x: x.name)  
        self.model = RestModel(rests=self.rest_list)
        self.ui.restList.setModel(self.model)
        
        #set the connections ------------------------------------------------------------------------------
        self.ui.newButton.clicked.connect(lambda: self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.restList.clicked.connect(self.load_rest)
        self.ui.addButton.clicked.connect(self.add)
        self.ui.updateButton.clicked.connect(self.update)
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.groupBoxNew.clicked.connect(self.hide_message_public)
        self.ui.closeMessageButton.clicked.connect(self.hide_message_public)
            
        
        #set auto clean connection for reset of the controls-----------------------------------------------
        

        self.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
        self.ui.durationEdit.textChanged.connect(lambda :self.cleanEdit('duration'))
        self.ui.tempEdit.textChanged.connect(lambda :self.cleanEdit('temperature'))
        

        
    #-----------------------------------------------------------------------------
    def add(self):
        #add a new ingredient to the public list
        data=self.read_new_form()
        if(data != False):
            result= add_rest(data)
            if(result == 'OK'):
                #print('success')
                self.cleanNewForm()
                self.set_message_public('success', 'Le palier a été correctement enregistré')
                self.ui.labelMessage.setVisible(True)
                self.model.rests.append(data)
                self.rest_list.sort(key=lambda x: x.name)
                self.model.layoutChanged.emit()
            else:
                #print('failure')
                self.set_message_public('failure', result),
                self.ui.labelMessage.setVisible(True)  
     
    #--------------------------------------------------------------------------           
    def update(self):
        #update an existing ingredient in the public list
        indexes = self.ui.restList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.model.rests[index.row()]
            read_item=self.read_new_form()
            if(read_item != False):
        #thi id has been set while loading form with selected item
                read_item.id=self.ui.idEdit.text()
                #attempt update in database
                result = update_rest(read_item)
                if(result == 'OK'):
                    self.cleanNewForm()
                    self.set_message_public('success', 'Le palier a été correctement enregistré')
                    self.ui.labelMessage.setVisible(True)
                    selection=self.model.rests[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.temperature=read_item.temperature
                    selection.duration=read_item.duration
                    
                    self.rest_list.sort(key=lambda x: x.name)
                    self.model.layoutChanged.emit()
                
                

    #-------------------------------------------------------------------------------            
    def delete(self):
        #delete an ingredient from the public list
        indexes = self.ui.restList.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            selected_item= self.model.rests[index.row()]
            #delete from database
            result=delete_rest(selected_item.id)
            if (result == 'OK'):
                self.set_message_public('success', 'Le palier a été correctement supprimé')
                self.ui.labelMessage.setVisible(True)
                # Remove the item and refresh.
                del self.model.rests[index.row()]
                self.model.layoutChanged.emit()
                # Clear the selection (as it is no longer valid).
                self.ui.restList.clearSelection()
            else:
                self.set_message_public('failure', result)
                self.ui.labelMessage.setVisible(True)    

    #-------------------------------------------------------------------------------------------    
    def load_rest(self):
        #load a rest's values in the new form after it has been selected in the public QListView
        indexes = self.ui.restList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.rests[index.row()]
            self.ui.idEdit.setText(str(selected_item.id))
            self.ui.nameEdit.setText(selected_item.name)
            self.ui.tempEdit.setText(str(selected_item.temperature))
            self.ui.durationEdit.setText(str(selected_item.duration))
            
            
    #---------------------------------------------------------------------------------------
    def set_message_public(self, style, text):
        self.ui.labelMessage.setText(text)
        if(style =='success'):
            #print('message success')
            self.ui.labelMessage.setStyleSheet('background-color:green; color: white;padding:10px')
            self.timer=QTimer()
            self.timer.timeout.connect(self.hide_message_public)
            self.timer.start(2000) 
        if(style == 'failure'):
                #print('message failure')
                self.ui.labelMessage.setStyleSheet('background-color:red; color: white;padding:10px')
                self.ui.closeMessageButton.setVisible(True)
    
   
    #-----------------------------------------------------------------------------------------          
    def   hide_message_public(self):
        self.ui.labelMessage.setVisible(False)  
        self.ui.closeMessageButton.setVisible(False) 
      
    #------------------------------------------------------------------------------------    

    #------------------------------------------------------------------------------------------
 
      
    #-----------------------------------------------------------------------------------------------                    
    def read_new_form(self):
    #read the new rest form and check inputs are validated
    #returns False if not validated, returns new rest otherwise
        validated=True
        name=self.ui.nameEdit.text().upper()
        if(name == ''):
            self.ui.nameEdit.setStyleSheet('background-color: red; color:white;')
            validated = False

        temperature=self.ui.tempEdit.text()
        r=self.first_validator.validate(temperature,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.tempEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        duration=self.ui.durationEdit.text()
        r=self.first_validator.validate(duration,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.durationEdit.setStyleSheet('background-color: red; color:white;')
            validated=False     

        if(validated == True):
            e=Rest (None,name,temperature,duration,None  )
            #print(e)
            return e
        else:
            #print('not validated rest')
            return False   


  
    #-----------------------------------------------------------------------------------------------
    def cleanEdit(self, what):
        #auto clean a QLineEdit or a QComboBox after it has been marqued wrong when using it again
        match what:
           
            case 'name':
                self.ui.nameEdit.setStyleSheet('background-color: white;color:black;')  
            case 'temperature':
                self.ui.tempEdit.setStyleSheet('background-color: white;color:black;')   
            case 'duration':
                self.ui.durationEdit.setStyleSheet('background-color: white;color:black;')   
   

  
  
    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        #clean the form for adding or updating a public ingredient
        self.ui.nameEdit.setText('')
        self.ui.tempEdit.setText('')
        self.ui.durationEdit.setText('')
   
      


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
            self.load_rest()
            self.showNewInputs(True)
            self.ui.addButton.setVisible(False)
            self.ui.updateButton.setVisible(True) 
       

        

             
 ##############################################################################################################
 # ############################################################################################################     
   
class RestModel(QtCore.QAbstractListModel):
    #a model for the public QListView
    def __init__(    self, *args, rests=None, **kwargs):
        super(RestModel,self).__init__(*args, **kwargs)
        self.rests = rests or []
           
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            r=self.rests[index.row()] 
            rname=self.str_normalize(r.name,15)
            return rname
     
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.rests)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

         
                     
