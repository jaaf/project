'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from SelectorWidgetBase import Ui_Selector as selself
from PyQt6.QtWidgets import QWidget,QCheckBox,QGroupBox,QPushButton,QHBoxLayout,QVBoxLayout,QLineEdit,QLabel
from PyQt6 import QtCore
from PyQt6.QtCore import Qt,QRegularExpression
from database.fermentables.fermentable_brand import all_fbrand, find_fbrand_by_name
from database.fermentables.fermentable import all_fermentable
from database.yeasts.yeast import all_ybrand
from database.yeasts.yeast import all_yeast
from database.hops.hop import all_hop
from database.miscs.misc import all_misc

from parameters import yeast_target,yeast_form

from BrewUtils import BrewUtils
from PyQt6 import QtGui
from database.hops.hop_suppliers import all_hsupplier
import re
from database.profiles.rest import Rest
from PyQt6.QtGui import QRegularExpressionValidator,QPalette
from SignalObject import SignalObject
from MyQListView import MyQListView
from parameters import  raw_ingredients, fermentable_categories
from parameters import  raw_ingredients,  hop_forms,hop_purposes

from RecipeFermentable import RecipeFermentable
from RecipeHop import RecipeHop
from RecipeYeast import RecipeYeast
from RecipeMisc import RecipeMisc
from HelpMessage import HelpMessage
from CheckableComboBox import CheckableComboBox,MyStandardItem
from pathlib import Path

