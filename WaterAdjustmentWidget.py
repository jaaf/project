'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from WaterAdjustmentWidgetBase import Ui_WaterAdjustmentWidget as WAWdgt
from PyQt6.QtWidgets import QDialog,QLabel,QHBoxLayout,QVBoxLayout,QWidget,QFrame,QPushButton,QGroupBox,QListView,QTextEdit,QWidget,QLayout,QLineEdit
from PyQt6 import QtCore,QtWidgets
from database.profiles.water import Water,all_water as all_base, find_water_by_id as find_base_by_id
from database.profiles.watertarget import WaterTarget,all_water as all_style, find_water_by_id as find_style_by_id
from PyQt6.QtCore import QObject
import copy
import jsonpickle,math
from HelpMessage import HelpMessage
from pathlib import Path

class SaltAdditions(QObject):
    def __init__(self, CaSO4,MgSO4,CaCl2,MgCl2,CaOH2,NaHCO3):
        super(SaltAdditions, self).__init__()
        self.CaSO4=CaSO4
        self.MgSO4=MgSO4
        self.CaCl2=CaCl2
        self.MgCl2=MgCl2
        self.CaOH2=CaOH2
        self.NaHCO3=NaHCO3

    def __repr__(self) :
        return f"SaltAdditions ,{self.CaSO4},{self.MgSO4},{self.CaCl2},{self.MgCl2},{self.CaOH2},{self.NaHCO3}"   

class Salt(QObject):
    def __init__(self,name,formula,ca,mg,na,cl,so4,alca):
        self.name=name
        self.formula=formula
        self.ca=ca
        self.mg=mg
        self.na=na
        self.cl=cl
        self.so4=so4
        self.alca=alca



