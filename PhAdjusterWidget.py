'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from PhAdjusterWidgetBase import Ui_Adjuster 
from DiphItemWidget import DiphItemWidget
from PyQt6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QLineEdit,QLabel,QListView,QPushButton,QGroupBox
from PyQt6 import QtCore
from PyQt6.QtCore import Qt,QRegularExpression,QTimer,QModelIndex,pyqtSignal,QObject
from database.fermentables.fermentable_brand import all_fbrand, find_fbrand_by_name
from PyQt6 import QtGui
from parameters import acids,get_acid_by_name
import copy,os
from SignalObject import SignalObject

class Communication(QObject):
    signal_change=pyqtSignal(SignalObject)

class PhAdjusterWidget(QWidget):
    def __init__(self,parent=None):
        #context may be recipe, brew or inventory
        super().__init__(parent) 
        self.parent=parent 
        self.ui =Ui_Adjuster()
        self.ui.setupUi(self)
        self.communicator=Communication()

        if self.parent.pH_adjuster_enabled is not None:
            self.ui.mainCheckBox.setChecked(self.parent.pH_adjuster_enabled)
        else:
            self.ui.mainCheckBox.setChecked(False)    
        #this will set self.pH_adjuster_enabled
        self.activate()

        self.pH_target=self.parent.pH_target
        self.diph_items=[]
        
        self.diph_layout=QVBoxLayout()
        self.scroll_content=QWidget()
        
        #initialize drop list of acidAgentCombo
        self.ui.acidAgentCombo.addItem('')
        for acid in acids:
            self.ui.acidAgentCombo.addItem(acid.name)
        if self.parent.acid_agent is not None:
            self.ui.acidAgentCombo.setCurrentText(self.parent.acid_agent)
        if self.parent.pH_target is not None:
            self.ui.spinBox.setValue(round(self.parent.pH_target,2))
        self.ui.phAdjustMessageLabel.setText('')
        self.ui.spargeAdjustMessageLabel.setText('')
        self.set_connections()
    

    #-----------------------------------------------------------------------------------
    def set_connections(self):
        self.ui.spinBox.valueChanged.connect(self.update_pH_target)
        self.ui.acidAgentCombo.currentTextChanged.connect(self.refresh_view)
        self.ui.mainCheckBox.stateChanged.connect(self.activate)
        self.communicator.signal_change.connect(self.diph_item_changed)

    #-----------------------------------------------------------------------------------
    def diph_item_changed(self):
        self.calculate()

    def activate(self):
        if self.ui.mainCheckBox.isChecked() ==True:
            self.ui.mainCheckBox.setText("Ajustement du pH en service")
            self.ui.mainCheckBox.setStyleSheet("color:darkgreen; font-size:16")
            self.ui.controlGroupbox.setVisible(True)
            self.ui.groupboxMaltsDiph.setVisible(True)
            self.pH_adjuster_enabled = True
        else:
            self.ui.mainCheckBox.setText("Ajustement du pH hors service")
            self.ui.mainCheckBox.setStyleSheet("color:red; font-size:16")   
            self.ui.controlGroupbox.setVisible(False)
            self.ui.groupboxMaltsDiph.setVisible(False)
            self.pH_adjuster_enabled = False
    #-------------------------------------------------------------------------------------
    def update_pH_target(self):
        try:
            self.pH_target=float(self.ui.spinBox.value())
            self.refresh_view()
        except:
            self.pH_target=None
    
    #-----------------------------------------------------------------------------------
    def calculate(self):
        #check the phAdjuster view is complete
        if self.pH_adjuster_ready():
            self.pH_before_acid_additions()
            #the result is ignored as the method set the text in the text area
            rqvol=self.required_mash_acid_volume(self.pH_target)
            if self.parent.waterAdjustmentDialog.water_for_sparge is not None:
                #the result is ignored as the method set the text in the text area
                rqsvol=self.required_sparge_acid_volume(6)
            else:
                self.ui.spargeAdjustMessageLabel.setText("<p>Vous devez d'abord choisir une eau de rinçage dans l'onglet « Ajustement du profil d'eau »</p>")  
                self.ui.spargeAdjustMessageLabel.setStyleSheet("color:red")
    #-----------------------------------------------------------------------------------
    def refresh_view(self):
        #this is triggered each time there is a reason for updating the view and the calculation
    
        self.clean_and_reset()
        if self.parent.waterAdjustmentDialog.water_adjustment_state is not None:
           
            
            self.ui.acidAgentCombo.setVisible(True)
            self.ui.phAdjustMessageLabel.setText('')
            self.ui.spargeAdjustMessageLabel.setText('')
            self.calculate()

        else:   
            
         
            self.ui.acidAgentCombo.setVisible(False) 
            self.parent.acid_agent=None
            self.ui.phAdjustMessageLabel.setText("<p>Vous devez d'abord créer un profil d'eau dans l'onglet « Ajustement du profil d'eau »</p>")
            self.ui.phAdjustMessageLabel.setStyleSheet("color:red")
            self.ui.spargeAdjustMessageLabel.setText('')
            
      
        
              

    #-----------------------------------------------------------------------------------
    def pH_adjuster_ready(self):  
        self.ui.phAdjustMessageLabel.setText('')
        message=''
        if not self.diph_documented() :
            message+="<p>Vous devez documenter le DI pH et la capacité tampon de tous les malts</p>"
        
        if self.pH_target  is None:
            message += "<p>Vous devz choisir une cible de pH pour l'empâtage</p>"
        if  self.ui.acidAgentCombo.currentText()=='':
            message += "<p>Vous devez choisir un agent d'acidification ci-dessus</p>"
        self.ui.phAdjustMessageLabel.setText(message) 
        self.ui.phAdjustMessageLabel.setStyleSheet("color:red")
        if message !='':
            return False
        return True

    #-----------------------------------------------------------------------------------
    def diph_documented(self):
        #check that DI pH and buffering capacity are documented for all mashable fermentables
      
        for it in self.diph_items:
            if it.item.diph is None:
                return False    
            elif it.item.buffering_capacity is None: 
                return False
        return True

    #-----------------------------------------------------------------------------------   
    def init_diph(self):
        #create the diph items 
        self.diph_items=[]
        for item in self.parent.fermentable_selector.destination_model.items:
            
            if (item.usage =='empâtage'):
                it=DiphItemWidget(item,self)
                self.diph_layout.addWidget(it)
                self.diph_items.append(it)
        self.scroll_content.setLayout(self.diph_layout) 
        self.diph_layout.setSpacing(2)   
            
        self.ui.groupboxMaltsDiph.setWidget(self.scroll_content)
        
        
          

        
    #-------------------------------------------------------------------------------------------------------
    def clean(self):
        #empty the diph_layout
        l=self.diph_layout
        children=[]
        for i in range(l.count()):
            item = l.itemAt(i).widget()
            if item:
                children.append(item)
        for child in children:
            child.deleteLater()

    #-------------------------------------------------------------------------------------------------------
    def clean_and_reset(self):
        self.clean()
        self.init_diph() 
    #-------------------------------------------------------------------------------------------------------    
    def percentDissociation(self,pH_target,pKa):
            return 1 - (1 / (1 + 10 ** (pH_target - pKa)))

    def acid_strength(self,acid,pH_target):
        acid_mass_per_volume_unit=acid.concentration *acid.density #g of pure acid per ml
        molarity = acid_mass_per_volume_unit *1000 /acid.mole_weight #moles/l or mmoles/ml (presume full dissociation)
        normality=molarity * acid.valence #mEq/ml
        k_dissociation=0
        for i in range(acid.valence):
            k_dissociation = k_dissociation + self.percentDissociation(pH_target,acid.pKa[i])
        k_dissociation =k_dissociation /acid.valence
        strength= normality * k_dissociation #mEq/ml
        return strength
        

   
    def charge_at_pH(self,pH):
        #6.38 is pK1 for acid carbonique H2CO3
        #base_vs_acid is the ratio of conjugated base vs remaining undissociated acid
        base_vs_acid =10 **(pH-6.38)
        #see percentage of dissociation of acid depending on pH
        return (base_vs_acid /(base_vs_acid +1))
    
    def ZAlkalinity(self,alkalinity,titration_pH,pH_target):
        #see theory in Water book of Palmer and Kaminski page 95
        #titration_pH is the pH of water at which alkalinity is given(end point around 4.3)
        #alkalinity in ppm of HCO3- not as CaCO3
        mEq_per_liter=alkalinity /61 # in mEq/L divisor would be 50 if alka given as CaCO3
        Ct=mEq_per_liter /(self.charge_at_pH(titration_pH)-0.01) #mmole/L
        ZAlka=(self.charge_at_pH(titration_pH)-self.charge_at_pH(pH_target))*Ct
        return ZAlka
 
    def water_mEq_contribution(self,pH_target):
        #return a positive value in mEq
        ZAlka=self.ZAlkalinity(self.parent.waterAdjustmentDialog.adjusted_water.alca,self.parent.waterAdjustmentDialog.mixed_water.pH,pH_target)
        return ZAlka * self.parent.mash_water_mass
    
    def select_sparge_water(self):
        water_name=self.parent.waterAdjustmentDialog.water_for_sparge
        water=None
        match water_name:
            case "Eau de base":
                water=self.parent.waterAdjustmentDialog.base_water
            case "Eau de dilution":
                water= self.parent.waterAdjustmentDialog.dilution_water 
            case "Eau mélangée brute" :
                 water= self.parent.waterAdjustmentDialog.mixed_water
            case "Eau mélangée ajustée":
                water= self.parent.waterAdjustmentDialog.adjusted_water
        return water
    
    def sparge_water_mEq_contribution(self,pH_target):
        
        water=self.select_sparge_water()
        ZAlka=self.ZAlkalinity(water.alca,water.pH,pH_target)
        return ZAlka * self.parent.sparge_water_mass

    def CaMg_mEq_contribution(self):
        #negative contribution in mEq
        water= self.parent.waterAdjustmentDialog.adjusted_water
        #20 and 12.1 stand respectively for Ca molecular weight an Mg molecular weight
        return (-(water.ca /20)*self.parent.mash_water_mass/3.5 - (water.mg /12.1)*self.parent.mash_water_mass /7) #mEq
    
    def sparge_CaMg_mEq_contribution(self):
        #negative contribution in mEq
        water= self.select_sparge_water()
        #20 and 12.1 stand respectively for Ca molecular weight an Mg molecular weight
        return (-(water.ca /20)*self.parent.mash_water_mass/3.5 - (water.mg /12.1)*self.parent.mash_water_mass /7) #mEq
       
    def grist_mEq_contribution(self,pH_target):
        grist_contribution=0
        for it in self.diph_items:
            it_contribution= it.item.buffering_capacity * it.item.quantity * (it.item.diph - pH_target)
            if it.item.fermentable.category == "acidulated":
                it_contribution=it_contribution +290 * it.item.quantity
            grist_contribution += it_contribution
        return grist_contribution   

    def mEq_before_acid_additions(self,pH_target):
        mEq=\
            self.water_mEq_contribution(pH_target)\
            +self.CaMg_mEq_contribution()\
            +self.grist_mEq_contribution(pH_target)
        
        return mEq
    
    def sparge_mEq_before_acid_additions(self,pH_target):
        mEq=\
            self.sparge_water_mEq_contribution(pH_target)\
            +self.sparge_CaMg_mEq_contribution()
        
        return mEq

    def pH_before_acid_additions(self):
        old_mEq=0
        pH=5.4 #a starting value for pH
        mEq=self.mEq_before_acid_additions(pH)
        max_pH=6.3
        min_pH=3
        zalka=None
        cpt=0
        while (abs(mEq-old_mEq)>0.01) and cpt<120:
            old_mEq=mEq
            mEq=self.mEq_before_acid_additions(pH)+1
            if mEq>0.01:
                #still too much alkalinity
                min_pH=pH
                pH=(pH +max_pH)/2
            else:
                if mEq<0.01:
                    #not enough alkalinity
                    max_pH=pH
                    pH=(min_pH+pH)/2  
            cpt+=1  

        self.ui.phBeforeEdit.setText(str(round(pH,2)))
        return pH
    
    def required_mash_acid_volume(self,pH_target):
        mEq_before_acid_base_addition=self.mEq_before_acid_additions(pH_target)
        if mEq_before_acid_base_addition >=0:
            acid=get_acid_by_name(self.ui.acidAgentCombo.currentText())
            required_volume= mEq_before_acid_base_addition/self.acid_strength(acid,self.pH_target)
            required_volume_1N=required_volume*acid.k_1N
            message="<p> L'empâtage nécessite <strong>" +str(round(required_volume,2))+" ml </strong> d'acide « "+str(self.ui.acidAgentCombo.currentText())+ " » pour atteindre le pH cible.</p>"
            message+="<p>ou encore  <strong>"+str(round(required_volume_1N,2))+ " ml </strong>de la dilution 1M de cet acide.</p>"
            self.ui.phAdjustMessageLabel.setText(message)
            self.ui.phAdjustMessageLabel.setStyleSheet("color: #148F77")
            return required_volume

    def required_sparge_acid_volume(self,pH_target): 
        message="<p>L'eau de rinçage choisie est "+self.parent.waterAdjustmentDialog.water_for_sparge+'</p>'
        mEq_before_acid_base_addition=self.sparge_mEq_before_acid_additions(pH_target)
        if mEq_before_acid_base_addition >=0:
            acid=get_acid_by_name(self.ui.acidAgentCombo.currentText())
            required_volume=mEq_before_acid_base_addition /self.acid_strength(acid,pH_target)
            required_volume_1N=required_volume*acid.k_1N
            message+="<p>Ramener le pH de l'eau de rinçage en dessous de 6 pH nécessite "+str(round(required_volume,2))+" ml d'acide« "+str(self.ui.acidAgentCombo.currentText())+" »</p>"
            message+="<p>ou encore  <strong>"+str(round(required_volume_1N,2))+ " ml </strong>de la dilution 1M de cet acide.</p>"
           
        else:
            required_volume=0
            message+="<p>Vous n'avez pas besoin d'acide pour l'eau de rinçage."     
            
        self.ui.spargeAdjustMessageLabel.setText(message)
        self.ui.spargeAdjustMessageLabel.setStyleSheet("color: #148F77")
        return required_volume
