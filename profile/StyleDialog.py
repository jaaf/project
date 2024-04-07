
from profile.StyleDialogBase import Ui_StyleDialog as wsel
from PyQt6.QtWidgets import QDialog
from PyQt6 import QtCore
from database.profiles.style import all_style, update_style,Style, add_style,delete_style, find_style_by_id
from dateUtils import DateUtils
from PyQt6.QtCore import Qt,QRegularExpression,QTimer
from database.commons.country import all_country,find_country_by_code
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator,QIntValidator
from PyQt6 import QtGui
import sys, datetime
from database.profiles.watertarget import delete_water,find_water_by_id,find_water_by_name

class StyleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =wsel()
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
        #self.setGeometry(self.px,self.py+150,self.w,self.h-150)
        today=datetime.date.today()
        current_year=today.year
       
        #initialize the various comboBox-----------------------------------------------------------------------------
        
        self.input_color=''
        self.color_update='lightgray'
        self.color_add='honeydew'

  
        
        #set the validators-----------------------------------------------------------------------------------------
        #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
        accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]{3}"))
        locale=QtCore.QLocale('en')    
        self.first_validator = QDoubleValidator(0.0,2000.0,3)
        self.first_validator.setLocale(locale)   
        self.first_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)  
        
        self.OG_validator = QDoubleValidator(1.0,1.999,3)
        self.OG_validator.setLocale(locale)   
        self.OG_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.OGMinEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[1]{1}[\\.][0-9]{3}")))
        self.ui.OGMaxEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[1]{1}[\\.][0-9]{3}")))
        self.ui.FGMinEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[1]{1}[\\.][0-9]{3}")))
        self.ui.FGMaxEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[1]{1}[\\.][0-9]{3}")))
        self.ui.OGMinEdit.setToolTip('min 1.000 max 1.999')
        self.ui.OGMaxEdit.setToolTip('min 1.000 max 1.999')
        self.ui.FGMinEdit.setToolTip('min 1.000 max 1.999')
        self.ui.FGMaxEdit.setToolTip('min 1.000 max 1.999')

        self.ABV_validator = QDoubleValidator(0.0,15.9,1)
        self.ABV_validator.setLocale(locale)   
        self.ABV_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.ABVMinEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{1,2}[\\.][0-9]{1}")))
        self.ui.ABVMaxEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{1,2}[\\.][0-9]{1}")))
        self.ui.ABVMinEdit.setToolTip("de 0 à 15.9 en saisie mais peut être limité par ailleurs")
        self.ui.ABVMaxEdit.setToolTip("de 0 à 15.9 en saisie mais peut être limité par ailleurs")

        self.IBU_validator = QDoubleValidator(0.0,99.0,0)
        self.IBU_validator.setLocale(locale)   
        self.IBU_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.IBUMinEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{1,2}")))
        self.ui.IBUMaxEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{1,2}")))
        self.ui.IBUMinEdit.setToolTip("de 0 à 99 en saisie mais peut être limité par ailleurs")
        self.ui.IBUMaxEdit.setToolTip("de 0 à 99 en saisie mais peut être limité par ailleurs")

        self.BUvsGU_validator = QDoubleValidator(0.0,1.99,0)
        self.BUvsGU_validator.setLocale(locale)   
        self.BUvsGU_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.BUvsGUMinEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-1]{1}[\\.][0-9]{0,2}")))
        self.ui.BUvsGUMaxEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-1]{1}[\\.][0-9]{0,2}")))
        self.ui.BUvsGUMinEdit.setToolTip("de 0 à 1.5 en saisie mais peut être limité par ailleurs")
        self.ui.BUvsGUMaxEdit.setToolTip("de 0 à 1.5 en saisie mais peut être limité par ailleurs")
 
        self.SRM_validator = QDoubleValidator(0.0,99.0,0)
        self.SRM_validator.setLocale(locale)   
        self.SRM_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.SRMMinEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{1,2}")))
        self.ui.SRMMaxEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{1,2}")))
        self.ui.SRMMinEdit.setToolTip("de 0 à 99 en saisie mais peut être limité par ailleurs")
        self.ui.SRMMaxEdit.setToolTip("de 0 à 99 en saisie mais peut être limité par ailleurs") 

        self.appAtt_validator = QDoubleValidator(60.0,99.0,0)
        self.appAtt_validator.setLocale(locale)   
        self.appAtt_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.appAttMinEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[6-9]{1}[0-9]{1}")))
        self.ui.appAttMaxEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[6-9]{1}[0-9]{1}")))
        self.ui.appAttMinEdit.setToolTip("de 70 à 99 en saisie mais peut être limité par ailleurs")
        self.ui.appAttMaxEdit.setToolTip("de 70 à 99 en saisie mais peut être limité par ailleurs")

        self.CO2_validator = QDoubleValidator(1.0,2.9,0)
        self.CO2_validator.setLocale(locale)   
        self.appAtt_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.CO2MinEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[1-2]{1}[\\.]{1}[0-9]{1}")))
        self.ui.CO2MaxEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[1-2]{1}[\\.]{1}[0-9]{1}")))
        self.ui.CO2MinEdit.setToolTip("de 1 à 2.9 en saisie mais peut être limité par ailleurs")
        self.ui.CO2MaxEdit.setToolTip("de 1 à 2.9 en saisie mais peut être limité par ailleurs")


       

        #Complete the GUI --------------------------------------------------------------------------------
       
        self.ui.idEdit.setVisible(False)
        self.hide_message_public()
        self.ui.groupBoxNew.setVisible(False)
        self.ui.styleList.setSpacing(6)
        
        #set the models ---------------------------------------------------------------------------------
        self.style_list=all_style()
        self.style_list.sort(key=lambda x: x.name)  
        self.model = StyleModel(styles=self.style_list)
        self.ui.styleList.setModel(self.model)
        
        #set the connections ------------------------------------------------------------------------------
        self.ui.newButton.clicked.connect(lambda: self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.styleList.clicked.connect(self.load_style)
        self.ui.addButton.clicked.connect(self.add)
        self.ui.updateButton.clicked.connect(self.update)
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.groupBoxNew.clicked.connect(self.hide_message_public)
        self.ui.closeMessageButton.clicked.connect(self.hide_message_public)
            
        
        #set auto clean connection for reset of the controls-----------------------------------------------
        

        self.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
        self.ui.familyEdit.textChanged.connect(lambda :self.cleanEdit('family'))
        self.ui.OGMinEdit.textChanged.connect(lambda :self.cleanEdit('OG_min'))
        self.ui.FGMinEdit.textChanged.connect(lambda :self.cleanEdit('FG_min'))
        self.ui.IBUMinEdit.textChanged.connect(lambda :self.cleanEdit('IBU_min'))
        self.ui.BUvsGUMinEdit.textChanged.connect(lambda :self.cleanEdit('BUvsGU_min'))
        self.ui.ABVMinEdit.textChanged.connect(lambda :self.cleanEdit('ABV_min'))
        self.ui.SRMMinEdit.textChanged.connect(lambda :self.cleanEdit('SRM_min'))
        self.ui.appAttMinEdit.textChanged.connect(lambda :self.cleanEdit('appAtt_min'))
        self.ui.CO2MinEdit.textChanged.connect(lambda :self.cleanEdit('CO2_min'))
        self.ui.OGMaxEdit.textChanged.connect(lambda :self.cleanEdit('OG_max'))
        self.ui.FGMaxEdit.textChanged.connect(lambda :self.cleanEdit('FG_max'))
        self.ui.IBUMaxEdit.textChanged.connect(lambda :self.cleanEdit('IBU_max'))
        self.ui.BUvsGUMaxEdit.textChanged.connect(lambda :self.cleanEdit('BUvsGU_max'))
        self.ui.ABVMaxEdit.textChanged.connect(lambda :self.cleanEdit('ABV_max'))
        self.ui.SRMMaxEdit.textChanged.connect(lambda :self.cleanEdit('SRM_max'))
        self.ui.appAttMaxEdit.textChanged.connect(lambda :self.cleanEdit('appAtt_max'))
        self.ui.CO2MaxEdit.textChanged.connect(lambda :self.cleanEdit('CO2_max'))


        
    #-----------------------------------------------------------------------------
    def add(self):
        #add a new ingredient to the public list
        data=self.read_new_form()
        if(data != False):
            result= add_style(data)
            if(result == 'OK'):
                #print('success')
                self.cleanNewForm()
                self.set_message_public('success', 'Le style a été correctement enregistré')
                self.ui.labelMessage.setVisible(True)
                self.model.styles.append(data)
                self.style_list.sort(key=lambda x: x.name)
                self.model.layoutChanged.emit()
            else:
                #print('failure')
                self.set_message_public('failure', result),
                self.ui.labelMessage.setVisible(True)  
     
    #--------------------------------------------------------------------------           
    def update(self):
        #update an existing ingredient in the public list
        indexes = self.ui.styleList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.model.styles[index.row()]
            read_item=self.read_new_form()
            if(read_item != False):
        #thi id has been set while loading form with selected item
                read_item.id=self.ui.idEdit.text()
                #attempt update in database
                result = update_style(read_item)
                if(result == 'OK'):
                    self.cleanNewForm()
                    self.set_message_public('success', 'Le style a été correctement enregistré')
                    self.ui.labelMessage.setVisible(True)
                    selection=self.model.styles[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.og_min=read_item.og_min
                    selection.fg_min=read_item.fg_min
                    selection.ibu_min=read_item.ibu_min
                    selection.abv_min=read_item.abv_min
                    selection.bu_vs_gu_min=read_item.bu_vs_gu_min
                    selection.srm_min=read_item.srm_min
                    selection.app_att_min=read_item.app_att_min
                    selection.co2_min=read_item.co2_min
                    selection.og_max=read_item.og_max
                    selection.fg_max=read_item.fg_max
                    selection.ibu_max=read_item.ibu_max
                    selection.abv_max=read_item.abv_max
                    selection.bu_vs_gu_max=read_item.bu_vs_gu_max
                    selection.srm_max=read_item.srm_max
                    selection.app_att_max=read_item.app_att_max
                    selection.co2_max=read_item.co2_max
                    self.style_list.sort(key=lambda x: x.name)
                    self.model.layoutChanged.emit()
                
                

    #-------------------------------------------------------------------------------            
    def delete(self):
        #delete an ingredient from the public list
        indexes = self.ui.styleList.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            selected_item= self.model.styles[index.row()]
            #delete from database
            associated_water=find_water_by_name(selected_item.name)

            if associated_water:
                print(associated_water)
                delete_water(associated_water.id)
            else:
                print("no associated water")
            

            result=delete_style(selected_item.id)
            if (result == 'OK'):
                self.set_message_public('success', "Le style a été correctement supprimé ainsi que son éventuel profil d'eau associé.")
                self.ui.labelMessage.setVisible(True)
                # Remove the item and refresh.
                del self.model.styles[index.row()]
                self.model.layoutChanged.emit()
                # Clear the selection (as it is no longer valid).
                self.ui.styleList.clearSelection()
                self.parent().waterTargetDialogWidget.refresh()
            else:
                self.set_message_public('failure', result)
                self.ui.labelMessage.setVisible(True)    

    #-------------------------------------------------------------------------------------------    
    def load_style(self):
        #load a style's values in the new form after it has been selected in the public QListView
        indexes = self.ui.styleList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.styles[index.row()]
            self.ui.idEdit.setText(str(selected_item.id))
            self.ui.nameEdit.setText(selected_item.name)
            self.ui.familyEdit.setText(selected_item.family)
            self.ui.OGMinEdit.setText(str(selected_item.og_min))
            self.ui.FGMinEdit.setText(str(selected_item.fg_min))
            self.ui.ABVMinEdit.setText(str(selected_item.abv_min))
            self.ui.IBUMinEdit.setText(str(selected_item.ibu_min))
            self.ui.BUvsGUMinEdit.setText(str(selected_item.bu_vs_gu_min))
            self.ui.SRMMinEdit.setText(str(selected_item.srm_min))
            self.ui.appAttMinEdit.setText(str(selected_item.app_att_min))
            self.ui.CO2MinEdit.setText(str(selected_item.co2_min))
            
            self.ui.OGMaxEdit.setText(str(selected_item.og_max))
            self.ui.FGMaxEdit.setText(str(selected_item.fg_max))
            self.ui.ABVMaxEdit.setText(str(selected_item.abv_max))
            self.ui.IBUMaxEdit.setText(str(selected_item.ibu_max))
            self.ui.BUvsGUMaxEdit.setText(str(selected_item.bu_vs_gu_max))
            self.ui.SRMMaxEdit.setText(str(selected_item.srm_max))
            self.ui.appAttMaxEdit.setText(str(selected_item.app_att_max))
            self.ui.CO2MaxEdit.setText(str(selected_item.co2_max))
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
    #read the new style form and check inputs are validated
    #returns False if not validated, returns new style otherwise
        validated=True
        name=self.ui.nameEdit.text().upper()
        if(name == ''):
            self.ui.nameEdit.setStyleSheet('background-color: red; color:white;')
            validated = False
        family=self.ui.familyEdit.text().upper()
        if(family == ''):
            self.ui.familyEdit.setStyleSheet('background-color: red; color:white;')
            validated = False

        og_min=self.ui.OGMinEdit.text()
        r=self.OG_validator.validate(og_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.OGMinEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        fg_min=self.ui.FGMinEdit.text()
        r=self.OG_validator.validate(fg_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.FGMinEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        abv_min=self.ui.ABVMinEdit.text()
        r=self.ABV_validator.validate(abv_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.ABVMinEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        ibu_min=self.ui.IBUMinEdit.text()
        r=self.IBU_validator.validate(ibu_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.IBUMinEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        bu_vs_gu_min=self.ui.BUvsGUMinEdit.text()
        r=self.BUvsGU_validator.validate(bu_vs_gu_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.BUvsGUMinEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        srm_min=self.ui.SRMMinEdit.text()
        r=self.SRM_validator.validate(srm_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.SRMMinEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        

        app_att_min=self.ui.appAttMinEdit.text()
        r=self.appAtt_validator.validate(app_att_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.appAttMinEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        co2_min=self.ui.CO2MinEdit.text()
        r=self.CO2_validator.validate(co2_min,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.CO2MinEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        og_max=self.ui.OGMaxEdit.text()
        r=self.OG_validator.validate(og_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.OGMaxEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        if og_min>og_max:
            self.ui.OGMaxEdit.setStyleSheet('background-color: orange; color:white;')
            self.ui.OGMinEdit.setStyleSheet('background-color: orange; color:white;')
            validated=False 

        fg_max=self.ui.FGMaxEdit.text()
        r=self.OG_validator.validate(fg_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.FGMaxEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        if fg_min>fg_max:
            self.ui.FGMaxEdit.setStyleSheet('background-color: orange; color:white;')
            self.ui.FGMinEdit.setStyleSheet('background-color: orange; color:white;')
            validated=False  

        abv_max=self.ui.ABVMaxEdit.text()
        r=self.ABV_validator.validate(abv_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.ABVMaxEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        if abv_min>abv_max:
            self.ui.ABVMaxEdit.setStyleSheet('background-color: orange; color:white;')
            self.ui.ABVMinEdit.setStyleSheet('background-color: orange; color:white;')
            validated=False  

        ibu_max=self.ui.IBUMaxEdit.text()
        r=self.IBU_validator.validate(ibu_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.IBUMaxEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        if ibu_min>ibu_max:
            self.ui.IBUMaxEdit.setStyleSheet('background-color: orange; color:white;')
            self.ui.IBUMinEdit.setStyleSheet('background-color: orange; color:white;')
            validated=False  

        bu_vs_gu_max=self.ui.BUvsGUMaxEdit.text()
        r=self.BUvsGU_validator.validate(bu_vs_gu_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.BUvsGUMaxEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        if bu_vs_gu_min>bu_vs_gu_max:
            self.ui.BUvsGUMaxEdit.setStyleSheet('background-color: orange; color:white;')
            self.ui.BUvsGUMinEdit.setStyleSheet('background-color: orange; color:white;')
            validated=False

        srm_max=self.ui.SRMMaxEdit.text()
        r=self.SRM_validator.validate(srm_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.SRMMaxEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        if srm_min>srm_max:
            self.ui.SRMMaxEdit.setStyleSheet('background-color: orange; color:white;')
            self.ui.SRMMinEdit.setStyleSheet('background-color: orange; color:white;')
            validated=False        

        app_att_max=self.ui.appAttMaxEdit.text()
        r=self.appAtt_validator.validate(app_att_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.appAttMaxEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        if app_att_min>app_att_max:
            self.ui.appAttMaxEdit.setStyleSheet('background-color: orange; color:white;')
            self.ui.appAttMinEdit.setStyleSheet('background-color: orange; color:white;')
            validated=False
        co2_max=self.ui.CO2MaxEdit.text()
        r=self.CO2_validator.validate(co2_max,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.CO2MaxEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        if co2_min>co2_max:
            self.ui.CO2MaxEdit.setStyleSheet('background-color: orange; color:white;')
            self.ui.CO2MinEdit.setStyleSheet('background-color: orange; color:white;')
            validated=False

        if(validated == True):
            e=Style (None,name,family,og_min,fg_min,abv_min,ibu_min,bu_vs_gu_min,srm_min,app_att_min,co2_min,og_max,fg_max,abv_max,ibu_max,bu_vs_gu_max,srm_max,app_att_max,co2_max)  
            #print(e)
            return e
        else:
            #print('not validated style')
            return False   


  
    #-----------------------------------------------------------------------------------------------
    def cleanEdit(self, what):
        #auto clean a QLineEdit or a QComboBox after it has been marqued wrong when using it again
        match what:
           
            case 'name':
                self.ui.nameEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'family':
                self.ui.familyEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            
            case 'OG_min':
                self.ui.OGMinEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'FG_min':
                self.ui.FGMinEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'ABV_min':
                self.ui.ABVMinEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'IBU_min':
                self.ui.IBUMinEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'BUvsGU_min':
                self.ui.BUvsGUMinEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'SRM_min':
                self.ui.SRMMinEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'appAtt_min':
                self.ui.appAttMinEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')   
            case 'CO2_min':
               self.ui.CO2MinEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'OG_max':
               self.ui.OGMaxEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'FG_max':
               self.ui.FGMaxEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'ABV_max':
               self.ui.ABVMaxEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'IBU_max':
               self.ui.IBUMaxEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'BUvsGU_max':
               self.ui.BUvsGUMaxEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'SRM_max':
               self.ui.SRMMaxEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'appAtt_max':
               self.ui.appAttMaxEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  
            case 'CO2_max':
               self.ui.CO2MaxEdit.setStyleSheet('background-color:'+self.input_color+';color:black;')  



  
  
    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        #clean the form for adding or updating a public ingredient
        self.ui.nameEdit.setText('')
        self.ui.familyEdit.setText('')
        self.ui.OGMinEdit.setText('')
        self.ui.FGMinEdit.setText('')
        self.ui.ABVMinEdit.setText('')
        self.ui.IBUMinEdit.setText('')
        self.ui.BUvsGUMinEdit.setText('')
        self.ui.SRMMinEdit.setText('')
        self.ui.appAttMinEdit.setText('')
        self.ui.CO2MinEdit.setText('')
        self.ui.OGMaxEdit.setText('')
        self.ui.FGMaxEdit.setText('')
        self.ui.ABVMaxEdit.setText('')
        self.ui.IBUMaxEdit.setText('')
        self.ui.BUvsGUMaxEdit.setText('')
        self.ui.SRMMaxEdit.setText('')
        self.ui.appAttMaxEdit.setText('')
        self.ui.CO2MaxEdit.setText('')
      
    def setColor(self,mode):
        if(mode =='update'):
            self.input_color=self.color_update
            self.ui.nameEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.familyEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.OGMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.FGMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.ABVMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.IBUMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.BUvsGUMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.SRMMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.appAttMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.CO2MinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.OGMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.FGMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.ABVMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.IBUMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.BUvsGUMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.SRMMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.appAttMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.CO2MaxEdit.setStyleSheet("background-color:"+self.input_color)
        if(mode =='add'):
            self.input_color=self.color_add
            self.ui.nameEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.familyEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.OGMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.FGMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.ABVMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.IBUMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.BUvsGUMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.SRMMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.appAttMinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.CO2MinEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.OGMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.FGMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.ABVMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.IBUMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.BUvsGUMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.SRMMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.appAttMaxEdit.setStyleSheet("background-color:"+self.input_color)
            self.ui.CO2MaxEdit.setStyleSheet("background-color:"+self.input_color)   

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
            self.setColor('add')
        if(mode == 'update'):
            self.load_style()
            self.showNewInputs(True)
            self.ui.addButton.setVisible(False)
            self.ui.updateButton.setVisible(True) 
            self.setColor('update')
       

        

             
 ##############################################################################################################
 # ############################################################################################################     
   
class StyleModel(QtCore.QAbstractListModel):
    #a model for the public QListView
    def __init__(    self, *args, styles=None, **kwargs):
        super(StyleModel,self).__init__(*args, **kwargs)
        self.styles = styles or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            s =self.styles[index.row()] 
            sname=self.str_normalize(s.name,50)
            sfamily=self.str_normalize(s.family,50)
            return '['+sfamily+'] '+sname
     
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.styles)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

         
                     
