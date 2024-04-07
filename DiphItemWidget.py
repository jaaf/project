'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from DiphItemWidgetBase import Ui_Form as diphItem
from PyQt6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QLineEdit,QLabel,QListView
from PyQt6 import QtCore
from PyQt6.QtCore import Qt,QRegularExpression,QTimer,QModelIndex
from database.fermentables.fermentable_brand import all_fbrand, find_fbrand_by_name

from SignalObject import SignalObject


class DiphItemWidget(QWidget):
    def __init__(self, item,parent=None):
        #context may be recipe, brew or inventory
        super().__init__(parent) 
        self.parent=parent 
        self.item=item
        self.ui =diphItem()
        self.ui.setupUi(self)
        self.complete_ui()
        self.set_connections()
        

    def set_connections(self):
        self.ui.diphEdit.textChanged.connect(self.set_diph)  
        self.ui.capacityEdit.textChanged.connect(self.set_buffering_capacity) 
        self.ui.pushButton.clicked.connect(self.preload_diph_and_capa) 

    def set_diph(self):
        print('setting item diph')
        try:
            self.item.diph=float(self.ui.diphEdit.text())
        except:
            self.item.diph=None    
        #print(self.item)
        self.parent.parent.fermentable_selector.update_fermentable() 
        self.parent.communicator.signal_change.emit(SignalObject('diph',self))


    def set_buffering_capacity(self):
        print('setting item buff_capa')
        try:
            self.item.buffering_capacity=float(self.ui.capacityEdit.text())
        except:
            self.item.buffering_capacity=None
        self.parent.communicator.signal_change.emit(SignalObject('buffering_capacity',self))

    def preload_diph_and_capa(self):
        print('in preload_diph_and_capa')
        s_diph=self.suggested_diph(self.item.fermentable)
        print(str(s_diph))
        if s_diph is not None:
            self.ui. diphEdit.setText(str(round(s_diph,2)))    
        else:
            self.ui.diphEdit.setText('')     
        s_capa=self.suggested_capacity(self.item.fermentable)  
        if s_capa is not None:
            self.ui.capacityEdit.setText(str(round(s_capa,0)))
        else:
            self.ui.capacityEdit.setText('')    
        self.parent.communicator.signal_change.emit(SignalObject('buffering_capacity',self))

    def complete_ui(self):
        self.ui.nameLabel.setText(str(self.item.fermentable.name))
        #capacity
        s_capa=self.suggested_capacity(self.item.fermentable)
        if s_capa is not None:
            self.ui.capacitySuggestedLabel.setText(str(round(s_capa,0))+' mEq/pH.kg')
        else:
             self.ui.capacitySuggestedLabel.setText('??'+' mEq/pH.kg')
        if self.item.buffering_capacity is not None:
            self.ui.capacityEdit.setText(str(round(self.item.buffering_capacity,2)))
        else:
            self.ui.capacityEdit.setText('')  
        #diph
        s_diph=self.suggested_diph(self.item.fermentable)
        if s_diph is not None:
            self.ui.diphSuggestedLabel.setText(str(round(s_diph,2))+' pH')
        else:
            self.ui.diphSuggestedLabel.setText('?? pH')  
        if self.item.diph is not None:
            self.ui.diphEdit.setText(str(round(self.item.diph,2)))
        else:
            self.ui.diphEdit.setText('')    

       
    def suggested_capacity(self,fermentable):
        match (fermentable.form):
            case 'Grain malté':
                return self.Buffering_capacity(fermentable)
            case 'Flocons':
                return self.Buffering_capacity(fermentable)
            
    def suggested_diph(self,fermentable) :
        #return the diph suggested for this item  
        match(fermentable.form):
            case 'Grain malté':
                return self.MaltDIpH(fermentable)
            case 'Flocons'  :
                return self.Buffering_capacity(fermentable) 

    def find_cat(self,malt):
        cat=''
        match (malt.category):
            case "Base":
                cat = "base"
            case "Base (Pilsner|Lager)":
                cat = "base"
            case "Base (Pale)":
                cat = "base"
            case "Base (Pale Ale)":
                cat = "base"
            case "Base (Blé)":
                cat = "wheat"
            case "Base (Sègle)":
                cat = "base"
            case "Base (Fumé)":
                cat = "base"
            case "Acidulated":
                cat = "base"
            case "Vienne":
                cat = "vienna"
            case "Munich":
                cat = "base"
            case "Arômatique":
                cat = "ccd" #brewer's friend says speciality
             
            case "Amber|Biscuit|Victory":
                cat = "ccd" #brewers's friens says roasted
             
            case "Brown Malt":
                cat = "roasted"
            case "Caramel|Crystal":
                cat = "ccd"
            case "Dextrin Malt":
                cat = "ccd"
            case "Honey Malt":
                cat * "ccd" #Brewfather = Brewers's friend
            
            case "Pale Chocolate":
                cat = "roasted"
            case "Chocolate":
                cat = "roasted"
            case "Malt noir désamérisé":
                cat = "roasted"
            case "Malt de blé noir":
                cat = "roasted"
            case "Orge rôtie":
                cat = "roasted"
            case "Avoine rôtie":
                cat = "roasted"
            case "Sègle rôti":
                cat = "roasted"
            case "Malt noir":
                cat = "roasted"
        
        return cat
    
    def  MaltDIpH(self,malt):
        cat=self.find_cat(malt)
        col = (malt.color / 1.97 + 0.6) / 1.35
        match (cat) :
            case "base":
                return 5.82 - 0.0465 * col 
            case "ccd":
                return 5.57 - 0.023 * col
            case 'munich': 
                return 5.57#not used
            case 'wheat':
                return 6.04

            case "vienna":
                return 5.69
            case "bab":
                return 5.14
            case "honey":
                return 4.94
            case "aromatic":
                return 5.39
            case "roasted":
                return 4.32
            case "acidulated":
                return None
            
        return None
        
    def Buffering_capacity(self,malt):
        cat=self.find_cat(malt)
        
        col = (malt.color / 1.97 + 0.6) / 1.35
        match (cat):
            case "base":
                return 32 #idem BrewFather
            case "ccd":
                return 32
            case 'munich': 
                return  53.7 #not used
            case 'wheat':
                return 32

            case "vienna":
                return 52.3 #not used
            case "bab":
                return 39.1#not used 
            case "honey":
                return  62.6 #not used
            case "aromatic":
                return 55.1#not used
            case "roasted":
                return 32
            case "acidulated":
                
                return None #not used idem base
           
        return None
        
    def  FlakeDIpH(fermentable):
        match (fermentable.raw_ingredient):
            case "barley":
                return 5.65
            case "wheat":
                return 6.57
            case "spelt":
                return None
            case "oat":
                return 6.21
            case "rye":
                return 6.65
            case "rice":
                return None
            case "corn":
                return 6.24
        return None
    
    def  FlakeCapacity(fermentable):
        match (fermentable.raw_ingredient):
            case "barley":
                return 32
            case "wheat":
                return 32
            case "spelt":
                return None
            case "oat":
                return 32
            case "rye":
                return 32
            case "rice":
                return None
            case "corn":
                return 32
        return None