class WaterAdjustmentWidget(QWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self,base_water,dilution_water, dilution,style_water,target_water,water_for_sparge,salt_additions,water_adjustment_state,parent=None):
        super().__init__(parent)
        self.parent=parent
        self.ui =WAWdgt()
        self.this_file_path=Path(__file__).parent
    
        self.base_water=base_water
        self.dilution_water=dilution_water
        self.water_adjustment_state=water_adjustment_state
        self.style_water=style_water
        if salt_additions is not None:
            self.salt_additions=salt_additions
        else:
            self.salt_additions=SaltAdditions(0,0,0,0,0,0)

        if target_water is not None:
            self.target_water=target_water
        else:
            self.target_water=WaterTarget(None,None,None,None,None, None, None, None,None,None,None, None, None, None)
     
        self.water_for_sparge=water_for_sparge
        
        self.ui.setupUi(self)
        self.ui.HelpButton.setText('❓')
        self.ui.HelpButton.setStyleSheet('color:green')

        self.sparge_water_mass=self.parent.sparge_water_mass
        self.init_combos()
        self.set_connections()
         
        
        self.mixed_water=Water(None,None,None,None,None, None, None, None,None)
        
        self.adjusted_water=Water(None,None,None,None,None, None, None, None,None)
        self.CaSO4=Salt('Sulfate de calcium',"CaSO₄—2H₂O",232.8,0,0,0,557.7,0)
        self.MgSO4=Salt('Sulfate de magnésium','MgSO₄—7H₂O',0,98.6,0,0,389.6,0)
        self.CaCl2=Salt('Chlorure de calcium','CaCl₂—2H₂O',272.6,0,0,482.3,9,0)
        self.MgCl2=Salt('Chlorure de magnésium','MgCl₂—2H₂O',0,119.5,0,348.7,0,0)
        self.CaOH2=Salt('Chaux éteint','Ca(OH)₂',541,0,0,0,0,1350)
        self.NaHCO3=Salt('Bicarbonate de soude','NaHCO₃',0,0,274,0,0,584)
        #self.NaCl=Salt('Chlorure de sodium','NaCl',0,0,393.4,606.6,0,0)
        #self.CaCO3=Salt('Carbonate de calcium','CaCO₃', 199,0,0,0,0,498)
        if self.salt_additions is not None:
            self.CaSO4_val=self.salt_additions.CaSO4 #mg/l
            self.MgSO4_val=self.salt_additions.MgSO4
            self.CaCl2_val=self.salt_additions.CaCl2
            self.MgCl2_val=self.salt_additions.MgCl2
            self.CaOH2_val=self.salt_additions.CaOH2
            self.NaHCO3_val=self.salt_additions.NaHCO3
           

        else:
            self.CaSO4_val=0 #mg/l
            self.MgSO4_val=0
            self.CaCl2_val=0
            self.MgCl2_val=0
            self.CaOH2_val=0
            self.NaHCO3_val=0

        self.ui.RatioGroupbox.setVisible(False)
        self.ui.DilutionSpin.setEnabled(False)
        self.disable_salt_values()
        
        if self.base_water is not None:
            self.ui.BaseCombo.setCurrentText(self.base_water.name)#triggers currentTextChanged and load the values in the display
        if (self.dilution_water is not None):
            self.ui.DilutionCombo.setCurrentText(self.dilution_water.name)
      
        self.dilution=dilution   #use the parameter now because loading of Base and Dilution Combos resets self.dilution to 0 
        if self.dilution is not None:
                self.ui.DilutionSpin.setValue(self.dilution)
                
                
        else:
            self.ui.DilutionSpin.setValue(0) 
        if self.style_water is not None:
            self.ui.StyleCombo.setCurrentText(self.style_water.name)   
        if self.target_water.name is not None:
            self.init_target_water_display()  


    def after_init(self):
        #to be launched in the BrewWidget after the BrewWidget has been fully initialized
        self.dilution_changed()
        
        if self.water_for_sparge is not None:
            self.ui.SpargeWaterSelectCombo.setCurrentText(self.water_for_sparge)
        if self.target_water.name is not None:
            self.ui.RatioGroupbox.setVisible(True)
        self.init_salt_additions_display()
        if self.water_adjustment_state is not None:
            match self.water_adjustment_state:
                case 'as_is':
                    self.use_water_as_is()
                case 'adjusted':
                    self.auto_adjust()

      
    #------------------------------------------------------------------------------------------------    
    def set_connections(self):
        self.ui.BaseCombo.currentTextChanged.connect(self.load_base_water)
        self.ui.BaseCombo.activated.connect(self.base_combo_activated)
        self.ui.DilutionCombo.currentTextChanged.connect(self.load_dilution_water)
        self.ui.DilutionCombo.activated.connect(self.dilution_combo_activated)
        self.ui.DilutionSpin.valueChanged.connect(self.dilution_changed)
        self.ui.SpargeWaterSelectCombo.currentTextChanged.connect(self.sparge_water_changed)
        self.ui.StyleCombo.currentTextChanged.connect(self.load_style_water)
        self.ui.adviceButton.clicked.connect(self.load_style_advised_water)
        self.ui.AdjustButton.clicked.connect(self.auto_adjust)
        self.ui.AsIsButton.clicked.connect(self.use_water_as_is)
        self.ui.clearAdviceButton.clicked.connect(self.clear_target_profile)
        widgets = (self.ui.target_profile_layout.itemAt(i).widget() for i in range(self.ui.target_profile_layout.count())) 
        for widget in widgets:
            if isinstance(widget, QLineEdit):
                widget.textEdited.connect(self.target_profile_edited)

        self.ui.CaSO4Value.valueChanged.connect(self.update_adjusted_water)
        self.ui.MgSO4Value.valueChanged.connect(self.update_adjusted_water)
        self.ui.CaSO4Value.valueChanged.connect(self.update_adjusted_water)
        self.ui.MgCl2Value.valueChanged.connect(self.update_adjusted_water)
        self.ui.CaCl2Value.valueChanged.connect(self.update_adjusted_water)
        self.ui.CaOH2Value.valueChanged.connect(self.update_adjusted_water)
        self.ui.NaHCO3Value.valueChanged.connect(self.update_adjusted_water)

        self.ui.IgnoreCheckbox.stateChanged.connect(self.ignore_checkbox_changed)
        self.ui.MgCl2Checkbox.stateChanged.connect(self.set_so4_vs_cl_ratio)
        self.ui.CaOH2Checkbox.stateChanged.connect(self.set_so4_vs_cl_ratio)
        self.ui.NaHCO3Checkbox.stateChanged.connect(self.set_so4_vs_cl_ratio)
        self.ui.RatioTargetEdit.textChanged.connect(self.set_so4_vs_cl_ratio)

        self.ui.HelpButton.clicked.connect(lambda: self.show_contextual_help('bidon'))
    #--------------------------------------------------------------------------------
    def disable_salt_values(self):
        self.ui.CaSO4Value.setEnabled(False)
        self.ui.MgSO4Value.setEnabled(False)
        self.ui.CaCl2Value.setEnabled(False)
        self.ui.MgCl2Value.setEnabled(False)
        self.ui.CaOH2Value.setEnabled(False)
        self.ui.NaHCO3Value.setEnabled(False)     
    #---------------------------------------------------------------------------------
    def enable_salt_values(self):
            self.ui.CaSO4Value.setEnabled(True)
            self.ui.MgSO4Value.setEnabled(True)
            self.ui.CaCl2Value.setEnabled(True)
            self.ui.MgCl2Value.setEnabled(True)
            self.ui.CaOH2Value.setEnabled(True)
            self.ui.NaHCO3Value.setEnabled(True)      
    #--------------------------------------------------------------------------------- 
    def show_contextual_help(self,what):
        helpPopup=HelpMessage()
        filename=(self.this_file_path/"help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
         
        helpPopup.set_title('Ajustement de l\'eau')
        filename=(self.this_file_path/"help/WaterAdjustment.html").resolve()
        text=open(filename,'r',encoding="utf-8").read()
        helpPopup.set_message(prepend+text)

        helpPopup.exec()

    def init_target_water_display(self):
        
        self.ui.CaMinTargetEdit.setText(str(self.target_water.ca_min))    
        self.ui.MgMinTargetEdit.setText(str(self.target_water.mg_min))    
        self.ui.NaMinTargetEdit.setText(str(self.target_water.na_min))    
        self.ui.ClMinTargetEdit.setText(str(self.target_water.cl_min))
        self.ui.So4MinTargetEdit.setText(str(self.target_water.so4_min))    
        self.ui.AlkaMinTargetEdit.setText(str(self.target_water.alca_min))        
        self.ui.CaMaxTargetEdit.setText(str(self.target_water.ca_max))    
        self.ui.MgMaxTargetEdit.setText(str(self.target_water.mg_max))    
        self.ui.NaMaxTargetEdit.setText(str(self.target_water.na_max))    
        self.ui.ClMaxTargetEdit.setText(str(self.target_water.cl_max))
        self.ui.So4MaxTargetEdit.setText(str(self.target_water.so4_max))    
        self.ui.AlkaMaxTargetEdit.setText(str(self.target_water.alca_max))  

    def init_combos(self):
        self.water_list=all_base()
        self.water_style_list=all_style()
        self.ui.BaseCombo.addItem('',None)
        for w in self.water_list:
            self.ui.BaseCombo.addItem(w.name,w.id)

        self.ui.DilutionCombo.addItem('',None)    
        for w in self.water_list:
            self.ui.DilutionCombo.addItem(w.name,w.id)  

        self.ui.StyleCombo.addItem('',None)
        for wt in self.water_style_list:
            self.ui.StyleCombo.addItem(wt.name,wt.id)

        self.ui.SpargeWaterSelectCombo.addItem('')
        self.ui.SpargeWaterSelectCombo.addItem('Eau de base')   
        self.ui.SpargeWaterSelectCombo.addItem('Eau de dilution')  
        self.ui.SpargeWaterSelectCombo.addItem('Eau mélangée brute')  
        self.ui.SpargeWaterSelectCombo.addItem('Eau mélangée ajustée')  
        self.ui.SpargeWaterSelectCombo.addItem('Eau distillée')



    #------------------------------------------------------------------------------------------------  
    def target_profile_edited(self):
        self.update_target_water()
        if(float(self.ui.CaMinTargetEdit.text()))>float(self.ui.CaMaxTargetEdit.text()):
            self.ui.CaMinTargetEdit.setStyleSheet('background-color: red')
            self.ui.CaMaxTargetEdit.setStyleSheet('background-color: red')
        else:
            self.ui.CaMinTargetEdit.setStyleSheet('background-color: white')
            self.ui.CaMaxTargetEdit.setStyleSheet('background-color: white')  

        if(float(self.ui.MgMinTargetEdit.text()))>float(self.ui.MgMaxTargetEdit.text()):
            self.ui.MgMinTargetEdit.setStyleSheet('background-color: red')
            self.ui.MgMaxTargetEdit.setStyleSheet('background-color: red')
        else:
            self.ui.MgMinTargetEdit.setStyleSheet('background-color: white')
            self.ui.MgMaxTargetEdit.setStyleSheet('background-color: white')  
            
        if(float(self.ui.NaMinTargetEdit.text()))>float(self.ui.NaMaxTargetEdit.text()):
            self.ui.NaMinTargetEdit.setStyleSheet('background-color: red')
            self.ui.NaMaxTargetEdit.setStyleSheet('background-color: red')
        else:
            self.ui.NaMinTargetEdit.setStyleSheet('background-color: white')
            self.ui.NaMaxTargetEdit.setStyleSheet('background-color: white') 

        if(float(self.ui.ClMinTargetEdit.text()))>float(self.ui.ClMaxTargetEdit.text()):
            self.ui.ClMinTargetEdit.setStyleSheet('background-color: red')
            self.ui.ClMaxTargetEdit.setStyleSheet('background-color: red')
        else:
            self.ui.ClMinTargetEdit.setStyleSheet('background-color: white')
            self.ui.ClMaxTargetEdit.setStyleSheet('background-color: white')   
          
        if(float(self.ui.So4MinTargetEdit.text()))>float(self.ui.So4MaxTargetEdit.text()):
            self.ui.So4MinTargetEdit.setStyleSheet('background-color: red')
            self.ui.So4MaxTargetEdit.setStyleSheet('background-color: red')
        else:
            self.ui.So4MinTargetEdit.setStyleSheet('background-color: white')
            self.ui.So4MaxTargetEdit.setStyleSheet('background-color: white')    

        if(float(self.ui.AlkaMinTargetEdit.text()))>float(self.ui.AlkaMaxTargetEdit.text()):
            self.ui.AlkaMinTargetEdit.setStyleSheet('background-color: red')
            self.ui.AlkaMaxTargetEdit.setStyleSheet('background-color: red')
        else:
            self.ui.AlkaMinTargetEdit.setStyleSheet('background-color: white')
            self.ui.AlkaMaxTargetEdit.setStyleSheet('background-color: white')     
        self.set_so4_vs_cl_ratio()#clean the salt values and turn the button to red
    #-------------------------------------------------------------------------------------------------- 
    def update_target_water(self):
        self.target_water.name='target water'
        self.target_water.ca_min=float(self.ui.CaMinTargetEdit.text())
        self.target_water.mg_min=float(self.ui.MgMinTargetEdit.text())
        self.target_water.na_min=float(self.ui.NaMinTargetEdit.text())
        self.target_water.cl_min=float(self.ui.ClMinTargetEdit.text())
        self.target_water.so4_min=float(self.ui.So4MinTargetEdit.text())
        self.target_water.alca_min=float(self.ui.AlkaMinTargetEdit.text())

        self.target_water.ca_max=float(self.ui.CaMaxTargetEdit.text())
        self.target_water.mg_max=float(self.ui.MgMaxTargetEdit.text())
        self.target_water.na_max=float(self.ui.NaMaxTargetEdit.text())
        self.target_water.cl_max=float(self.ui.ClMaxTargetEdit.text())
        self.target_water.so4_max=float(self.ui.So4MaxTargetEdit.text())
        self.target_water.alca_max=float(self.ui.AlkaMaxTargetEdit.text())
        self.reset_so4_vs_cl_ratio()
       
    #---------------------------------------------------------------------------------------------------
    def load_style_advised_water(self):
        index = self.ui.StyleCombo.currentData()
        if index:            
            self.style_water=find_style_by_id(index)
            self.ui.CaMinTargetEdit.setText(str(self.style_water.ca_min))
            self.target_water.ca_min=self.style_water.ca_min

            self.ui.MgMinTargetEdit.setText(str(self.style_water.mg_min))
            self.target_water.mg_min=self.style_water.mg_min

            self.ui.NaMinTargetEdit.setText(str(self.style_water.na_min))
            self.target_water.na_min=self.style_water.na_min

            self.ui.ClMinTargetEdit.setText(str(self.style_water.cl_min))
            self.target_water.cl_min=self.style_water.cl_min

            self.ui.So4MinTargetEdit.setText(str(self.style_water.so4_min))
            self.target_water.so4_min=self.style_water.so4_min

            self.ui.AlkaMinTargetEdit.setText(str(self.style_water.alca_min)) 
            self.target_water.alca_min=self.style_water.alca_min
            
            self.ui.CaMaxTargetEdit.setText(str(self.style_water.ca_max))
            self.target_water.ca_max=self.style_water.ca_max

            self.ui.MgMaxTargetEdit.setText(str(self.style_water.mg_max))
            self.target_water.mg_max=self.style_water.mg_max

            self.ui.NaMaxTargetEdit.setText(str(self.style_water.na_max))
            self.target_water.na_max=self.style_water.na_max

            self.ui.ClMaxTargetEdit.setText(str(self.style_water.cl_max))
            self.target_water.cl_max=self.style_water.cl_max

            self.ui.So4MaxTargetEdit.setText(str(self.style_water.so4_max))
            self.target_water.so4_max=self.style_water.so4_max

            self.ui.AlkaMaxTargetEdit.setText(str(self.style_water.alca_max))
            self.target_water.alca_max=self.style_water.alca_max
            self.target_water.name='Target Water'
            self.reset_so4_vs_cl_ratio()
            self.ui.RatioGroupbox.setVisible(True)
            self.reset_so4_vs_cl_ratio()
            self.enable_salt_values()
            self.water_adjustment_state=None
            self.parent.phAdjuster.refresh_view()

            
    #------------------------------------------------------------------------------------------------
    def clear_target_profile(self):
        self.ui.CaMinTargetEdit.setText('0')
        self.ui.MgMinTargetEdit.setText('0')
        self.ui.NaMinTargetEdit.setText('0')
        self.ui.ClMinTargetEdit.setText('0')
        self.ui.So4MinTargetEdit.setText('0')
        self.ui.AlkaMinTargetEdit.setText('0') 
        
        self.ui.CaMaxTargetEdit.setText('0')
        self.ui.MgMaxTargetEdit.setText('0')
        self.ui.NaMaxTargetEdit.setText('0')
        self.ui.ClMaxTargetEdit.setText('0')
        self.ui.So4MaxTargetEdit.setText('0')
        self.ui.AlkaMaxTargetEdit.setText('0')

        self.target_water=WaterTarget(None,None, None,None,None, None, None, None, None,None,None, None, None, None)
        self.ui.RatioGroupbox.setVisible(False)
        self.water_adjustment_state=None
        self.parent.phAdjuster.refresh_view()
                             
    #------------------------------------------------------------------------------------------------ 
    def load_style_water(self):
        index = self.ui.StyleCombo.currentData()
        if index:
            self.style_water=find_style_by_id(index)
            self.ui.CaMinStyleEdit.setText(str(self.style_water.ca_min))
            self.ui.MgMinStyleEdit.setText(str(self.style_water.mg_min))
            self.ui.NaMinStyleEdit.setText(str(self.style_water.na_min))
            self.ui.ClMinStyleEdit.setText(str(self.style_water.cl_min))
            self.ui.So4MinStyleEdit.setText(str(self.style_water.so4_min))
            self.ui.AlkaMinStyleEdit.setText(str(self.style_water.alca_min)) 
            
            self.ui.CaMaxStyleEdit.setText(str(self.style_water.ca_max))
            self.ui.MgMaxStyleEdit.setText(str(self.style_water.mg_max))
            self.ui.NaMaxStyleEdit.setText(str(self.style_water.na_max))
            self.ui.ClMaxStyleEdit.setText(str(self.style_water.cl_max))
            self.ui.So4MaxStyleEdit.setText(str(self.style_water.so4_max))
            self.ui.AlkaMaxStyleEdit.setText(str(self.style_water.alca_max))
        else:
            self.style_water=WaterTarget(None,None, None,None,None, None, None, None, None,None,None, None, None, None)
            self.ui.CaMinStyleEdit.setText('')
            self.ui.MgMinStyleEdit.setText('')
            self.ui.NaMinStyleEdit.setText('')
            self.ui.ClMinStyleEdit.setText('')
            self.ui.So4MinStyleEdit.setText('')
            self.ui.AlkaMinStyleEdit.setText('') 
            
            self.ui.CaMaxStyleEdit.setText('')
            self.ui.MgMaxStyleEdit.setText('')
            self.ui.NaMaxStyleEdit.setText('')
            self.ui.ClMaxStyleEdit.setText('')
            self.ui.So4MaxStyleEdit.setText('')
            self.ui.AlkaMaxStyleEdit.setText('')  
    #----------------------------------------------------------------------------------------------
    def base_combo_activated(self):
        self.water_adjustment_state=None
        #self.parent.phAdjuster.refresh_view()

    def load_base_water(self):
        index=self.ui.BaseCombo.currentData()
        if index:
            self.base_water=find_base_by_id(index)
            self.ui.CaBaseEdit.setText(str(self.base_water.ca))
            self.ui.MgBaseEdit.setText(str(self.base_water.mg))
            self.ui.NaBaseEdit.setText(str(self.base_water.na))
            self.ui.ClBaseEdit.setText(str(self.base_water.cl))
            self.ui.So4BaseEdit.setText(str(self.base_water.so4))
            self.ui.AlkaBaseEdit.setText(str(self.base_water.alca))
           
       
        else:
            self.base_water= Water(None,None,None,None,None, None, None, None,None)
            self.mixed_water=Water(None,None,None,None,None, None, None, None,None)
            self.ui.CaBaseEdit.setText('')
            self.ui.MgBaseEdit.setText('')
            self.ui.NaBaseEdit.setText('')
            self.ui.ClBaseEdit.setText('')
            self.ui.So4BaseEdit.setText('')
            self.ui.AlkaBaseEdit.setText('')  
            
            self.ui.CaMixedEdit.setText('')
            self.ui.MgMixedEdit.setText('')
            self.ui.NaMixedEdit.setText('')
            self.ui.ClMixedEdit.setText('')
            self.ui.So4MixedEdit.setText('')
            self.ui.AlkaMixedEdit.setText('') 

        self.dilution_changed() 
        self.ui.DilutionCombo.setCurrentText(self.ui.BaseCombo.currentText())
        #self.parent.phAdjuster.refresh_view() 
    #--------------------------------------------------------------------------------------------------
    def dilution_combo_activated(self):
        self.water_adjustment_state=None
        

    def load_dilution_water(self):
        
        index=self.ui.DilutionCombo.currentData()
        self.ui.DilutionSpin.setValue(0)
        if index:
            self.ui.DilutionSpin.setEnabled(True)
            self.dilution_water=find_base_by_id(index)
            self.ui.CaDilutionEdit.setText(str(self.dilution_water.ca))
            self.ui.MgDilutionEdit.setText(str(self.dilution_water.mg))
            self.ui.NaDilutionEdit.setText(str(self.dilution_water.na))
            self.ui.ClDilutionEdit.setText(str(self.dilution_water.cl))
            self.ui.So4DilutionEdit.setText(str(self.dilution_water.so4))
            self.ui.AlkaDilutionEdit.setText(str(self.dilution_water.alca))
            self.dilution_changed()
            #self.parent.phAdjuster.refresh_view()
        else:
        
            self.dilution_water=Water(None,None,None,None,None, None, None, None,None)
            
            self.ui.DilutionSpin.setEnabled(False)
           
            self.ui.CaDilutionEdit.setText('')
            self.ui.MgDilutionEdit.setText('')
            self.ui.NaDilutionEdit.setText('')
            self.ui.ClDilutionEdit.setText('')
            self.ui.So4DilutionEdit.setText('')
            self.ui.AlkaDilutionEdit.setText('')  
            self.ui.CaMixedEdit.setText('')
            self.ui.MgMixedEdit.setText('')
            self.ui.NaMixedEdit.setText('')
            self.ui.ClMixedEdit.setText('')
            self.ui.So4MixedEdit.setText('')
            self.ui.AlkaMixedEdit.setText('') 

        
    #--------------------------------------------------------------------------------------------------
    def pH_mixed(self,base_water,dilution_water,dilution):
        #dilution is a factor between 0 and 1
        base_concentration=10 ** (-1* self.base_water.pH)
        dilution_concentration = 10 **(-1 * self.dilution_water.pH)
        mixed_concentration= (1-dilution)*base_concentration +dilution * dilution_concentration
        return -math.log10(mixed_concentration)
    #-------------------------------------------------------------------------------------------------
    def dilution_changed(self):
        if self.ui.DilutionCombo.currentText() != '' and self.ui.BaseCombo.currentText()!= '':
            self.mash_water_mass=round(self.parent.mash_water_mass,2)
            self.dilution=self.ui.DilutionSpin.value()
            percent=self.dilution/100
            self.ui.MashMixedEdit.setText(str(self.mash_water_mass))
            self.ui.MashBaseEdit.setText(str(round(self.mash_water_mass * (1-percent),2)))
            self.ui.MashDilutionEdit.setText(str(round(self.mash_water_mass * (percent),2))) 
    
            ca_mixed=float(self.ui.CaBaseEdit.text()) * (1-percent) +float(self.ui.CaDilutionEdit.text()) * percent
            self.ui.CaMixedEdit.setText(str(round(ca_mixed,2))) 
            self.mixed_water.ca=ca_mixed
            mg_mixed=float(self.ui.MgBaseEdit.text()) * (1-percent) +float(self.ui.MgDilutionEdit.text()) * percent
            self.ui.MgMixedEdit.setText(str(round(mg_mixed,2)))
            self.mixed_water.mg=mg_mixed
            na_mixed=float(self.ui.NaBaseEdit.text()) * (1-percent) +float(self.ui.NaDilutionEdit.text()) * percent
            self.ui.NaMixedEdit.setText(str(round(na_mixed,2)))
            self.mixed_water.na=na_mixed
            cl_mixed=float(self.ui.ClBaseEdit.text()) * (1-percent) +float(self.ui.ClDilutionEdit.text()) * percent
            self.ui.ClMixedEdit.setText(str(round(cl_mixed,2)))
            self.mixed_water.cl=cl_mixed
            so4_mixed=float(self.ui.So4BaseEdit.text()) * (1-percent) +float(self.ui.So4DilutionEdit.text()) * percent
            self.ui.So4MixedEdit.setText(str(round(so4_mixed,2)))  
            self.mixed_water.so4=so4_mixed
            alca_mixed=float(self.ui.AlkaBaseEdit.text()) * (1-percent) +float(self.ui.AlkaDilutionEdit.text()) * percent
            self.ui.AlkaMixedEdit.setText(str(round(alca_mixed,2)))  
            self.mixed_water.alca=alca_mixed
            pH_mixed=self.pH_mixed(self.base_water,self.dilution_water,self.dilution/100)
            self.mixed_water.pH=pH_mixed
            self.mixed_water.name='Mixed water'
            self.adjusted_water=copy.deepcopy(self.mixed_water)
            self.adjusted_water.name='Adjusted_water'
            self.update_adjusted_water()#set the display
            self.reset_so4_vs_cl_ratio()#reset the average ratio
            self.clean_salt_values()
            
        else: 
        
            self.mixed_water=Water(None,None,None,None,None, None,None, None,None)
           
            self.set_so4_vs_cl_ratio()#to clean the salts values

            self.ui.RatioGroupbox.setVisible(False)
        
    #--------------------------------------------------------------------------------------------------
    def colorize_adjusted_water(self):
        if self.adjusted_water is not None:
            if self.adjusted_water.ca >self.target_water.ca_min and self.adjusted_water.ca<self.target_water.ca_max:
                self.ui.CaAdjustedEdit.setStyleSheet('background-color: green; color: white')
            else:
                self.ui.CaAdjustedEdit.setStyleSheet('background-color: red; color: white;')    
        else:
            self.ui.CaAdjustedEdit.setStyleSheet('background-color: white; color: blue;')
    #--------------------------------------------------------------------------------------------------
    def sparge_water_changed(self):
        #update the various edit related to sparge water 
        self.sparge_water_mass=round(self.parent.sparge_water_mass,2)
        self.water_for_sparge = self.ui.SpargeWaterSelectCombo.currentText()
        if self.water_for_sparge:
            match self.water_for_sparge :
                case 'Eau de base':
                    self.ui.SpargeBaseEdit.setText(str(round(self.sparge_water_mass ,2)))
                    self.ui.SpargeDilutionEdit.setText('0')
                    self.ui.SpargeMixedEdit.setText('0') 
                    self.hide_sparge_salt_edits() 
                case 'Eau de dilution':
                    self.ui.SpargeBaseEdit.setText('0')
                    self.ui.SpargeDilutionEdit.setText(str(round(self.sparge_water_mass,2)))
                    self.ui.SpargeMixedEdit.setText('0')  
                    self.hide_sparge_salt_edits()  
                case 'Eau mélangée brute' :  
                    self.ui.SpargeBaseEdit.setText('0')
                    self.ui.SpargeDilutionEdit.setText('0')
                    self.ui.SpargeMixedEdit.setText(str(round(self.sparge_water_mass,2)))     
                    self.hide_sparge_salt_edits()          
                case 'Eau mélangée ajustée' :     
                    self.ui.SpargeBaseEdit.setText('0')
                    self.ui.SpargeDilutionEdit.setText('0')
                    self.ui.SpargeMixedEdit.setText(str(round(self.sparge_water_mass,2))) 
                    self.show_sparge_salt_edits() 
                case 'Eau distillée':
                    self.ui.SpargeBaseEdit.setText('0')
                    self.ui.SpargeDilutionEdit.setText('0')
                    self.ui.SpargeMixedEdit.setText('0')
                    self.hide_sparge_salt_edits() 
        self.parent.phAdjuster.refresh_view()
    #----------------------------------------------------------------------------------------------
    def hide_sparge_salt_edits(self):
        self.ui.SpargeTotalLabel.setVisible(False)
        self.ui.CaSO4SpargeTotalValue.setVisible(False)
        self.ui.MgSO4SpargeTotalValue.setVisible(False)
        self.ui.CaCl2SpargeTotalValue.setVisible(False)
        self.ui.MgCl2SpargeTotalValue.setVisible(False)
        self.ui.CaOH2SpargeTotalValue.setVisible(False)
        self.ui.NaHCO3SpargeTotalValue.setVisible(False)
        
        self.ui.CaSO4SpargeLabel.setVisible(False)
        self.ui.MgSO4SpargeLabel.setVisible(False)
        self.ui.CaCl2SpargeLabel.setVisible(False)
        self.ui.MgCl2SpargeLabel.setVisible(False)
        self.ui.CaOH2SpargeLabel.setVisible(False)
        self.ui.NaHCO3SpargeLabel.setVisible(False)
    #----------------------------------------------------------------------------------------------
    def show_sparge_salt_edits(self):
        self.ui.SpargeTotalLabel.setVisible(True)
        self.ui.CaSO4SpargeTotalValue.setVisible(True)
        self.ui.MgSO4SpargeTotalValue.setVisible(True)
        self.ui.CaCl2SpargeTotalValue.setVisible(True)
        self.ui.MgCl2SpargeTotalValue.setVisible(True)
        self.ui.CaOH2SpargeTotalValue.setVisible(True)
        self.ui.NaHCO3SpargeTotalValue.setVisible(True)   
        self.ui.CaSO4SpargeLabel.setVisible(True)
        self.ui.MgSO4SpargeLabel.setVisible(True)
        self.ui.CaCl2SpargeLabel.setVisible(True)
        self.ui.MgCl2SpargeLabel.setVisible(True)
        self.ui.CaOH2SpargeLabel.setVisible(True)
        self.ui.NaHCO3SpargeLabel.setVisible(True) 

    #------------------------------------------------------------------------------------------------
    def update_adjusted_water(self):
        if self.mixed_water.name is not None :
            self.CaSO4_val=float(self.ui.CaSO4Value.value())
            self.MgSO4_val=float(self.ui.MgSO4Value.value())
            self.CaCl2_val=float(self.ui.CaCl2Value.value())
            self.MgCl2_val=float(self.ui.MgCl2Value.value())
            self.CaOH2_val=float(self.ui.CaOH2Value.value())
            self.NaHCO3_val=float(self.ui.NaHCO3Value.value())

            self.adjusted_water.ca=self.mixed_water.ca +( self.CaSO4_val * self.CaSO4.ca  + self.CaCl2_val * self.CaCl2.ca + self.CaOH2_val * self.CaOH2.ca )/1000
            self.adjusted_water.mg =self.mixed_water.mg +( self.MgSO4_val * self.MgSO4.mg + self.MgCl2_val * self.MgCl2.mg)/1000
            self.adjusted_water.na= self.mixed_water.na +(self.NaHCO3_val * self.NaHCO3.na ) /1000
            self.adjusted_water.cl=self.mixed_water.cl + (self.CaCl2_val * self.CaCl2.cl + self.MgCl2_val * self.MgCl2.cl)/1000
            self.adjusted_water.so4 =self.mixed_water.so4 +(self.CaSO4_val * self.CaSO4.so4 +self.MgSO4_val * self.MgSO4.so4)/1000
            self.adjusted_water.alca=self.mixed_water.alca +(self.CaOH2_val * self.CaOH2.alca + self.NaHCO3_val * self.NaHCO3.alca)/1000

            self.ui.CaAdjustedEdit.setText(str(round(self.adjusted_water.ca,2)))
            self.ui.MgAdjustedEdit.setText(str(round(self.adjusted_water.mg,2)))
            self.ui.NaAdjustedEdit.setText(str(round(self.adjusted_water.na,2)))
            self.ui.ClAdjustedEdit.setText(str(round(self.adjusted_water.cl,2)))
            self.ui.SO4AdjustedEdit.setText(str(round(self.adjusted_water.so4,2)))
            self.ui.AlkaAdjustedEdit.setText(str(round(self.adjusted_water.alca,2)))
            
            mash_salt_mass=self.CaSO4_val*self.mash_water_mass/1000
            sparge_salt_mass=self.CaSO4_val*self.sparge_water_mass/1000
            self.ui.CaSO4MashTotalValue.setText(str(round(mash_salt_mass,2)))
            self.ui.CaSO4SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))
            
            mash_salt_mass=self.MgSO4_val*self.mash_water_mass/1000
            sparge_salt_mass=self.MgSO4_val*self.sparge_water_mass/1000
            self.ui.MgSO4MashTotalValue.setText(str(round(mash_salt_mass,2)))
            self.ui.MgSO4SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))

            mash_salt_mass=self.CaCl2_val*self.mash_water_mass/1000
            sparge_salt_mass=self.CaCl2_val*self.sparge_water_mass/1000
            self.ui.CaCl2MashTotalValue.setText(str(round(mash_salt_mass,2)))
            self.ui.CaCl2SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))

            mash_salt_mass=self.MgCl2_val*self.mash_water_mass/1000
            sparge_salt_mass=self.MgCl2_val*self.sparge_water_mass/1000
            self.ui.MgCl2MashTotalValue.setText(str(round(mash_salt_mass,2)))
            self.ui.MgCl2SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))

            mash_salt_mass=self.CaOH2_val*self.mash_water_mass/1000
            sparge_salt_mass=self.CaOH2_val*self.sparge_water_mass/1000
            self.ui.CaOH2MashTotalValue.setText(str(round(mash_salt_mass,2)))
            self.ui.CaOH2SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))

            mash_salt_mass=self.NaHCO3_val*self.mash_water_mass/1000
            sparge_salt_mass=self.NaHCO3_val*self.sparge_water_mass/1000
            self.ui.NaHCO3MashTotalValue.setText(str(round(mash_salt_mass,2)))
            self.ui.NaHCO3SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))

            #self.salt_additions=SaltAdditions(self.CaSO4_val,self.MgSO4_val,self.CaCl2_val,self.MgCl2_val,self.CaOH2_val,self.NaHCO3_val)
          
            self.actualize_flags()
   
    #---------------------------------------------------------------------------------------------   
    def actualize_flags(self):
        if self.target_water.name is not None:
            self.actual_ratio=None
            
            self.preference=None
            if self.adjusted_water.cl !=0:
                self.actual_ratio=self.adjusted_water.so4 /self.adjusted_water.cl
                if self.target_so4_vs_cl_ratio <self.actual_ratio:
                    self.preference ='Cl'
                else:
                    self.preference ='SO4'
            else:
                preference='Cl' #to avoid division by zero

            self.ui.RatioActualEdit.setText(str(round(self.actual_ratio,2)) )   
        
            #disponibility
            self.MgCl2_available = self.ui.MgCl2Checkbox.isChecked()
            self.CaOH2_available= self.ui.CaOH2Checkbox.isChecked()
            self.NaHCO3_available=self.ui.NaHCO3Checkbox.isChecked()

            #for calcium
            if self.adjusted_water.ca <self.target_water.ca_min:
                self.needs_ca=True
                self.welcomes_ca=True
                self.accepts_ca=True
            else:
                self.needs_ca=False
                if self.adjusted_water.ca<(self.target_water.ca_min +self.target_water.ca_max)/2:
                    self.welcomes_ca=True
                    self.accepts_ca=True
                else:
                    self.welcomes_ca=False
                    if self.adjusted_water.ca<self.target_water.ca_max:
                        self.accepts_ca=True
                    else:
                        self.accepts_ca=False   
            #for magnesium          
            if self.adjusted_water.mg <self.target_water.mg_min:
                self.needs_mg=True
                self.welcomes_mg=True
                self.accepts_mg=True
            else:
                self.needs_mg=False
                if self.adjusted_water.mg<(self.target_water.mg_min +self.target_water.mg_max)/2:
                    self.welcomes_mg=True
                    self.accepts_mg=True
                else:
                    self.welcomes_mg=False
                    if self.adjusted_water.mg<self.target_water.mg_max:
                        self.accepts_mg=True
                    else:
                        self.accepts_ca=False  

            #for sodium          
            if self.adjusted_water.na <self.target_water.na_min:
                self.needs_na=True
                self.welcomes_na=True
                self.accepts_na=True
            else:
                self.needs_na=False
                if self.adjusted_water.na<(self.target_water.na_min +self.target_water.na_max)/2:
                    self.welcomes_na=True
                    self.accepts_na=True
                else:
                    self.welcomes_na=False
                    if self.adjusted_water.na<self.target_water.na_max:
                        self.accepts_na=True
                    else:
                        self.accepts_na=False    
            #for chloride         
            if self.adjusted_water.cl <self.target_water.cl_min:
                self.needs_cl=True
                self.welcomes_cl=True
                self.accepts_cl=True
            else:
                self.needs_cl=False
                if self.adjusted_water.cl<(self.target_water.cl_min +self.target_water.cl_max)/2:
                    self.welcomes_cl=True
                    self.accepts_cl=True
                else:
                    self.welcomes_cl=False
                    if self.adjusted_water.cl<self.target_water.cl_max:
                        self.accepts_cl=True
                    else:
                        self.accepts_cl=False    

            #for sulfate         
            if self.adjusted_water.so4 <self.target_water.so4_min:
                self.needs_so4=True
                self.welcomes_so4=True
                self.accepts_so4=True
            else:
                self.needs_so4=False
                if self.adjusted_water.so4<(self.target_water.so4_min +self.target_water.so4_max)/2:
                    self.welcomes_so4=True
                    self.accepts_so4=True
                else:
                    self.welcomes_so4=False
                    if self.adjusted_water.so4<self.target_water.so4_max:
                        self.accepts_so4=True
                    else:
                        self.accepts_so4=False  

            #for alkalinity          
            if self.adjusted_water.alca <self.target_water.alca_min:
                self.needs_alca=True
                self.welcomes_alca=True
                self.accepts_alca=True
            else:
                self.needs_alca=False
                if self.adjusted_water.alca<(self.target_water.alca_min +self.target_water.alca_max)/2:
                    self.welcomes_alca=True
                    self.accepts_alca=True
                else:
                    self.welcomes_alca=False
                    if self.adjusted_water.alca<self.target_water.alca_max:
                        self.accepts_alca=True
                    else:
                        self.accepts_alca=False      

    #---------------------------------------------------------------------------------------------
    def useCaSO4(self) :
        #use 0.1mg of MgSO4 per liter
        val=self.ui.CaSO4Value.value()
        self.ui.CaSO4Value.setValue(val+0.1)
        mash_salt_mass=(val+0.1)*self.mash_water_mass/1000
        sparge_salt_mass=(val+0.1)*self.sparge_water_mass/1000
        self.ui.CaSO4MashTotalValue.setText(str(round(mash_salt_mass,2)))
        self.ui.CaSO4SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))
 
    #---------------------------------------------------------------------------------------------
    def useMgSO4(self) :
        #use 0.1mg of MgSO4 per liter
        val=self.ui.MgSO4Value.value()
        self.ui.MgSO4Value.setValue(val+0.1)
        mash_salt_mass=(val+0.1)*self.mash_water_mass/1000
        sparge_salt_mass=(val+0.1)*self.sparge_water_mass/1000
        self.ui.MgSO4MashTotalValue.setText(str(round(mash_salt_mass,2)))
        self.ui.MgSO4SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))
    #------------------------------------------------------------------------------------------
    def removeMgSO4(self):
        val=self.ui.MgSO4Value.value()
        self.ui.MgSO4Value.setValue(val-0.1)
     #---------------------------------------------------------------------------------------------
    def useCaCl2(self) :
        #use 0.1mg of CaCl2 per liter
        val=self.ui.CaCl2Value.value()
        self.ui.CaCl2Value.setValue(val+0.1) 
        mash_salt_mass=(val+0.1)*self.mash_water_mass/1000
        sparge_salt_mass=(val+0.1)*self.sparge_water_mass/1000
        self.ui.CaCl2MashTotalValue.setText(str(round(mash_salt_mass,2)))
        self.ui.CaCl2SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))
  
    #---------------------------------------------------------------------------------------------
    def useMgCl2(self) :
        #use 0.1mg of MgCl2 per liter
        val=self.ui.MgCl2Value.value()
        self.ui.MgCl2Value.setValue(val+0.1)     
        mash_salt_mass=(val+0.1)*self.mash_water_mass/1000
        sparge_salt_mass=(val+0.1)*self.sparge_water_mass/1000
        self.ui.MgCl2MashTotalValue.setText(str(round(mash_salt_mass,2)))
        self.ui.MgCl2SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))

   #---------------------------------------------------------------------------------------------
    def useCaOH2(self) :
        #use 0.1mg of CaOH2 per liter
        val=self.ui.CaOH2Value.value()
        self.ui.CaOH2Value.setValue(val+0.1)   
        mash_salt_mass=(val+0.1)*self.mash_water_mass/1000
        sparge_salt_mass=(val+0.1)*self.sparge_water_mass/1000
        self.ui.CaOH2MashTotalValue.setText(str(round(mash_salt_mass,2)))
        self.ui.CaOH2SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))     


   #---------------------------------------------------------------------------------------------
    def useNaHCO3(self) :
        #use 0.1mg of NaHCO3 per liter
        val=self.ui.NaHCO3Value.value()
        self.ui.NaHCO3Value.setValue(val+0.1)        
        mash_salt_mass=(val+0.1)*self.mash_water_mass/1000
        sparge_salt_mass=(val+0.1)*self.sparge_water_mass/1000
        self.ui.NaHCO3MashTotalValue.setText(str(round(mash_salt_mass,2)))
        self.ui.NaHCO3SpargeTotalValue.setText(str(round(sparge_salt_mass,2)))  
    #----------------------------------------------------------------------------------------------------
    def ignore_checkbox_changed(self):
        if self.ui.IgnoreCheckbox.isChecked():
            self.ui.RatioTargetEdit.setEnabled(True)
            self.ui.RatioTargetEdit.setValue(float(self.target_so4_vs_cl_ratio))  #triggers a set_so4_vs_cl_ratio  
            
        else:
            self.reset_so4_vs_cl_ratio()
            self.ui.RatioTargetEdit.setEnabled(False)
    #---------------------------------------------------------------------------------------------
    def reset_so4_vs_cl_ratio(self):
        if self.target_water.name is not None:
            average_so4=(float(self.target_water.so4_min) + float(self.target_water.so4_max))/2
            average_cl=(float(self.target_water.cl_min) + float(self.target_water.cl_max))/2
            if average_cl != 0:
                self.target_so4_vs_cl_ratio=average_so4/average_cl
                self.ui.RatioTargetEdit.setValue(self.target_so4_vs_cl_ratio)
                self.ui.RatioTargetEdit.setEnabled(False)
    
        else:
            self.target_so4_vs_cl_ratio=1  


    #-----------------------------------------------------------------------------------------------
    def set_so4_vs_cl_ratio(self):
        self.target_so4_vs_cl_ratio=(self.ui.RatioTargetEdit.value())
        self.clean_salt_values()
        
        self.ui.RatioGroupbox.setVisible(True)
    
    #---------------------------------------------------------------------------------------------
    def read_salt_additions(self):
        return SaltAdditions(self.CaSO4_val,self.MgSO4_val,self.CaCl2_val,self.MgCl2_val,self.CaOH2_val,self.NaHCO3_val)
    #-----------------------------------------------------------------------------------------------
    def init_salt_additions_display(self):
        self.ui.CaSO4Value.setValue((self.salt_additions.CaSO4))
        self.ui.MgSO4Value.setValue((self.salt_additions.MgSO4))
        self.ui.CaCl2Value.setValue((self.salt_additions.CaCl2))
        self.ui.MgCl2Value.setValue((self.salt_additions.MgCl2))
        self.ui.CaOH2Value.setValue((self.salt_additions.CaOH2))
        self.ui.NaHCO3Value.setValue((self.salt_additions.NaHCO3))
    #------------------------------------------------------------------------------------------------
    def clean_salt_values(self):
        self.ui.CaSO4Value.setValue(0)
        self.ui.MgSO4Value.setValue(0)
        self.ui.CaCl2Value.setValue(0)
        self.ui.MgCl2Value.setValue(0)
        self.ui.CaOH2Value.setValue(0)
        self.ui.NaHCO3Value.setValue(0) 
        self.ui.AdjustButton.setStyleSheet('background-color: red; color:white') 
        self.ui.AdjustButton.setText('Lancer le pré-ajustement')
        self.ui.CaSO4MashTotalValue.setText('')
        self.ui.MgSO4MashTotalValue.setText('')
        self.ui.CaCl2MashTotalValue.setText('')
        self.ui.MgCl2MashTotalValue.setText('')
        self.ui.CaOH2MashTotalValue.setText('')
        self.ui.NaHCO3MashTotalValue.setText('')
        self.ui.CaSO4SpargeTotalValue.setText('')
        self.ui.MgSO4SpargeTotalValue.setText('')
        self.ui.CaCl2SpargeTotalValue.setText('')
        self.ui.MgCl2SpargeTotalValue.setText('')
        self.ui.CaOH2SpargeTotalValue.setText('')
        self.ui.NaHCO3SpargeTotalValue.setText('')
    #------------------------------------------------------------------------------------------------    
    def auto_adjust(self):
        
        if self.target_water.name is not None:
            
            self.actualize_flags()
            #try to satisfy Ca min
            while self.needs_ca :
                if self.preference == 'Cl' and self.accepts_cl:
                    self.useCaCl2()  
                else:
                    if self.accepts_so4:
                        self.useCaSO4()
                    else:
                        if self.accepts_cl:
                            self.useCaCl2()#accept drift of ratio because ca min is priority
                        else:
                            break
                self.actualize_flags()  
            #try to satisfy Mg min
            while self.needs_mg:
                if self.preference == 'Cl' and self.MgCl2_available:
                    self.useMgCl2
                else:
                    self.useMgSO4  
             
            #try to satisfy Ca average because more calcium is better
            #only if it doesn't degrade ratiouse_water_as_is
            while self.welcomes_ca:
                if self.preference == 'Cl':
                    if self.accepts_cl:
                        self.useCaCl2()
                    else:
                        break   # once ca min is satisfied we no longer accept drift in ratio  
                else:
                    if self.accepts_so4:
                        self.useCaSO4() 
                    else:
                        break       
            
            #try to satisfy Mg average
            #only if it doesn't degrade ratio
            while self.welcomes_mg:
                if self.preference == 'Cl':
                    if self.accepts_cl and self.MgCl2_available:
                        self.useMgCl2()
                    else:
                        break
                else:
                    if self.accepts_so4:
                        self.useMgSO4()    
                    else:
                        break    
            
            #try to satisfy Cl min if still necessary
            #let ratio evolve freely
            while self.needs_cl:
                if self.preference == 'Cl' :
                    if self.accepts_ca:
                        self.useCaCl2()
                    else:
                        if self.accepts_mg and self.MgCl2_available:
                            self.useMgCl2() 
                        else:
                            break #no further mean to add Cl
                else:
                    #preference is SO4 (add SO4 to increase the ratio and allow more Cl)
                    if self.accepts_ca:
                        self.useCaSO4() 
                    else:
                        if self.accepts_mg:
                            self.useMgSO4()  
                        else:
                            break                   
                 
            #try to satisfy SO4 min if still necessary
            #let ratio evolve freely
            while self.needs_so4:
                if self.preference == 'SO4'  :
                    if self.accepts_ca:
                        self.useCaSO4()
                    else:
                        if self.accepts_mg:
                            self.useMgSO4()
                        else:
                            break
                else:
                    #preference is Cl (add Cl to lower the ratio and thuse allow more SO4) 
                    if self.accepts_ca:
                        self.useCaCl2()
                    else:
                        if self.accepts_mg and self.MgCl2_available:
                            self.useMgCl2()
                        else:
                            break                    
            
            #try to statisfy alca min
            while self.needs_alca:
                if self.accepts_ca and self.CaOH2_available:
                    self.useCaOH2()   
                else:
                    if self.accepts_na and self.NaHCO3_available:
                        self.useNaHCO3()
                    else:
                        break        
                                                                            
            self.ui.AdjustButton.setStyleSheet('background-color: green; color: white') 
            self.ui.AdjustButton.setText('Profil d\'eau pré-ajusté')
            self.ui.AsIsButton.setText("Utiliser l'eau sans ajustement")
            self.ui.AsIsButton.setStyleSheet('background-color: red; color: white;')
            self.enable_salt_values()
            self.water_adjustment_state='adjusted'
            self.parent.water_adjustment_state="adjusted"
            self.parent.phAdjuster.refresh_view()

    #-------------------------------------------------------------------------------------
    def use_water_as_is(self):
        if self.mixed_water.name is not None:
            self.adjusted_water=copy.deepcopy(self.mixed_water)
            self.clean_salt_values()
            self.update_adjusted_water()
            self.ui.AsIsButton.setStyleSheet('background-color: green; color: white;')
            self.ui.AsIsButton.setText('Eau utilisée sans ajustement')
            self.water_adjustment_state='as_is'
            self.parent.water_adjustment_state = 'as_is'
            self.parent.phAdjuster.refresh_view()
              
                