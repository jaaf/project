from profile.EquipmentDialogWidgetBase import Ui_Form as equipmentDlg
from PyQt6 import QtCore,QtWidgets
from PyQt6.QtWidgets import QDialog,QWidget
from database.profiles.equipment import all_equipment, update_equipment,Equipment, add_equipment,delete_equipment, find_equipment_by_id
from dateUtils import DateUtils
from PyQt6.QtCore import Qt,QRegularExpression,QTimer
from parameters import equipment_type,cooler_type
from database.commons.country import all_country,find_country_by_code
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator,QIntValidator
from PyQt6 import QtGui
import sys, datetime
from HelpMessage import HelpMessage
from SignalObject import SignalObject
from BrewWidget import Communication
from pathlib import Path



class EquipmentDialogWidget(QWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =equipmentDlg()
        self.ui.setupUi(self)
        self.id=id
       
        self.parent=parent
        self.this_file_path=Path(__file__).parent
        today=datetime.date.today()

        app = QtWidgets.QApplication.instance()
        #as use of setStyleSheet prevents correct font propagation. Prepend all style with this prefix to fix this issue
        self.font_style_prefix='font:'+str(app.font().pointSize())+'pt '+app.font().family()+';'
        #don't understand why font is not correctly propagated though is is for hop and yeasts
        self.setFont(app.font())
        mylist=self.findChildren(QWidget)
        app_font=app.font()
        for item in mylist:
            item.setFont(app_font)
        fbold=QtGui.QFont()    
        fbold.setFamily(app_font.family())
        fbold.setBold(True)
        fbold.setPointSize(app_font.pointSize()+2)
        self.ui.fermentorLabel.setFont(fbold)
        self.ui.mashTunLabel.setFont(fbold)
        self.ui.kettleLabel.setFont(fbold)
        self.ui.generalLabel.setFont(fbold)


        self.c=Communication()
        #initialize the various comboBox-----------------------------------------------------------------------------
        for t in equipment_type:
            self.ui.typeCombo.addItem(t)
        
        for ct in cooler_type:
            self.ui.coolTypeCombo.addItem(ct)
  
        
        #set the validators-----------------------------------------------------------------------------------------
        #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
        accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]"))
        locale=QtCore.QLocale('en')    
     

        self.tun_capacity_validator=QDoubleValidator(0.0,200.0,1)#200 l maximun
        self.tun_capacity_validator.setLocale(locale)   
        self.tun_capacity_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation) 
        self.ui.mtCapacityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}[\\.][0-9]{0,1}")))
        self.ui.ktCapacityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}[\\.][0-9]{0,1}")))
        self.ui.fmCapacityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}[\\.][0-9]{0,1}")))
        self.ui.fmCapacityEdit.setToolTip("Entre 0 et 200")
        self.ui.ktCapacityEdit.setToolTip("Entre 0 et 200")
        self.ui.mtCapacityEdit.setToolTip("Entre 0 et 200")

        self.retention_validator=QDoubleValidator(0.0,40.0,1)#200 l maximun
        self.retention_validator.setLocale(locale)   
        self.retention_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation) 
        self.ui.mtRetentionEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,2}[\\.][0-9]{0,1}")))
        self.ui.ktRetentionEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,2}[\\.][0-9]{0,1}")))
        self.ui.fmRetentionEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,2}[\\.][0-9]{0,1}")))
        self.retention_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation) 
        self.ui.mtRetentionEdit.setToolTip("Entre 0 et 40")
        self.ui.ktRetentionEdit.setToolTip("Entre 0 et 40")
        self.ui.fmRetentionEdit.setToolTip("Entre 0 et 40")

        self.altitude_validator = QDoubleValidator(0.0,3000.0,1)
        self.altitude_validator.setLocale(locale)   
        self.altitude_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.altitudeEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{1,4}")))
        self.ui.altitudeEdit.setToolTip("Entre 0 et 3000")
     
        self.hop_absorption_validator=QDoubleValidator(5.0,10.0,2)
        self.hop_absorption_validator.setLocale(locale)
        self.hop_absorption_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.hopAbsorptionEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,1}[\\.][0-9]{0,2}")))
        self.ui.hopAbsorptionEdit.setToolTip("Autour de 8 (entre 5 et 10)")
        
        self.hop_absorption_reduction_validator=QDoubleValidator(0.0,1.0,2)
        self.hop_absorption_reduction_validator.setLocale(locale)
        self.hop_absorption_reduction_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.looseCoeffEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-1]{0,1}[\\.][0-9]{0,2}")))
        self.ui.looseCoeffEdit.setToolTip("Entre 0 et 1")

        self.grain_absorption_validator=QDoubleValidator(0.7,1.7,2)
        self.grain_absorption_validator.setLocale(locale)
        self.grain_absorption_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.grainAbsorptionEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-1]{0,1}[\\.][0-9]{0,2}")))
        self.ui.grainAbsorptionEdit.setToolTip("entre 0.7 et 1.7")
        
        self.kettle_heat_slope_validator=QDoubleValidator(7.0,50.0,2)
        self.kettle_heat_slope_validator.setLocale(locale)
        self.kettle_heat_slope_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.kettleHeatSlopeEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,2}\\.[0-9]{1,2}")))
        self.ui.kettleHeatSlopeEdit.setToolTip("entre 7 et 50")
        
        self.under_grain_validator=QDoubleValidator(0.0,40.0,2)#20 % max de capacité
        self.under_grain_validator.setLocale(locale)
        self.under_grain_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.mtUnderGrainEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}\\.[0-9]{1,2}")))
        self.ui.mtUnderGrainEdit.setToolTip("Entre 0 et 40")
        
        self.thermal_losses_validator=QDoubleValidator(0.0,5.0,2)#20 % max de capacité
        self.thermal_losses_validator.setLocale(locale)
        self.thermal_losses_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.mtThermalLossesEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-5]{0,1}\\.[0-9]{1,2}")))
        self.ui.mtThermalLossesEdit.setToolTip("Entre 0 et 5")
      
        self.heat_capacity_equiv_validator=QDoubleValidator(0.0,10.0,2)#20 % max de capacité
        self.heat_capacity_equiv_validator.setLocale(locale)
        self.heat_capacity_equiv_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.mtHeatCapacityEquivEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,1}\\.[0-9]{1,2}"))) 
        self.ui.mtHeatCapacityEquivEdit.setToolTip("Enttre 0 et 10")

        self.thickness_validator=QDoubleValidator(0.0,6.0,2)
        self.thickness_validator.setLocale(locale)
        self.thickness_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.mashThicknessEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-5]{0,1}\\.[0-9]{1,2}")))    
        self.ui.mashThicknessEdit.setToolTip("Entre 0 et 6") 

        self.efficiency_validator=QDoubleValidator(40.0,100.0,2)
        self.efficiency_validator.setLocale(locale)
        self.efficiency_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.mashEfficiencyEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{1,2}\\.[0-9]{1,2}"))) 
        self.ui.mashEfficiencyEdit.setValidator(accepted_chars)
        self.ui.mashEfficiencyEdit.setToolTip("Entre 40 et 100")
        
        self.diameter_validator=QDoubleValidator(0.0,150,2)
        self.diameter_validator.setLocale(locale)
        self.diameter_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.ktDiameterEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}\\.[0-9]{1,2}"))) 
        self.ui.ktSteamExitEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}\\.[0-9]{1,2}"))) 
        self.ui.ktSteamExitEdit.setToolTip("Entre 0 et 150")
        self.ui.ktDiameterEdit.setToolTip("Entre 0 et 150")

        self.evaporation_validator=QDoubleValidator(0.0,5.0,2)
        self.evaporation_validator.setLocale(locale)
        self.evaporation_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.ktEvaporationEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-5]{0,1}\\.[0-9]{1,2}"))) 
        self.ui.ktEvaporationEdit.setToolTip("Entre 0 et 5")

        self.cooler_slope_validator=QDoubleValidator(0.0,5.0,2)
        self.cooler_slope_validator.setLocale(locale)
        self.cooler_slope_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.coolSlopeEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-5]{0,1}\\.[0-9]{1,2}")))  
        self.ui.coolSlopeEdit.setToolTip("Entre 0 et 5")    
        
        self.cooler_flow_rate_validator=QDoubleValidator(0.0,5.0,2)
        self.cooler_flow_rate_validator.setLocale(locale)
        self.cooler_flow_rate_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.coolFlowRateEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-5]{0,1}\\.[0-9]{1,2}")))  
        self.ui.coolFlowRateEdit.setToolTip("Entre 0 et 5")      
     
       

        #Complete the GUI --------------------------------------------------------------------------------
        #self.ui.equipmentList.setStyleSheet('padding: 50px')
        self.ui.label.setStyleSheet(self.font_style_prefix+'font-weight:600')
        self.ui.idEdit.setVisible(False)
        self.hide_message_public()
        self.ui.groupBoxNew.setVisible(False)
        self.ui.equipmentList.setSpacing(6)
        self.ui.looseHelpButton.setText('?')
        self.ui.grainAbsorptionHelpButton.setText('?')
        
        self.ui.coolSlopeButton.setText('?')
        
        self.ui.coolFlowRateButton.setText('?')
        
        self.ui.kettleHeatSlopeHelpButton.setText('?')
        
        
        #set the models ---------------------------------------------------------------------------------
        self.equipment_list=all_equipment()
        self.equipment_list.sort(key=lambda x: x.name)  
        self.model = EquipmentModel(equipments=self.equipment_list)
        self.ui.equipmentList.setModel(self.model)
        
        #set the connections ------------------------------------------------------------------------------
        self.ui.newButton.clicked.connect(lambda: self.show_group_box('add'))
        self.ui.editButton.clicked.connect(lambda: self.show_group_box('update'))
        self.ui.equipmentList.clicked.connect(self.load_equipment)
        self.ui.addButton.clicked.connect(self.add)
        self.ui.updateButton.clicked.connect(self.update)
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.groupBoxNew.clicked.connect(self.hide_message_public)
        self.ui.closeMessageButton.clicked.connect(self.hide_message_public)
        self.ui.looseHelpButton.clicked.connect(lambda: self.show_contextual_help('loose_hop'))
        self.ui.grainAbsorptionHelpButton.clicked.connect(lambda: self.show_contextual_help('grain_absorption'))
        self.ui.coolSlopeButton.clicked.connect(lambda: self.show_contextual_help('cooler_slope'))
        self.ui.coolFlowRateButton.clicked.connect(lambda: self.show_contextual_help('cooler_flow_rate'))
        self.ui.kettleHeatSlopeHelpButton.clicked.connect(lambda: self.show_contextual_help('kettle_heat_slope'))
        self.ui.mashTunCapaCaloHelpButton.clicked.connect(lambda: self.show_contextual_help("mash_tun_capa_calo"))
        
        #set auto clean connection for reset of the controls-----------------------------------------------
        
        self.ui.typeCombo.currentIndexChanged.connect(lambda :self.cleanEdit('type'))
        self.ui.coolTypeCombo.currentIndexChanged.connect(lambda :self.cleanEdit('cooler_type'))
        self.ui.nameEdit.textChanged.connect(lambda :self.cleanEdit('name'))
        self.ui.hopAbsorptionEdit.textChanged.connect(lambda :self.cleanEdit('hop_absorption'))
        self.ui.grainAbsorptionEdit.textChanged.connect(lambda :self.cleanEdit('grain_absorption'))
        self.ui.altitudeEdit.textChanged.connect(lambda :self.cleanEdit('altitude'))
        self.ui.mtUnderGrainEdit.textChanged.connect(lambda :self.cleanEdit('mt_undergrain'))
        self.ui.mtCapacityEdit.textChanged.connect(lambda :self.cleanEdit('mt_capacity'))
        self.ui.mtRetentionEdit.textChanged.connect(lambda :self.cleanEdit('mt_retention'))
        self.ui.mtThermalLossesEdit.textChanged.connect(lambda :self.cleanEdit('mt_thermal_losses'))
        self.ui.mtHeatCapacityEquivEdit.textChanged.connect(lambda :self.cleanEdit('mt_heat_capacity'))
        self.ui.mtHeatCapacityEquivEdit.textChanged.connect(lambda :self.cleanEdit('mt_heat_capacity'))
        self.ui.mashThicknessEdit.textChanged.connect(lambda :self.cleanEdit('mash_thickness'))
        self.ui.mashEfficiencyEdit.textChanged.connect(lambda :self.cleanEdit('mash_efficiency'))
        self.ui.ktCapacityEdit.textChanged.connect(lambda :self.cleanEdit('kettle_capacity'))
        self.ui.ktRetentionEdit.textChanged.connect(lambda :self.cleanEdit('kettle_retention'))
        self.ui.ktDiameterEdit.textChanged.connect(lambda :self.cleanEdit('kettle_diameter'))
        self.ui.ktSteamExitEdit.textChanged.connect(lambda :self.cleanEdit('kettle_steam_exit'))
        self.ui.ktEvaporationEdit.textChanged.connect(lambda :self.cleanEdit('kettle_evaporation_rate'))
        self.ui.fmCapacityEdit.textChanged.connect(lambda :self.cleanEdit('fermenter_capacity'))
        self.ui.fmRetentionEdit.textChanged.connect(lambda :self.cleanEdit('fermenter_retention'))
        self.ui.coolTypeCombo.currentTextChanged.connect(lambda : self.cleanEdit('cooler_type'))
        self.ui.coolSlopeEdit.textChanged.connect(lambda :self.cleanEdit('cooler_slope'))
        self.ui.coolFlowRateEdit.textChanged.connect(lambda :self.cleanEdit('cooler_flow_rate'))
        self.ui.kettleHeatSlopeEdit.textChanged.connect(lambda : self.cleanEdit('kettle_heat_slope'))
        self.ui.looseCoeffEdit.textChanged.connect(lambda: self.cleanEdit('loose_coeff'))
        
    #-----------------------------------------------------------------------------------------------
    def cleanEdit(self, what):
        #auto clean a QLineEdit or a QComboBox after it has been marqued wrong when using it again
        match what:
           
            case 'name':
                self.ui.nameEdit.setStyleSheet('background-color: white;color:black;')  
            case 'type':
                self.ui.typeCombo.setStyleSheet('background-color: white;color:black;')
                self.mash_tun_toggle()
            case 'hop_absorption':
                self.ui.hopAbsorptionEdit.setStyleSheet('background-color: white;color:black;') 

            case  'grain_absorption':
                self.ui.grainAbsorptionEdit.setStyleSheet('background-color: white;color:black;')
            case 'altitude':
                self.ui.altitudeEdit.setStyleSheet('background-color: white;color:black;')
            case 'mt_capacity':
                self.ui.mtCapacityEdit.setStyleSheet('background-color: white;color:black;')
            case 'mt_retention':
                self.ui.mtRetentionEdit.setStyleSheet('background-color: white;color:black;')
            case 'mt_undergrain':
                self.ui.mtUnderGrainEdit.setStyleSheet('background-color: white;color:black;') 
            case 'mt_thermal_losses':
                self.ui.mtThermalLossesEdit.setStyleSheet('background-color: white;color:black;')
            case 'mt_heat_capacity':
                self.ui.mtHeatCapacityEquivEdit.setStyleSheet('background-color: white;color:black;')
            case 'mash_thickness':
                self.ui.mashThicknessEdit.setStyleSheet('background-color: white;color:black;')
            case 'mash_efficiency':
                self.ui.mashEfficiencyEdit.setStyleSheet('background-color: white;color:black;')

            case 'kettle_capacity':
                self.ui.ktCapacityEdit.setStyleSheet('background-color: white;color:black;')
            case 'kettle_retention':
                self.ui.ktRetentionEdit.setStyleSheet('background-color: white;color:black;')
            case 'kettle_diameter':
                self.ui.ktDiameterEdit.setStyleSheet('background-color: white;color:black;')
            case 'kettle_steam_exit':
                self.ui.ktSteamExitEdit.setStyleSheet('background-color: white;color:black;')   
            case 'kettle_evaporation_rate':
                self.ui.ktEvaporationEdit.setStyleSheet('background-color: white;color:black;')
            case 'kettle_heat_slope' :
                self.ui.kettleHeatSlopeEdit.setStyleSheet('background-color: white;color:black;')

            case 'fermenter_capacity':
                self.ui.fmCapacityEdit.setStyleSheet('background-color: white;color:black;')
            case 'fermenter_retention':
                self.ui.fmRetentionEdit.setStyleSheet('background-color: white;color:black;')

            case 'cooler_type':
                self.ui.coolTypeCombo.setStyleSheet('background-color: white;color:black;')
                self.cooler_toggle()
            case 'cooler_slope':
                self.ui.coolSlopeEdit.setStyleSheet('background-color: white;color:black;')
            case 'cooler_flow_rate':
                self.ui.coolFlowRateEdit.setStyleSheet('background-color: white;color:black;') 
            case 'loose_coeff':
                self.ui.looseCoeffEdit.setStyleSheet('background-color: white;color:black;')  
        #------------------------------------------------------------------------------------------------------------------------
    def show_contextual_help(self,what):
        #print('what is '+str(what))
        helpPopup=HelpMessage()
        filename=(self.this_file_path/"../help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
        filename=(self.this_file_path/'../help/CoolFlowRateHelp.html').resolve()
        match what:
            case "mash_tun_capa_calo":
                helpPopup.set_title("Capacité calorifique de la cuve en équivalent grain")
                filename=(self.this_file_path/"../help/MashTunCapaCaloHelp.html").resolve()
            case 'loose_hop':
                helpPopup.set_title("Coefficient réducteur de l'absorption d'eau par les houblons ?")    
                filename=(self.this_file_path/"../help/LooseCoeffHelp.html").resolve()
            case 'grain_absorption':
                helpPopup.set_title("Absorption d'eau par le grain")
                filename=(self.this_file_path/"../help/GrainAbsorption.html").resolve()    
            case 'cooler_slope':
                helpPopup.set_title("Pente du refroidisseur")
                filename=(self.this_file_path/"../help/CoolSlopeHelp.html").resolve()
            case 'cooler_flow_rate':
                helpPopup.set_title("Débit au refroidissement")
                filename=(self.this_file_path/"../help/CoolFlowRateHelp.html").resolve() 
            case 'kettle_heat_slope':
                helpPopup.set_title("Vitesse de chauffe de la bouilloire")
                filename=(self.this_file_path/"../help/KettleHeatSlopeHelp.html").resolve()             

        text=open(filename,'r',encoding='utf-8').read()
        helpPopup.set_message(prepend+text)
        helpPopup.exec()

        
    #-----------------------------------------------------------------------------
    def add(self):
        #add a new ingredient to the public list
        data=self.read_new_form()
        if(data != False):
            result= add_equipment(data)
            if(result == 'OK'):
                #print('success')
                self.cleanNewForm()
                self.set_message_public('success', 'L\'équipement a été correctement enregistré')
                self.ui.labelMessage.setVisible(True)
                self.model.equipments.append(data)
                self.equipment_list.sort(key=lambda x: x.name)
                self.model.layoutChanged.emit()
            else:
                #print('failure')
                self.set_message_public('failure', result),
                self.ui.labelMessage.setVisible(True)  
     
    #--------------------------------------------------------------------------           
    def update(self):
        #update an existing equipment in the public list
        indexes = self.ui.equipmentList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selection=self.model.equipments[index.row()]
            read_item=self.read_new_form()
            if(read_item != False):
        #this id has been set while loading form with selected item
                read_item.id=self.ui.idEdit.text()
                #attempt update in database
                result = update_equipment(read_item)
                if(result == 'OK'):
                    self.cleanNewForm()
                    self.set_message_public('success', "L'équipement a été correctement enregistré.")
                    self.ui.labelMessage.setVisible(True)
                    selection=self.model.equipments[index.row()]
                    #update from form
                    selection.name=read_item.name
                    selection.type=read_item.type
                    selection.hop_absorption=read_item.hop_absorption
                    selection.grain_absorption=read_item.grain_absorption
                    selection.altitude=read_item.altitude
                    selection.mash_tun_capacity=read_item.mash_tun_capacity
                    selection.mash_tun_retention=read_item.mash_tun_retention
                    selection.mash_tun_undergrain=read_item.mash_tun_undergrain
                    selection.mash_tun_thermal_losses=read_item.mash_tun_thermal_losses
                    selection.mash_tun_heat_capacity_equiv=read_item.mash_tun_heat_capacity_equiv
                    selection.mash_thickness=read_item.mash_thickness
                    selection.mash_efficiency=read_item.mash_efficiency
                    selection.kettle_capacity=read_item.kettle_capacity
                    selection.kettle_retention=read_item.kettle_retention
                    selection.kettle_diameter=read_item.kettle_diameter
                    selection.kettle_steam_exit_diameter=read_item.kettle_steam_exit_diameter
                    selection.kettle_evaporation_rate=read_item.kettle_evaporation_rate
                    selection.kettle_heat_slope=read_item.kettle_heat_slope
                    selection.fermenter_capacity=read_item.fermenter_capacity
                    selection.fermenter_retention=read_item.fermenter_retention
                    selection.cooler_type=read_item.cooler_type
                    selection.cooler_slope=read_item.cooler_slope
                    selection.cooler_flow_rate=read_item.cooler_flow_rate
                 
                    self.equipment_list.sort(key=lambda x: x.name)
                    self.model.layoutChanged.emit()
                    print('emit equipment_update')
                    self.c.calculate.emit(SignalObject('equipment_update',read_item))
                    
              
                
                

    #-------------------------------------------------------------------------------            
    def delete(self):
        #delete an ingredient from the public list
        indexes = self.ui.equipmentList.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            selected_item= self.model.equipments[index.row()]
            #delete from database
            result=delete_equipment(selected_item.id)
            if (result == 'OK'):
                self.set_message_public('success', 'L\'équipement a été correctement supprimé')
                self.ui.labelMessage.setVisible(True)
                # Remove the item and refresh.
                del self.model.equipments[index.row()]
                self.model.layoutChanged.emit()
                # Clear the selection (as it is no longer valid).
                self.ui.equipmentList.clearSelection()
            else:
                self.set_message_public('failure', result)
                self.ui.labelMessage.setVisible(True)    

    #-------------------------------------------------------------------------------------------    
    def load_equipment(self):
        
        #load a equipment's values in the new form after it has been selected in the public QListView
        self.hide_message_public()
        indexes = self.ui.equipmentList.selectedIndexes()
        if indexes:
            index=indexes[0]
            selected_item=self.model.equipments[index.row()]
            self.ui.idEdit.setText(str(selected_item.id))
            self.ui.nameEdit.setText(selected_item.name)
            self.ui.typeCombo.setCurrentText(selected_item.type)
            self.ui.hopAbsorptionEdit.setText(str(selected_item.hop_absorption))
            self.ui.looseCoeffEdit.setText(str(selected_item.hop_absorption_reduction_coeff))
            self.ui.grainAbsorptionEdit.setText(str(selected_item.grain_absorption))
            self.ui.altitudeEdit.setText(str(selected_item.altitude))
            self.ui.mtCapacityEdit.setText(str(selected_item.mash_tun_capacity))
            self.ui.mtRetentionEdit.setText(str(selected_item.mash_tun_retention))
            self.ui.mtUnderGrainEdit.setText(str(selected_item.mash_tun_undergrain))
            self.ui.mtThermalLossesEdit.setText(str(selected_item.mash_tun_thermal_losses))
            self.ui.mtHeatCapacityEquivEdit.setText(str(selected_item.mash_tun_heat_capacity_equiv))
            self.ui.mashThicknessEdit.setText(str(selected_item.mash_thickness))
            self.ui.mashEfficiencyEdit.setText(str(selected_item.mash_efficiency))
            self.ui.ktCapacityEdit.setText(str(selected_item.kettle_capacity))
            self.ui.ktRetentionEdit.setText(str(selected_item.kettle_retention))
            self.ui.ktDiameterEdit.setText(str(selected_item.kettle_diameter))
            self.ui.ktSteamExitEdit.setText(str(selected_item.kettle_steam_exit_diameter))
            self.ui.ktEvaporationEdit.setText(str(selected_item.kettle_evaporation_rate))
            self.ui.kettleHeatSlopeEdit.setText(str(selected_item.kettle_heat_slope))
            self.ui.fmCapacityEdit.setText(str(selected_item.fermenter_capacity))
            self.ui.fmRetentionEdit.setText(str(selected_item.fermenter_retention))
            self.ui.coolTypeCombo.setCurrentText(selected_item.cooler_type)
            self.ui.coolSlopeEdit.setText(str(selected_item.cooler_slope))
            self.ui.coolFlowRateEdit.setText(str(selected_item.cooler_flow_rate))

    #---------------------------------------------------------------------------------------
    def set_message_public(self, style, text,time=5000):
        #print('in set_message_public')
        #print(style)
        #print(text)
        self.ui.labelMessage.setText(text)
        if(style =='success'):
            #print('message success')
            self.ui.labelMessage.setStyleSheet('background-color:green; color: white;padding:10px')
            self.timer=QTimer()
            self.timer.timeout.connect(self.hide_message_public)
            self.timer.start(time) 
        if(style == 'failure'):
                #print('message failure')
                self.ui.labelMessage.setStyleSheet('background-color:red; color: white;padding:10px')
                self.ui.closeMessageButton.setVisible(True)
        self.show_message_public()
        
    #-----------------------------------------------------------------------------------------          
    def   hide_message_public(self):
        self.ui.labelMessage.setVisible(False)  
        self.ui.closeMessageButton.setVisible(False) 
      
    #------------------------------------------------------------------------------------    
    def show_message_public(self):
        self.ui.labelMessage.setVisible(True)  
        self.ui.closeMessageButton.setVisible(True) 
    #------------------------------------------------------------------------------------------
 
      
    #-----------------------------------------------------------------------------------------------                    
    def read_new_form(self):
    #read the new equipment form and check inputs are validated
    #returns False if not validated, returns new equipment otherwise
        validated=True
        name=self.ui.nameEdit.text().upper()
        if(name == ''):
            self.ui.nameEdit.setStyleSheet('background-color: red; color:white;')
            validated = False
        type=self.ui.typeCombo.currentText()
        if(type == ''):
            self.ui.typeCombo.setStyleSheet('background-color: red; color:white;')
            validated=False

        grain_absorption=self.ui.grainAbsorptionEdit.text()
        r=self.grain_absorption_validator.validate(grain_absorption,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.grainAbsorptionEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        hop_absorption=self.ui.hopAbsorptionEdit.text()
        r=self.hop_absorption_validator.validate(hop_absorption,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.hopAbsorptionEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        hop_absorption_reduction_coeff=self.ui.looseCoeffEdit.text()   
        r=self.hop_absorption_reduction_validator.validate(hop_absorption_reduction_coeff,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.looseCoeffEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        
        altitude=self.ui.altitudeEdit.text()
        r=self.altitude_validator.validate(altitude,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.altitudeEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        mash_tun_capacity=self.ui.mtCapacityEdit.text()
        r=self.tun_capacity_validator.validate(mash_tun_capacity,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.mtCapacityEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
        
        mash_tun_retention=self.ui.mtRetentionEdit.text()
        r=self.retention_validator.validate(mash_tun_retention,0)
        if(r[0] != QtGui.QValidator.State.Acceptable)and type != 'Tout en un':
            self.ui.mtRetentionEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
            #print('cause mash retention')

        mash_tun_undergrain=self.ui.mtUnderGrainEdit.text()
        r=self.under_grain_validator.validate(mash_tun_undergrain,0)
        if(r[0] != QtGui.QValidator.State.Acceptable) :
            self.ui.mtUnderGrainEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        mash_tun_thermal_losses=self.ui.mtThermalLossesEdit.text()
        r=self.thermal_losses_validator.validate(mash_tun_thermal_losses,0)
        if(r[0] != QtGui.QValidator.State.Acceptable) and type != 'Tout en un':
            self.ui.mtThermalLossesEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
            #print('cause thermal losses')
             
        mash_tun_heat_capacity_equiv=self.ui.mtHeatCapacityEquivEdit.text()
        r=self.heat_capacity_equiv_validator.validate(mash_tun_heat_capacity_equiv,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.mtHeatCapacityEquivEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        mash_thickness=self.ui.mashThicknessEdit.text()
        r=self.thickness_validator.validate(mash_thickness,0)
        if(r[0] != QtGui.QValidator.State.Acceptable) and type != 'Brassage en sac':
            self.ui.mashThicknessEdit.setStyleSheet('background-color: red; color:white;')
            validated=False
            #print('cause thickness')

        mash_efficiency=self.ui.mashEfficiencyEdit.text()
        r=self.efficiency_validator.validate(mash_efficiency,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.mashEfficiencyEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        kettle_capacity=self.ui.ktCapacityEdit.text()
        r=self.tun_capacity_validator.validate(kettle_capacity,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.ktCapacityEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        kettle_retention=self.ui.ktRetentionEdit.text()
        r=self.retention_validator.validate(kettle_retention,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.ktRetentionEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        kettle_diameter=self.ui.ktDiameterEdit.text()
        r=self.diameter_validator.validate(kettle_diameter,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.ktDiameterEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        kettle_steam_exit_diameter=self.ui.ktSteamExitEdit.text()
        r=self.diameter_validator.validate(kettle_steam_exit_diameter,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.ktSteamExitEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        kettle_evaporation_rate=self.ui.ktEvaporationEdit.text()
        r=self.evaporation_validator.validate(kettle_evaporation_rate,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.ktEvaporationEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        kettle_heat_slope=self.ui.kettleHeatSlopeEdit.text()
        r=self.kettle_heat_slope_validator.validate(kettle_heat_slope,0)
        #print('r 0 '+str(r[0]))
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.kettleHeatSlopeEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        fermenter_capacity=self.ui.fmCapacityEdit.text()
        r=self.tun_capacity_validator.validate(fermenter_capacity,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.fmCapacityEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        fermenter_retention=self.ui.fmRetentionEdit.text()
        r=self.retention_validator.validate(fermenter_retention,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.fmRetentionEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        cooler_type=self.ui.coolTypeCombo.currentText()
        if(cooler_type == ''):
            self.ui.coolTypeCombo.setStyleSheet('background-color: red; color:white;')
            validated=False

        cooler_slope=self.ui.coolSlopeEdit.text()
        r=self.cooler_slope_validator.validate(cooler_slope,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.coolSlopeEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        cooler_flow_rate=self.ui.coolFlowRateEdit.text()
        r=self.cooler_flow_rate_validator.validate(cooler_flow_rate,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.coolFlowRateEdit.setStyleSheet('background-color: red; color:white;')
            validated=False

        if(validated == True):
            e=Equipment (None,name,type,hop_absorption,hop_absorption_reduction_coeff,grain_absorption,altitude,\
                mash_tun_capacity,mash_tun_retention,mash_tun_undergrain,mash_tun_thermal_losses,mash_tun_heat_capacity_equiv,\
                mash_thickness,mash_efficiency,\
                kettle_capacity,kettle_retention,kettle_diameter,kettle_steam_exit_diameter,kettle_evaporation_rate,kettle_heat_slope,\
                fermenter_capacity,fermenter_retention,\
                cooler_type,cooler_slope,cooler_flow_rate)  
            #print(e)
            return e
        else:
            #print('not validated equipment')
            return False   


  
 

    #--------------------------------------------------------------------------------
    def cooler_toggle(self):
        if(self.ui.coolTypeCombo.currentText() == 'Immersion'):
            self.ui.coolSlopeLabel.setVisible(True)
            self.ui.coolSlopeEdit.setText('')
            self.ui.coolFlowRateLabel.setVisible(True)
            self.ui.coolFlowRateEdit.setText(str(0))
        if(self.ui.coolTypeCombo.currentText() == 'Contre-courant'):
            self.ui.coolSlopeLabel.setVisible(True)    
            self.ui.coolSlopeEdit.setText(str(0))
            self.ui.coolFlowRateLabel.setVisible(True)
            self.ui.coolFlowRateEdit.setText('')
        

    #-----------------------------------------------------------------------------------------       
    def mash_tun_toggle(self):
        #print('toggling mash tun controls')
        #print(self.ui.typeCombo.currentText())
        if(self.ui.typeCombo.currentText() == 'Tout en un'):
            
            #print('cas Tout en un')
            self.ui.mtGBHeatLosses.setVisible(False)
            self.ui.mtThermalLossesEdit.setText(str(0))
            self.ui.mtGBRetention.setVisible(False)
            self.ui.mtRetentionEdit.setText(str(0))
            self.ui.mtGBMashThickness.setVisible(True)
            self.ui.mashThicknessEdit.setText('')
            return
        if(self.ui.typeCombo.currentText() == 'Classique'):
            self.ui.mtGBHeatLosses.setVisible(True)
            self.ui.mtThermalLossesEdit.setText('')
            self.ui.mtGBRetention.setVisible(True)
            self.ui.mtRetentionEdit.setText('')
            self.ui.mtGBMashThickness.setVisible(True)
            self.ui.mashThicknessEdit.setText('')
            return  
        if(self.ui.typeCombo.currentText() == 'Brassage en sac'):
            self.ui.mtGBHeatLosses.setVisible(True)
            self.ui.mtThermalLossesEdit.setText('')
            self.ui.mtGBRetention.setVisible(True)
            self.ui.mtRetentionEdit.setText('')
            self.ui.mtGBMashThickness.setVisible(False)
            self.ui.mashThicknessEdit.setText(str(0))
            return 
    #------------------------------------------------------------------------------------------                       
    def cleanNewForm(self):
        #clean the form for adding or updating a public ingredient
        self.ui.nameEdit.setText('')
        self.ui.typeCombo.setCurrentText('')
        self.ui.hopAbsorptionEdit.setText('')
        self.ui.looseCoeffEdit.setText('')
        self.ui.grainAbsorptionEdit.setText('')
        self.ui.altitudeEdit.setText('')

        self.ui.mtCapacityEdit.setText('')
        self.ui.mtRetentionEdit.setText('')
        self.ui.mtUnderGrainEdit.setText('')
        self.ui.mtThermalLossesEdit.setText('')
        self.ui.mtHeatCapacityEquivEdit.setText('')

        self.ui.mashThicknessEdit.setText('')
        self.ui.mashEfficiencyEdit.setText('')

        self.ui.ktCapacityEdit.setText('')
        self.ui.ktRetentionEdit.setText('')
        self.ui.ktEvaporationEdit.setText('')
        self.ui.kettleHeatSlopeEdit.setText('')
        self.ui.ktDiameterEdit.setText('')
        self.ui.ktSteamExitEdit.setText('')

        self.ui.fmCapacityEdit.setText('')
        self.ui.fmRetentionEdit.setText('')

        self.ui.coolTypeCombo.setCurrentText('')
        self.ui.coolSlopeEdit.setText('')
        self.ui.coolFlowRateEdit.setText('')
      


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
            indexes = self.ui.equipmentList.selectedIndexes()
           
            self.load_equipment()
            self.showNewInputs(True)
            self.ui.addButton.setVisible(False)
            self.ui.updateButton.setVisible(True) 
            if not indexes:
                self.set_message_public('failure',"Vous devez d'abord sélectionner un profil d'équipment.")     
       






##############################################################################################################
# ############################################################################################################     
   
class EquipmentModel(QtCore.QAbstractListModel):
    #a model for the public QListView
    def __init__(    self, *args, equipments=None, **kwargs):
        super(EquipmentModel,self).__init__(*args, **kwargs)
        self.equipments = equipments or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            e =self.equipments[index.row()] 
            ename=self.str_normalize(e.name,15)
            etype=self.str_normalize(str(e.type),20)
            return ename+' '+' de type' +etype +' Capacités : MT '+str(e.mash_tun_capacity)+'l | B '+str(e.kettle_capacity)+'l | F '+str(e.fermenter_capacity)+'l'\
            +'\n———————————————————————————————————————————————————————————————————————————————————————'
     
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.equipments)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

         
                   