class SelectorWidget(QWidget):
    def __init__(self, source_list,destination_list,what,context,parent=None):
        #context may be recipe, brew or inventory
        super().__init__(parent) 
        self.parent=parent 
        self.ui =selself()
        self.ui.setupUi(self)
        self.destination_list=destination_list
        self.source_list=source_list
        self.what=what
        self.context=context
        self.this_file_path=Path(__file__).parent
       
        self.source_selection=None
        self.destination_selection=None
        #for filters-------------------
        match self.what:
            case "fermentable":
                self.active_brands=[]
                self.active_categories=[]
                self.active_ingredients=[]
            case "hop":
                self.active_suppliers=[]
                self.active_forms=[]
                self.active_purposes=[]   
            case "yeast":
                self.active_brands=[]
                self.active_forms=[]
                self.active_targets=[]
            case "misc":
                pass

        #---------------------------------
     
    
        self.ui.fermentableControlGroupBox.setStyleSheet('color:black; background-color: white;')
        self.ui.hopControlGroupBox.setStyleSheet('color:black; background-color: white;')
        self.ui.yeastControlGroupBox.setStyleSheet('color:black; background-color: white;')
        self.ui.miscControlGroupBox.setStyleSheet('color:black; background-color: white;')
        self.ui.restControlGroupBox.setStyleSheet('color:black; background-color: white;')

        if what!='rest':
            self.ui.temperatureTransitionGroupbox.setVisible(False)

        self.ui.titleGroupBox.setStyleSheet('color:black; background-color:white;')
        
        match self.what:
            case 'fermentable':
                self.source_model=SourceModel(what='fermentable',items=self.source_list)
                self.ui.hopControlGroupBox.setVisible(False)
                self.ui.yeastControlGroupBox.setVisible(False)
                self.ui.miscControlGroupBox.setVisible(False)
                self.ui.restControlGroupBox.setVisible(False)

                self.hide_steeping_controls()
                self.ui.fermentableUsageLabel.setText('Usage')
                self.ui.fermentableUsageCombo.addItem('')
                self.ui.fermentableUsageCombo.addItem("empâtage") 
                self.ui.fermentableUsageCombo.addItem("trempage")
                self.ui.fermentableUsageCombo.addItem("ébullition")
               
            
            case 'hop':
                self.source_model=SourceModel(what='hop',items=self.source_list)    
                self.ui.fermentableControlGroupBox.setVisible(False)
                self.ui.yeastControlGroupBox.setVisible(False)
                self.ui.miscControlGroupBox.setVisible(False)
                self.ui.restControlGroupBox.setVisible(False)
                

                #self.ui.hopUsageLabel.setText('Houblonnage')
                self.ui.hopUsageCombo.addItem('')
                self.ui.hopUsageCombo.addItem("à l'empâtage") 
                self.ui.hopUsageCombo.addItem("au premier moût")
                self.ui.hopUsageCombo.addItem("à l'ébullition")
                self.ui.hopUsageCombo.addItem("hors flamme")
                self.ui.hopUsageCombo.addItem("au fermenteur")
                 
            case 'yeast':
                self.source_model=SourceModel(what='yeast',items=self.source_list)
                self.ui.fermentableControlGroupBox.setVisible(False)
                self.ui.hopControlGroupBox.setVisible(False)
                self.ui.miscControlGroupBox.setVisible(False)
                self.ui.restControlGroupBox.setVisible(False)

                self.ui.yeastPitchingRateUnitLabel.setVisible(True)
             
            case 'misc':
                self.source_model=SourceModel(what='misc',items=self.source_list)  
                self.ui.fermentableControlGroupBox.setVisible(False)
                self.ui.hopControlGroupBox.setVisible(False)
                self.ui.yeastControlGroupBox.setVisible(False)
                self.ui.restControlGroupBox.setVisible(False)
          
            case 'rest':
                self.source_model=SourceModel(what='rest',items=self.source_list)  
                self.ui.fermentableControlGroupBox.setVisible(False)
                self.ui.hopControlGroupBox.setVisible(False)
                self.ui.yeastControlGroupBox.setVisible(False)
                self.ui.miscControlGroupBox.setVisible(False)
                self.ui.temperatureMethodCombo.addItem('','')
                self.ui.temperatureMethodCombo.addItem('Chauffage','Heating')
                self.ui.temperatureMethodCombo.addItem('Infusion','Infusion')
                self.ui.temperatureMethodCombo.addItem('Décoction','Decoction')
                if self.context=='recipe':
                    self.hide_temperature_transition_control_group()
                    self.ui.thicknessReferenceCheckbox.setVisible(False)
                if self.context=='brew':
                    self.ui.grainTemperatureEdit.setText(str(self.parent.grain_temperature))
                    self.ui.additionsTemperatureEdit.setText(str(self.parent.additions_temperature))
                    self.ui.temperatureMethodCombo.setCurrentText(self.parent.temperature_method)
                self.ui.restHelpButton.setStyleSheet('background-color:green; color:White')
                self.ui.restHelpButton.setToolTip("Obtenir de l'information sur les paliers d'empâtage")    

        #we use a derived class of QListView to take into account a click elsewhere than on an item
        self.destinationList=MyQListView(name='destination')
        self.destinationLayout=QVBoxLayout()
        self.destinationControlLayout=QHBoxLayout()

        self.destinationLayout.addWidget(self.destinationList)
        self.destinationLayout.addLayout(self.destinationControlLayout)
        
        ##self.ui.horizontalLayout_6.addWidget(self.destinationList)
        self.ui.groupBox_left.setLayout(self.destinationLayout)
        
        self.sourceList=MyQListView(name='source')
        self.sourceLayout=QVBoxLayout()
   
        self.add_filters( self.what)
        self.sourceLayout.addWidget(self.sourceList)
        self.sourceLayout.addWidget(self.filterGroupbox)
        #self.filterGroupbox.setLayout(self.filterLayout)
        ##self.ui.horizontalLayout_6.addLayout(self.sourceLayout)
        self.ui.groupBox_right.setLayout(self.sourceLayout)
        #self.ui.horizontalLayout_6.addWidget(self.ui.sourceList)
        self.sourceList.setModel(self.source_model)
        self.sourceList.setSpacing(6)
        self.ui.importButton.setVisible(False)
        #hide buttons
        self.ui.deleteButton.setVisible(False)
        self.ui.importButton.setText('Non actif')
        #self.ui.groupBox_left.setStyleSheet('background-color:red;color: white;')
        #complete GUI
        match self.what:
            case 'fermentable':
                self.destination_model=DestinationModel(what='fermentable',context=context,items=self.destination_list)
                if(context == 'recipe'):
                    self.ui.fermentableUnitHelpButton.setText('?')
                    self.ui.fermentableUnitHelpButton.setStyleSheet('background-color:green;color:white;')
                else:
                    self.ui.fermentableUnitHelpButton.setVisible(False)    
            case 'hop':
                self.destination_model=DestinationModel(what='hop',context=context,items=self.destination_list)
                self.hide_non_permanent_hop_controls()
                self.ui.looseHelpButton.setText('?')
                self.ui.looseHelpButton.setStyleSheet('background-color:green;color:white;')
                self.ui.multiplicatorButton.setText('?')
                self.ui.multiplicatorButton.setStyleSheet('background-color:green;color:white;')  
                self.ui.hopStandHelpButton.setText('?')
                self.ui.hopStandHelpButton.setStyleSheet('background-color:green;color:white;')
                self.ui.multiplicatorButton.setVisible(False)
            case 'yeast':
                self.destination_model=DestinationModel(what='yeast',context=context,bw=self.parent,items=self.destination_list)
            case 'misc':
                self.destination_model=DestinationModel(what='misc',context=context,items=self.destination_list)  
            case 'rest':
                self.ui.calculationHelpButton.setText('?')
                self.ui.calculationHelpButton.setStyleSheet('background-color:green;color:white;')
                self.ui.calculationHelpButton.setToolTip("Get help on the way the various water additions are calculated")
                self.destination_model=DestinationModel(what='rest',context=context,bw=self.parent,items=self.destination_list)      
            
        self.destinationList.setModel(self.destination_model)
        self.destinationList.setSpacing(6)
        self.sourceList.setVisible(False)
        self.toggle_tab_view()
        self.ui.restTemperatureEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,2}[\\.][0-9]{1,2}")))
        self.ui.fermentableQuantityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}([\\.][0-9]{3}){0,1}")))
        self.ui.hopQuantityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}\\.][0-9]{1,2}")))
        self.ui.hopMinutesEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}")))
        self.ui.miscQuantityEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}([\\.][0-9]{3}){0,1}")))
        self.ui.miscReferenceVolumeEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}([\\.][0-9]{0,2}){0,1}")))

     
        self.ui.restDurationEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}")))

        self.sourceList.setStyleSheet("QListView{border: 2px solid green;}"\
                                         "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                            "QListView::item{border-bottom:2px solid gray}")
        self.destinationList.setStyleSheet("QListView{border: 2px solid green;}"\
                                            "QListView::item:selected{border: 3px solid red;color:blue;background-color:white}"\
                                                "QListView::item{border-bottom:2px solid gray}")

        
        #set connections
        self.set_connections()
        
            
        for what in ['fermentable_quantity','fermentable_usage','fermentable_steeping','hop_quantity','hop_usage','hop_utilisation','hop_multiplicator','hop_days','hop_hours','hop_minutes',\
        'yeast_quantity','yeast_reference_volume','misc_quantity','misc_reference_volume','rest_temperature','rest_duration']:
            self.clean_edit(what)
    #-----------------------------------------------------------------------------------------------------------
    def remove_all_fermentables(self):
        print("remove all called")
        self.destination_model.items=[]
        self.destination_model.layoutChanged.emit()

    def receive_signal(self,obj):
        print('signal received '+obj.name)
    def set_connections(self):

        match self.what:
            case 'fermentable':
                self.brandFilterCombo.closedPopup.connect(self.on_brand_closedPopup)
                self.brand_checkbox.stateChanged.connect(self.toggle_brand_filter)
                self.categoryFilterCombo.closedPopup.connect(self.on_category_closedPopup)
                self.category_checkbox.stateChanged.connect(self.toggle_category_filter)
                self.ingredientFilterCombo.closedPopup.connect(self.on_ingredient_closedPopup)
                self.ingredient_checkbox.stateChanged.connect(self.toggle_ingredient_filter)
                self.searchEdit.editingFinished.connect(self.search_in_name)
                self.searchHelpButton.clicked.connect(lambda: self.show_contextual_help('filter_f')) 
                
            case "hop":
                self.supplierFilterCombo.closedPopup.connect(self.on_supplier_closedPopup)
                self.supplier_checkbox.stateChanged.connect(self.toggle_supplier_filter)
                self.formFilterCombo.closedPopup.connect(self.on_form_closedPopup)
                self.form_checkbox.stateChanged.connect(self.toggle_form_filter)
                self.purposeFilterCombo.closedPopup.connect(self.on_purpose_closedPopup)
                self.purpose_checkbox.stateChanged.connect(self.toggle_purpose_filter)
                self.yearSearchEdit.editingFinished.connect(self.search_year)
                self.searchEdit.editingFinished.connect(self.search_in_name)    
                self.searchHelpButton.clicked.connect(lambda: self.show_contextual_help('filter_h'))        
            case "yeast": 
                self.brandFilterCombo.closedPopup.connect(self.on_brand_closedPopup)
                self.brand_checkbox.stateChanged.connect(self.toggle_brand_filter)
                self.formFilterCombo.closedPopup.connect(self.on_form_closedPopup)
                self.form_checkbox.stateChanged.connect(self.toggle_form_filter)
                self.targetFilterCombo.closedPopup.connect(self.on_target_closedPopup)
                self.target_checkbox.stateChanged.connect(self.toggle_target_filter)
                self.searchEdit.editingFinished.connect(self.search_in_name)        
                self.searchHelpButton.clicked.connect(lambda: self.show_contextual_help('filter'))
            #nothing for misc
            case 'rest':
                self.ui.temperatureMethodCombo.currentTextChanged.connect(self.temperature_method_changed)
                self.ui.additionsTemperatureEdit.textChanged.connect(self.additions_temperature_changed)
                self.ui.grainTemperatureEdit.textChanged.connect(self.grain_temperature_changed)
                self.ui.restHelpButton.clicked.connect(lambda:self.show_contextual_help('rest'))

        self.sourceList.clicked.connect(self.select_source)
        self.sourceList.mysignal.connect(self.on_mysignal)
        	
        self.destinationList.clicked.connect(self.select_destination)
        self.destinationList.mysignal.connect(self.on_mysignal)

        self.ui.importButton.clicked.connect(self.apply_prepared_operation)
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.fermentableQuantityEdit.textChanged.connect(lambda: self.clean_edit('fermentable_quantity') )
        self.ui.fermentableUsageCombo.currentTextChanged.connect(lambda: self.clean_edit('fermentable_usage'))
        self.ui.fermentableSteepingEdit.textChanged.connect(lambda : self.clean_edit('fermentable_steep'))
        self.ui.fermentableUsageCombo.currentTextChanged.connect(self.toggle_steeping_controls)

        self.ui.hopQuantityEdit.textChanged.connect(lambda: self.clean_edit('hop_quantity'))
        self.ui.hopUsageCombo.currentTextChanged.connect(lambda: self.clean_edit('hop_usage'))
        self.ui.hopUtilisationEdit.textChanged.connect(lambda: self.clean_edit('hop_utilisation'))
        self.ui.hopMultiplicatorEdit.textChanged.connect(lambda: self.clean_edit('hop_multiplicator'))
        self.ui.hopDaysEdit.textChanged.connect(lambda: self.clean_edit('hop_days'))
        self.ui.hopHoursEdit.textChanged.connect(lambda: self.clean_edit('hop_hours'))
        self.ui.hopMinutesEdit.textChanged.connect(lambda: self.clean_edit('hop_minutes'))
        self.ui.hopTemperatureEdit.textChanged.connect(lambda : self.clean_edit('hop_temperature'))
        self.ui.pitchingRateSpinBox.valueChanged.connect(lambda: self.clean_edit('yeast_pitching_rate'))
     

        self.ui.hopUsageCombo.currentTextChanged.connect(self.adapt_hop_control_view)

        self.ui.pitchingRateSpinBox.valueChanged.connect(lambda: self.clean_edit('yeast_quantity'))
        #self.ui.yeastReferencVolumeEdit.textChanged.connect(lambda :self.clean_edit('yeast_reference_volume'))

        self.ui.miscQuantityEdit.textChanged.connect(lambda: self.clean_edit('misc_quantity'))
        self.ui.miscReferenceVolumeEdit.textChanged.connect(lambda :self.clean_edit('misc_reference_volume'))

        self.ui.restTemperatureEdit.textChanged.connect(lambda :self.clean_edit('rest_temperature'))
        self.ui.restDurationEdit.textChanged.connect(lambda :self.clean_edit('rest_duration'))
        
        self.ui.toggleViewButton.clicked.connect(self.toggle_tab_view)
        self.ui.steepYieldHelpButton.clicked.connect(lambda: self.show_contextual_help('steep_yield'))    
        self.ui.fermentableUnitHelpButton.clicked.connect(lambda: self.show_contextual_help('fermentable_unit'))
        self.ui.looseHelpButton.clicked.connect(lambda: self.show_contextual_help('loose_hop'))
        self.ui.hopStandHelpButton.clicked.connect(lambda : self.show_contextual_help('hop_stand'))
        self.ui.multiplicatorButton.clicked.connect(lambda: self.show_contextual_help('multiplicator'))
        self.ui.calculationHelpButton.clicked.connect(lambda: self.show_contextual_help('water_additions'))

    #-----------------------------------------------------------------
    def add_filters(self,what):
        self.filterGroupbox=QGroupBox()
        self.filterLayout=QHBoxLayout()
        #self.filterGroupbox.setFixedHeight(100)
        match what:
            case "fermentable":
                self.fermentableFilterLayout=QHBoxLayout()
                self.brandLayout=QVBoxLayout()
                self.brandFilterCombo=CheckableComboBox()       
                self.brands=all_fbrand()
                for brand in self.brands:
                    item = MyStandardItem(brand.name)
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.brandFilterCombo.model().appendRow(item) 
                self.brand_checkbox=QCheckBox('Filtrer les marques')
                self.brandLayout.addWidget(self.brand_checkbox)
                self.brandLayout.addWidget(self.brandFilterCombo)
                self.fermentableFilterLayout.addLayout(self.brandLayout)
                self.brandFilterCombo.setVisible(False)
                

                self.categoryLayout=QVBoxLayout()
                self.categoryFilterCombo=CheckableComboBox()       
                self.categories=fermentable_categories
                for category in self.categories:
                    item = MyStandardItem(category)
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.categoryFilterCombo.model().appendRow(item)     
                self.category_checkbox=QCheckBox('Filtrer les catégories')
                self.categoryLayout.addWidget(self.category_checkbox)
                self.categoryLayout.addWidget(self.categoryFilterCombo)
                self.fermentableFilterLayout.addLayout(self.categoryLayout)
                self.categoryFilterCombo.setVisible(False)

                self.ingredientLayout=QVBoxLayout()
                self.ingredientFilterCombo=CheckableComboBox()       
                self.ingredients=raw_ingredients#import from parameters
                for ingredient in self.ingredients:
                    item = MyStandardItem(ingredient)
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.ingredientFilterCombo.model().appendRow(item)   
                self.ingredient_checkbox=   QCheckBox('Filtrer les ingrédients')   
                self.ingredientLayout.addWidget(self.ingredient_checkbox)
                self.ingredientLayout.addWidget(self.ingredientFilterCombo)
                self.fermentableFilterLayout.addLayout(self.ingredientLayout)
                self.ingredientFilterCombo.setVisible(False)

                self.searchEdit=QLineEdit()
                self.searchEdit.setPlaceholderText('🔍Entrée en fin de saisie')
                self.fermentableFilterLayout.addWidget(self.searchEdit)

                #self.fermentableFilterLayout.addStretch()
                #self.ui.filterGroupBox.setLayout(self.fermentableFilterLayout)
                self.filterLayout.addLayout(self.fermentableFilterLayout)
            case "hop":
                #suppliers
                self.hopFilterLayout=QHBoxLayout()
                self.supplierLayout=QVBoxLayout()
                self.supplierFilterCombo=CheckableComboBox()       
                self.suppliers=all_hsupplier()
                for supplier in self.suppliers:
                    item = MyStandardItem(supplier.name)
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.supplierFilterCombo.model().appendRow(item) 
                self.supplier_checkbox=QCheckBox('Filtrer fournisseurs')
                self.supplierLayout.addWidget(self.supplier_checkbox)
                self.supplierLayout.addWidget(self.supplierFilterCombo)
                self.hopFilterLayout.addLayout(self.supplierLayout)
                self.supplierFilterCombo.setVisible(False)
                #forms
                self.formLayout=QVBoxLayout()
                self.formFilterCombo=CheckableComboBox()       
                self.forms=hop_forms
                for form in self.forms:
                    item = MyStandardItem(form[1],form[0])
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.formFilterCombo.model().appendRow(item)     
                self.form_checkbox=QCheckBox('Filtrer les formes')
                self.formLayout.addWidget(self.form_checkbox)
                self.formLayout.addWidget(self.formFilterCombo)
                self.hopFilterLayout.addLayout(self.formLayout)
                self.formFilterCombo.setVisible(False)
                #purpose
                self.purposeLayout=QVBoxLayout()
                self.purposeFilterCombo=CheckableComboBox()       
                self.purposes=hop_purposes#import from parameters
                for purpose in self.purposes:
                    item = MyStandardItem(purpose[1],purpose[0])
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.purposeFilterCombo.model().appendRow(item)   
                self.purpose_checkbox=   QCheckBox('Filtrer les buts')   
                self.purposeLayout.addWidget(self.purpose_checkbox)
                self.purposeLayout.addWidget(self.purposeFilterCombo)
                self.hopFilterLayout.addLayout(self.purposeLayout)
                self.purposeFilterCombo.setVisible(False)
                #year
                self.yearLayout=QVBoxLayout()
                self.yearSearchLabel=QLabel('Année')
                self.yearSearchLabel.setFixedWidth(60)
                self.yearSearchEdit=QLineEdit()
                self.yearSearchEdit.setFixedWidth(60)
                self.yearSearchEdit.setPlaceholderText('? ')
                self.yearLayout.addWidget(self.yearSearchLabel)
                self.yearLayout.addWidget(self.yearSearchEdit)
                self.hopFilterLayout.addLayout(self.yearLayout)

                #search
                self.nameLayout=QVBoxLayout()
                self.nameSearchLabel=QLabel('Chercher dans nom')
                self.searchEdit=QLineEdit()
                self.searchEdit.setPlaceholderText('? ')
                self.nameLayout.addWidget(self.nameSearchLabel)
                self.nameLayout.addWidget(self.searchEdit)
                self.hopFilterLayout.addLayout(self.nameLayout)               

                #self.fermentableFilterLayout.addStretch()
                #self.ui.filterGroupBox.setLayout(self.fermentableFilterLayout)
                self.filterLayout.addLayout(self.hopFilterLayout)
            case "yeast":
                self.yeastFilterLayout=QHBoxLayout()
                #brands
                self.brandLayout=QVBoxLayout()
                self.brandFilterCombo=CheckableComboBox()       
                self.brands=all_ybrand()
                for brand in self.brands:
                    item = MyStandardItem(brand.name)
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.brandFilterCombo.model().appendRow(item) 
                self.brand_checkbox=QCheckBox('Filtrer les marques')
                self.brandLayout.addWidget(self.brand_checkbox)
                self.brandLayout.addWidget(self.brandFilterCombo)
                self.yeastFilterLayout.addLayout(self.brandLayout)
                self.brandFilterCombo.setVisible(False)
                
                #forms
                self.formLayout=QVBoxLayout()
                self.formFilterCombo=CheckableComboBox()       
                self.forms=yeast_form
                for form in self.forms:
                    item = MyStandardItem(form)
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.formFilterCombo.model().appendRow(item)     
                self.form_checkbox=QCheckBox('Filtrer les formes')
                self.formLayout.addWidget(self.form_checkbox)
                self.formLayout.addWidget(self.formFilterCombo)
                self.yeastFilterLayout.addLayout(self.formLayout)
                self.formFilterCombo.setVisible(False)
                #target
                self.targetLayout=QVBoxLayout()
                self.targetFilterCombo=CheckableComboBox()       
                self.targets=yeast_target#import from parameters
                for target in self.targets:
                    item = MyStandardItem(target)
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.targetFilterCombo.model().appendRow(item)   
                self.target_checkbox=   QCheckBox('Filtrer les cibles')   
                self.targetLayout.addWidget(self.target_checkbox)
                self.targetLayout.addWidget(self.targetFilterCombo)
                self.yeastFilterLayout.addLayout(self.targetLayout)
                self.targetFilterCombo.setVisible(False)

                self.searchEdit=QLineEdit()
                self.searchEdit.setPlaceholderText('🔍Entrée en fin de saisie')
                self.yeastFilterLayout.addWidget(self.searchEdit)
                self.filterLayout.addLayout(self.yeastFilterLayout)
        

                #self.yeastFilterLayout.addStretch()
               
            case "misc":
                self.miscFilterLayout=QHBoxLayout()
                self.searchEdit=QLineEdit()
                self.searchEdit.setPlaceholderText('🔍Entrée en fin de saisie')

                self.miscFilterLayout.addWidget(self.searchEdit)
                self.filterLayout.addLayout(self.miscFilterLayout)

        self.searchHelpButton=QPushButton('?')
        self.searchHelpButton.setFixedWidth(24)
        self.searchHelpButton.setStyleSheet('background-color:green; color:White')
        self.searchHelpButton.setToolTip("Obtenir de l'aide sur le filtrage et la recherche")
        self.filterLayout.addWidget(self.searchHelpButton)  
        self.filterGroupbox.setLayout(self.filterLayout)
      
        self.filterGroupbox.setStyleSheet("background-color:#D5F5E3")
               

       
    #-------------------------------------------------------------------------
    @QtCore.pyqtSlot()
    def on_brand_closedPopup(self):
        self.active_brands=self.brandFilterCombo.checkedItems()
        self.filter_list()  
    #----------------------------------------------
    def toggle_brand_filter(self):
        if self.brand_checkbox.isChecked():
            self.brandFilterCombo.setVisible(True)
        else:
            self.brandFilterCombo.setVisible(False)
            
        self.filter_list()
    #---------------------------------------------
    @QtCore.pyqtSlot()
    def on_category_closedPopup(self):
        self.active_categories=self.categoryFilterCombo.checkedItems()
        self.filter_list()       
    
    #----------------------------------------------
    def toggle_category_filter(self):
        if self.category_checkbox.isChecked():
            self.categoryFilterCombo.setVisible(True)
        else:
            self.categoryFilterCombo.setVisible(False)
        
        self.filter_list()
        
    #---------------------------------------------
    @QtCore.pyqtSlot()
    def on_ingredient_closedPopup(self):
        self.active_ingredients=self.ingredientFilterCombo.checkedItems()
        self.filter_list()       
    
    #----------------------------------------------
    def toggle_ingredient_filter(self):
        if self.ingredient_checkbox.isChecked():
            self.ingredientFilterCombo.setVisible(True)
        else:
            self.ingredientFilterCombo.setVisible(False)

        self.filter_list()
    #---------------------------------------------------------------------------
    QtCore.pyqtSlot()
    def on_supplier_closedPopup(self):
        self.active_suppliers=self.supplierFilterCombo.checkedItems()
        self.filter_list()
    #----------------------------------------------
    def toggle_supplier_filter(self):
        if self.supplier_checkbox.isChecked():
            self.supplierFilterCombo.setVisible(True)
        else:
            self.supplierFilterCombo.setVisible(False)
            
        self.filter_list()

    #---------------------------------------------------------------------------
    QtCore.pyqtSlot()
    def on_form_closedPopup(self):
        self.active_forms=self.formFilterCombo.checkedItems()
        self.filter_list()
    #----------------------------------------------
    def toggle_form_filter(self):
        if self.form_checkbox.isChecked():
            self.formFilterCombo.setVisible(True)
        else:
            self.formFilterCombo.setVisible(False)
            
        self.filter_list()
     
    #---------------------------------------------------------------------------
    QtCore.pyqtSlot()
    def on_purpose_closedPopup(self):
        self.active_purposes=self.purposeFilterCombo.checkedItems()
        self.filter_list()
    #----------------------------------------------    
    def toggle_purpose_filter(self):
        if self.purpose_checkbox.isChecked():
            self.purposeFilterCombo.setVisible(True)
        else:
            self.purposeFilterCombo.setVisible(False)
            
        self.filter_list()     
    
    @QtCore.pyqtSlot()
    def on_brand_closedPopup(self):
        self.active_brands=self.brandFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.filter_list()  
    #----------------------------------------------
    def toggle_brand_filter(self):
        if self.brand_checkbox.isChecked():
            self.brandFilterCombo.setVisible(True)
        else:
            self.brandFilterCombo.setVisible(False)
            
        self.filter_list()
    #---------------------------------------------
    @QtCore.pyqtSlot()
    def on_form_closedPopup(self):
        self.active_forms=self.categoryFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.filter_list()       
    
    #----------------------------------------------
    def toggle_form_filter(self):
        if self.form_checkbox.isChecked():
            self.formFilterCombo.setVisible(True)
        else:
            self.formFilterCombo.setVisible(False)
        
        self.filter_list()
        
    #---------------------------------------------
    @QtCore.pyqtSlot()
    def on_target_closedPopup(self):
        self.active_targets=self.targetFilterCombo.checkedItems()
        self.searchEdit.setText('')
        self.filter_list()       
  
    #----------------------------------------------
    def toggle_target_filter(self):
        if self.target_checkbox.isChecked():
            self.targetFilterCombo.setVisible(True)
        else:
            self.targetFilterCombo.setVisible(False)

        self.filter_list()
          
    #-----------------------------------------------------------------------------------------------
    def refresh_source(self):
        match self.what:
            case "fermentable":
                self.source_list=all_fermentable()
                self.source_list.sort(key=lambda x: (x.brand,x.name,x.version))
            case "hop":
                self.source_list=all_hop()
                self.source_list.sort(key=lambda x: (x.supplier,x.name,x.crop_year))

            case "yeast":
                self.source_list=all_yeast()
                self.source_list.sort(key=lambda x: (x.target,x.brand,x.name))
            case "misc":
                self.source_list=all_misc()

        self.source_model.items=self.source_list
        self.source_model.layoutChanged.emit()  


    #----------------------------------------------------------------------------------------------
    def filter_list(self):
        items=self.source_list
        filtered=None
        match self.what:
            case "fermentable":
                filtered=list(filter(lambda x:\
                                        (x.brand in self.active_brands or not self.brand_checkbox.isChecked()) and \
                                            (x.category in self.active_categories or not self.category_checkbox.isChecked()) and \
                                                (x.raw_ingredient in self.active_ingredients or not self.ingredient_checkbox.isChecked())\
                                                    ,items ))
                
                filtered.sort(key=lambda x: (x.brand,x.name,x.version))
            case "hop":
                filtered=list(filter(lambda x:\
                    (x.supplier in self.active_suppliers or not self.supplier_checkbox.isChecked()) and \
                        (x.form in self.active_forms or not self.form_checkbox.isChecked()) and \
                            (x.purpose in self.active_purposes or not self.purpose_checkbox.isChecked())\
                                ,items))
                filtered.sort(key=lambda x: (x.supplier,x.name,x.crop_year))
            case "yeast":
                filtered=list(filter(lambda x:\
                            (x.brand in self.active_brands or not self.brand_checkbox.isChecked()) and \
                            (x.form in self.active_forms or not self.form_checkbox.isChecked()) and \
                                (x.target in self.active_targets or not self.target_checkbox.isChecked())\
                                    ,items ))

                filtered.sort(key=lambda x: (x.target,x.brand,x.name))

        self.source_model.items=filtered 
        self.source_model.layoutChanged.emit()  
    #------------------------------------------------------------------------------------------------
    def search_in_name(self):
        self.filter_list()#we start with the filtered list
        pattern=self.searchEdit.text()
        if pattern != '':
            items=self.source_model.items #we search only in the filtered list
            sorted_array=list(filter(lambda x: re.search(pattern, x.name,re.IGNORECASE),items)) 
            self.source_model.items=sorted_array
            self.source_model.layoutChanged.emit()
    #----------------------------------------------------------------------------------------------
    def search_year(self):
        self.searchEdit.setText('')
        self.filter_list()#we start with the filtered list
        pattern=self.yearSearchEdit.text()
        if pattern != '':
            items=self.source_model.items #we search only in the filtered list
            sorted_array=list(filter(lambda x: re.search(pattern, x.crop_year,re.IGNORECASE),items)) 
            self.source_model.items=sorted_array
            self.source_model.layoutChanged.emit()
       
    #------------------------------------------------------------------

    
    def show_contextual_help(self,what):
        filename=(self.this_file_path/"help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
        helpPopup=HelpMessage()  

        match what:
            case 'filter_f':
                helpPopup.set_title('À propos du filtrage et de la recherche')
              

                filename=(self.this_file_path/"help/FermentableSearchHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
            case 'filter_h':
                helpPopup.set_title('À propos du filtrage et de la recherche')
                filename=(self.this_file_path/"help/HopSearchHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)            
            case 'steep_yield':
                helpPopup.set_title('À propos du rendement au trempage')
                filename=(self.this_file_path/"help/SteepYieldHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
            case 'fermentable_unit':
                helpPopup.set_title ("Pourquoi l'absence d'unité de masse de fermentable")
                filename=(self.this_file_path/"help/FermentableUnitHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
            case 'loose_hop':
                helpPopup.set_title("À quoi sert l'indicateur en vrac ?")    
                filename=(self.this_file_path/"help/LooseHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
            case 'multiplicator':
                helpPopup.set_title('Le multiplicateur')
                filename=(self.this_file_path/"help/Multiplicator.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
            case 'hop_stand':
                helpPopup.set_title('Le houblonnage Hors Flamme')
                filename=(self.this_file_path/"help/Hopstand.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
            case "water_additions":
                helpPopup.set_title("Calcul des additions d'eau et de leur température")
                filename=(self.this_file_path/"help/WaterAdditions.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
            case "rest":
                helpPopup.set_title("Information sur les paliers d'empâtage")
                filename=(self.this_file_path/"help/Rests.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)  
        helpPopup.exec()

    #------------------------------------------------------------------------
    def on_mysignal(self,obj):
        #this signal is emitted from a custom class that allow to take into account a click elsewhere than on an item
        #in that way, we can call self.select_destination for clearing the selection
        match obj.value:
            case 'source':
                indexes=self.sourceList.selectedIndexes()
                if indexes:   
                    self.select_source()
                else:
                    pass   
            case 'destination':
                indexes=self.destinationList.selectedIndexes()
                if indexes:   
                    self.select_destination()
                else:
                    pass                
    #------------------------------------------------------------------------
    def additions_temperature_changed(self):
        try:
            self.parent.additions_temperature=round(float(self.ui.additionsTemperatureEdit.text()),1)
        except:
            self.parent.additions_temperature=None    
            
        self.destination_model.layoutChanged.emit()
        self.signal_changes()
    #-------------------------------------------------------------------------
    def grain_temperature_changed(self):
        try:
            self.parent.grain_temperature=float(self.ui.grainTemperatureEdit.text())
        except:
            self.parent.grain_temperature=None
        self.destination_model.layoutChanged.emit()
        self.signal_changes()

    def temperature_method_changed(self):
        self.parent.temperature_method = self.ui.temperatureMethodCombo.currentText()
        if self.what =='rest' and self.parent.temperature_method =='Chauffage':
            for item in self.destination_model.items:
                pass#item.thickness_reference=False
            self.ui.thicknessReferenceCheckbox.setVisible(False)    
              
        else:
            self.ui.thicknessReferenceCheckbox.setVisible(True)  
        
        self.destination_model.layoutChanged.emit()
        self.signal_changes()      
    #-------------------------------------------------------------------------
    def hide_non_permanent_hop_controls(self):
        self.ui.hopMultiplicatorEdit.setVisible(False)
        self.ui.multiplicatorButton.setVisible(False)
        self.ui.hopMultiplicatorLabel.setVisible(False)
        self.ui.hopUtilisationEdit.setVisible(False)
        self.ui.hopUtilisationLabel.setVisible(False) 
        self.ui.hopDaysEdit.setVisible(False)
        self.ui.hopDaysLabel.setVisible(False) 
        self.ui.hopHoursEdit.setVisible(False)
        self.ui.hopHoursLabel.setVisible(False) 
        self.ui.hopMinutesEdit.setVisible(False)
        self.ui.hopTemperatureEdit.setVisible(False)
        self.ui.hopTemperatureLabel.setVisible(False)
        self.ui.hopMinutesLabel.setVisible(False)
        self.ui.hopDurationLabel.setVisible(False)
    #-------------------------------------------------------------------------
    def adapt_hop_control_view(self):
        self.hide_non_permanent_hop_controls()
        self.ui.looseCheckBox.setVisible(True)
        self.ui.looseHelpButton.setVisible(True)
        match self.ui.hopUsageCombo.currentText():  
                
            case "à l'empâtage":
                self.ui.hopMultiplicatorEdit.setVisible(True)
                self.ui.hopMultiplicatorLabel.setVisible(True)
                self.ui.multiplicatorButton.setVisible(True)
                self.ui.looseCheckBox.setVisible(False)
                self.ui.looseHelpButton.setVisible(False)
                self.ui.hopStandHelpButton.setVisible(False)
                self.ui.hopTemperatureLabel.setVisible(False)
            case "au premier moût"  :
                self.ui.hopMultiplicatorEdit.setVisible(True)
                self.ui.hopMultiplicatorLabel.setVisible(True)
                self.ui.multiplicatorButton.setVisible(True)
                self.ui.hopTemperatureLabel.setVisible(False) 
                self.ui.hopStandHelpButton.setVisible(False)
            case "à l'ébullition":
                self.ui.hopDurationLabel.setVisible(True)
                self.ui.hopMinutesEdit.setVisible(True)
                self.ui.hopMinutesLabel.setVisible(True)
                self.ui.hopTemperatureLabel.setVisible(False) 
                self.ui.hopStandHelpButton.setVisible(False)
            case "hors flamme":
                self.ui.hopTemperatureLabel.setVisible(True)
                self.ui.hopTemperatureEdit.setVisible(True)
                self.ui.hopDurationLabel.setVisible(True)
                self.ui.hopMinutesLabel.setVisible(True)
                self.ui.hopMinutesEdit.setVisible(True) 
                self.ui.hopStandHelpButton.setVisible(True)
              
            case "au fermenteur":
                self.ui.hopDurationLabel.setVisible(True)
                self.ui.hopDaysEdit.setVisible(True)
                self.ui.hopDaysLabel.setVisible(True)
                self.ui.hopHoursEdit.setVisible(True)
                self.ui.hopHoursLabel.setVisible(True)
                self.ui.hopUtilisationEdit.setVisible(True)
                self.ui.hopUtilisationLabel.setVisible(True) 
                self.ui.hopStandHelpButton.setVisible(False)
    #-------------------------------------------------------------------------
    def toggle_steeping_controls(self):
        val=self.ui.fermentableUsageCombo.currentText()
        if val == 'trempage':
            self.show_steeping_controls()
            return
        if val == '' or val == 'empâtage' or val== 'ébullition':
            self.hide_steeping_controls()
  
    def show_steeping_controls(self):
        self.ui.steepYieldHelpButton.setText('?')
        self.ui.steepYieldHelpButton.setStyleSheet('background-color:green;color:white;')
        self.ui.steepYieldHelpButton.setVisible(True)
        self.ui.fermentableSteepingLabel.setVisible(True)
        self.ui.fermentableSteepingEdit.setVisible(True)
        self.ui.fermentableSteepingUnitLabel.setVisible(True)
        self.ui.fermentableSteepingEdit.setToolTip("Il s'agit du rendement au trempage.Les valeurs, toujours inférieures à celle de l'empâtage, varient significativement selon les types de malt et la pratique.\
         Renseignez-vous pour la valeur à utiliser en fonction du type de malt, de la température et de la durée.")
    
    #-------------------------------------------------------------------------
    def hide_steeping_controls(self):
        self.ui.steepYieldHelpButton.setVisible(False)
        self.ui.fermentableSteepingLabel.setVisible(False)
        self.ui.fermentableSteepingEdit.setVisible(False)
        self.ui.fermentableSteepingUnitLabel.setVisible(False)
        

    #-------------------------------------------------------------------
    def toggle_tab_view(self):
        if(self.sourceList.isVisible()):
            
            #self.searchEdit.setVisible(False)
            #self.searchEdit.setVisible(False)
            #self.searchLabel.setVisible(False)
            self.ui.toggleViewButton.setText('Montrer le sélecteur')
            self.sourceList.setVisible(False)
            self.filterGroupbox.setVisible(False)
        else:
               
            #self.searchEdit.setVisible(True)
            #self.searchLabel.setVisible(True)  
            self.ui.toggleViewButton.setText('Cacher le sélecteur')
            self.sourceList.setVisible(True) 
            self.filterGroupbox.setVisible(True)
    #-------------------------------------------------------------------------
    def hide_source_list(self):
        #contrarily to toggle_tab_view hide the selector whatever the visibility of it
        self.ui.toggleViewButton.setText('Montrer le sélecteur')
        self.sourceList.setVisible(False)
        self.filterGroupbox.setVisible(False)
        self.ui.toggleViewButton.setVisible(False)
    #---------------------------------------------------------------------------
    def prepare_form_for_add(self):
        #prepare the form for additional values when adding an item from source list to destination list
        self.ui.importButton.setText('Ajouter à la recette')
        self.ui.importButton.setVisible(True)

        self.ui.deleteButton.setVisible(False)
        self.ui.controlGroupBox.setVisible(True)
        match self.what:
            case'fermentable':
                #self.show_fermentable_control_group()
                
                self.ui.fermentableQuantityEdit.setText('')  
                self.ui.fermentableUsageCombo.setCurrentText('')
            case 'hop':
                #self.show_hop_control_group()
                self.ui.hopQuantityEdit.setText('')
                self.ui.hopUsageCombo.setCurrentText('') 
                self.ui.hopUtilisationEdit.setText('')
                self.ui.hopMultiplicatorEdit.setText('')
                self.ui.hopDaysEdit.setText('')
                self.ui.hopHoursEdit.setText('')
                self.ui.hopMinutesEdit.setText('')
                self.ui.hopTemperatureEdit.setText('')  
                self.ui.looseCheckBox.setChecked(False)
            case 'misc':
                self.ui.miscQuantityEdit.setText('')  
                self.ui.miscReferenceVolumeEdit.setText('')
                self.ui.miscMassUnitLabel.setText(self.source_selection.unit)
                self.ui.miscUsageEdit.setText('')
            case 'yeast':
                self.ui.pitchingRateSpinBox.setValue(0)
                #self.ui.yeastReferencVolumeEdit.setText('')
                self.ui.yeastPitchingRateUnitLabel.setText('10⁹ cel./litre/plato')                       
            case 'rest' :
                self.ui.restDurationEdit.setText(str(self.source_selection.duration))
                self.ui.restTemperatureEdit.setText(str(self.source_selection.temperature)) 
                self.ui.thicknessReferenceCheckbox.setChecked(False)

    #-----------------------------------------------------------------------------------------
    def prepare_form_for_update(self):
        #prepare the form of additional values for update in the destination liste
        self.ui.importButton.setText('Mettre à jour')
        self.ui.importButton.setVisible(True)
        self.ui.deleteButton.setVisible(True)
        self.ui.controlGroupBox.setVisible(True)

        match self.what:
            case 'fermentable':
                #self.show_fermentable_control_group()
                
                self.ui.fermentableQuantityEdit.setText(str(round(self.destination_selection.quantity,3)))
                self.ui.fermentableUsageCombo.setCurrentText(self.destination_selection.usage)
                self.ui.fermentableSteepingEdit.setText(str(round(self.destination_selection.steep_potential)))
            case 'hop':
                #self.show_hop_control_group()
                self.ui.hopQuantityEdit.setText(str(round(self.destination_selection.quantity,0)))
                usage=self.destination_selection.usage
                self.ui.hopUsageCombo.setCurrentText(usage)
                match usage:
                    case "à l'empâtage":
                        self.ui.hopUtilisationEdit.setText(str(self.destination_selection.utilisation))
                    case "au premier moût":
                        self.ui.hopMultiplicatorEdit.setText(str(self.destination_selection.multiplicator))
                    case "à l'ébullition":
                        self.ui.hopMinutesEdit.setText(str(self.destination_selection.minutes))    
                    case "hors flamme":
                        
                        self.ui.hopTemperatureEdit.setText(str(self.destination_selection.temperature))  
                        self.ui.hopMinutesEdit.setText(str(self.destination_selection.minutes))      
                              
                self.ui.looseCheckBox.setChecked(self.destination_selection.loose)                
            case 'misc':
                self.ui.miscQuantityEdit.setText(str(self.destination_selection.quantity))
                self.ui.miscReferenceVolumeEdit.setText(str(self.destination_selection.reference_volume))
                self.ui.miscUsageEdit.setText(self.destination_selection.usage)
                self.ui.miscMassUnitLabel.setText(self.destination_selection.misc.unit)
            case 'yeast':
                self.ui.pitchingRateSpinBox.setValue(self.destination_selection.quantity)
                #self.ui.yeastReferencVolumeEdit.setText(str(self.destination_selection.reference_volume))
                self.ui.yeastPitchingRateUnitLabel.setText('10⁹ cel./litre/plato') 
            case 'rest':
                self.ui.restDurationEdit.setText(str(self.destination_selection.duration))
                self.ui.restTemperatureEdit.setText(str(self.destination_selection.temperature))
                self.ui.thicknessReferenceCheckbox.setVisible(True)
                if self.destination_selection.thickness_reference is not None:
                    self.ui.thicknessReferenceCheckbox.setChecked(self.destination_selection.thickness_reference)
     

    #-------------------------------------------------------------------------------------------
    def prepare_form_for_replace(self):
        self.ui.importButton.setText('Remplacer')
        self.ui.importButton.setVisible(True)
        self.ui.deleteButton.setVisible(False)
        self.ui.controlGroupBox.setVisible(True)
        match self.what:
            case  'fermentable':
                #self.show_fermentable_control_group()
                
                self.ui.fermentableQuantityEdit.setText(str(round(self.destination_selection.quantity,3)))
                self.ui.fermentableUsageCombo.setCurrentText(self.destination_selection.usage)

            case  'hop':
                #self.show_hop_control_group()
                self.ui.hopQuantityEdit.setText(str(round(self.destination_selection.quantity,0)))
                self.ui.hopUsageCombo.setCurrentText(self.destination_selection.usage)
                match self.ui.hopUsageCombo.currentText():
                    case "à l'empâtage":
                        self.ui.hopUtilisationEdit.setText(str(self.destination_selection.utilisation))
                    case "au premier moût":
                        self.ui.hopMultiplicatorEdit.setText(str(self.destination_selection.multiplicator))  
                        self.ui.looseCheckBox.setChecked(self.destination_selection.loose)
                    case "à l'ébullition":
                        self.ui.hopMinutesEdit.setText(str(self.destination_selection.minutes)) 
                        self.ui.looseCheckBox.setChecked(self.destination_selection.loose)
                    case "hors flamme":
                        
                        self.ui.hopTemperatureEdit.setText(str(self.destination_selection.temperature))
                        self.ui.hopMinutesEdit.setText(str(self.destination_selection.minutes))        
                    case "au fermenteur":
                        self.ui.hopDaysEdit.setText(str(self.destination_selection.days))
                        self.ui.hopHoursEdit.setText(str(self.destination.selection.hours))
                        self.ui.looseCheckBox.setChecked(self.destination_selection.loose)

            case 'misc':
                self.ui.miscQuantityEdit.setText(str(self.destination_selection.quantity))
                self.ui.miscReferenceVolumeEdit.setText(str(self.destination_selection.reference_volume))
                self.ui.miscUsageEdit.setText(self.destination_selection.usage)
                self.ui.miscMassUnitLabel.setText(self.destination_selection.misc.unit)

            case 'yeast':
                self.ui.pitchingRateSpinBox.setValue(float(self.destination_selection.quantity))
                #self.ui.yeastReferencVolumeEdit.setText(str(self.destination_selection.reference_volume))
                self.ui.yeastPitchingRateUnitLabel.setText('10⁹ cel./litre/plato') 

            case 'rest':
                self.ui.restDurationEdit.setText(str(self.destination_selection.duration))
                self.ui.restTemperatureEdit.setText(str(self.destination_selection.temperature))
                if(self.what =='misc'):
                    self.ui.miscMassUnitLabel.setText(self.destination_selection.misc.unit)
                if(self.what == 'yeast'):
                    self.ui.miscMassUnitLabel.setText('10⁹ cellules')   
                if self.destination_selection.thickness_reference is not None:
                    self.ui.thicknessReferenceCheckbox.setChecked(self.destination_selection.thickness_reference)

           
    #------------------------------------------------------------------------------------------------------
    def select_destination(self):
        #select an element in the destination list either for deletion, or update, or replacement
        old_selection=self.destination_selection
        indexes = self.destinationList.selectedIndexes()
        if indexes:
            index=indexes[0]
            self.destination_selection=self.destination_model.items[index.row()]
            if (old_selection==self.destination_selection):  
                self.clear_selection('destination')
        else:
            self.clear_selection('destination') 
            self.reset_form()
        self.adapt_form()    

    #------------------------------------------------------------------------------------------   
    def select_source(self):
        #select an item in the source list for addition to the destination list
        old_selection=self.source_selection
        indexes =self.sourceList.selectedIndexes()
        if indexes:
            index=indexes[0]
            self.source_selection=self.source_model.items[index.row()]
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
                self.sourceList.clearSelection() 
                #self.reset_form()
                #to delete the inverted highlight background on the last selected item
                self.sourceList.clearFocus()
            case 'destination':
                self.destination_selection=None
                self.destinationList.clearSelection()
                self.reset_form()
                #to delete the inverted highlight background on the last selected item
                self.destinationList.clearFocus()
            case 'both':
                self.destinationList.clearSelection()
                self.destination_selection=None  
                self.destinationList.clearFocus()
                self.sourceList.clearSelection() 
                self.source_selection=None
                self.sourceList.clearFocus()
        self.adapt_form()  
    #------------------------------------------------------------------------------------------------------
    def hide_all_controls(self):
        self.ui.controlGroupBox.setVisible(False)
        self.ui.commonControlGroupBox.setVisible(False)

    #-----------------------------------------------------------------------------------------
    def hide_temperature_transition_control_group(self):
        self.ui.temperatureTransitionGroupbox.setVisible(False)  

    #----------------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------------------
    def adapt_form(self):
        #adapt the form for additional values depending on the operation to perform
        if(self.source_selection and self.destination_selection):
            self.prepare_form_for_replace()
        if(self.source_selection and not(self.destination_selection)):
            self.prepare_form_for_add()
        if(not self.source_selection and self.destination_selection):
            self.prepare_form_for_update()
        self.ui.commonControlGroupBox.setVisible(True)
        self.ui.controlGroupBox.setVisible(True)
        if( not self.source_selection and not self.destination_selection):
            #self.hide_all_controls()
            self.ui.controlGroupBox.setVisible(False)
            self.ui.commonControlGroupBox.setVisible(False)
            #self.ui.importButton.setVisible(False)
            #self.ui.deleteButton.setVisible(False)  


    #---------------------------------------------------------------------------------------------
    def reset_form(self):
        #some controls may be hidden as a consequence of some of the statements here
        self.clean_all_quantities()
        match self.what:
            case 'fermentable':
                self.ui.fermentableUsageCombo.setCurrentText('')
                self.ui.fermentableSteepingEdit.setText('')
            case 'hop':
                self.ui.hopUsageCombo.setCurrentText('')    
            case 'yeast':
                pass
                #self.ui.yeastReferencVolumeEdit.setText('')
            case 'misc':
                self.ui.miscReferenceVolumeEdit.setText('')  
                self.ui.miscUsageEdit.setText('') 
            case 'rest':
                self.ui.restTemperatureEdit.setText('')
                self.ui.restDurationEdit.setText('')
    #-----------------------------------------------------------------------------------------
    def delete(self):
        if(self.destination_selection):
            self.destination_model.items.remove(self.destination_selection)
            self.destination_model.layoutChanged.emit()   
            self.destination_selection=None
            self.reset_form()
            self.signal_changes()


    #--------------------------------------------------------------------------
    def signal_changes(self):
        #each time an operation such as add , update, etc is applied this function sends a signal 
        #that will be use to launch the calculation in the BrewWidget
        if(self.context =='brew'):
                match self.what:
                    case 'fermentable':
                        self.parent.c.calculate.emit(SignalObject('fermentable',self.destination_model.items))
                    case 'hop':
                           
                        self.parent.c.calculate.emit(SignalObject('hop',self.destination_model.items)) 
                    case 'yeast':
                        pass

                    case 'rest':
                        self.parent.c.calculate.emit(SignalObject('rest',None))    

        if self.context=='recipe':
            match self.what:
                case 'fermentable':
                    self.parent.c.calculate.emit(SignalObject('fermentable',None))
                case 'yeast':
                    self.parent.c.calculate.emit(SignalObject('yeast',None))              
    #---------------------------------------------------------------------------
    def apply_prepared_operation(self):  
        #ADD OPERATION
        if(self.source_selection and not self.destination_selection):
            result=self.add()
            if result ==True:
                print('result of adding rest was true')
                if(self.what == 'rest'):
                    self.destination_model.items.sort(key=lambda x: float(x.temperature)) 
                self.clear_selection('both')
                self.signal_changes()
            return
  
        #UPDATE OPERATION
        if(self.destination_selection and not self.source_selection):
            self.update()
            if(self.what == 'rest'):
                self.destination_model.items.sort(key=lambda x: float(x.temperature)) 
            self.clear_selection('both')
            self.signal_changes()  
                     
            return  

        #REPLACE OPERATION
        if(self.source_selection and self.destination_selection):
            if self.what== 'fermentable' and not self.check_usage_compatibility():
                return 
            self.destination_model.items.remove(self.destination_selection) 
            self.add()
            if(self.what == 'rest'):
                self.destination_model.items.sort(key=lambda x: float(x.temperature))
            self.destination_model.layoutChanged.emit()
            self.clear_selection('both')
            self.signal_changes()
            self.reset_form()             
            return

    #------------------------------------------------------------------------------------------------
    def check_usage_compatibility(self):
        source=self.source_selection
        destination=self.destination_selection
        combo=self.ui.fermentableUsageCombo
        if source :
            #we are adding a new fermentable or exchanging it
            if (source.form =='Extrait liquide' or source.form=='Extrait sec' or source.form=='Sucre') and combo.currentText() != "ébullition":  
                self.parent.set_message('failure', "L'usage pour un extrait ou un sucre doit être 'ébullition' ") 
                return False  
            if (source.form !='Extrait liquide' and source.form !='Extrait sec' and source.form!='Sucre') and combo.currentText() == "ébullition":      
                self.parent.set_message('failure', "L'usage 'ébullition' est réservé aux extraits et aux sucres. Choisissez 'trempage' ou 'empâtage' ") 
                return False
            if ((source.category.startswith("Base") or source.category.startswith("Munich") or source.category.startswith("Vienne")) and  (combo.currentText() =="trempage"  or combo.currentText()=="ébullition")):
                self.parent.set_message('failure',"Un malt de cette catégorie ne doit être ni trempé ni bouilli mais empâté.")
                return False
            if (combo.currentText()=="empâtage" and self.parent.ui.typeCombo.currentText()=="Extraits"):
                self.parent.set_message("failure","Vous ne pouvez empâter des malts dans une recette de type Extraits.")
                return False
            
        if (destination and not source)   :
            #we are modifying an already selected fermentable
            if (destination.fermentable.form =='Extrait liquide' or destination.fermentable.form=='Extrait sec' or destination.fermentable.form =='Sucre') and combo.currentText() != "ébullition":  
                self.parent.set_message('failure', "L'usage pour un extrait ou un sucre doit être 'ébullition' ") 
                return False  
            if (destination.fermentable.form !='Extrait liquide' and destination.fermentable.form !='Extrait sec' and destination.fermentable.form !='Sucre') and combo.currentText() == "ébullition":      
                self.parent.set_message('failure', "L'usage 'ébullition' est réservé aux extraits et aux sucres. Choisissez 'trempage' ou 'empâtage' ") 
                return False
            if ((destination.fermentable.category.startswith("Base") or destination.fermentable.category.startswith("Munich") or destination.fermentable.category.startswith("Vienne")) and  (combo.currentText() =="trempage"  or combo.currentText()=="ébullition")):
                self.parent.set_message('failure',"Un malt de cette catégorie ne doit être ni trempé ni bouilli mais empâté.")
                return False
        return True            
    #-------------------------------------------------------------------------------------------------    
    def add_fermentable (self):
        if (not self.check_usage_compatibility()):
            return False
        try:
            quantity=float(self.ui.fermentableQuantityEdit.text())
            
            usage=self.ui.fermentableUsageCombo.currentText()
            if(usage == 'trempage'):
                try:
                    steep_potential=float(self.ui.fermentableSteepingEdit.text())
                except:
                    steep_potential=float(0) 
            else: steep_potential=float(0)   
            if(usage ==''):
                self.ui.fermentableUsageCombo.setStyleSheet("background-color:red; color:white")  
                return False
            if (usage == 'trempage' and ( steep_potential == 0  or  steep_potential>85 )) :
                self.ui.fermentableSteepingEdit.setStyleSheet("background-color:red; color:white")   
                return False
            #None for id, diph and buffering_capacity
            ingredient=RecipeFermentable(None,quantity,usage,steep_potential,None,None,self.source_selection)
            self.destination_model.items.append(ingredient)
        except:
            self.ui.fermentableQuantityEdit.setStyleSheet("background-color:red; color:white")
            return False

        
        self.destination_model.layoutChanged.emit()
        self.reset_form()
        return True
    #---------------------------------------------------------------------------------
    def update_fermentable(self):
        steep_potential=None
        if not self.check_usage_compatibility():
            return False
        try:
            quantity=float(self.ui.fermentableQuantityEdit.text())
                
            usage=self.ui.fermentableUsageCombo.currentText()
            if(usage == 'trempage'):
                try:
                    steep_potential=float(self.ui.fermentableSteepingEdit.text())
                except:
                    steep_potential=float(0) 
            else: steep_potential=float(0)   
            if(usage ==''):
                self.ui.fermentableUsageCombo.setStyleSheet("background-color:red; color:white")  
                return
            if (usage == 'trempage' and ( steep_potential == 0  or  steep_potential>85 )) :
                self.ui.fermentableSteepingEdit.setStyleSheet("background-color:red; color:white")   
                return False
                
            self.destination_selection.quantity=round(float(self.ui.fermentableQuantityEdit.text()),3) 
            self.destination_selection.usage=self.ui.fermentableUsageCombo.currentText()  
            self.destination_selection.steep_potential=steep_potential
            self.destination_model.layoutChanged.emit()  
            #self.parent.refresh_di_ph_items()
            self.prepare_form_for_update() #to be ready for an other update on the same item
        except:
            self.ui.fermentableQuantityEdit.setStyleSheet('background-color:red; color:white')
            return False
    #---------------------------------------------------------------------------------
    def update_all_hops(self,temperature, minutes):
        #called after updating or adding a hop to equalize temperature and minutes
        for item in self.destination_model.items:
            if item.usage=='hors flamme':
                item.temperature = temperature
                item.minutes = minutes

    def add_hop(self):
       
        #add the selected item in the source list to the destination list, with additional values 
        #from the form
        try:
            
            quantity=float(self.ui.hopQuantityEdit.text())
           
        except:
            self.ui.hopQuantityEdit.setStyleSheet("background-color:red; color:white")  
            return False
        usage=self.ui.hopUsageCombo.currentText()
        if(usage == ''):
            self.ui.hopUsageCombo.setStyleSheet("background-color:red; color:white")
            return False
        utilisation=None  
        multiplicator=None  
        temperature=None
        minutes=None
        hours=None
        days=None
        loose=False
        ibu=0
        match usage:
            case "à l'empâtage":
                try:
                    multiplicator =float(self.ui.hopMultiplicatorEdit.text())
                    
                except:
                    self.ui.hopMultiplicatorEdit.setStyleSheet("background-color:red; color:white") 
                    return False
            case "au premier moût":
                try:
                    multiplicator= float(self.ui.hopMultiplicatorEdit.text())  
                except:
                    self.ui.hopMultiplicatorEdit.setStyleSheet("background-color:red; color:white") 
                    return False
            case "à l'ébullition":
                try:
                    minutes=float(self.ui.hopMinutesEdit.text())  
                except:
                    self.ui.hopMinutesEdit.setStyleSheet("background-color:red; color:white")  
                    return   False
            case "hors flamme":
               
                try:
                    minutes=float(self.ui.hopMinutesEdit.text())     
                except:
                    self.ui.hopMinutesEdit.setStyleSheet("background-color:red; color:white")   
                    return False
                try:
                    temperature=float(self.ui.hopTemperatureEdit.text())
                except:
                    self.ui.hopTemperatureEdit.setStyleSheet("background-color:red; color:white")
                    return  False
            case "au fermenteur":
                try:
                    utilisation=float(self.ui.hopUtilisationEdit.text())
                except:
                    self.ui.hopUtilisationEdit.setStyleSheet('background-color:red; color:white')  
                    return False
                try:
                    days=float(self.ui.hopDaysEdit.text())
                    hours=float(self.ui.hopHoursEdit.text())
                except:
                    pass
                if(days == None and hours ==None)   :
                    self.ui.hopDaysEdit.setStyleSheet('background-color:red; color:white') 
                    self.ui.hopHoursEdit.setStyleSheet('background-color:red; color:white') 
                    return False
        loose=self.ui.looseCheckBox.isChecked()
        ingredient=RecipeHop(None,quantity,usage,utilisation,multiplicator,temperature,minutes,hours, days,loose,ibu,self.source_selection)
        if temperature:
            self.update_all_hops(temperature, minutes)

        self.destination_model.items.append(ingredient)
        
        self.clear_selection('source')
        self.destination_model.layoutChanged.emit()
        self.reset_form()
        return True

    #------------------------------------------------------------------------------------
    def update_hop(self):
        #os.system('clear')
        try:
            quantity=float(self.ui.hopQuantityEdit.text())
        except:
            self.ui.hopQuantityEdit.setStyleSheet('background-color:red; color:white')
            
            return
        usage=self.ui.hopUsageCombo.currentText()
        utilisation=None
        multiplicator=None
        temperature=None
        minutes=None
        hours=None
        days=None
        loose=self.ui.looseCheckBox.isChecked()
        ibu=0
        match usage:
           
            case "à l'empâtage":
                try:
                    multiplicator=float(self.ui.hopMultiplicatorEdit.text())
                except:
                    self.ui.hopMultiplicatorEdit.setStyleSheet('background-color:red; color:white')  
                    return
            case "au premier moût":
                try:
                    multiplicator=float(self.ui.hopMultiplicatorEdit.text())
                except:
                    self.ui.hopMultiplicatorEdit.setStyleSheet('background-color:red; color:white')  
                    return   
            case "à l'ébullition":
                try:
                    minutes=self.ui.hopMinutesEdit.text()
                except:
                    self.ui.hopMinutesEdit.setStyleSheet('background-color:red; color:white')  
                    return 
            case "hors flamme":

                try:
                    minutes=float(self.ui.hopMinutesEdit.text())     
                except:
                    self.ui.hopMinutesEdit.setStyleSheet("background-color:red; color:white")   
                    return
                try:
                    temperature=float(self.ui.hopTemperatureEdit.text())
                except:
                    self.ui.temperatureEdit.setStyleSheet("background-color:red; color:white")
                    return              
            case "au fermenteur":
                try:
                    utilisation=float(self.ui.hopUtilisationEdit.text())
                except:
                    self.ui.hopUtilisationEdit.setStyleSheet('background-color:red; color:white')  
                    return  
                try:
                    days=float(self.ui.hopDaysEdit.text())
                    hours=float(self.ui.hopHoursEdit.text())
                except:
                    pass
                if(days == None and hours ==None)   :
                    self.ui.hopDaysEdit.setStyleSheet('background-color:red; color:white') 
                    self.ui.hopHoursEdit.setStyleSheet('background-color:red; color:white') 
                    return

        self.destination_selection.quantity=quantity
        self.destination_selection.usage=usage
        self.destination_selection.utilisation=utilisation
        self.destination_selection.multiplicator=multiplicator
        self.destination_selection.temperature=temperature
        self.destination_selection.minutes=minutes
        self.destination_selection.hours=hours
        self.destination_selection.days
        self.destination_selection.loose=loose
        self.destination_selection.ibu=ibu
        if temperature:
            self.update_all_hops(temperature, minutes) 
        self.destination_model.layoutChanged.emit() 
        self.signal_changes()
        self.clear_selection('destination')
        self.reset_form()
                    
    #--------------------------------------------------------------------------------------
    def add_yeast (self):
        try:
            quantity=float(self.ui.pitchingRateSpinBox.value())
           
            ingredient=RecipeYeast(None,quantity,self.source_selection) 
            
            if quantity ==0:
                self.ui.pitchingRateSpinBox.setStyleSheet("background-color:red; color:white")  
                return False
        except:
            self.ui.pitchingRateSpinBox.setStyleSheet("background-color:red; color:white")  
            return False
        self.destination_model.items.append(ingredient)  
        print('clearing selection in add_yeast')   
        self.clear_selection('source')
        self.destination_model.layoutChanged.emit()
        self.reset_form()
        return True
    #-------------------------------------------------------------------------------------
    def update_yeast(self):
        try:
            quantity=float(self.ui.pitchingRateSpinBox.value())
        except:
            self.ui.pitchingRateSpinBox.setStyleSheet('background-color:red; color:white')
            return  
               
        self.destination_selection.quantity=quantity
        self.destination_model.layoutChanged.emit() 

    #--------------------------------------------------------------------------------------
    def add_misc(self):
        try:
            quantity=float(self.ui.miscQuantityEdit.text())
            usage=self.ui.miscUsageEdit.text()
        except:
            self.ui.miscQuantityEdit.setStyleSheet('background-color:red; color:white')
            return  False  
    


        try:
            reference_volume=float(self.ui.miscReferenceVolumeEdit.text())
        except:
            self.ui.miscReferenceVolumeEdit.setStyleSheet("background-color:red; color:white") 
            return False

        ingredient=RecipeMisc(None,quantity,reference_volume,usage,self.source_selection)   
        self.destination_model.items.append(ingredient)
        
        self.clear_selection('source')
        self.destination_model.layoutChanged.emit()
        self.reset_form()
        return True

    #-------------------------------------------------------------------------------------
    def update_misc(self):
        try:
            quantity=float(self.ui.miscQuantityEdit.text())
        except:
            self.ui.miscQuantityEdit.setStyleSheet('background-color:red; color:white') 
            return 
        try:
            reference_volume=  float(self.ui.miscReferenceVolumeEdit.text())
        except:
            self.ui.miscReferenceVolumeEdit.setStyleSheet('background-color:red; color:white')
            return
        self.destination_selection.reference_volume=reference_volume
        self.destination_selection.quantity=quantity
        self.destination_selection.usage=self.ui.miscUsageEdit.text()
    #--------------------------------------------------------------------------------------
    def add_rest(self):
        #rest is not an ingredient, treating differently
        validated=True
        thickness_reference=self.ui.thicknessReferenceCheckbox.isChecked()
        try:
            temperature=float(self.ui.restTemperatureEdit.text())
        except:
            self.ui.restTemperatureEdit.setStyleSheet('background-color:red; color:white')
            validated=False
        try:
            duration=float(self.ui.restDurationEdit.text())
        except:
            self.ui.restDurationEdit.setStyleSheet('background-color:red; color:white')
            validated=False
        if(validated):
            if thickness_reference:
                self.clean_other_thickness_reference('add')
            rest=Rest(self.source_selection.id,self.source_selection.name, temperature,duration,thickness_reference) 
            self.destination_model.items.append(rest)
            
        
            self.clear_selection('source')
            self.destination_model.layoutChanged.emit()
            self.reset_form()
            return True
    #----------------------------------------------------------------------------------
    def clean_other_thickness_reference(self,mode):
        #when setting thickness_reference for an item, clean others
        match mode:
            case 'update':
                for item in self.destination_model.items:
                    if item != self.destination_selection:
                        item.thickness_reference=False
            case 'add':
                for item in self.destination_model.items:
                    item.thickness_reference=False            

    #------------------------------------------------------------------------------------
    def update_rest(self):
        try:
            temperature=float(self.ui.restTemperatureEdit.text())    
        except:
            self.ui.restTemperatureEdit.setStyleSheet('background-color:red; color:white') 
            return
        try:
            duration=float(self.ui.restDurationEdit.text()  )  
        except:
            self.ui.restTemperatureEdit.setStyleSheet('background-color:red; color:white') 
            return    
        self.destination_selection.temperature=temperature
        self.destination_selection.duration=duration  
        self.destination_selection.thickness_reference=self.ui.thicknessReferenceCheckbox.isChecked() 
        if self.destination_selection.thickness_reference:
            self.clean_other_thickness_reference('update')
        

    #--------------------------------------------------------------------------------------
    def add(self):
        match self.what:
            case 'fermentable':
                result=self.add_fermentable()
            case 'hop':
                result=self.add_hop()
            case 'yeast':
                result=self.add_yeast()    
            case 'misc':
                result=self.add_misc()
            case  'rest':
                result=self.add_rest()    
        return result        

    #--------------------------------------------------------------------------------------------
    def update(self):
        #update an item in the destination list
        match self.what:
            case 'fermentable':
                result=self.update_fermentable() 
            case  'hop':
                result=self.update_hop()
            case 'yeast':
                result=self.update_yeast()    
            case 'misc':
                result=self.update_misc()      
            case 'rest':
                result=self.update_rest()
            
        self.destination_model.layoutChanged.emit()
        return result

    #---------------------------------------------------------------------------------------------
    def clean_all_quantities(self):
        self.clean_edit('fermentable_quantity')            
        self.clean_edit('hop_quantity')            
        self.clean_edit('yeast_quantity')            
        self.clean_edit('misc_quantity')
        self.ui.fermentableQuantityEdit.setText('')   
        self.ui.hopQuantityEdit.setText('')   
        self.ui.pitchingRateSpinBox.setValue(0)   
        self.ui.miscQuantityEdit.setText('')   
               
    #-----------------------------------------------------------------------------------------------   
    def clean_edit(self,what):
        #used to restore original colors after an input has been marked as missing (generally white on red)
        match what:
            case 'fermentable_quantity':
                   self.ui.fermentableQuantityEdit.setStyleSheet('background-color:white; color: black;')
            case 'fermentable_usage':
                self.ui.fermentableUsageCombo.setStyleSheet('background-color:white; color: black;')
                
            case 'fermentable_steep':
                self.ui.fermentableSteepingEdit.setStyleSheet('background-color:white; color: black;')
            case 'hop_quantity':
                   self.ui.hopQuantityEdit.setStyleSheet('background-color:white; color: black;')
            case 'hop_usage':
                self.ui.hopUsageCombo.setStyleSheet('background-color:white; color: black;')
            case 'hop_utilisation':
                self.ui.hopUtilisationEdit.setStyleSheet('background-color:white; color: black;')
            case 'hop_multiplicator':
                self.ui.hopMultiplicatorEdit.setStyleSheet('background-color:white; color: black;')
           
            case 'hop_days':
                self.ui.hopDaysEdit.setStyleSheet('background-color: white; color: black;')
            case 'hop_hours':
                self.ui.hopHoursEdit.setStyleSheet('background-color: white; color: black;')
     
                self.ui.hopMinutesEdit.setStyleSheet('background-color: white; color: black;')                
            case 'yeast_quantity':
                   self.ui.hopQuantityEdit.setStyleSheet('background-color: white; color: black;')
            case 'misc_quantity':
                   self.ui.miscQuantityEdit.setStyleSheet('background-color: white; color: black;')
            case 'misc_reference_volume':
                #self.ui.yeastReferencVolumeEdit.setStyleSheet('background-color:'+self.parent.WinBg+'; color: '+self.parent.WinFg+';')
                self.ui.miscReferenceVolumeEdit.setStyleSheet('background-color:white; color: black;')
            case 'yeast_pitching_rate':
                self.ui.pitchingRateSpinBox.setStyleSheet('background-color:white; color: black;')
            case 'rest_temperature':
                self.ui.restTemperatureEdit.setStyleSheet('background-color:white; color: black;')
            case 'rest_duration':
                self.ui.restDurationEdit.setStyleSheet('background-color:white; color: black;')
        
            
                
    #-----------------------------------------------------------------------------------------------

 ##################################################################################################
 ##################################################################################################
class SourceModel(QtCore.QAbstractListModel):
    #a model for the source QListView
    def __init__(    self, *args, what,items=None, **kwargs):
        super(SourceModel,self).__init__(*args, **kwargs)
        self.items= items or []   
        self.what=what 
        
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            item =self.items[index.row()] 
            match self.what:
                case 'fermentable':
                    
                    fname=self.str_normalize(item.name,15)
                    fbrand=self.str_normalize(str(item.brand),20)
                    #forced str conversion avoid trouble when one property is None
                    return str(item.id)+' '+str(fname)+' '+str(item.version )+' [' +str(fbrand)+' ]  '+'\n ('+str(item.form)+', '+str(item.category)+', '+str(item.color)+' EBC, '+str(item.potential)+'%, '+str(item.raw_ingredient)+')'
                case 'hop': 
                    #forced str conversion avoid trouble when one property is None
                    return str(item.id)+ ' '+str(item.name)+' '+str(item.crop_year)+' '+str(item.supplier)+'\n' +'Forme : '+str(item.form)+ ' Alpha acides : '+str(round(item.alpha,1))+' %  But : '+str(item.purpose)
                case 'yeast':
                    return 'ID : '+str(item.id)+' – '+str(item.name)+' de '+str(item.brand)+' – '+str(item.pack_unit)\
                    +'\n Forme : '+str(item.form)+ ' – Cible : '+str(item.target)+' – Att. '+str(item.attenuation)+ ' % — Floc. '+str(item.floculation)+' – Sedim. '+str(item.sedimentation)
                case 'misc':
                    #forced str conversion avoid trouble when one property is None
                    return str(item.name)    
                case 'rest':
                    #forced str conversion avoid trouble when one property is None
                    return str(item.id) + ' '+str(item.name)     

        if (role == Qt.ItemDataRole.DecorationRole):
            item=self.items[index.row()]
            match self.what:
                case 'fermentable':
                    fb=find_fbrand_by_name(str(item.brand))
                    if(fb):
                        filename='./w20/'+fb.country_code+'.png'
                        return QtGui.QImage(filename)
                    else:
                        return None    
                case 'hop':
                    filename='./w20/'+item.country_code+'.png'    
                    return QtGui.QImage(filename)

                case 'rest':
                    return ''    
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.items)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       
##################################################################################################
class DestinationModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, what,context,bw=None,items=None, **kwargs):
        super(DestinationModel,self).__init__(*args, **kwargs)
        self.items= items or [] 
        self.what=what  
        self.initialized=False
        self.context=context
        self.bw=bw # the brew widget
    def set_initialized(self,val):
        self.initialized=val      

          #--------------------------------------------------------------
    def evaluate_yeast_units(self,value,threshold):
        decimal_part=value % 1
        int_part=int(value)
        if int_part ==0:
            return 1
        else:
            if decimal_part>threshold:
                return int_part+1
            else:
                return int_part  
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            item =self.items[index.row()] 
            total=0
            if(self.what == 'fermentable' or self.what=='hop'):
                for i in self.items:
                    total+=i.quantity 
         
            match self.what:
                case 'fermentable':
                    if(total>0):
                        p=item.quantity/total*100#pourcentage
                    else:
                        p=0    
                    fname=self.str_normalize(item.fermentable.name,15)    
                    fbrand=self.str_normalize(str(item.fermentable.brand),20)
                    item.quantity_display=round(item.quantity,2)
                    item.steep_potential_display=round(item.steep_potential,2)
                    steep_info=''
                    if(item.usage == 'trempage'):
                        steep_info=' (Rend. trempage : '+str(item.steep_potential_display)+ ' %)'
                    
                    if(self.initialized ):
                        #befor initialization unit is not defined
                        return fname+' '+item.fermentable.version +' ' +fbrand + 'Rendement: '+str(item.fermentable.potential)+'   Couleur: '+str(round(item.fermentable.color,1))+' EBC \n \
                        Quantité : '+str(item.quantity_display)  +' kg — '+str(round(p,1))+' % — Usage : '+item.usage + steep_info +' — diph : '+str(item.diph)
                    else:
                         return fname+' '+item.fermentable.version +' ' +fbrand + 'Rendement: '+str(item.fermentable.potential)+' % \n \
                          Quantité : '+str(item.quantity_display)  +' — '+str(round(p,1))+' % — Usage : '+item.usage +steep_info+' — diph : '+str(item.diph)
                #-------------------------------------------------------------------------------------------------------------------
                case 'hop':
                    if(total>0):
                        p=item.quantity/total*100#pourcentage
                    else:
                        p=0    
                    hname=self.str_normalize(item.hop.name,15)
                    hsupplier=self.str_normalize(item.hop.supplier, 15)
                    hdetails=''
                    match item.usage:
                        case "à l'empâtage":
                            hdetails += ' – multiplicator : '+str(item.multiplicator)
                            if self.context=='brew':
                                hdetails += ' – '+str(round(item.ibu,1))+' ibu'
                        case  "au premier moût":
                            hdetails += ' – multiplicator : '+str(item.multiplicator)   
                            if(item.loose):
                                hdetails += ' – en vrac' 
                            if self.context == 'brew':
                                hdetails += ' – '+str(round(item.ibu,1))+' ibu'
                        case "à l'ébullition":
                            hdetails += ' – durée : '+str(item.minutes)+' min.'        
                            if(item.loose):
                                hdetails += ' – en vrac' 
                            if(self.context=='brew') :   
                                hdetails += ' – '+str(round(item.ibu,1))+' ibu'
                        case "hors flamme":
                            if(item.temperature):
                                hdetails += ' – HS température : '+str(item.temperature)+ ' – durée : '+str(item.minutes)
                            if(item.loose):
                                hdetails += ' – en vrac'   
                            if self.context == 'brew':    
                                hdetails += ' – '+str(round(item.ibu,1))+' ibu'
                    return hname + ' '+item.hop.crop_year +' '+hsupplier   + ' – alpha : '+str(round(item.hop.alpha,1)) +' – pourcentage : ' +str(round(p,1))+' %'+\
                    '\nQuantité : '+str(round(item.quantity,0))+' – Usage : '+item.usage +hdetails+" — Forme : "+item.hop.form
                
                case 'yeast':
                    try:
                        #needed_units=self.evaluate_yeast_units(item.quantity * BrewUtils.SG_to_Plato(self.bw.og)*self.bw.batch_volume/item.yeast.cells_per_pack)
                        platos=BrewUtils.SG_to_Plato(self.bw.og)
                        packs_need=item.quantity * platos * self.bw.batch_volume /item.yeast.cells_per_pack
                        #needed_units=self.evaluate_yeast_units(packs_need,0.1)
                        needed_units=round(packs_need,2)
                    except:
                        needed_units=''    

                    yname=self.str_normalize(item.yeast.name,25)   
                    return yname+' de '+item.yeast.brand+' — ID public : '+str(item.yeast.id)+' \n'\
                        +item.yeast.form+' – Att. '+str(item.yeast.attenuation)+' % – Ensemencement : '+str(round(item.quantity,2))+'  10⁹ cellules/litre/plato '\
                        +'\n Unités nécessaires : '+str(needed_units)
                
                case 'misc':
                    mname=self.str_normalize(item.misc.name,25)
                    return mname +' '+str((item.quantity)) + ' '+item.misc.unit+ ' pour '+str(item.reference_volume)+' /l usage : '+item.usage
                case 'rest':
                    water_line=''
                    thinness_segment=None

                    try:
                        thinness= item.water_mass /self.bw.total_mash_fermentable_mass
                        thinness_segment=' — Finesse maishe : '+str(round(thinness,1))+' l/kg'
                    except:
                        thinness_segment= ''
                    method=''
                    if self.context=="brew" and self.bw.temperature_method:
                        method=self.bw.temperature_method
                    match method:
                        case 'Chauffage':
                            if (index.row()==0):
                                water_line='ajouter '+str(item.addition)+" kg d'eau, soit "+str(item.addition_hot) + " litres à "+str(item.addition_temperature)+' °C '+\
                                   thinness_segment+'\n'
                            else:
                                water_line=''   
                        case 'Infusion':
                            water_line=   'ajouter '+str(item.addition)+" kg d'eau, soit "+str(item.addition_hot) + " litres à "+str(item.addition_temperature)+' °C '\
                                +thinness_segment+'\n'      

                    return item.name+' — '+str(item.temperature)+' °C / '+str(item.duration)+' min.  \n' \
                        +water_line \
                        +'---------------------------------------------------------------'
      
        if (role == Qt.ItemDataRole.DecorationRole):
            item=self.items[index.row()]
            match self.what:
                case 'fermentable':
                    
                    fb=find_fbrand_by_name(item.fermentable.brand)
                    filename='./w20/'+fb.country_code+'.png'
                    return QtGui.QImage(filename)
                case 'hop':
                    filename='./w20/'+item.hop.country_code+'.png'
                    return QtGui.QImage(filename)
                    
                case 'rest':
                    method=''
                    if self.context=="Brew" and self.bw.temperature_method:
                        method=self.bw.temperature_method
                    if method !='Chauffage':
                        if item.thickness_reference:
                            filename='./base-data/images/star-svgrepo-com.png'
                            return QtGui.QImage(filename)
                        else: 
                            filename= './base-data/images/empty-image.png'
                            return QtGui.QImage(filename)
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.items)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s 

##################################################################################################
##################################################################################################

##################################################################################################
##################################################################################################
  

##################################################################################################
##################################################################################################    

##################################################################################################
##################################################################################################

