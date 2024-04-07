'''def set_messagedef set_message
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from RecipeWidgetBase import Ui_RecipeWidget as recipeWgt
from BrewWidget import BrewWidget
from PyQt6.QtWidgets import QDialog,QLabel,QHBoxLayout,QVBoxLayout,QWidget,QFrame,QPushButton,QGroupBox,QMessageBox
from PyQt6 import QtCore,QtWidgets
from PyQt6.QtCore import Qt, QSize
#from database.profiles.equipment import all_equipment, update_equipment,Equipment, add_equipment,delete_equipment, find_equipment_by_id
from database.fermentables.fermentable import all_fermentable
from database.hops.hop import all_hop
from database.yeasts.yeast import all_yeast
from database.miscs.misc import all_misc
from database.profiles.style import all_style,find_style_by_name
from database.profiles.rest import all_rest
from database.recipes.recipe import Recipe,all_recipe,update_recipe,add_recipe,delete_recipe,find_recipe_by_id,find_recipe_by_name
from dateUtils import DateUtils
from PyQt6.QtCore import Qt,QRegularExpression,pyqtSignal,QObject
from database.commons.country import all_country,find_country_by_code
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator,QIntValidator,QPalette,QColor
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon
from LevelIndicator import LevelIndicator
from SelectorWidget import SelectorWidget
from RecipeFermentable import RecipeFermentable
import  datetime
import jsonpickle
from ConfirmationDialog import ConfirmationDialog
import copy,json
from BrewUtils import BrewUtils
from HelpMessage import HelpMessage
from SignalObject import SignalObject
import os
from pathlib import Path
class RecipeCommunication(QObject):
    calculate=pyqtSignal(SignalObject)

class RecipeWidget(QWidget):
    def __init__(self, id,parent=None):
        super().__init__(parent)
        self.ui =recipeWgt()
        self.ui.setupUi(self)
        self.parent=parent  
        self.id=id
        self.c=RecipeCommunication()
        self.currentStackIndex=None
        self.initial_recipe=Recipe(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
        dirname = os.path.dirname(__file__)
        self.helpPath=os.path.join(dirname,'help/')
        self.icon_path='base-data/icons/'
        self.icon_size=QSize(32,32)
        self.this_file_path=Path(__file__).parent

        
        today=datetime.date.today()
        current_year=today.year

        #-----------------------------------------
        #complete GUI
        self.disabled_edit_bgcolor='Lavender'
        self.disabled_edit_color='#666'
        self.ui.abvEdit.setStyleSheet('background-color:'+self.disabled_edit_bgcolor+';color:'+self.disabled_edit_color+';')
        self.ui.colorEdit.setStyleSheet('background-color:'+self.disabled_edit_bgcolor+';color:'+self.disabled_edit_color+';')
        self.ui.abvHelpButton.setStyleSheet('background-color:green; color:white;')
        self.ui.colorHelpButton.setStyleSheet('background-color:green; color:white;')
        toolbarLayout=QHBoxLayout()
        self.closeButton=QPushButton()
        self.closeButton.setIcon(QIcon(self.icon_path+'close-square-svgrepo-com.svg'))
        self.closeButton.setIconSize(self.icon_size)
        self.closeButton.setToolTip("Fermer la recette")
        self.saveButton=QPushButton()
        self.saveButton.setIcon(QIcon(self.icon_path+'save-left-svgrepo-com.svg'))
        self.saveButton.setIconSize(self.icon_size)
        self.saveButton.setToolTip("Sauvegarder la recette")
        self.deleteButton=QPushButton()
        self.deleteButton.setIcon(QIcon(self.icon_path+'trash-can-svgrepo-com.svg'))
        self.deleteButton.setIconSize(self.icon_size)
        self.deleteButton.setToolTip("Supprimer la recette")
        self.brewButton=QPushButton()
        self.brewButton.setIcon(QIcon(self.icon_path+'cauldron-svgrepo-com.svg'))
        self.brewButton.setIconSize(self.icon_size)
        self.brewButton.setToolTip('Brasser cette recette')
        if not self.id:
            self.brewButton.setVisible(False)

        title=QLabel()
        title.setText('RECETTE EN ÉDITION ')
        title.setStyleSheet('font-size: 24px; font-weight:bold; color:black;')
        toolbarLayout.addWidget(title)
        spacerItem = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        spacerItemSmall = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        toolbarLayout.addItem(spacerItem)

        toolbarLayout.addWidget(self.brewButton)
        toolbarLayout.addWidget(self.saveButton)
        toolbarLayout.addWidget(self.deleteButton)
        toolbarLayout.addWidget(self.closeButton)
 
        toolbarLayout.setSpacing(20)
        self.ui.toolbarGroupBox.setLayout(toolbarLayout)
        self.style=None
        
        self.ui.typeCombo.addItem('')
        self.ui.typeCombo.addItem('Tout grain')
        self.ui.typeCombo.addItem('Empâtage partiel')
        self.ui.typeCombo.addItem('Extraits')
         
      

        #----------------------------------------
        #SET VARIOUS COMBO
        self.ui.targetOGUnitCombo.addItem('SG')
        self.ui.targetOGUnitCombo.addItem('Platos')
        self.styles=all_style()
        self.ui.styleCombo.addItem('')
        for s in self.styles:
            self.ui.styleCombo.addItem(s.name)
        
        #load the recipe if id passed    
        self.load_recipe()
        self.set_selectors()
        self.set_validators()
        self.set_connections()

    def initial_hide_for_extract_type(self):
      
        self.ui.tabWidget.setTabVisible(4,False)
    #---------------------------------------------------------
    def showEvent(self,e):
        self.fermentable_selector.refresh_source()
        self.hop_selector.refresh_source()
        self.yeast_selector.refresh_source()
        self.misc_selector.refresh_source()
        
    #------------------------------------------------------
    def set_selectors(self):
        fermentable_list=all_fermentable()
        self.fermentable_selector=SelectorWidget(fermentable_list,self.recipe_fermentables,'fermentable','recipe',self)
        vl=QVBoxLayout()
        vl.addWidget(self.fermentable_selector)
        self.ui.groupBox_0.setLayout(vl)
        self.ui.tabWidget.setTabText(0,'Fermentables')
        self.fermentable_selector.ui.fermentableMassUnitLabel.setVisible(False)#only proportions matter in a recipe
        
        hop_list=all_hop()
        self.hop_selector=SelectorWidget(hop_list,self.recipe_hops,'hop','recipe',self)
        vh=QVBoxLayout()
        vh.addWidget(self.hop_selector)
        self.ui.groupBox_1.setLayout(vh)
        self.ui.tabWidget.setTabText(1,'Houblons')

        yeast_list=all_yeast()
        self.yeast_selector=SelectorWidget(yeast_list,self.recipe_yeasts,'yeast','recipe',self)
        vy=QVBoxLayout()
        vy.addWidget(self.yeast_selector)
        self.ui.groupBox_2.setLayout(vy)
        self.ui.tabWidget.setTabText(2,'Levures')
     
        rest_list=all_rest()
        self.rest_selector=SelectorWidget(rest_list,self.recipe_rests,'rest','recipe',self)
        vr=QVBoxLayout()
        vr.addWidget(self.rest_selector)
        self.ui.groupBox_4.setLayout(vr)
        self.ui.tabWidget.setTabText(4,'Programme d\'empâtage')

        misc_list=all_misc()
        self.misc_selector=SelectorWidget(misc_list,self.recipe_miscs,'misc','recipe',self)
        vm=QVBoxLayout()
        vm.addWidget(self.misc_selector)
        self.ui.groupBox_3.setLayout(vm)
        self.ui.tabWidget.setTabText(3,'Divers ingrédients')
    #-------------------------------------------------------
    def set_validators(self):
        #accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]+([eE][-+]?[0-9]+)?"))   
        accepted_chars = QRegularExpressionValidator(QRegularExpression("[-+]?[0-9]*[\\.]?[0-9]{3}"))
        locale=QtCore.QLocale('en')   
        #self.abv_validator =QDoubleValidator(0.0,20.0,1)
        self.abv_validator= QDoubleValidator(1.0,20.0,1)
        self.ui.abvEdit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{1,2}[\\.]?[0-9]{0,1}"))) 
        self.abv_validator.setLocale(locale) 
        self.abv_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)

        self.first_validator = QDoubleValidator(0.0,2000.0,3)
        self.first_validator.setLocale(locale)   
        self.first_validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)

        self.ui.bitternessEdit.setValidator(accepted_chars)
        self.ui.targetOGEdit.setValidator(accepted_chars)
        self.ui.boilTimeEdit.setValidator(accepted_chars)
        self.ui.colorEdit.setValidator(accepted_chars)

    #-------------------------------------------------------
    def set_connections(self):
        self.parent.parent.keyboard_signal.connect(self.handle_shortcuts)
        self.c.calculate.connect(self.handle_calculate_signal)
        self.brewButton.clicked.connect(self.create_brew)
        self.saveButton.clicked.connect(self.add)
        self.closeButton.clicked.connect(self.close)
        self.deleteButton.clicked.connect(self.delete)
        self.ui.nameEdit.textChanged.connect(lambda :self.clean_edit('name'))
        self.ui.authorEdit.textChanged.connect(lambda :self.clean_edit('author'))
        self.ui.typeCombo.currentIndexChanged.connect(self.recipe_type_changed)
        self.ui.styleCombo.currentIndexChanged.connect(lambda :self.clean_edit('style'))
        self.ui.bitternessEdit.textChanged.connect(lambda :self.clean_edit('bitterness'))
        self.ui.targetOGEdit.textChanged.connect(self.calculate_attenuation_and_ABV)#(lambda :self.clean_edit('og'))
        self.ui.boilTimeEdit.textChanged.connect(lambda :self.clean_edit('boil_time'))
        self.ui.abvEdit.textChanged.connect(lambda :self.clean_edit('abv'))
        self.ui.colorEdit.textChanged.connect(lambda :self.clean_edit('color'))
        self.ui.colorHelpButton.clicked.connect(lambda:self.show_contextual_help('color'))
        self.ui.abvHelpButton.clicked.connect(lambda:self.show_contextual_help('abv'))

    #----------------------------------------------
    def handle_shortcuts(self,obj):
        match obj.value:
            case "toggle_header":
                self.toggle_header_view()
        #---------------------------------------------------------------------
    def toggle_header_view(self):
        if self.ui.headerGroupBox.isVisible():
            self.ui.headerGroupBox.setVisible(False)
        else:
            self.ui.headerGroupBox.setVisible(True)      


    #--------------------------------------------------
    def handle_calculate_signal(self, obj):
        match obj.name:
            case 'fermentable':
                self.recipe_fermentables=self.fermentable_selector.destination_model.items
                self.average_fermentable_yield()
            case 'yeast':
                #not set before the first saving 
                self.recipe_yeasts=self.yeast_selector.destination_model.items
                self.calculate_attenuation_and_ABV()
    #---------------------------------------------------------------------   
    def recipe_type_changed(self):
        self.clean_edit("type")
        if self.ui.typeCombo.currentText()=="Extraits":
            self.ui.tabWidget.setTabVisible(4,False) 
            self.fermentable_selector.remove_all_fermentables()
            
        else:
            self.ui.tabWidget.setTabVisible(4,True)

    def setCurrentStackIndex(self,val):
        self.currentStackIndex=val   
    #----------------------------------------------------------------------
        #------------------------------------------------------------------
    def show_contextual_help(self,what):
        filename=(self.this_file_path/"help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
        helpPopup=HelpMessage()
        match what:
            case 'abv':
                helpPopup.set_title("À propos du taux d'alcool en volume visé")
                filename=(self.this_file_path/"help/ABVHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
            case 'color':
                helpPopup.set_title("À propos de la couleur visée")
                filename=(self.this_file_path/"help/ColorHelp.html").resolve()
                text=open(filename,'r',encoding="utf-8").read()
                helpPopup.set_message(prepend+text)
        helpPopup.exec()
    #---------------------------------------------------------------
    def delete(self):
             #before deletion
        current_recipe=find_recipe_by_id(self.id)#imported function
        if current_recipe:
            msgBox=ConfirmationDialog()
            msgBox.setTitle('Confirmer suppression')
            
            msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
            msgBox.setMessage('Vous êtes sur le point de supprimer une recette. Cette suppression sera définitive. \n Confirmez-vous la suppression ?') 
            msgBox.setCancelButtonText('Non. Ne pas supprimer')
            msgBox.setConfirmButtonText('Oui. Supprimer.')
            confirm=msgBox.exec()   
            if(confirm == 1):

                result = delete_recipe(self.id)#imported function
                if result == 'OK':
                    self.parent.recipes=all_recipe()
                    self.parent.model.recipes=all_recipe()
                    self.parent.model.layoutChanged.emit()  
                    self.close()
                else:
                    self.set_message('failure', result)
        else:
            self.set_message('failure', "Cette recette n'existe pas encore en base de données. Contentez-vous de la fermer si vous ne voulez pas la créer.")        
    #-------------------------------------------------------------------
    def close(self):
        index=self.parent.parent.swapWidget('brew')
        self.parent.parent.stackedWidget.setCurrentIndex(index)
    #----------------------------------------------------------------------
    def create_brew(self):
        new_brew=BrewWidget(None,self.id,self.parent.parent.brewListWidget)#in order to being able to update the list
        new_index=self.parent.parent.brewTabWidget.addTab(new_brew,new_brew.nameEdit.text())
        self.parent.parent.brewTabWidget.setCurrentIndex(new_index)
        #retrieve the added widget
        widget=self.parent.parent.stackedWidget.widget(1)
        if(widget.__class__.__name__)=='BrewListWidget':
            self.parent.parent.swapWidget('brew',self.parent.parent.brewTabWidget)

        self.parent.parent.stackedWidget.setCurrentIndex(1)
        self.parent.parent.actionToolRecipes.setChecked(False)
        self.parent.parent.actionToolBrews.setChecked(True)
        
    #----------------------------------------------------------------------------------------------
    def read_form(self):
        #read the form and check acceptability of values
        validated=True
        name=self.ui.nameEdit.text()
        if(name ==''):
            self.ui.nameEdit.setStyleSheet("background-color:red;color: white;")
            print('name error')
            validated=False
        author=self.ui.authorEdit.text()
        if(author ==''):
            self.ui.authorEdit.setStyleSheet("background-color:red;color: white;")
            print('author error')
            validated=False
        rtype=self.ui.typeCombo.currentText()
        if(rtype ==''):
            self.ui.typeCombo.setStyleSheet("background-color:red;color: white;")
            print('type error')
            validated=False
        style=self.ui.styleCombo.currentText()
        if(style ==''):
            self.ui.styleCombo.setStyleSheet("background-color:red;color: white;")
            print('style error')
            validated=False
        bitterness=self.ui.bitternessEdit.text()
        r=self.first_validator.validate(bitterness,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.bitternessEdit.setStyleSheet("background-color: red;color: white;")
            print('bitterness error')
            validated=False
        og=self.ui.targetOGEdit.text()
        r=self.first_validator.validate(og,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.targetOGEdit.setStyleSheet("background-color: red;color: white;")
            print('og error')
            validated=False
        abv=(self.ui.abvEdit.text())
        r=self.abv_validator.validate(abv,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.abvEdit.setStyleSheet("border: 2px solid red")
            print("Bad ABV")
            validated=False
        color=self.ui.colorEdit.text()
        r=self.first_validator.validate(color,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            print('color error')
            validated=False
        else:
            print("og correct")
        boil_time=self.ui.boilTimeEdit.text()
        r=self.first_validator.validate(boil_time,0)
        if(r[0] != QtGui.QValidator.State.Acceptable):
            self.ui.boilTimeEdit.setStyleSheet("background-color:red ;color: white;")
            print('boil time error')
            validated=False
   
        fermentables=jsonpickle.encode(self.fermentable_selector.destination_model.items)
        if(fermentables == '[]'):
            self.set_message('failure',"Vous n'avez pas déclaré de fermetables")
            print('fermentables error')
            validated=False
        hops=jsonpickle.encode(self.hop_selector.destination_model.items)
        if(hops=='[]'):
            self.set_message('failure',"Vous n'avez pas déclaré de houblons")
            print('hops error')
            validated=False
        miscs=jsonpickle.encode(self.misc_selector.destination_model.items)
   
        yeasts=jsonpickle.encode(self.yeast_selector.destination_model.items)
        if(yeasts == '[]'):
            self.set_message('failure',"Vous n'avez pas déclaré de levures")
            print('yeast error')
            validated=False
        rests=jsonpickle.encode(self.rest_selector.destination_model.items)
        if(rests=='[]' and rtype !='Extraits'):
            self.set_message('failure','Vous n\avez pas déclaré de palier d\'empâtage')
            print('rest error')
            validated=False
        if(validated==True):
            print("VValidated true")
            read_item=Recipe(self.id,name,author,rtype,style,bitterness,og,abv,color,boil_time,fermentables,hops,yeasts, miscs,rests)
            return read_item
        else:
            self.calculate_ABV
            return False
    


    #------------------------------------------------------------------------------------
    def attenuation(self):
        attenuation=None
        if self.recipe_yeasts:
            for ryeast in self.recipe_yeasts:
                if attenuation is not None:
                    if  ryeast.yeast.attenuation >attenuation:
                        attenuation =ryeast.yeast.attenuation
                else:
                    attenuation=ryeast.yeast.attenuation
        else:
            pass
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

    #----------------------------------------------------------------------------   
    def calculate_attenuation_and_ABV(self):
        self.average_fermentable_yield()
        attenuation=self.attenuation()
        try:
            self.og=float(self.ui.targetOGEdit.text())
        except:
            
            self.og=None    
        if attenuation is not None and self.og is not None:
            self.ui.abvEdit.setText(str(round(self.calculate_ABV(self.og,attenuation,6,45)*100,1)))#we suppose sugar that, for carbonation, sugar will be diluted in 45 g of water
        else:
            self.ui.abvEdit.setText('')
        self.clean_edit('og')    
    #-----------------------------------------------------------------------------
    def average_fermentable_yield(self):
        total_MCU=0
        total_quantity=0#declared in the recipe, proportion not true value
        average_potential=0
        for f in self.fermentable_selector.destination_model.items:
            total_quantity+=f.quantity
        if total_quantity>0: #to avoid division by zero
            for f in self.fermentable_selector.destination_model.items:
                if f.usage =='empâtage' or f.usage=='ébullition':
                    average_potential+=f.fermentable.potential * f.quantity/total_quantity
                else:
                    average_potential+=f.steep_potential * f.quantity/total_quantity
            
            try:
                og=float(self.ui.targetOGEdit.text())
                
                total_extract=BrewUtils.sugar_mass_from_SG_and_volume(og,19)#we assume volume is 19 liters /5 gal.
                print('total_extract is '+str(total_extract))
                total_extract_from_efficiency=total_extract/72*100 #we consider efficiency of the brewhouse at 72% 
                print('total_extract from eff  is '+str(total_extract_from_efficiency))
                total_true_quantity=total_extract_from_efficiency/average_potential*100
                print('total_true_quantity is '+str(total_true_quantity))

                for f in self.fermentable_selector.destination_model.items:
                    f_actual_quantity=f.quantity*total_true_quantity/total_quantity
                    print('f_actual_quantity '+str(f_actual_quantity))
                    total_MCU+=(4.23*f.fermentable.color*f_actual_quantity)/19
                color=  2.939 * (total_MCU**0.6859)  
                print('color is '+str(color))

        
            
                print('quantity : '+str(total_quantity))
                print('average potential : '+str(average_potential))
                self.ui.colorEdit.setText(str(int(color)))
            except:
                pass    
        else:
            self.ui.colorEdit.setText('')    

    def load_recipe(self):
        #load a recipe or create a new one
        recipe=find_recipe_by_id(self.id)
        
        if(recipe):
            #save a copy to track changes
            self.initial_recipe=copy.deepcopy(recipe)
            self.ui.nameEdit.setText(recipe.name)
            self.ui.authorEdit.setText(recipe.author)
            self.ui.typeCombo.setCurrentText(recipe.rtype)
            self.ui.styleCombo.setCurrentText(recipe.style)
            self.ui.bitternessEdit.setText(str(recipe.bitterness)) 
            self.ui.targetOGEdit.setText(str(recipe.og)) 
            
            self.ui.abvEdit.setText(str(recipe.abv))  #will be estimated from OG and yeast attenuation in session
            self.ui.colorEdit.setText(str(recipe.color)) 
            self.ui.boilTimeEdit.setText(str(recipe.boil_time)) 
            #will be used to set the model for each ingredient
            
            self.recipe_fermentables=jsonpickle.decode(recipe.fermentables) #returns an array
            self.recipe_hops=jsonpickle.decode(recipe.hops) 
            self.recipe_yeasts=jsonpickle.decode(recipe.yeasts) 
            self.recipe_miscs=jsonpickle.decode(recipe.miscs) 
            self.recipe_rests=jsonpickle.decode(recipe.rests) 
            attenuation=self.attenuation()
            if attenuation is not None and recipe.og is not None:
                self.ui.abvEdit.setText(str(round(self.calculate_ABV(recipe.og,attenuation,6,45)*100,1)))#we suppose sugar that, for carbonation, sugar will be diluted in 45 g of water

            
        else:
            self.recipe_fermentables=None    
            self.recipe_hops=None
            self.recipe_rests=None
            self.recipe_miscs=None
            self.recipe_yeasts=None
        if self.ui.typeCombo.currentText()=="Extraits":
            self.ui.tabWidget.setTabVisible(4,False)
        else:
            self.ui.tabWidget.setTabVisible(4,True)
    #---------------------------------------------------------------------------------
    def close(self):
        if(self.id):
            #the recipe has already been save at least once
            r=self.read_form() 
            #fermentables have already been encoded ,come back to list
            fs=jsonpickle.decode(r.fermentables)
            fis=jsonpickle.decode(self.initial_recipe.fermentables)
            #hops have already been encoded ,come back to list
            hs=jsonpickle.decode(r.hops)
            his=jsonpickle.decode(self.initial_recipe.hops)
            #yeasts have already been encoded ,come back to list
            ys=jsonpickle.decode(r.yeasts)
            yis=jsonpickle.decode(self.initial_recipe.yeasts) 
            #miscs have already been encoded ,come back to list
            ms=jsonpickle.decode(r.miscs)
            mis=jsonpickle.decode(self.initial_recipe.miscs)  
            #rests have already been encoded ,come back to list
            rs=jsonpickle.decode(r.rests)
            ris=jsonpickle.decode(self.initial_recipe.rests)

            #check if changes have been brought to the recipe
            if  BrewUtils.are_equal_recipe_commons(r,self.initial_recipe) \
            and BrewUtils.are_equal_fermentables(fs,fis)\
            and BrewUtils.are_equal_hops(hs,his)\
            and BrewUtils.are_equal_yeasts(ys,yis)\
            and BrewUtils.are_equal_miscs(ms,mis)\
            and BrewUtils.are_equal_rests(rs,ris):
                #everything has been saved, we can close safely
                index=self.parent.parent.swapWidget('recipe')
                self.parent.parent.stackedWidget.setCurrentIndex(index)
            else:
                msgBox=ConfirmationDialog()
                msgBox.setTitle('Confirmer fermeture')
                
                msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
                msgBox.setMessage('Des changements ont été apportés à cette recette. \nEn confirmant la fermeture, ces changements seront abandonnés.\n Confirmez-vous la fermeture sans avoir sauvegardé?') 
                msgBox.setCancelButtonText('Non. Ne pas fermer')
                msgBox.setConfirmButtonText('Oui. Fermer sans sauvegarder.')
                confirm=msgBox.exec()  
                if(confirm == 1):
                    index=self.parent.parent.swapWidget('recipe')
                    self.parent.parent.stackedWidget.setCurrentIndex(index)
        else:
            #the recipe has never been saved (creation) 
            msgBox=ConfirmationDialog()
            msgBox.setTitle('Confirmer fermeture')
            
            msgBox.setIcon(self.icon_path+'alert-48px-svgrepo-com.svg')
            msgBox.setMessage("Votre recette n'a pas encore été enregistrée en base de données. Si vous ne la sauvegardez pas, elle sera perdue. \n Confirmez-vous l'abandon de cette recette'?") 
            msgBox.setCancelButtonText('Non. Ne pas fermer')
            msgBox.setConfirmButtonText('Oui. Abandonner la recette.')
            confirm=msgBox.exec()   
            if(confirm == 1):
                index=self.parent.parent.swapWidget('recipe')
                self.parent.parent.stackedWidget.setCurrentIndex(index)
            

    #----------------------------------------------------------------------------------
    def add(self):
        r=self.read_form()
        if(r):
            if(self.id):
                r.id=self.id
                result=update_recipe(r)
                if result == 'OK':
                    #to reset changes to no change
                    self.initial_recipe=copy.deepcopy(r)
                    self.set_message('success','La recette a été correctement sauvegardée')
                else:
                    self.set_message('failure', result),
            else:
                result=add_recipe(r)
                if(result == 'OK'):   
                    #to reset changes to no change
                    self.initial_recipe=copy.deepcopy(r)
                    self.set_message('success','La recette a été correctement sauvegardée')
                    
                    
                    self.parent.model.recipes.append(r)
                    self.parent.model.layoutChanged.emit()
                    recip=find_recipe_by_name(r.name)
                    if recip:
                        self.id=recip.id
                        self.brewButton.setVisible(True)
                else:   
                    self.set_message('failure', result),
        
        #self.parent.ui.listView.recipes.append(r)
        #self.parent.model.layoutChanged.emit()

    #--------------------------------------------------------------------------------------------------

    def set_message(self,style,text,time=500):
        print(text)
        if style =="success":
            messagePopup=QMessageBox(QMessageBox.Icon.Information,style,text,QMessageBox.StandardButton.Ok,self,Qt.WindowType.FramelessWindowHint)
            messagePopup.setStyleSheet("background-color:green;color: white;font-weight:bold")
        else:
             messagePopup=QMessageBox(QMessageBox.Icon.Critical,style,text,QMessageBox.StandardButton.Ok,self,Qt.WindowType.FramelessWindowHint)
             messagePopup.setStyleSheet("background-color:red;color: white;font-weight:bold")
        messagePopup.exec()
        
    #--------------------------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------------------------
    def clean_edit(self,what):
       
        match what:
            case 'name':
                self.ui.nameEdit.setStyleSheet('background-color:white; color: black;')    
            case 'author':
                self.ui.authorEdit.setStyleSheet('background-color:white; color: black;') 
            case 'type':
                self.ui.typeCombo.setStyleSheet('background-color:white; color: black;')  
            case 'style':   
                self.ui.styleCombo.setStyleSheet('background-color:white; color: black;')   
            case 'bitterness':
                self.ui.bitternessEdit.setStyleSheet('background-color:white; color: black;')  
            case 'og':
                self.ui.targetOGEdit.setStyleSheet('background-color:white; color: black;') 
                self.ui.abvEdit.setStyleSheet("border: 1px solid gray")
            case 'boil_time':
                self.ui.boilTimeEdit.setStyleSheet('background-color:white; color: black;')  
        
