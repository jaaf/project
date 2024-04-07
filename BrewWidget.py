'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License alongdate with this program. If not, see <https://www.gnu.org/licenses/>.
'''

import copy
import datetime
import json
import os
import sys
import time
from datetime import date
import jsonpickle
from PyQt6 import QtCore, QtGui, QtWidgets,QtPrintSupport


from PyQt6.QtCore import (QFile, QObject, QRegularExpression, QSize, Qt,
                          QTextStream, QTimer, pyqtSignal)
from PyQt6.QtGui import (QColor, QDoubleValidator, QIcon, QIntValidator,
                         QPalette, QRegularExpressionValidator,QScreen)
from PyQt6.QtWidgets import (QDateEdit, QDialog, QFrame, QGroupBox,QInputDialog,
                             QHBoxLayout, QLabel, QLayout, QLineEdit,
                             QListView, QPushButton, QTextEdit, QVBoxLayout,QMessageBox,
                             QWidget)
from FeedbackWidget import FeedbackWidget
from BrewUtils import BrewUtils
from BrewWidgetBase import Ui_BrewWidget as brewWgt
from calculator import Calculator
from ConfirmationDialog import ConfirmationDialog
from database.brews.brew import (Brew, add_brew, all_brew, delete_brew,
                                 find_brew_by_id, find_brew_by_name, 
                                 update_brew)
from database.commons.country import all_country, find_country_by_code
from database.fermentables.fermentable import all_fermentable
from database.fermentables.inventory_fermentable import (
    all_inventory_fermentable, delete_inventory_fermentable,
    update_inventory_fermentable)
from database.hops.hop import all_hop
from database.hops.inventory_hop import (all_inventory_hop,
                                         delete_inventory_hop,
                                         update_inventory_hop)
from database.miscs.misc import (all_inventory_misc,
                                           delete_inventory_misc,
                                           update_inventory_misc)
from database.miscs.misc import all_misc
from database.profiles.equipment import (Equipment, add_equipment,
                                         all_equipment, delete_equipment,
                                         find_equipment_by_name,
                                         update_equipment)
from database.profiles.rest import all_rest
from database.profiles.style import all_style, find_style_by_name
from database.recipes.recipe import find_recipe_by_id
from database.yeasts.yeast import (all_inventory_yeast, all_yeast,
                                   delete_inventory_yeast,
                                   update_inventory_yeast)
from dateUtils import DateUtils
from datetime import date
from HelpMessage import HelpMessage
from LevelIndicator import LevelIndicator
from parameters import cooler_type, equipment_type
from PhAdjusterWidget import PhAdjusterWidget
from SelectorWidget import SelectorWidget
from SignalObject import SignalObject
from WaterAdjustmentWidget import WaterAdjustmentWidget
from PDFWritter import PDFWriter
from ExportBrewSheet import ExportBrewSheet
from NameDialog import NameDialog
from pathlib import Path


#from help.TargetOGHelp import TargetOGHelp


class Communication(QObject):
    calculate=pyqtSignal(SignalObject)
    refresh_display=pyqtSignal(SignalObject)

class MyWidget(QWidget):
    def resizeEvent(self,event):
        pass #to allow overwrite of the method

class BrewWidget(MyWidget):
    resized = QtCore.pyqtSignal()
    def __init__(self, id,recipe_id,parent=None):
        super().__init__(parent)
        self.ui =brewWgt()
        self.ui.setupUi(self)
        self.id=id
        self.recipe_id=recipe_id
        self.parent=parent
        self.this_file_path=Path(__file__).parent
        
        #os.system('clear')
        keyPressed = QtCore.pyqtSignal(int)
        self.initial_brew=Brew(
                    None,#id\
                    None,#name\ 
                    None,#equipment\
                    None,#batch_volume\
                    None,#brew_date\
                    None,#rtype\ 
                    None,#style\
                    None,#bitterness\
                    None,#og\
                    None,#abv\
                    None,#color\
                    None,#boil_time\
                    None,#fermentables\
                    None,#hops\
                    None,#yeasts\
                    None,#miscs\
                    None,#rests\
                    None,#grain_temperature
                    None,#additions_temperature
                    None,#temperature_method
                    None,#base_water\
                    None,#dilution_water\
                    None,#dilution\
                    None,#style_water\
                    None,#target_water\
                    None,#water_for_sparge\
                    None,#salt_additions\
                    None,#water_adjustment_state
                    None,#pH_adjuster_enabled
                    None,#pH_target
                    None,#acid_agent
                    None,#launched
                    None,#feedback\
                    )
        self.declare_variables()
        self.c=Communication()
        self.icon_path='base-data/icons/'
        self.icon_size=QSize(32,32)

        app = QtWidgets.QApplication.instance()
        #as use of setStyleSheet prevents correct font propagation. Prepend all style with this prefix to fix this issue
        self.font_style_prefix='font:'+str(app.font().pointSize())+'pt '+app.font().family()+';'
        #don't understand why font is not correctly propagated though is is for hop and yeasts
        self.setFont(app.font())
        self.ui.tabWidget.setTabEnabled(7,False)
        self.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
        self.today=datetime.date.today()
        current_year=self.today.year
        self.disabled_edit_bgcolor='Lavender'
        self.disabled_edit_color='#666'
        self.enabled_edit_bgcolor='white'
        self.enabled_edit_color='black'
        self.ui.equipmentCombo.setStyleSheet(self.font_style_prefix+'') 
        self.finish_gui()
        self.ui.equipmentRefreshButton.setVisible(False)
        self.ui.equipmentRefreshButton.setStyleSheet('background-color:red; color:white; font-weight:bold;')
        self.start_from_scratch=False
        #load brew checks if id passed  
        self.load_brew()
        self.add_tab_content()
        self.ui.calculatedIBUEdit.setStyleSheet(self.font_style_prefix+'background-color:'+self.disabled_edit_bgcolor+';color:'+self.disabled_edit_color)
        if self.start_from_scratch:
             #start_from_scratch set in load_brew
             self.selectors_show_actual_values()
        self.set_input_filters()
        self.ui.targetOGCheckBox.setDisabled(True)#will be enabled after a fist fermentable calculation
        self.ui.targetIBUCheckBox.setDisabled(True)#will be enabled after a fist hop calculation
        self.ui.targetOGEdit.setVisible(True)
        #connection must be established before update_all() to trigger the first calculation of end_sugar
        self.set_connections()
        self.update_all()
        self.c.calculate.emit(SignalObject('equipment',self.equipment))
        self.waterAdjustmentDialog.after_init()

        if self.launched:
            #to disable a lot of fields
            self.set_launched()
  
    #--------------------------------------------------------------------------------------
    def style_disabled_edit(self,list,v=None):
        for item in list:
            try:
                if item.__class__.__name__=="QLineEdit":
                    if item.isEnabled()==True:
                        item.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.disabled_edit_color+';')
                        item.setFont(self.font())
                    else:
                        item.setStyleSheet(self.font_style_prefix+'color:'+self.disabled_edit_color+'; background-color:'+self.disabled_edit_bgcolor+';')
                        item.setFont(self.font())
                else:
                    item.setFont(self.font())
                    item.setStyleSheet(self.font_style_prefix)     
            except Exception as e:
                print(e)
                pass
        
    #--------------------------------------------------------------------------------------
    def finish_gui(self):
        #set style of disabled inputs
        mylist=self.ui.general1GroupBox.findChildren(QWidget)
        mylist+=self.ui.general2GroupBox.findChildren(QWidget)
        mylist+=self.ui.general3GroupBox.findChildren(QWidget)
        mylist+=self.ui.general4GroupBox.findChildren(QWidget)
        mylist+=self.ui.calculationGroupBox.findChildren(QWidget)
        mylist+=self.ui.general6GroupBox.findChildren(QWidget)
        self.style_disabled_edit(mylist)
        
        #set style of help button
        self.ui.ogHelpButton.setText('?')
        self.ui.ibuHelpButton.setStyleSheet(self.font_style_prefix+'color:white; background-color:green;')
        self.ui.volumesHelpButton.setText('?')
        self.ui.volumesHelpButton.setStyleSheet(self.font_style_prefix+'color:white; background-color:green;')
        self.ui.ibuHelpButton.setText('?')
        self.ui.preboilGravityHelpButton.setText('?')
        self.ui.preboilGravityHelpButton.setStyleSheet(self.font_style_prefix+'color:white; background-color:green;')

        #complete GUI
        self.ui.calculatedOGEdit.setVisible(False)
        self.ui.calculatedOGLabel.setVisible(False)
        self.ui.calculatedOGUnitLabel.setVisible(False)
        self.style=None
        self.ui.targetOGUnitCombo.setVisible(False)#not used at the moment

        #create a toolbar 
        toolbarLayout=QHBoxLayout()
        self.duplicateButton=QPushButton()
        self.duplicateButton.setIcon(QIcon(self.icon_path+'duplicate-svgrepo-com.svg'))
        self.duplicateButton.setIconSize(self.icon_size)
        self.duplicateButton.setToolTip("Cloner la session de brassage")
        self.closeButton=QPushButton()
        self.closeButton.setIcon(QIcon(self.icon_path+'close-square-svgrepo-com.svg'))
        self.closeButton.setIconSize(self.icon_size)
        self.closeButton.setToolTip("Fermer la session de brassage")
        self.saveButton=QPushButton()
        self.saveButton.setIcon(QIcon(self.icon_path+'save-left-svgrepo-com.svg'))
        self.saveButton.setIconSize(self.icon_size)
        self.saveButton.setToolTip("Sauvegarder la session de brassage")
        self.deleteButton=QPushButton()
        self.deleteButton.setIcon(QIcon(self.icon_path+'trash-can-svgrepo-com.svg'))
        self.deleteButton.setIconSize(self.icon_size)
        self.deleteButton.setToolTip("Supprimer la session de brassage")
        self.lockButton=QPushButton()
        self.lockButton.setIcon(QIcon(self.icon_path+'lock-svgrepo-com.svg'))
        self.lockButton.setIconSize(self.icon_size)
        self.lockButton.setToolTip("Exécuter la session et prélever les consommables")
        self.lockButton.setStyleSheet(self.font_style_prefix+"border: 2 solid red;border-radius: 5")
        self.printButton=QPushButton()
        self.printButton.setIcon(QIcon(self.icon_path+"printer-print-svgrepo-com.svg"))
        self.printButton.setIconSize(self.icon_size)
        self.printButton.setToolTip("Imprimer la fiche de session")
        

        #HEADER the part at the top that contains title, level indicators and toolbar
        self.headerLayout=QHBoxLayout()
        #title on the left
        self.title=QLabel()
        self.title.setText('SESSION DE BRASSAGE  EN ÉDITION ')
        self.title.setStyleSheet(self.font_style_prefix+'font-size: 20px; font-weight:bold; color:'+self.enabled_edit_color)
        self.titleLayout=QVBoxLayout()
        self.titleLayout.addWidget(self.title)
        self.subtitleLayout=QHBoxLayout()
        self.nameEdit=QLineEdit()
        self.subtitleLayout.addWidget(self.nameEdit)
        self.dateEdit=QDateEdit()
        self.dateEdit.setDate(self.today)
        self.dateEdit.setCalendarPopup(True)
        self.titleLayout.addWidget(self.dateEdit)
        self.titleLayout.addLayout(self.subtitleLayout)
        self.headerLayout.addLayout(self.titleLayout)
        spacerItem = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        spacerItemSmall = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.headerLayout.addSpacerItem(spacerItem)

        #indicators in the middle signature (pad,w,h,decimals)
        self.og_indicator=LevelIndicator(30,250,20,3)
        self.og_indicator.setText('OG')
        self.ibu_indicator=LevelIndicator(30,250,20,0)
        self.ibu_indicator.setText('IBU') 
        self.abv_indicator=LevelIndicator(30,250,20,1)
        self.abv_indicator.setText('ABV %') 
        self.color_indicator=LevelIndicator(30,250,20,0)
        self.color_indicator.setText('COLOR SRM')
        self.indicatorLayout=QHBoxLayout()
        self.indicatorLayoutRight=QVBoxLayout()
        self.indicatorLayoutRight.addWidget(self.color_indicator)
        self.indicatorLayoutRight.insertWidget(0,self.ibu_indicator)
        self.indicatorLayoutLeft=QVBoxLayout()
        self.indicatorLayoutLeft.addWidget(self.abv_indicator)  
        self.indicatorLayoutLeft.insertWidget(0,self.og_indicator)
        self.indicatorLayoutRight.setSpacing(3)
        self.indicatorLayoutLeft.setSpacing(3)
        self.indicatorLayout.addLayout(self.indicatorLayoutRight)
        self.indicatorLayout.addSpacing(20)
        self.indicatorLayout.addLayout(self.indicatorLayoutLeft)
        self.indicatorFrame=QFrame()
        self.indicatorFrame.setLayout(self.indicatorLayout)
        self.headerLayout.addWidget(self.indicatorFrame)
        self.headerLayout.addSpacerItem(spacerItem)
        self.ui.calculatedIBUUnitLabel.setStyleSheet(self.font_style_prefix+"color:red")

        #toolbar on the right
        self.toolbarLayout=QHBoxLayout()
        self.toolbarLayout.addItem(spacerItem)
        self.toolbarLayout.addWidget(self.lockButton)
        self.toolbarLayout.addWidget(self.duplicateButton)
        self.toolbarLayout.addWidget(self.saveButton)
        self.toolbarLayout.addWidget(self.deleteButton) 
        self.toolbarLayout.addWidget(self.printButton)
        self.toolbarLayout.addWidget(self.closeButton)
        self.toolbarLayout.setSpacing(20)
        self.headerLayout.addLayout(self.toolbarLayout)
        self.ui.headerGroupBox.setLayout(self.headerLayout)

        #----------------------------------------
        #SET VARIOUS COMBO
        self.ui.targetOGUnitCombo.addItem('SG')
        self.ui.targetOGUnitCombo.addItem('Platos')
        self.styles=all_style()
        self.ui.styleCombo.addItem('')
        for s in self.styles:
            self.ui.styleCombo.addItem(s.name)
        equipments=all_equipment()
        self.ui.equipmentCombo.addItem('')
        for equipment in equipments:
            self.ui.equipmentCombo.addItem(equipment.name)
        self.ui.typeCombo.addItem('')
        self.ui.typeCombo.addItem('Tout grain')
        self.ui.typeCombo.addItem('Empâtage partiel')
        self.ui.typeCombo.addItem('Extraits')        
     
        #-----------------------------------------------------------------------
    def handle_calculate_signal(self,obj):
        #each time an input value (e.g. boil_time) changes it calls its update function
        #this function triggers a calculate signal from Communication class and this signal 
        #calls the present function
        #print('in handle_calculate_signal '+obj.name)
        name=obj.name
        if(self.og_as_target):#gravity is a target
            match name:
                case 'boil_time':
                    Calculator.boil_evaporation(self)
                case 'batch_volume':
                    Calculator.end_sugar(self)
                    Calculator.end_water_mass(self)
                    Calculator.end_boil_Volume_hot(self)
                    Calculator.beer_forecast_abv(self)
                case 'og':
                    Calculator.end_sugar(self)   
                    Calculator.beer_forecast_abv(self) 
                case 'equipment':
                    if self.equipment is not None:
                        self.ui.mashEfficiencyEdit.setText(str(self.equipment.mash_efficiency))
                        Calculator.mash_hop_absorbed_water(self)
                        Calculator.boil_temperature_kelvin(self)
                        Calculator.weighted_average_potential(self) 
                        Calculator.end_sugar(self)
                        Calculator.total_fermentable_mass(self)
                        Calculator.mash_fermentables_absorbed_water(self)
                        Calculator.mash_water_mass(self)
                        Calculator.boil_evaporation(self)
                        Calculator.compute_rests(self)
                        Calculator.beer_forecast_abv(self)
              
                    
                case 'fermentable':
                    self.toggle_og_as_target(False)
                    Calculator.weighted_average_potential(self) 
                    Calculator.boil_sugar(self) 
                    Calculator.beer_color(self)
                    self.phAdjuster.clean_and_reset()
                case 'boil_fermentable':
                    pass
                case 'equipment_update':
                    self.load_brew()
                case 'rest':
                    Calculator.compute_rests(self)
                case 'yeast':
                    Calculator.beer_forecast_abv(self)
        
        else:#gravity is not a target but a result of calculation
            match name:
                case 'batch_volume':
                    Calculator.end_water_mass(self)
                    Calculator.end_boil_Volume_hot(self)
                case 'fermentable':
                    Calculator.weighted_average_potential(self)  
                    Calculator.boil_sugar(self) 
                    Calculator.preboil_water_mass(self)
                    Calculator.beer_color(self)
                    self.phAdjuster.clean_and_reset()
                case 'hop':
                    Calculator.mash_hop_absorbed_water(self)    
                case 'yeast':
                    Calculator.beer_forecast_abv(self)
                case 'equipment': 
                    self.ui.mashEfficiencyEdit.setText(str(self.equipment.mash_efficiency))
                    
                    Calculator.mash_hop_absorbed_water(self)
                    Calculator.boil_temperature_kelvin(self)
                    Calculator.mash_fermentables_absorbed_water(self) 
                    Calculator.mash_sugar(self)
                    Calculator.end_water_mass(self)  
                    Calculator.mash_water_mass(self)
                    Calculator.compute_rests(self)
                case "rest":
                    Calculator.compute_rests(self)      
                case 'boil_time':
                    Calculator.preboil_water_mass(self)    
                case 'equipment_update':
                    self.load_brew()    
                   
        if(self.bitterness_as_target):#bitterness is a target
            match name:
                case "bitterness":
                    Calculator.ibu_before_scaling(self) 
                    #Calculator.total_hop_mass(self)
                case "boil_time":
                    #Calculator.weighted_average_ibu_yield(self) 
                    Calculator.ibu_before_scaling(self) 
                case "batch_volume":
                    Calculator.total_hop_mass(self)    
                case "hop": 
                    self.toggle_bitterness_as_target(False) 
                    Calculator.total_hop_mass(self)
                    Calculator.mash_hop_absorbed_water(self)
        else:#bitterness is not a target but a result of calculation
            match name:
                case "bitterness":
                    Calculator.bitterness(self)
                case "hop" : 
                    Calculator.total_hop_mass(self) 
                    #Calculator.weighted_average_ibu_yield(self)
                    Calculator.ibu_before_scaling(self)
                    #Calculator.bitterness(self)                             
    #-------------------------------------------------------------
    def declare_variables(self):
        #alphabetic order
        self.boil_evaporation=0
        self.end_water_mass=0
        self.end_sugar=0
        self.fermenter_water_mass=0
        self.hop_absorbed_water=0
        self.hop_water_cpt=0
        self.mash_fermentables_absorbed_water=0
        self.mash_sugar=0 
        self.mash_water_mass=0 
        self.boil_sugar=0
        self.og=1.0
        self.old_hop_absorbed_water=10
        self.preboil_gravity=0
        self.preboil_water_mass=0
        self.sparge_water_mass=0
        self.total_fermentable_mass=0
        self.total_fermentable_mass=0
        self.total_hop_mass=0
        self.mash_hop_absorbed_water=0
        self.total_mash_fermentable_mass=0
        self.total_boil_steeped_mass=0
        self.total_water_mass=0
        self.utilisation_gravity_factor=0
        self.weighted_average_potential=0
        self.weighted_average_ibu_yield=0
        self.ibu_before_scaling=0

    #--------------------------------------------------------------------------
    def set_launched(self):
        #when the brew has already been or is launched
        self.ui.tabWidget.setTabEnabled(7,True)
        self.setStyleSheet("QTabBar::tab::enabled {} ")
        mylist=self.feedbackDialog.ui.groupBox.findChildren(QWidget)
        self.style_disabled_edit(mylist)
        self.feedbackDialog.ui.observedMashEfficiencyEdit.setStyleSheet(self.font_style_prefix+"background-color:lightgreen;color:magenta;")
        self.feedbackDialog.ui.observedGrainAbsorptionEdit.setStyleSheet(self.font_style_prefix+"background-color:lightgreen;color:magenta;")
        self.feedbackDialog.ui.beforeBoilVolumeEdit.setStyleSheet(self.font_style_prefix+"border:none; background-color:transparent")
        self.feedbackDialog.ui.expectedAddedWaterEdit.setStyleSheet(self.font_style_prefix+"border:none; background-color:transparent")
        self.feedbackDialog.ui.expectedAdditionalBoilTimeEdit.setStyleSheet(self.font_style_prefix+"border:none; background-color:transparent")
        try:    
            
            self.feedbackDialog.ui.observedAfterSpargeVolumeEdit.setText(self.brew_feedback.after_sparge_wort_volume)
            self.feedbackDialog.ui.observedAfterSpargeGravityEdit.setText(self.brew_feedback.after_sparge_gravity)
            self.feedbackDialog.ui.observedAddedWaterEdit.setText(self.brew_feedback.additional_water)
            self.feedbackDialog.ui.observedAdditionalBoilTime.setText(self.brew_feedback.additional_boil_time)
            self.feedbackDialog.ui.observedAferBoilVolumeEdit.setText(self.brew_feedback.after_boil_wort_volume)
            self.feedbackDialog.ui.observedOriginalGravityEdit.setText(self.brew_feedback.after_boil_gravity)
            self.feedbackDialog.note_model.notes=jsonpickle.decode(self.brew_feedback.notes)
           
             
        except Exception as e: 
            print("exception dans set_launched ")
            print(e)
            pass
        #some textEdit are set from calculator
        self.feedbackDialog.ui.expectedMashEfficiencyEdit.setText(str(self.equipment.mash_efficiency))
        vol=(self.batch_volume+self.equipment.kettle_retention)*1.04
        self.feedbackDialog.ui.expectedAfterBoilVolumeEdit.setText(str(round(vol,2)))
        self.feedbackDialog.ui.expectedGrainAbsorptionEdit.setText(str(self.equipment.grain_absorption))
        
        #no longer need the source lists
        self.fermentable_selector.hide_source_list()
        self.hop_selector.hide_source_list()
        self.yeast_selector.hide_source_list()
        self.misc_selector.hide_source_list()
        self.rest_selector.hide_source_list()

        self.lockButton.setStyleSheet(self.font_style_prefix+"border: 2 solid green; border-radius: 5;")   
        self.lockButton.setEnabled(False) 
        self.lockButton.setToolTip('Bouton désactivé. La session est déjà en exécution ou exécutée.')
        self.ui.typeCombo.setEnabled(False)
        self.ui.typeCombo.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.ui.equipmentCombo.setEnabled(False) 
        self.ui.equipmentCombo.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.ui.styleCombo.setEnabled(False) 
        self.ui.styleCombo.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.ui.batchVolumeEdit.setEnabled(False) 
        self.ui.batchVolumeEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.ui.boilTimeEdit.setEnabled(False) 
        self.ui.boilTimeEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.ui.targetIBUEdit.setEnabled(False)
        self.ui.targetIBUEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.ui.targetIBUCheckBox.setEnabled(False)
        self.ui.targetIBUCheckBox.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.ui.targetOGEdit.setEnabled(False)
        self.ui.targetOGEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.ui.targetOGCheckBox.setEnabled(False)
        self.ui.targetOGCheckBox.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.BaseCombo.setEnabled(False)
        self.waterAdjustmentDialog.ui.BaseCombo.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.DilutionCombo.setEnabled(False)
        self.waterAdjustmentDialog.ui.DilutionCombo.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.StyleCombo.setEnabled(False)
        self.waterAdjustmentDialog.ui.StyleCombo.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.CaMinTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.MgMinTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.NaMinTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.ClMinTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.So4MinTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.AlkaMinTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.CaMaxTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.MgMaxTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.NaMaxTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.ClMaxTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.So4MaxTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.AlkaMaxTargetEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.adviceButton.setEnabled(False)
        self.waterAdjustmentDialog.ui.adviceButton.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.CaSO4Value.setEnabled(False)
        self.waterAdjustmentDialog.ui.CaSO4Value.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.MgSO4Value.setEnabled(False)
        self.waterAdjustmentDialog.ui.MgSO4Value.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.CaCl2Value.setEnabled(False)
        self.waterAdjustmentDialog.ui.CaCl2Value.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")        
        self.waterAdjustmentDialog.ui.MgCl2Value.setEnabled(False)
        self.waterAdjustmentDialog.ui.MgCl2Value.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.CaOH2Value.setEnabled(False)        
        self.waterAdjustmentDialog.ui.NaHCO3Value.setEnabled(False)
        self.waterAdjustmentDialog.ui.NaHCO3Value.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.CaOH2Value.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.CaAdjustedEdit.setEnabled(False)
        self.waterAdjustmentDialog.ui.CaAdjustedEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")        
        self.waterAdjustmentDialog.ui.MgAdjustedEdit.setEnabled(False)
        self.waterAdjustmentDialog.ui.MgAdjustedEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.NaAdjustedEdit.setEnabled(False)
        self.waterAdjustmentDialog.ui.NaAdjustedEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.ClAdjustedEdit.setEnabled(False)
        self.waterAdjustmentDialog.ui.ClAdjustedEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.SO4AdjustedEdit.setEnabled(False)
        self.waterAdjustmentDialog.ui.SO4AdjustedEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.AlkaAdjustedEdit.setEnabled(False)
        self.waterAdjustmentDialog.ui.AlkaAdjustedEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.AdjustButton.setEnabled(False)
        self.waterAdjustmentDialog.ui.AdjustButton.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.IgnoreCheckbox.setEnabled(False)
        self.waterAdjustmentDialog.ui.IgnoreCheckbox.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.AsIsButton.setEnabled(False)
        self.waterAdjustmentDialog.ui.AsIsButton.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.waterAdjustmentDialog.ui.SpargeWaterSelectCombo.setEnabled(False)
        self.waterAdjustmentDialog.ui.SpargeWaterSelectCombo.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.phAdjuster.ui.mainCheckBox.setEnabled(False)
        self.pH_adjuster_enabled=False
        self.phAdjuster.ui.spinBox.setEnabled(False)
        self.phAdjuster.ui.spinBox.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        self.phAdjuster.ui.acidAgentCombo.setEnabled(False)
        self.phAdjuster.ui.acidAgentCombo.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
        for item in self.phAdjuster.diph_items:
            item.ui.diphEdit.setEnabled(False)
            item.ui.diphEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
            item.ui.capacityEdit.setEnabled(False)
            item.ui.capacityEdit.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;color:black")
            item.ui.pushButton.setEnabled(False)
        try:
            self.fermentable_selector.destinationList.mysignal.disconnect()
            self.fermentable_selector.destinationList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")
            self.hop_selector.destinationList.mysignal.disconnect()
            self.hop_selector.destinationList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")
            self.yeast_selector.destinationList.mysignal.disconnect()
            self.yeast_selector.destinationList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")
            self.misc_selector.destinationList.mysignal.disconnect()
            self.misc_selector.destinationList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")
            self.rest_selector.destinationList.mysignal.disconnect()
            self.rest_selector.destinationList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")
            
        except Exception as Error:
            print(Error)
            pass
        try:
            self.fermentable_selector.sourceList.mysignal.disconnect()
            self.fermentable_selector.sourceList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")
            self.hop_selector.sourceList.mysignal.disconnect()
            self.hop_selector.sourceList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")
            self.yeast_selector.sourceList.mysignal.disconnect()
            self.yeast_selector.sourceList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")
            self.misc_selector.sourceList.mysignal.disconnect() 
            self.misc_selector.sourceList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")
            self.rest_selector.sourceList.mysignal.disconnect()
            self.rest_selector.sourceList.setStyleSheet(self.font_style_prefix+"background-color:LightSteelBlue;")

        except Exception as Error:
            print(Error)
            pass

    #--------------------------------------------------------------------------
    def set_connections(self):
        #set connections
        self.duplicateButton.clicked.connect(self.duplicate_brew)
        self.printButton.clicked.connect(self.create_brew_sheet)
        self.parent.parent.keyboard_signal.connect(self.handle_shortcuts)
        self.ui.tabWidget.currentChanged.connect(self.tab_changed)
        self.c.calculate.connect(self.handle_calculate_signal)
        self.saveButton.clicked.connect(self.add)
        self.closeButton.clicked.connect(self.close)
        self.deleteButton.clicked.connect(self.delete)
        self.lockButton.clicked.connect(self.before_lock)
        self.ui.equipmentRefreshButton.clicked.connect(self.refresh_equipment)

        self.ui.styleCombo.currentTextChanged.connect(self.set_style)


        self.nameEdit.textChanged.connect(lambda :self.clean_edit('name'))
        self.ui.batchVolumeEdit.textChanged.connect(self.batch_volume_update)
        self.ui.equipmentCombo.currentTextChanged.connect(self.change_equipment)
        self.ui.equipmentCombo.currentIndexChanged.connect(lambda : self.clean_edit('equipment'))
        self.ui.typeCombo.currentIndexChanged.connect(lambda :self.clean_edit('type'))
        self.ui.styleCombo.currentIndexChanged.connect(lambda :self.clean_edit('style'))
        self.ui.targetIBUEdit.textChanged.connect(self.bitterness_update)
        self.ui.colorEdit.textChanged.connect(lambda : self.clean_edit('color'))

        self.ui.targetOGEdit.textChanged.connect(self.og_update)
        self.ui.targetIBUEdit.textChanged.connect(self.bitterness_update)
        self.ui.targetOGCheckBox.clicked.connect(lambda: self.toggle_og_as_target(self.ui.targetOGCheckBox.checkState()==Qt.CheckState.Checked))
        self.ui.targetIBUCheckBox.clicked.connect(lambda: self.toggle_bitterness_as_target(self.ui.targetIBUCheckBox.checkState()==Qt.CheckState.Checked))

        self.ui.boilTimeEdit.textChanged.connect(self.boil_time_update)
        self.ui.coldPreboilWaterVolumeEdit.setText('66.66')

        self.ui.ogHelpButton.clicked.connect(lambda: self.show_contextual_help('targetOG'))
        self.ui.ibuHelpButton.clicked.connect(lambda: self.show_contextual_help('targetIBU'))
        self.ui.volumesHelpButton.clicked.connect(lambda: self.show_contextual_help('volumes'))
        self.ui.preboilGravityHelpButton.clicked.connect(lambda: self.show_contextual_help('preboil_gravity'))

        

    #--------------------------------------------------------------------------
    def resizeEvent(self,event):
        #when using small resolution screens need to remove indicators
        app = QtWidgets.QApplication.instance()
        screen_resolution=app.primaryScreen().size()
        swidth, sheight = screen_resolution.width(), screen_resolution.height()
        print("screen resolution is :"+str(swidth)+'x'+str(sheight))
        print("width :"+str(event.size().width())+ " / height: "+str(event.size().height()))
        if event.size().height()<720:
            self.indicatorFrame.setVisible(False)
            self.fermentable_selector.ui.titleGroupBox.setVisible(False)
            self.hop_selector.ui.titleGroupBox.setVisible(False)
            self.yeast_selector.ui.titleGroupBox.setVisible(False)
            self.misc_selector.ui.titleGroupBox.setVisible(False)
            self.rest_selector.ui.titleGroupBox.setVisible(False)
        else:
            self.indicatorFrame.setVisible(True)
            self.fermentable_selector.ui.titleGroupBox.setVisible(True)
            self.hop_selector.ui.titleGroupBox.setVisible(True)
            self.yeast_selector.ui.titleGroupBox.setVisible(True)
            self.misc_selector.ui.titleGroupBox.setVisible(True)
            self.rest_selector.ui.titleGroupBox.setVisible(True)

    #-------------------------------------------------------------------------
    def initial_hide_for_extract_type(self):
        self.ui.coldSpargeWaterVolumeEdit.setVisible(False)
        self.ui.coldSpargeWaterVolumeLabel.setVisible(False) 
        self.ui.coldSpargeWaterVolumeUnitLabel.setVisible(False) 
        self.ui.coldMashWaterLabel.setVisible(False)
        self.ui.coldMashWaterVolumeEdit.setVisible(False)
        self.ui.coldMashWaterUnitLabel.setVisible(False)
        self.ui.calculationGroupBox.setVisible(False)
        self.ui.tabWidget.setTabVisible(4,False)
    #-------------------------------------------------------------------------
    def rest_data_changed(self):
        self.c.calculate.emit("rest_data",None)        

    #--------------------------------------------------------------------------
    def handle_shortcuts(self,obj):
        match obj.value:
            case "toggle_header":
                self.toggle_header_view()
            case "toggle_calculations":
                self.toggle_calculation_view()
            case "screen":
                print('in brew session screen resized')    

    #---------------------------------------------------------------------
    def toggle_header_view(self):
        if self.ui.headerGroupBox.isVisible():
            self.ui.headerGroupBox.setVisible(False)
        else:
            self.ui.headerGroupBox.setVisible(True)      
            
    #---------------------------------------------------------------------
    def toggle_calculation_view(self):
        if self.ui.calculationGroupBox.isVisible():
            self.ui.calculationGroupBox.setVisible(False) 
            self.ui.general6GroupBox.setVisible(False)
        else:
            self.ui.calculationGroupBox.setVisible(True) 
            self.ui.general6GroupBox.setVisible(True) 
        
    #------------------------------------------------------------------
    def tab_changed(self):
        if self.ui.tabWidget.currentIndex() == 6:
            self.phAdjuster.refresh_view()

    #------------------------------------------------------------------
    def show_contextual_help(self,what):
        helpPopup=HelpMessage()
        filename=(self.this_file_path/"help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
       
        match what:
            case "preboil_gravity":
                helpPopup.set_title("À propos de la densité de pré-ébullition")
                filename=(self.this_file_path/"help/PreboilGravityHelp.html").resolve()
            case 'volumes':
                helpPopup.set_title('À propos des volumes intermédiaires')
                filename=(self.this_file_path/'help/IntermediaryVolumes.html').resolve()
                
            case 'targetOG':
                helpPopup.set_title('À propos de la densité initiale')
                filename=(self.this_file_path/"help/TargetOGHelp.html").resolve()

            case 'targetIBU':
                helpPopup.set_title('À propos de l\'amertume')
                filename=(self.this_file_path/"help/TargetIBUHelp.html").resolve()

        text=open(filename,'r',encoding="utf-8").read()
        helpPopup.set_message(prepend+text)
        helpPopup.exec()

    #-------------------------------------------------------------------
    def duplicate_brew(self):
        if self.id is not None:
            read_brew=self.read_form()
            if read_brew:
                read_brew.id=None
                read_brew.brew_date=date.today()
                read_brew.feedback=""
                read_brew.launched=0
                self.name_dlg=NameDialog(self)
                intro="Merci de choisir un nom pour votre nouvelle session de brassage"
                self.name_dlg.set_intro(intro)
                self.name_dlg.set_name(read_brew.name)
                if self.name_dlg.exec():
                    read_brew.name=self.name_dlg.name
                    result=add_brew(read_brew)
                    if isinstance(result,int):
                        self.set_message("success","Duplication réussie. Une nouvelle session de brassage dont le nom est «" +read_brew.name +\
                                         " » a été ajoutée à la base de données.Vous pouvez y accéder en fermant cette session.")
                        self.parent.brews=all_brew()
                        self.parent.model.brews=all_brew()
                        self.parent.model.layoutChanged.emit()  
                    else:
                        self.set_message("failure","La duplication a échoué. \n"+result)    
        else:
            self.set_message("failure","Vous ne pouvez dupliquer une session de brassage qui n’a jamais été enregistrée. Complétez-la d’abord et enregistréz-la.")
           

    #-------------------------------------------------------------------
    def delete(self):
        #before deletion
        current_brew=find_brew_by_id(self.id)
        if current_brew:
            msgBox=ConfirmationDialog()
            msgBox.setTitle('Confirmer suppression')
            msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
            msgBox.setMessage('Vous êtes sur le point de supprimer une session de brassage. Cette suppression sera définitive. \n Confirmez-vous la suppression ?') 
            msgBox.setCancelButtonText('Non. Ne pas supprimer')
            msgBox.setConfirmButtonText('Oui. Supprimer.')
            confirm=msgBox.exec()   
            if(confirm == 1):
                result = delete_brew(self.id)#imported function
                if result == 'OK':
                    self.parent.brews=all_brew()
                    self.parent.model.brews=all_brew()
                    self.parent.model.layoutChanged.emit()  
                    self.manage_closure()
                else:
                    self.set_message('failure', 'raté')
        else:
            self.set_message('failure', "Cette session n'existe pas encore en base de données. Contentez-vous de la fermer si vous ne voulez pas la créer.")   

    #--------------------------------------------------------------
    def changes_saved(self):
        r=self.read_form() 
        reason=None
        #fermentables have already been encoded ,come back to list
        fs=jsonpickle.decode(r.fermentables)
        fis=jsonpickle.decode(self.initial_brew.fermentables)
        #hops have already been encoded ,come back to list
        hs=jsonpickle.decode(r.hops)
        his=jsonpickle.decode(self.initial_brew.hops)
        #yeasts have already been encoded ,come back to list
        ys=jsonpickle.decode(r.yeasts)
        yis=jsonpickle.decode(self.initial_brew.yeasts) 
        #miscs have already been encoded ,come back to list
        ms=jsonpickle.decode(r.miscs)
        mis=jsonpickle.decode(self.initial_brew.miscs)  
        #rests have already been encoded ,come back to list
        rs=jsonpickle.decode(r.rests)
        ris=jsonpickle.decode(self.initial_brew.rests)

        #check if changes have been brought to the recipe
        are_equal=True
        reason=''
        commons=BrewUtils.are_equal_brew_commons(r,self.initial_brew)
        if not commons[0]:
            are_equal=False
            reason+=commons[1]

        if not BrewUtils.are_equal_fermentables(fs,fis):
            are_equal=False
            reason+='\n➨les fermentables sont différents'

        if not BrewUtils.are_equal_hops(hs,his):
            are_equal=False
            reason+='\n➨les houblons sont différents'

        if not BrewUtils.are_equal_yeasts(ys,yis):
            are_equal=False
            reason+='\n➨les levures sont différentes'

        if not BrewUtils.are_equal_miscs(ms,mis):
            are_equal=False
            reason+='\n➨les divers ingrédients sont différents'

        if not BrewUtils.are_equal_rests(rs,ris):
            are_equal=False
            reason += "\n➨les paliers d'empâtage sont différents"
        
        return [are_equal,reason]
    
    #--------------------------------------------------------------
    def close(self):
        try:
            are_equal=self.changes_saved()
            if are_equal[0]:
                self.manage_closure()
            else:
                msgBox=ConfirmationDialog()
                msgBox.setTitle('Confirmer fermeture')
                
                msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
                message='Des changements ont été apportés à cette session de brassage. '
                message +="\nen particulier :"
                message += are_equal[1]
                message +="\nAttention tous les changements ne sont pas directs. Certains peuvent en avoir entraîné d'autres par calcul."
                message += '\nEn confirmant la fermeture, ces changements seront abandonnés.\n Confirmez-vous la fermeture sans avoir sauvegardé?'
                msgBox.setMessage(message) 
                msgBox.setCancelButtonText('Non. Ne pas fermer')
                msgBox.setConfirmButtonText('Oui. Fermer sans sauvegarder.')
                confirm=msgBox.exec()   
                if(confirm == 1):
                    self.manage_closure()
        except Exception as e:
            #the reading of the form was not good
            msgBox=ConfirmationDialog()
            msgBox.setTitle('Confirmer fermeture')
            
            msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
            msgBox.setMessage('Les saisies de valeurs sont incomplètes  ou incorrectes pour être sauvegardée.\n Confirmez-vous cependant la fermeture sans avoir sauvegardé?') 
            msgBox.setCancelButtonText('Non. Ne pas fermer')
            msgBox.setConfirmButtonText('Oui. Fermer sans sauvegarder.')
            confirm=msgBox.exec()   
            if(confirm == 1):
                self.manage_closure()           
               
    #-------------------------------------------------------------------
    def before_lock(self):
        read_brew=self.read_form()
        if(read_brew):
            if(self.id):
                read_brew.id=self.id
                result=update_brew(read_brew)
                if result =="OK":
                    #to reset changes to no change
                    self.initial_brew=copy.deepcopy(read_brew)
                    self.set_message('success','La session de brassage a été correctement sauvegardée')
                    self.lock()
                else:
                    self.set_message('failure', result),     

    #----------------------------------------------------------------
    def lock(self):
        message=''
        #--FERMENTABLES--
        result= self.check_all_fermentables_availability()
        if result =="OK":
            print('fermentables available')
            
        else:
            message += result
        #---HOPS--
        result= self.check_all_hops_availability()
        if result =="OK":
            print('hops available')
            
        else:
            message += result
        #-- yEASTs--
        result=self.check_all_yeasts_availibility()
        if result == "OK":
            print('yeasts available')
        else:
            print(result)
            message += result
        #--MISCELLANEOUS --
        result=self.check_all_miscs_availability()
        if result == "OK":
            print("miscs available")
        else:
            print(result)
            message+= result
        #water
        if self.water_adjustment_state != "adjusted" and self.water_adjustment_state != 'as_is':
            
            message +="\n Vous devez remplir le formulaire sur l'eau "
        #phAdjuster
        if self.pH_adjuster_enabled and not self.phAdjuster.pH_adjuster_ready():
            message += "\n Votre ajustement de pH n'est pas terminé. Faites le dans l'onglet « Ajustement du pH »."

        if message !='':
            self.set_message('failure',message)
        else:
            
            msgBox=ConfirmationDialog()
            msgBox.setTitle("Confirmer l'exécution de la session")
            
            msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
            message="Vous êtes sur le point de lancer l'exécution de la session. Cela provoquera de manière irréversible le retrait \
                \ndes consommables(fermentables, houblons, ingrédients divers, etc.) de leur inventaire. De plus la session ne pourra plus être modifiée.\
                    \n Tous les changements apportés depuis votre dernière sauvegarde seront également sauvegardés."
            if not self.pH_adjuster_enabled:
                message += "\n Vous n'avez pas utilisé l'ajustement du pH. Cela reste facultatif."
            msgBox.setMessage(message) 
            msgBox.setCancelButtonText("Non. Ne pas lancer l'exécution")
            msgBox.setConfirmButtonText("Oui. Lancer l'exécution")
            confirm=msgBox.exec()   
            if(confirm == 1):
                self.lockButton.setStyleSheet(self.font_style_prefix+"border: 2 solid green; border-radius: 5;")   
                self.lockButton.setEnabled(False) 
                self.lockButton.setToolTip('Bouton désactivé. La session est déjà en exécution ou exécutée.')
                self.withdraw_fermentables()
                self.withdraw_hops()
                self.withdraw_yeasts()
                self.withdraw_miscs()
                self.set_launched()
                self.launched=True
                self.add()
        #-----------------------------------------------------------
    def check_fermentable_availability(self,id,quantity):
        inv_fermentables=all_inventory_fermentable()
        available_quantity=0
        for inv_f in inv_fermentables:
            if(inv_f.fermentable_id == id):
                print('found identical id')
                available_quantity+=inv_f.quantity
        if available_quantity>=quantity:
            return ['success',None]
        else:
            return ['failure',round(quantity-available_quantity,2)]        

    #-----------------------------------------------------------------
    def check_all_fermentables_availability(self):
        message =''
        available=True
        for f in self.fermentable_selector.destination_model.items:
            check=self.check_fermentable_availability(f.fermentable.id,f.quantity)
            if  check[0] != 'success':
                message+="\nIl manque " +str(check[1])+" kg du fermentable « "+f.fermentable.name +" » de chez "+f.fermentable.brand+" et d'ID public "+str(f.fermentable.id)+". Veuiller approvisionner."
                available =False
        if available:
            return "OK"
        else:
            return message
        
    #-----------------------------------------------------------
    def check_hop_availability(self,id,quantity):
        #check one hop only
        inv_hops=all_inventory_hop()
        available_quantity=0
        for inv_h in inv_hops:

            if(inv_h.hop_id == id):
                available_quantity+=inv_h.quantity
        if available_quantity>=quantity:
            return ["success",None]
        else:
            return ['failure',round(quantity-available_quantity,0)]       

    #-----------------------------------------------------------------
    def check_all_hops_availability(self):
        message =''
        available=True
        for h in self.hop_selector.destination_model.items:
            check = self.check_hop_availability(h.hop.id,h.quantity)
            if check[0] != 'success':
                message+="\n Il mamque "+str(check[1])+" g du houblon « "+h.hop.name +" » de chez "+h.hop.supplier+" et d'ID pubic "+str(h.hop.id)+". Veuiller approvisionner."
                available =False
        if available:
            return "OK"
        else:
            return message

    #--------------------------------------------------------------
    def evaluate_yeast_units(self,value,threshold):
        #when threshold<decimal part, we use one more pack
        decimal_part=value % 1
        int_part=int(value)
        if int_part ==0:
            return 1
        else:
            if decimal_part>threshold:
                return int_part+1
            else:
                return int_part

    #----------------------------------------------------------------        
    def check_yeast_availability(self,id,quantity,cells_per_pack):
        inv_yeasts=all_inventory_yeast()
        available_quantity=0
        platos=BrewUtils.SG_to_Plato(self.og)
        #be careful quantity is a pitching rate in 10⁹ cells per liter per plato
        true_need=quantity *self.batch_volume * platos/cells_per_pack
        needed_quantity=self.evaluate_yeast_units(true_need,0.2)
        #print('needed quantity is '+str(needed_quantity))
        for inv_y in inv_yeasts:
            if(inv_y.yeast_id == id):
                #found identical id
                available_quantity +=inv_y.quantity 
        #print('available quantity is '+str(available_quantity))
        if available_quantity>=needed_quantity:
            return ['success',None]
        else:
            return ['failure',round(needed_quantity-available_quantity,2)]
        
    #------------------------------------------------------------
    def check_all_yeasts_availibility(self):
        message=''
        available=True
        for y in self.yeast_selector.destination_model.items:
            check=self.check_yeast_availability(y.yeast.id,y.quantity,y.yeast.cells_per_pack)
            if check[0] != 'success':
                message+="\nIl manque " +str(check[1])+" unités de la levure « "+y.yeast.name +" » de chez "+y.yeast.brand+" et d'ID public "+str(y.yeast.id)+". Veuiller approvisionner."
                available =False
        if available:
            return "OK"
        else:
            return message        
    #-----------------------------------------------------------
    def check_misc_availability(self,id,quantity):
        inv_miscs=all_inventory_misc()
        available_quantity=0
        for inv_misc in inv_miscs:
            if inv_misc.misc_id==id:
                available_quantity+=inv_misc.quantity
        if available_quantity>=quantity:
            return['success',None]
        else:
            return ['failure',round(quantity-available_quantity,2)]
        
    #-------------------------------------------------------------
    def check_all_miscs_availability(self):
        message=''
        available=True
        for m in self.misc_selector.destination_model.items:
            check=self.check_misc_availability(m.misc.id,m.quantity)
            if check[0]!= 'success':
                message += "\nIl manque "+str(check[1])+" "+str(m.misc.unit)+ " de l'ingrédient divers "+m.misc.name+" dont l'ID public est "+str(m.misc.id)+". Veuillez approvisionner."
                available = False
        if available:
            return "OK"
        else:
            return message       


    #-------------------------------------------------------------
    def withdraw_fermentables(self):
        for f in self.fermentable_selector.destination_model.items:
            cost=0
            residual_quantity=f.quantity
            inv_fermentables=all_inventory_fermentable()
            for inv_f in inv_fermentables:
                if (inv_f.fermentable_id == f.fermentable.id):
                    if inv_f.quantity<residual_quantity:
                        #we withdraw all
                        residual_quantity -= inv_f.quantity
                        cost+= inv_f.cost
                        inv_f.quantity =0
                        inv_f.cost=0
                        delete_inventory_fermentable(inv_f.id)
                    else:
                        Δ_cost = round(inv_f.cost * residual_quantity / inv_f.quantity,2)
                        cost += Δ_cost
                        inv_f.quantity= inv_f.quantity - round(residual_quantity,2)
                        inv_f.cost -= round(Δ_cost,2)
                        update_inventory_fermentable(inv_f)
                        residual_quantity=0
    
    #-------------------------------------------------------------
    def withdraw_hops(self):
        for h in self.hop_selector.destination_model.items:
            cost=0
            residual_quantity=h.quantity
            inv_hops=all_inventory_hop()
            for inv_h in inv_hops:
                if (inv_h.hop_id == h.hop.id):
                    if inv_h.quantity<residual_quantity:
                        #we withdraw all
                        residual_quantity -= inv_h.quantity
                        cost+= inv_h.cost
                        inv_h.quantity =0
                        inv_h.cost=0
                        delete_inventory_hop(inv_h.id)
                    else:
                        Δ_cost = round(inv_h.cost * residual_quantity / inv_h.quantity,2)
                        cost += Δ_cost
                        inv_h.quantity= inv_h.quantity - round(residual_quantity,2)
                        inv_h.cost -= round(Δ_cost,2)
                        update_inventory_hop(inv_h)
                        residual_quantity=0

    #------------------------------------------------------------
    def withdraw_yeasts(self):
        for y in self.yeast_selector.destination_model.items:
            cost=0
            platos=BrewUtils.SG_to_Plato(self.og)
            #y.quantity is a pitching rate in 10⁹ cells per liter per plato
            #residual_quantity is in packs
            residual_quantity=y.quantity*platos*self.batch_volume/y.yeast.cells_per_pack
            #round the number of packs
            residual_quantity=self.evaluate_yeast_units(residual_quantity,0.2)
            inv_yeasts=all_inventory_yeast()
            for inv_y in inv_yeasts:
                if (inv_y.yeast_id == y.yeast.id):
                    if inv_y.quantity<residual_quantity:
                        #we withdraw all this one purchase
                        residual_quantity -= inv_y.quantity
                        cost+= inv_y.cost
                        inv_y.quantity =0
                        inv_y.cost=0
                        delete_inventory_hop(inv_y.id)
                    else:
                        Δ_cost = round(inv_y.cost * residual_quantity / inv_y.quantity,2)
                        cost += Δ_cost
                        inv_y.quantity= inv_y.quantity - round(residual_quantity,2)
                        inv_y.cost -= round(Δ_cost,2)
                        update_inventory_yeast(inv_y)
                        residual_quantity=0


    #--------------------------------------------------------------
    def withdraw_miscs(self):
        for m in self.misc_selector.destination_model.items:
            cost=0
            residual_quantity=m.quantity
            inv_miscs=all_inventory_misc()
            for inv_m in inv_miscs:
                if inv_m.misc_id == m.misc.id:
                    if inv_m.quantity<residual_quantity:
                        #we withdraw all this one
                        residual_quantity-= inv_m.quantity
                        cost+=inv_m.cost
                        inv_m.quantity=0
                        inv_m.cost=0
                        delete_inventory_misc(inv_m.id)
                    else:
                        #this inv m 's quantity is too much
                        Δ_cost = round(inv_m.cost * residual_quantity / inv_m.quantity,2)
                        cost += Δ_cost
                        inv_m.quantity= inv_m.quantity - round(residual_quantity,2)
                        inv_m.cost -= round(Δ_cost,2)
                        update_inventory_misc(inv_m)
                        residual_quantity=0

    #------------------------------------------------------------
    def manage_closure(self):
        i=self.parent.parent.stackedWidget.currentIndex()
        self.parent.parent.brewTabWidget.removeTab(self.parent.parent.stackedWidget.currentIndex()-1)
        c=self.parent.parent.brewTabWidget.count()
        if(c==0):
            index=self.parent.parent.swapWidget('brew')
            self.parent.parent.stackedWidget.setCurrentIndex(index)

    #-------------------------------------------------------------
    def update_all(self):
        #to trigger all calculation at loading
        self.rtype_update()
        self.batch_volume_update()
        self.bitterness_update()
        self.boil_time_update()
        self.og_update()
        Calculator.weighted_average_potential(self) 
        Calculator.end_water_mass(self)
    #-------------------------------------------------------------
    def rtype_update(self):
        read_rtype=self.ui.typeCombo.currentText()
        self.ui.typeCombo.setStyleSheet(self.font_style_prefix+'background-color:'+self.enabled_edit_bgcolor+'; color:'+self.enabled_edit_color+';')  

    #--------------------------------------------------------------    
    def batch_volume_update(self):    
        try:
            read_vol=float(self.ui.batchVolumeEdit.text())
            if(read_vol>0 and read_vol<100):
                self.batch_volume=read_vol
                #this signal is used to chain the calculation(see handle_calculate_signal)
                self.c.calculate.emit(SignalObject('batch_volume',self.batch_volume))
            else:
                self.batch_volume=0    
        except:
            self.batch_volume=0
        self.ui.batchVolumeEdit.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.enabled_edit_color+';')
     
    #----------------------------------------------------------------
    def bitterness_update(self):
        try:
            read_bitterness=float(self.ui.targetIBUEdit.text())
            if(read_bitterness >0 and read_bitterness<100):
                self.bitterness=read_bitterness
                #this signal is used to chain the calculation(see handle_calculate_signal)
                self.c.calculate.emit(SignalObject('bitterness',self.bitterness))
            else:
                self.bitterness=None
        except:
            self.bitterness=None        
        self.ui.targetIBUEdit.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.enabled_edit_color+';')   
        
    #----------------------------------------------------------------
    def refresh_equipment(self):
        self.ui.targetOGCheckBox.setChecked(False)
        self.toggle_og_as_target(False)
        self.change_equipment()
        self.ui.equipmentRefreshButton.setVisible(False)
        self.ui.equipmentCombo.setStyleSheet(self.font_style_prefix+'')
    
    #---------------------------------------------------------------------
    def change_equipment(self):
        equip=find_equipment_by_name(self.ui.equipmentCombo.currentText())
        if(equip != None):
            self.equipment=equip
            if self.equipment.type == 'Tout en un':
                self.rest_selector.ui.temperatureMethodCombo.setCurrentText('Chauffage')
                self.rest_selector.ui.temperatureMethodCombo.setEnabled(False)
            else:
                self.rest_selector.ui.temperatureMethodCombo.setEnabled(True)
           
            #this signal is used to chain the calculation(see handle_calculate_signal)self.og
            self.c.calculate.emit(SignalObject('equipment',self.equipment))
        else:
            self.equipment=None   

    #-----------------------------------------------------------------
    def og_update(self):
        #input is filtered at source so that values are empty or good
        try:
            self.og=float(self.ui.targetOGEdit.text())
            self.og_indicator.setValue(self.og)
            #this signal is used to chain the calculation (see handle_calculate_signal)
            self.c.calculate.emit(SignalObject('og',self.og))
        except :
            self.og=None
        self.ui.targetOGEdit.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.enabled_edit_color+';')    

    #-----------------------------------------------------------------
    def bitterness_update(self):
        #input is filtered at source so that values are empty or good
        try:
            self.bitterness=float(self.ui.targetIBUEdit.text()) 
            self.ibu_indicator.setValue(self.bitterness)
            #this signal is used to chain the calculation (see handle_calculate_signal)
            self.c.calculate.emit(SignalObject('bitterness',self.bitterness))
        except :
            self.bitterness=None
        self.ui.targetIBUEdit.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.enabled_edit_color+';')   

    #-------------------------------------------------------------------        
    def abv_update(self):
        print('in abv_update')
        try:
            self.abv=float(self.ui.abvEdit.text()) 
            #this signal is used to chain the calculation (see handle_calculate_signal)
            self.c.calculate.emit(SignalObject('abv',self.abv))
            self.abv.indicator.setValue(self.abv)
        except:
            self.abv=None
        self.ui.abvEdit.setStyleSheet(self.font_style_prefix+'color:'+self.disabled_edit_color+'; background-color:'+self.disabled_edit_bgcolor+'; border: 1px solid '+self.disabled_edit_color+';')   
        
    #---------------------------------------------------------------------
    def boil_time_update(self):
        try:
            self.boil_time=float(self.ui.boilTimeEdit.text()) 
            #this signal is used to chain the calculation (see handle_calculate_signal)
            self.c.calculate.emit(SignalObject('boil_time',self.boil_time))
        except:
            self.boil_time=None
        self.ui.boilTimeEdit.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.enabled_edit_color+';')   
                
    #---------------------------------------------------------------
    def toggle_og_as_target(self, val):
        #toggle the calculation mode for gravity
        if(val):
            self.og_as_target=True
            self.ui.targetOGEdit.setVisible(True)
            self.ui.targetOGEdit.setText(str(round(self.og,3)))
            self.ui.calculatedOGEdit.setText('')  
            self.og_indicator.setValue(self.og)
            self.ui.targetOGCheckBox.setText('Libérer DI')
            self.ui.targetOGLabel.setVisible(True)
            self.ui.calculatedOGEdit.setVisible(False)
            self.ui.calculatedOGLabel.setVisible(False)
            self.ui.calculatedOGUnitLabel.setVisible(False)
        else:
            self.og_as_target=False    
            self.ui.targetOGCheckBox.setCheckState(Qt.CheckState.Unchecked)  
            self.ui.targetOGEdit.setVisible(False)
            self.ui.targetOGCheckBox.setText('Imposer DI')
            self.ui.targetOGLabel.setVisible(False)
            self.ui.calculatedOGEdit.setVisible(True)
            self.ui.calculatedOGLabel.setVisible(True)
            self.ui.calculatedOGUnitLabel.setVisible(True)
            #print('on the verge on setting og_indicator ')
            self.ui.calculatedOGEdit.setText(str(self.og))
            self.og_indicator.setValue(self.og)

        self.ui.targetOGCheckBox.setDisabled(False)
            
    #---------------------------------------------------------------
    def toggle_bitterness_as_target(self, val):
        #toggle the calculation mode for IBU
        
        if(val):
            self.bitterness_as_target=True
            self.ui.targetIBUEdit.setVisible(True)
            try:
                self.ui.targetIBUEdit.setText(str(round(self.bitterness,0)))
            except:
                pass
            self.ui.targetIBUEdit.setVisible(True)
            self.ui.targetIBULabel.setVisible(True)
            self.ui.calculatedIBUEdit.setText('')
            self.ibu_indicator.setValue(self.bitterness)
        else:
            self.bitterness_as_target=False   
            self.ui.targetIBUCheckBox.setCheckState(Qt.CheckState.Unchecked)  
            self.ui.targetIBUEdit.setVisible(False)
            self.ui.targetIBULabel.setVisible(False)
            self.ui.calculatedIBUEdit.setText(str(round(self.bitterness,0)))
 
    #--------------------------------------------------------------------------
    def set_style(self):
        self.style=find_style_by_name(self.ui.styleCombo.currentText())
        
        if(self.style):
            self.abv_indicator.setValues(self.style.abv_min,self.style.abv_max,2)
            self.ibu_indicator.setValues(self.style.ibu_min,self.style.ibu_max,0)
            self.og_indicator.setValues(self.style.og_min,self.style.og_max,1.0)
            self.color_indicator.setValues(self.style.srm_min,self.style.srm_max,0)
            try:
                self.abv_indicator.setValue(self.abv)
                self.ibu_indicator.setValue(self.bitterness)
                self.og_indicator.setValue(self.og)
                self.color_indicator.setValue(self.color)
            except:
                pass
        else:
            #print('resetting indicators')
            self.abv_indicator.reset()
            self.ibu_indicator.reset()   
            self.og_indicator.reset() 
            self.cololr_indicator.reset()
            
    #------------------------------------------------------------------------------------
    def attenuation(self):
        attenuation=None
        for ryeast in self.brew_yeasts:
            if attenuation is not None:
                if  ryeast.yeast.attenuation >attenuation:
                    attenuation =ryeast.yeast.attenuation
            else:
                attenuation=ryeast.yeast.attenuation
        return attenuation


    #-----------------------------------------------------------------------------------------------
    def calculate_ABV(self, OG, att, csm, cwm):
       #att is given as 0.80 attenuation of the yeast
       #csm is the quantity of sugar added per liter for bottle carbonation
       #cwm the quantity of water to dilute the carbonation sugar per liter

       #molecular mass of CO2=44,098 , molecular mass of alcool Ethanol is 46,088
       #when 1 g of CO2 is produced and evacuated, we have 1/44,098*46,088=1,04512 g of alcool produced
       #OG -FG represent the quantity of CO2 lost 
       #(OG - FG) *1.04678 represent the quantity (mass) of alcool produced
       # thus ABM is (OG -FG)*1.04678 /FG
       # ABV =ABM /0.789
       #print('OG is '+str(OG))
       OP=BrewUtils.SG_to_Plato(OG)#original platos
       OSugar=OP*OG*1000/100 #g of sugar per liter of wort
       OWater=(OG*1000)-OSugar #g of water per liter of wort
       NSugar=OSugar+csm #new sugar mass per liter after adding carbonation sugar
       NWater=OWater+cwm #new water mass per liter after adding carbonation sugar
       NP=(NSugar/(NSugar+NWater))#new platos after adding carbonation sugar
       NOG=BrewUtils.Plato_to_Sg(NP) #new original gravity
       FG=((NOG-1)*(1-att))+1
       ABV =(NOG-FG)*1.047 /FG /0.789
       return ABV
    
    #-------------------------------------------------------------------------------------
    def add_tab_content(self):
        #------------------------------------------
        try:
            #the public list
            fermentable_list=all_fermentable()
            #this is after load_brew
            self.fermentable_selector=SelectorWidget(fermentable_list,self.brew_fermentables,'fermentable','brew',self)
            vl=QVBoxLayout()
            vl.addWidget(self.fermentable_selector)
            self.ui.groupBox_f.setLayout(vl)
            self.ui.tabWidget.setTabText(0,'Fermentables')
            
            hop_list=all_hop()
            self.hop_selector=SelectorWidget(hop_list,self.brew_hops,'hop','brew',self)
            vh=QVBoxLayout()
            vh.addWidget(self.hop_selector)
            self.ui.groupBox_h.setLayout(vh)
            self.ui.tabWidget.setTabText(1,'Houblons')
            
            yeast_list=all_yeast()
            self.yeast_selector=SelectorWidget(yeast_list,self.brew_yeasts,'yeast','brew',self)
            vy=QVBoxLayout()
            vy.addWidget(self.yeast_selector)
            self.ui.groupBox_y.setLayout(vy)
            self.ui.tabWidget.setTabText(2,'Levures')

            misc_list=all_misc()
            self.misc_selector=SelectorWidget(misc_list,self.brew_miscs,'misc','brew',self)
            vm=QVBoxLayout()
            vm.addWidget(self.misc_selector)
            self.ui.groupBox_m.setLayout(vm)
            self.ui.tabWidget.setTabText(3,'Ingrédients divers')

            rest_list=all_rest()
            self.rest_selector=SelectorWidget(rest_list,self.brew_rests,'rest','brew',self)
            vr=QVBoxLayout()
            vr.addWidget(self.rest_selector)
            self.ui.groupBox_r.setLayout(vr)
            self.ui.tabWidget.setTabText(4,'Programme d\'empâtage')

            self.waterAdjustmentDialog = WaterAdjustmentWidget(self.base_water, self.dilution_water, self.dilution,self.style_water,self.target_water,\
            self.water_for_sparge,self.salt_additions,self.water_adjustment_state,parent=self)
            vw=QVBoxLayout()
            vw.addWidget(self.waterAdjustmentDialog)
            self.ui.groupBox_w.setLayout(vw)
            self.ui.tabWidget.setTabText(5,"Ajustement du profil d'eau")

            self.phAdjuster=PhAdjusterWidget(parent=self)
            vph=QVBoxLayout()
            vph.addWidget(self.phAdjuster)
            self.ui.groupBox_ph.setLayout(vph)
            self.ui.tabWidget.setTabText(6,'Estim. et ajustement du pH')

            self.feedbackDialog=FeedbackWidget(parent=self) 
            vfb=QVBoxLayout()
            vfb.addWidget(self.feedbackDialog)
            self.ui.groupBox_fb.setLayout(vfb)
            self.ui.tabWidget.setTabText(7,'Résultats observés')

            
         
            self.ui.ogHelpButton.setStyleSheet(self.font_style_prefix+'color:white; background-color:green;')
       
        except Exception as ex:
            print('exception dans add_tab content '+str(ex))

    #--------------------------------------------------------------------------------------
    def selectors_show_actual_values(self):
            #to display actual values and units in list views
            self.fermentable_selector.destination_model.set_initialized(True)
            self.fermentable_selector.ui.fermentableMassUnitLabel.setText(' kg')
            self.fermentable_selector.ui.fermentableMassUnitLabel.setVisible(True)
            self.start_from_scratch=False

    #----------------------------------------------------------------------------    
    def set_input_filters(self):  
        accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]{3}"))
        locale=QtCore.QLocale('en')    
        self.first_validator = QDoubleValidator(0.0,2000.0,3)
        self.first_validator.setLocale(locale)   
        self.first_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation) 
        self.ui.batchVolumeEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,2}[\\.][0-9]{1}")))
        
        self.ui.targetOGEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[1]{1}[\\.][0,1]{1}[0-9]{1,2}")))
        self.ui.targetIBUEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,3}[\\.][0-9]{1}")))
        
        self.ui.abvEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-1]{0,1}[0-9]{1}[\\.][0-9]{1}")))
        self.ui.boilTimeEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-2]{0,1}[0-9]{1,2}")))
        self.ui.colorEdit.setValidator(accepted_chars)

    #---------------------------------------------------------------------------------
    def read_form(self):
        #read the form into a Brew object
        validated=True
        message=''
        name=self.nameEdit.text()
        if(name ==''):
            self.nameEdit.setStyleSheet(self.font_style_prefix+"background-color:red; color: white;")
            message += "\n Le nom est incorrect"
            validated=False
        if not self.batch_volume>0:
            self.ui.batchVolumeEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;') 
            message+= "\n le volume du lot est incorrect"
            validated=False   
        additions_temperature=None
        reference_set=False#rest for which mash thickness is defined
        if(self.equipment ):
            equipment=jsonpickle.encode(self.equipment)  
        else:
            self.ui.equipmentCombo.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')  
            message+="\n L'équipment n'est pas défini."
            validated=False     
           
           
        if self.rest_selector.ui.temperatureMethodCombo.currentText() !='':
            temperature_method=self.rest_selector.ui.temperatureMethodCombo.currentText()
        else:
            temperature_method=None
            message += "\nVous n'avez pas sélectionné une méthode de transition des températures dans l'onglet « Programme d'empâtage »"
            validated=False        

        if len(self.rest_selector.destination_model.items)>1:
            for item in self.rest_selector.destination_model.items:
                if item.thickness_reference :
                    reference_set=True  
        else:
            reference_set=True
        if not reference_set:
            message += "\nVous n'avez pas précisé pour quel palier l'épaisseur d'empâtage est définie dans l'onglet « Programme d'empâtage »"
            validated=False
        try: 
            additions_temperature =float(self.rest_selector.ui.additionsTemperatureEdit.text())
        except:
            if temperature_method is not None and temperature_method == 'Infusion':
                message += "\nVous n'avez pas indiqué la température des ajouts d'eau dans l'onglet « Programme d'empâtage »" 
                validated=False


        if self.ui.typeCombo.currentText()!="Extraits":   
                
            try:
                grain_temperature=float(self.rest_selector.ui.grainTemperatureEdit.text())
            except:
                message += "\nVous n'avez pas indiqué la température du grain dans l'onglet « Programme d'empâtage »"
                validated=False   
        else:
            grain_temperature=None
        
       
        #brew_date=self.dateEdit.date().toString('yyyy-MM-dd')
        brew_date=date.fromisoformat(self.dateEdit.date().toString('yyyy-MM-dd'))
        rtype=self.ui.typeCombo.currentText()
        if(rtype ==''):
            self.ui.typeCombo.setStyleSheet(self.font_style_prefix+"background-color:red; color: white;")
            message +="\nLe type de recette n'est pas indiqué"
            validated=False
        style=self.ui.styleCombo.currentText()
        if(style ==''):
            self.ui.styleCombo.setStyleSheet(self.font_style_prefix+"background-color:red; color: white;")
            message +="\n Le style n'est pas précisé"
            validated=False

        if not self.bitterness:
            self.ui.targetIBUEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;') 
            message +="\n La cible d'amertume n'est pas précisée"
            validated=False
        
        if not self.og:
            self.ui.targetOGEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            message += "\n La cible de densité initiale n'est pas précisée"
            validated=False

        if not self.abv:
            self.ui.abvEdit.setStyleSheet(self.font_style_prefix+'border: 2px solid red;')
            #print('bad abv')
            validated=False

        
        try:
            self.color=float(self.ui.colorEdit.text())
            
            #print('bad color')
        except:    
            self.ui.colorEdit.setStyleSheet(self.font_style_prefix+'border: 2px solid red;')
            validated=False

        if not self.boil_time:
            self.ui.boilTimeEdit.setStyleSheet(self.font_style_prefix+'background-color: red; color:white;')
            message += "\n Le temps d'ébullition n'est pas précisé"
            validated=False
        
          
        fermentables=jsonpickle.encode(self.fermentable_selector.destination_model.items)
        if(fermentables == '[]'):
            message +="\n Vous n'avez pas déclaré de fermentables"
            validated=False
        hops=jsonpickle.encode(self.hop_selector.destination_model.items)
        if(hops=='[]'):
            message += "\n Vous n'avez pas déclaré de houblons"
            #print('bad hops')
            validated=False
        yeasts=jsonpickle.encode(self.yeast_selector.destination_model.items)
        if(yeasts == '[]'):
            message += '\n Vous n\'avez pas déclaré de levures'
            validated=False
        miscs=jsonpickle.encode(self.misc_selector.destination_model.items)
        rests=jsonpickle.encode(self.rest_selector.destination_model.items)
        if (rests=='[]' and rtype !='Extraits'):
            message += "\n Vous n'avez pas déclaré de palier d'empâtage"
            validated=False

        


        #for water adjustment
        base_water=jsonpickle.encode(self.waterAdjustmentDialog.base_water)
        dilution_water=jsonpickle.encode(self.waterAdjustmentDialog.dilution_water)
        dilution=self.waterAdjustmentDialog.dilution
        style_water=jsonpickle.encode(self.waterAdjustmentDialog.style_water )
        target_water=jsonpickle.encode(self.waterAdjustmentDialog.target_water)
        water_for_sparge=self.waterAdjustmentDialog.water_for_sparge
        salt_additions=jsonpickle.encode(self.waterAdjustmentDialog.read_salt_additions())
        water_adjustment_state=self.waterAdjustmentDialog.water_adjustment_state
        try:
            pH_target=float(self.phAdjuster.ui.spinBox.value())
        except:
            pH_target=None
        try:
            acid_agent=self.phAdjuster.ui.acidAgentCombo.currentText()   
        except:
            acid_agent=None
        pH_adjuster_enabled=self.phAdjuster.pH_adjuster_enabled
        launched=self.launched
        feedback=self.feedbackDialog.read_observed()
        self.brew_feedback=jsonpickle.decode(feedback) #it is not updated otherwise
        if(validated==True):
            read_item=Brew(self.id,name,equipment,self.batch_volume,brew_date,rtype,style,self.bitterness,round(self.og,3),self.abv,\
                           self.color,self.boil_time,fermentables,hops,yeasts, miscs,rests,grain_temperature,additions_temperature,temperature_method,\
            base_water, dilution_water, dilution, style_water, target_water, water_for_sparge, salt_additions,\
                water_adjustment_state,pH_adjuster_enabled,pH_target,acid_agent,launched,feedback)
            return read_item
        else:
            if message != '':
                self.set_message('failure',message)
            return False

    #-------------------------------------------------------------------------------
    def are_equal_equipments(self,eq1,eq2):
        if eq1.name != eq2.name :
            #print("le nom de l'équipement a changé")
            return False
        if eq1.type !=  eq2.type :
            #print("le type d'équipment a changé")
            return False
        if eq1.hop_absorption != eq2.hop_absorption :
            #print("le taux d'absorption des houblons a changé")
            return False
        if eq1.hop_absorption_reduction_coeff !=eq2.hop_absorption_reduction_coeff :
            #print("le coefficient de réduction du taux d'absorption des houblons a changé")
            return False
        if eq1.grain_absorption != eq2.grain_absorption :
            #print ("le taux d'absorption du grain a changé")
            return False
    
        if eq1.altitude != eq2.altitude :
            #print("l'altitude a changé dans")
            return False

        if eq1.mash_tun_capacity != eq2.mash_tun_capacity :
            #print("l'efficacité du brassage a changé")
            return False
        if eq1.mash_tun_retention !=eq2.mash_tun_retention :
            #print("le volume de rétention de la cuve d'empâtage a changé")
            return False
        if eq1.mash_tun_undergrain != eq2.mash_tun_undergrain :
            #print("le volume sous grain a changé")
            return False
        if eq1.mash_tun_thermal_losses != eq2.mash_tun_thermal_losses :
            #print("les pertes thermiques de la cuve d'empâtage ont changé")
            return False
        if eq1.mash_tun_heat_capacity_equiv != eq2.mash_tun_heat_capacity_equiv :
            #print("la capacité thermique de la cuve d'empâtage a changé")
            return False
        if eq1.mash_thickness != eq2.mash_thickness :
            #print("l'épaisseur d'empâtage a changé")
            return False
        if eq1.mash_efficiency != eq2.mash_efficiency :
            #print("l'efficatité d el'empâtage a changé")
            return False

        if eq1.kettle_capacity != eq2.kettle_capacity :
            #print("la capacité de la bouilloire a changé")
            return False
        if eq1.kettle_retention != eq2.kettle_retention :
            #print("le volume de rétention de la bouilloire a changé")
            return False
        if eq1.kettle_diameter != eq2.kettle_diameter :
            #print("le diamètre de la bouilloire a changé")
            return False
        if eq1.kettle_steam_exit_diameter != eq2.kettle_steam_exit_diameter :
            #print("le diamètre de la sortie de vapeur à changé")
            return False
        if eq1.kettle_evaporation_rate !=eq2.kettle_evaporation_rate :
            #print("le taux d'évaporation a changé")
            return False
        if eq1.kettle_heat_slope !=eq2.kettle_heat_slope :
            #print("la pente de montée en température de la bouilloire a changé")
            return False

        if eq1.fermenter_capacity != eq2.fermenter_capacity :
            #print("la capacité du fermenteur a changé")
            return False
        if eq1.fermenter_retention != eq2.fermenter_retention :
            #print("le volume de rétention du fermenteur a changé")
            return False

        if eq1.cooler_type != eq2.cooler_type :
            #print("le type de refroidisseur a changé")
            return False
        if eq1.cooler_slope != eq2.cooler_slope :
            #print("la pente du refroidisseur a changé")
            return False
        if eq1.cooler_flow_rate != eq2.cooler_flow_rate :
            #print("le débit du refroidisseur a changé")
            return False  
        return True     
    
    #---------------------------------------------------------------------------------
    def check_equipment(self): 
        #check if equipment has not changed in database after the BrewWidget page has been hidden and shown again
       
        DB_equipment=find_equipment_by_name(self.equipment.name)
        if DB_equipment is not None:
   
            if(self.are_equal_equipments(DB_equipment,self.equipment)):
                return
            else:
                print('equipment changed')
                self.set_message('failure',"Votre équipement a été modifié. Rafraichissez-le avec le bouton à flèche circulaire près de sélecteur, puis enregistrez votre session de brassage.",15000)
           
                self.ui.equipmentRefreshButton.setVisible(True)
        else:
            print('equipment not found' )
            self.set_message('failure',"Votre équipement n'est plus en base de données. Peut-être l'avez-vous effacé ou renommé. Veuillez le choisir à nouveau, puis enregistrer votre session de brassage.",15000)
            equipments=all_equipment()
            self.ui.equipmentCombo.clear()
            self.ui.equipmentCombo.addItem('')
            for equipment in equipments:
                print(equipment.name)
                self.ui.equipmentCombo.addItem(equipment.name)
            self.ui.equipmentCombo.setStyleSheet(self.font_style_prefix+'background-color: red')
        
    #---------------------------------------------------------------------------------
    def showEvent(self,event):
        #check if equipment has not changed in database after the BrewWidget page has been hidden and shown again
        if self.equipment is not None:
            self.check_equipment()
            
        event.accept()

    #---------------------------------------------------------------------------
    def compare_equipments(self,eq1,eq2):
        print('Comparing equipments')
        for attr1, value1 in eq1.__dict__.items():
            for attr2,value2 in eq2.__dict__.items():
                if attr1=="_sa_instance_state":
                    continue
                if attr1 ==attr2 and value1 != value2:
                    return False
        return True   
    
    #---------------------------------------------------------------------------------
    def load_brew(self):
        recipe=None
        brew=None
        if(self.id):
            brew=find_brew_by_id(self.id)
       
        if(brew):
            #loading an existing brew
            #save a copy to track changes
            self.title.setText('SESSION DE BRASSAGE')
            self.title.setMinimumWidth(500)
            self.initial_brew=copy.deepcopy(brew)
            self.brew_fermentables=jsonpickle.decode(brew.fermentables)
            self.nameEdit.setText(brew.name)
            self.equipment=jsonpickle.decode(brew.equipment)
            #DB_equipment=find_equipment_by_name(self.equipment.name)#an object      
            #Check of equipment (renamed, deleted or changed ) done in ShowEvenv
            self.ui.equipmentCombo.setCurrentText(self.equipment.name)
            self.ui.batchVolumeEdit.setText(str(brew.batch_volume))
            self.batch_volume=brew.batch_volume
            self.dateEdit.setDate(brew.brew_date)
            self.ui.typeCombo.setCurrentText(brew.rtype)
            self.ui.styleCombo.setCurrentText(brew.style)
            self.set_style()
            self.ui.targetIBUEdit.setText(str(brew.bitterness))
            self.bitterness=brew.bitterness
            self.bitterness_as_target=True
            self.ui.targetIBUCheckBox.setChecked(2)
            self.ui.targetOGEdit.setText(str(round(brew.og,3)))
            self.og=brew.og
            self.og_indicator.setValue(self.og)         
            self.og_as_target=True
            self.ui.targetOGCheckBox.setChecked(2)
            #to be dealt with later
            self.boil_sugar=0
            self.color=brew.color

            self.ui.boilTimeEdit.setText(str(brew.boil_time))
            self.boil_time=brew.boil_time

            #will be used to set the model for each ingredient
            self.brew_fermentables=jsonpickle.decode(brew.fermentables)
            self.brew_hops=jsonpickle.decode(brew.hops)
            self.brew_yeasts=jsonpickle.decode(brew.yeasts)
            self.brew_miscs=jsonpickle.decode(brew.miscs)
            self.brew_rests=jsonpickle.decode(brew.rests)
            self.grain_temperature=brew.grain_temperature
            self.additions_temperature=brew.additions_temperature
            
            self.abv=brew.abv
            attenuation=self.attenuation()
            self.abv=self.calculate_ABV(self.og,attenuation,6,0.015)
            #print('self.abv '+str(self.abv))
           
            self.temperature_method=brew.temperature_method
            self.base_water=jsonpickle.decode(brew.base_water)
            self.dilution_water=jsonpickle.decode(brew.dilution_water)
            self.dilution=brew.dilution
          
            self.style_water=jsonpickle.decode(brew.style_water)
            self.target_water=jsonpickle.decode(brew.target_water)
            self.water_for_sparge=brew.water_for_sparge
            self.salt_additions=jsonpickle.decode(brew.salt_additions)
            self.water_adjustment_state=brew.water_adjustment_state
            self.pH_adjuster_enabled=brew.pH_adjuster_enabled
            self.pH_target=brew.pH_target
            self.acid_agent=brew.acid_agent
            self.launched=brew.launched
            if brew.feedback:
                self.brew_feedback=jsonpickle.decode(brew.feedback)
            

        else:
            #there is no id passed, its a new brew from a recipe
            self.lockButton.setVisible(False)
            if(self.recipe_id):
                recipe=find_recipe_by_id(self.recipe_id)
            if(recipe):
                self.title.setText('CRÉATION D\'UNE SESSION DE BRASSAGE À PARTIR D\'UNE RECETTE')
                self.nameEdit.setText(recipe.name)
                self.nameEdit.setStyleSheet(self.font_style_prefix+"background-color: "+self.enabled_edit_bgcolor+"; color:"+self.enabled_edit_color+";")

                self.ui.typeCombo.setCurrentText(recipe.rtype)
                self.initial_brew.rtype=recipe.rtype
                self.ui.typeCombo.setEnabled(False)
                self.ui.typeCombo.setStyleSheet(self.font_style_prefix+"color:"+self.enabled_edit_color+";background-color:"+self.enabled_edit_bgcolor+";")
                self.equipment=None
                self.initial_brew.equipment=None
                self.batch_volume=None
                self.ui.styleCombo.setCurrentText(recipe.style)
                self.set_style()
                self.initial_brew.style=recipe.style
                

                self.ui.targetIBUEdit.setText(str(recipe.bitterness))
                self.bitterness=recipe.bitterness
                self.initial_brew.bitterness=recipe.bitterness
                self.bitterness_as_target=True
                self.ui.targetIBUCheckBox.setChecked(2)

                self.ui.targetOGEdit.setText(str(round(recipe.og,3)))
                self.og=recipe.og
                self.initial_brew.og=recipe.og
                self.og_as_target=True
                self.ui.targetOGCheckBox.setChecked(2)
                #to be dealt with later
                self.boil_sugar=0
                self.abv=recipe.abv
                self.initial_brew.abv=recipe.abv
                self.initial_brew.color=recipe.color

                self.ui.boilTimeEdit.setText(str(recipe.boil_time))
                self.boil_time=recipe.boil_time
                self.initial_brew.boil_time=recipe.boil_time

                self.brew_fermentables=jsonpickle.decode(recipe.fermentables)
                self.initial_brew.fermentables=recipe.fermentables
                self.brew_hops=jsonpickle.decode(recipe.hops) 
                self.initial_brew.hops=recipe.hops
                self.brew_yeasts=jsonpickle.decode(recipe.yeasts) 
                self.initial_brew.yeasts=recipe.yeasts 
                self.brew_miscs=jsonpickle.decode(recipe.miscs)
                self.initial_brew.miscs=recipe.miscs
                self.brew_rests=jsonpickle.decode(recipe.rests)
                self.initial_brew.rests=recipe.rests
                self.initial_brew.grain_temperature=None
                self.grain_temperature=None
                self.initial_brew.additions_temperature=None
                self.additions_temperature=None
                self.initial_brew.temperature_method=None
                self.temperature_method=None
                self.base_water=None
                self.dilution_water=None
                self.dilution=0
                self.style_water=None
                self.target_water=None
                self.water_for_sparge=None
                self.salt_additions=None
                self.water_adjustment_state=None
                self.pH_adjuster_enabled=None
                self.pH_target=None
                self.acid_agent=None
                self.launched=None

                #Calculator.init_fermentables(self)
            else:
                #create from scratch
                self.title.setText('CRÉATION D\'UNE SESSION DE BRASSAGE SANS RECETTE')
                self.initial_brew=Brew(
                    None,#id\
                    None,#name\ 
                    None,#equipment\
                    None,#batch_volume\
                    None,#brew_date\
                    None,#rtype\ 
                    None,#style\
                    None,#bitterness\
                    None,#og\
                    None,#abv\
                    None,#color\
                    None,#boil_time\
                    None,#fermentables\
                    None,#hops\
                    None,#yeasts\
                    None,#miscs\
                    None,#rests\
                    None,#grain_temperature
                    None,#additions_temperature
                    None,#temperature_method
                    None,#base_water\
                    None,#dilution_water\
                    None,#dilution\
                    None,#style_water\
                    None,#target_water\
                    None,#water_for_sparge\
                    None,#salt_additions\
                    None,#water_adjustment_state
                    None,#pH_target
                    None,#acid_agent
                    None,#feedback\
                    )
                self.nameEdit.setText('')
                self.ui.equipmentCombo.setCurrentText('')
                self.equipment=None
                self.ui.batchVolumeEdit.setText('')
                self.batch_volume=None
                self.ui.typeCombo.setCurrentText('')
                self.ui.styleCombo.setCurrentText('')
                
                self.ui.targetIBUEdit.setText('')
                self.bitterness=None
                self.bitterness_as_target=False
                self.ui.targetIBUCheckBox.setChecked(0)
                self.ui.targetIBUEdit.setVisible(False)

                self.ui.targetOGEdit.setText('')
                self.og=None
                self.boil_sugar=0
                self.og_as_target=False
                self.ui.targetOGCheckBox.setChecked(0)
                self.ui.targetOGEdit.setVisible(False)
                self.start_from_scratch=True
                
                self.ui.abvEdit.setText('')
                self.abv=None
                self.ui.abvEdit.setEnabled(False)
                self.ui.colorEdit.setText('')
                self.color=None

                self.ui.boilTimeEdit.setText('')
                self.boil_time=None
                self.brew_fermentables=[]
                self.brew_hops=[]
                self.brew_yeasts=[]  
                self.brew_miscs=[]
                self.brew_rests=[]
                self.grain_temperature=None
                self.additions_temperature=None
                self.temperature_method=None
        
                self.base_water=None
                self.dilution_water=None
                self.dilution=0
                self.style_water=None
                self.target_water=None
                self.water_for_sparge=None
                self.salt_additions=None
                self.water_adjustment_state=None
                self.pH_adjuster_enabled=None
                self.pH_target=None
                self.acid_agent=None
                self.launched=None
        if self.ui.typeCombo.currentText()=="Extraits":
            self.initial_hide_for_extract_type()   

    # ----------------------------------------------------------------------------------------------         
    def add(self):
        #add or update a Brew
        read_brew=self.read_form()

        if(read_brew):
            
            if(self.id):
                read_brew.id=self.id
                print('updating a brew in add')
                result=update_brew(read_brew)

                if result =="OK":
                    #to reset changes to no change
                    self.initial_brew=copy.deepcopy(read_brew)
                    self.set_message('success','La session de brassage a été correctement sauvegardée')

                else:
                    self.set_message('failure', result)     
            else:
                print('adding a brew in add')
                print(str(read_brew.id))
                result=add_brew(read_brew)
                if isinstance(result,int):
                    self.lockButton.setVisible(True)
                    self.id=result
                    #to reset changes to no change
                    self.initial_brew=copy.deepcopy(read_brew)
                    self.set_message('success','La session de brassage a été correctement sauvegardée')
                    self.parent.model.brews.append(read_brew)
                    self.parent.model.layoutChanged.emit()
                else:
                    if('Duplicate entry' in result):
                        self.set_message('failure','Une session de brassage de même nom et de même date de brassage existe déjà. Merci de modifier l\'un des deux.')
                    else:    
                        self.set_message('failure', result)    

    #-----------------------------------------------------------------------------------          
    def set_message(self,style,text,time=500):
        print(text)
        if style =="success":
            messagePopup=QMessageBox(QMessageBox.Icon.Information,style,text,QMessageBox.StandardButton.Ok,self,Qt.WindowType.FramelessWindowHint)
            messagePopup.setStyleSheet("background-color:green;color: white;font-weight:bold")
        else:
             messagePopup=QMessageBox(QMessageBox.Icon.Critical,style,text,QMessageBox.StandardButton.Ok,self,Qt.WindowType.FramelessWindowHint)
             messagePopup.setStyleSheet("background-color:red;color: white;font-weight:bold")
        messagePopup.exec()
        
    #--------------------------------------------------------------------------------------
    def clean_edit(self,what):
        #restore initial style for previously unaccepted edit
        match what:
            case 'name':
                self.nameEdit.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.enabled_edit_color+';')   
            #case 'batch_volume':
                self.ui.batchVolumeEdit.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.enabled_edit_color+';')   
            case 'type':
                self.ui.typeCombo.setStyleSheet(self.font_style_prefix+'background-color:'+self.enabled_edit_bgcolor+'; color:'+self.enabled_edit_color+';')    
            case 'style':
                self.ui.styleCombo.setStyleSheet(self.font_style_prefix+'background-color:'+self.enabled_edit_bgcolor+'; color:'+self.enabled_edit_color+';')     
            case 'bitterness':
                self.ui.targetIBUEdit.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.enabled_edit_color+';')   
            case 'equipment':
                self.ui.equipmentCombo.setStyleSheet(self.font_style_prefix+'color:'+self.enabled_edit_color+'; background-color:'+self.enabled_edit_bgcolor+'; border: 1px solid '+self.enabled_edit_color+';')  
            case 'color':
                self.ui.colorEdit.setStyleSheet("border: 1px solid gray;")

    #---------------------------------------------------------------------------
    def balise(self,balise,text):
        return "<"+balise+">"+text+"</"+balise+">"
    
    #---------------------------------------------------------------------------
    def create_brew_sheet(self):
        msgBox=ConfirmationDialog()
        msgBox.setTitle('Création de la fiche de session')
        
        msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
        msgBox.setMessage("La fiche de session décrira l'état de la session enregistrée, pas forcément ce que vous voyez à l'écran. \nVoulez-vous sauvegarder la session auparavant pour prendre en compte les derniers changements. ?") 
        msgBox.setConfirmButtonText("Oui. Sauvegardez d'abord")
        msgBox.setCancelButtonText("Non.Imprimer ce qui est sauvegardé même si des modifications ont été faites à l'écran.")
        confirm=msgBox.exec()   
        if(confirm == 1):
            print("sauvegarde demandée")
            self.add()
        try:
            export_dlg=ExportBrewSheet(self)
            export_dlg.exec()
        except Exception as e:
            self.set_message("failure","Une exception s’est produite lors de l’impression de la feuille de session \n"+str(e))
        
           
        
