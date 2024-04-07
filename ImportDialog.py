'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from ImportDialogBase import Ui_ImportDialog as theDlg
from PyQt6.QtWidgets import QDialog,QLabel,QHBoxLayout,QVBoxLayout,QWidget,QFrame,QPushButton,QGroupBox,QFileDialog
from PyQt6 import QtCore
from database.profiles.equipment import all_equipment, update_equipment,Equipment, add_equipment,delete_equipment, find_equipment_by_id
from database.fermentables.fermentable import Fermentable,all_fermentable,add_fermentable
from database.fermentables.fermentable_brand import FBrand, all_fbrand,add_fbrand,find_fbrand_by_name
from database.hops.hop import Hop, all_hop,add_hop
from database.hops.hop_suppliers import HSupplier, all_hsupplier,add_hsupplier,find_hsupplier_by_name
from database.miscs.misc import Misc, add_misc

from database.yeasts.yeast import YBrand, add_ybrand,all_ybrand,find_ybrand_by_name
from database.yeasts.yeast import Yeast, all_yeast,add_yeast
from database.profiles.style import Style,all_style,find_style_by_name,add_style
from database.commons.country import Country, add_country, find_country_by_name
from database.recipes.recipe import Recipe,all_recipe,update_recipe,add_recipe,delete_recipe,find_recipe_by_id
from database.profiles.water import Water,add_water as add_water_source
from database.profiles.rest import Rest,add_rest
from database.profiles.watertarget import WaterTarget,add_water as add_water_target
from BrewWidget import Communication
from dateUtils import DateUtils
from PyQt6.QtCore import Qt,QRegularExpression,QTimer,QFile,QTextStream
from parameters import equipment_type,cooler_type,fermentable_forms, fermentable_categories, raw_ingredients
from database.commons.country import all_country,find_country_by_code
from datetime import date
import chardet,os
#from help.RecipeHelp import recipe_help
from pathlib import Path

class ImportDialog(QDialog):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =theDlg()
        self.ui.setupUi(self)
        self.what=None
        self.filename=None
        self.ui.dialogTitle.setStyleSheet('font-weight: 600;font-size:16;')
        self.ui.comboBox.addItem('')
        self.ui.comboBox.addItem('pays')
        self.ui.comboBox.insertSeparator(2)
        self.ui.comboBox.addItem('marques de fermentables')
        self.ui.comboBox.addItem('fermentables')
        self.ui.comboBox.insertSeparator(5)
        self.ui.comboBox.addItem('vendeurs de houblons')
        self.ui.comboBox.addItem('houblons')
        self.ui.comboBox.insertSeparator(8)
        self.ui.comboBox.addItem('marques de levures')
        self.ui.comboBox.addItem('levures')
        self.ui.comboBox.insertSeparator(11)
        self.ui.comboBox.addItem('ingrédients divers')
        self.ui.comboBox.insertSeparator(13)
        self.ui.comboBox.addItem('eaux sources')
        self.ui.comboBox.addItem('eaux cibles')
        self.ui.comboBox.insertSeparator(16)
        self.ui.comboBox.addItem('styles')
        self.ui.comboBox.addItem("paliers d'empâtage")
        self.this_file_path=Path(__file__).parent


        #help text 
        
        filename=(self.this_file_path/"help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()  

        filename =(self.this_file_path/"help/ImportHelp.html").resolve()
        text=open(filename,'r',encoding="utf-8").read()
        self.ui.helpEdit.setHtml(prepend+text)
        self.ui.helpEdit.setReadOnly(True)
        self.ui.helpButton.setText("Voir l'aide") 
        self.ui.helpEdit.setVisible(False)      

        #connections 
        self.ui.helpButton.clicked.connect(self.toggle_help)        
        self.ui.choseButton.clicked.connect(self.select_file)
        self.ui.importButton.clicked.connect(self.do_import)
        self.ui.comboBox.currentTextChanged.connect(self.set_what)

    def set_what(self):
        self.what=self.ui.comboBox.currentText()   
        self.ui.textEdit.setText('')

    def toggle_help(self):
        if(self.ui.helpEdit.isVisible()):
            self.ui.helpEdit.setVisible(False)
            self.ui.helpButton.setText('Voir l\'aide')
        else:
            self.ui.helpEdit.setVisible(True)   
            self.ui.helpButton.setText('Cacher l\'aide') 

    def select_file(self):
        alist=QFileDialog.getOpenFileName(self,'Open File','./base-data','All Files(*.csv)')
        self.filename=str(alist[0])
        self.ui.fileNameEdit.setText(self.filename)
        # Using readlines()

    def set_help_text(self):
        filename ="help/ImportHelp.html"
        text=open(filename,'r',encoding="utf-8").read()
        self.ui.helpEdit.setText(text)    
    def do_import(self):
        print('in do_import '+self.what)
        if self.filename :
            
            match self.what:
                case 'marques de fermentables':
                    if os.path.basename(self.filename).startswith('mf-'):
                        self.do_import_fermentable_brands()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par mf-")
                case 'fermentables':
                    if os.path.basename(self.filename).startswith('f-'):
                        self.do_import_fermentables()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par f-")
                

                case 'vendeurs de houblons':
                    if os.path.basename(self.filename).startswith('vh-'):
                        self.do_import_hop_suppliers()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par vh-")
                case 'houblons':
                    if os.path.basename(self.filename).startswith('h-'):
                        self.do_import_hops()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par h-")

                case 'marques de levures':
                    if os.path.basename(self.filename).startswith('ml-'):
                        self.do_import_ybrands()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par ml-")
                case 'levures':
                    if os.path.basename(self.filename).startswith('l-'):
                        self.do_import_yeasts()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par l-")

                case "paliers d'empâtage":
                    if os.path.basename(self.filename).startswith('pe-'):
                        self.do_import_rests()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par pe-")

                case 'styles':
                    if os.path.basename(self.filename).startswith('s-'):
                        self.do_import_styles()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par s-")
                case 'pays':
                    if os.path.basename(self.filename).startswith('p-'):
                        self.do_import_countries()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par p-")
  
   
                case 'eaux sources':
                    if os.path.basename(self.filename).startswith('es-'):
                        self.do_import_source_waters()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par es-")
                case 'eaux cibles':
                    if os.path.basename(self.filename).startswith('ec-'):
                        self.do_import_target_waters()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par ec-") 
                case 'equipment_profile':
                    if os.path.basename(self.filename).startswith('eq-'):
                        self.do_import_equipmens()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par eq-")   
                case 'ingrédients divers':
                    if os.path.basename(self.filename).startswith('id-'):
                        self.do_import_miscs()
                    else:
                        self.ui.textEdit.setText("<p style='color: red; font-weight:600'>Vous n'avez pas choisi le bon fichier: il doit commencer par id-")
            

    #---------------------------------------------------------------------------------------------------
    def check_import(self,x_array):
        result=""
        match self.what:
            case "fermentables":
                if x_array[2]=='':
                    result+="<span style='margin-left: 20px'>  ☛Le nom est vide</span>"  
                             
                if not x_array[3] in fermentable_forms:
                    result="<span style='margin-left: 20px'>  ☛La forme n'est pas correcte.</span>" 
              
                if not x_array[4] in fermentable_categories:
                    result="<span style='margin-left: 20px'>  ☛La catégorie n'est pas correcte.</span>" 

                try:
                    if float(x_array[5])<0 or float(x_array[5])>3000:
                        result+="<span style='margin-left: 20px'>  ☛La couleur est hors des limites</span>"
                except:
                    result+="<span style='margin-left: 20px'>  ☛La couleur ne peut être converti en nombre</span>"    

                try:
                    if float(x_array[6])<10 or float(x_array[6])>99:
                            result+="<span style='margin-left: 20px'>  ☛Le potentiel est hors des limites</span>"
                except:
                    result+="<span style='margin-left: 20px'>  ☛Le potentiel ne peut être converti en nombre</span>"    
                        
                if not x_array[7] in raw_ingredients:

                    result="<span style='margin-left: 20px'>  ☛L'ingrédient de base n'est pas correct.</span>" 
                            
                if x_array[8] =='':
                    result+="<span style='margin-left: 20px'>  ☛La version est vide</span>"

            case "ingrédients divers":
                pass
            case "equipment_profile":
                if x_array[1]=='':
                    result="<span style='margin-left: 20px'>  ☛Le nom est vide</span>"
                if x_array[2]=='':
                    result="<span style='margin-left: 20px'>  ☛le type est vide</span>"
                try:
                    if float(x_array[3])<5 or float(x_array[3])>10:
                        result+="<span style='margin-left: 20px'>  ☛Absorption d'eau par le houblon hors des limites</span>"
                except:
                    result+="<span style='margin-left: 20px'>  ☛Absorption d'eau par le houblon ne peut être converti en nombre</span>"
                
                try:
                    if float(x_array[4])<0 or float(x_array[4])>1:
                        result+="<span style='margin-left: 20px'>  ☛Coeff de réduction pour le vrac est hors des limites</span>"
                except:
                    result +="<span>  ☛Coeff de réduction pour le vrac  ne peut être converti en nombre </span>"

                try:
                    if float(x_array[5])<0.7 or float(x_array[5])>1.7:
                        result+="<span style='margin-left: 20px'>  ☛Absorption d'eau par le grain est hors des limites</span>"
                except:
                    result +="<span>  ☛Absorption d'eau par le grain  ne peut être converti en nombre </span>"
                
                try:
                    if float(x_array[6])<0 or float(x_array[6])>3000:
                        result+="<span style='margin-left: 20px'>  ☛Altitude est hors des limites</span>"
                except:
                    result +="<span>  ☛Altitude   ne peut être converti en nombre </span>"
                
                try:
                    if float(x_array[7])<0 or float(x_array[7])>200:
                        result+="<span style='margin-left: 20px'>  ☛Capacité de la cuve d'empâtage est hors des limites</span>"
                except:
                    result +="<span>  ☛Capacité de la cuve d'empâtage  ne peut être converti en nombre </span>"

                try:
                    if float(x_array[8])<0 or float(x_array[8])>40:
                        result+="<span style='margin-left: 20px'>  ☛Rétention de la cuve d'empâtage est hors des limites</span>"
                except:
                    result +="<span>☛Rétention de la cuve d'empâtage  ne peut être converti en nombre </span>"

                try:
                    if float(x_array[9])<0 or float(x_array[9])>40:
                        result+="<span style='margin-left: 20px'>  ☛Volume sous grain de la cuve d'empâtage est hors des limites</span>"
                except:
                    result +="<span>   ☛Volume sous grain de la cuve d'empâtage ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[10])<0 or float(x_array[10])>5:
                        result+="<span style='margin-left: 20px'>  ☛Pertes thermiques de  la cuve d'empâtage est hors des limites</span>"
                except:
                    result +="<span>    ☛Pertes thermiques de  la cuve d'empâtagene peut être converti en nombre </span>"

                try:
                    if  float(x_array[11])<0 or float(x_array[11])>10:
                        result+="<span style='margin-left: 20px'>  ☛Capacité thermique de la cuve d'empâtage est hors des limites</span>"
                except:
                    result +="<span>   ☛Capacité thermique de la cuve d'empâtage ne peut être converti en nombre </span>"
                
                try:
                    if  float(x_array[12])<0 or float(x_array[12])>6:
                        result+="<span style='margin-left: 20px'>  ☛Épaisseur de la maische est hors des limites</span>"
                except:
                    result +="<span>  ☛Épaisseur de la maische  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[13])<40 or float(x_array[13])>100:
                        result+="<span style='margin-left: 20px'>  ☛Efficacité d'empâtage est hors des limites</span>"
                except:
                    result +="<span>  ☛Efficacité d'empâtage  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[14])<0 or float(x_array[14])>200:
                        result+="<span style='margin-left: 20px'>  ☛Capacité de la bouilloire est hors des limites</span>"
                except:
                    result +="<span>  ☛Capacité de la bouilloire  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[15])<0 or float(x_array[15])>40:
                        result+="<span style='margin-left: 20px'>  ☛Rétention de la bouilloire est hors des limites</span>"
                except:
                    result +="<span>  ☛Rétention de la bouilloire  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[16])<0 or float(x_array[16])>150:
                        result+="<span style='margin-left: 20px'>  ☛Diamètre de la bouilloire est hors des limites</span>"
                except:
                    result +="<span>  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[17])<0 or float(x_array[17])>150:
                        result+="<span style='margin-left: 20px'>  ☛Diamètre de l'orifice du couvercle de la bouilloire est hors des limites</span>"
                except:
                    result +="<span>   ☛Diamètre de l'orifice du couvercle de la bouilloire ne peut être converti en nombre </span>"
                
                try:
                    if  float(x_array[18])<0 or float(x_array[18])>5:
                        result+="<span style='margin-left: 20px'>  ☛Taux d'évaporation de la bouilloire est hors des limites</span>"
                except:
                    result +="<span>  ☛Taux d'évaporation de la bouilloire  ne peut être converti en nombre </span>"
                
                try:
                    if  float(x_array[19])<7 or float(x_array[19])>50:
                        result+="<span style='margin-left: 20px'>  ☛Vitesse de chauffe de la bouilloire est hors des limites</span>"
                except:
                    result +="<span> ☛Vitesse de chauffe de la bouilloire  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[20])<0 or float(x_array[20])>40:
                        result+="<span style='margin-left: 20px'>  ☛Capacité du fermenteur est hors des limites</span>"
                except:
                    result +="<span>  ☛Capacité du fermenteur  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[21])<0 or float(x_array[21])>40:
                        result+="<span style='margin-left: 20px'>  ☛Rétention du fermenteur est hors des limites</span>" 

                except:
                    result +="<span>  ☛Rétention du fermenteur   ne peut être converti en nombre </span>"
                    

               
                if  x_array[22]=='':
                    result+="<span style='margin-left: 20px'>  ☛Type de refroidisseur est vide</span>"

                try:
                    if  float(x_array[23])<0 or float(x_array[23])>5:
                        result+="<span style='margin-left: 20px'>  ☛Pente du refroidisseur est hors des limites</span>"
                except:
                    result +="<span>   ☛Pente du refroidisseur  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[24])<0 or float(x_array[24])>5:
                        result+="<span style='margin-left: 20px'>  ☛Débit du refroidisseur est hors des limites</span>"
                except:
                    result +="<span>  ☛Débit du refroidisseur  ne peut être converti en nombre </span>"
            #------------------------------------------------------------------------------        
            case "paliers d'empâtage":
                if x_array[1]=='':
                    result="<span style='margin-left: 20px'>  ☛Le nom est vide</span>"
                try:
                    if  float(x_array[2])<30 or float(x_array[2])>82:
                        result+="<span style='margin-left: 20px'>  ☛Température est hors des limites</span>"
                except:
                    result +="<span>   ☛Température  ne peut être converti en nombre </span>"
                try:
                    if  float(x_array[3])<1 or float(x_array[3])>300:
                        result+="<span style='margin-left: 20px'>  ☛Durée est hors des limites</span>"
                except:
                    result +="<span>   ☛Durée  ne peut être converti en nombre </span>"
            #------------------------------------------------------------------------------        
            case "eaux sources":

                if x_array[1]=='':
                    result="<span style='margin-left: 20px'>  ☛Le nom est vide</span>"  
                try:
                    if  float(x_array[2])<0 or float(x_array[2])>200:
                        result+="<span style='margin-left: 20px'>  ☛Ca est hors des limites</span>"
                except:
                    result +="<span>   ☛Ca  ne peut être converti en nombre </span>"
                try:
                    if  float(x_array[3])<0 or float(x_array[3])>200:
                        result+="<span style='margin-left: 20px'>  ☛Mg est hors des limites</span>"
                except:
                    result +="<span>   ☛Mg  ne peut être converti en nombre </span>"                               
                try:
                    if  float(x_array[4])<0 or float(x_array[4])>100:
                        result+="<span style='margin-left: 20px'>  ☛Na est hors des limites</span>"
                except:
                    result +="<span>   ☛Na  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[5])<0 or float(x_array[5])>500:
                        result+="<span style='margin-left: 20px'>  ☛Cl est hors des limites</span>"
                except:
                    result +="<span>   ☛Cl  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[6])<0 or float(x_array[6])>500:
                        result+="<span style='margin-left: 20px'>  ☛SO4 est hors des limites</span>"
                except:
                    result +="<span>   ☛SO4  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[7])<0 or float(x_array[7])>500:
                        result+="<span style='margin-left: 20px'>  ☛alcalinité est hors des limites</span>"
                except:
                    result +="<span>   ☛alcalinité  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[8])<5 or float(x_array[8])>8:
                        result+="<span style='margin-left: 20px'>  ☛pH est hors des limites</span>"
                except:
                    result +="<span>   ☛pH  ne peut être converti en nombre </span>"        
            
            case "eaux cibles":
                if x_array[1]=='':
                    result="<span style='margin-left: 20px'>  ☛Le nom est vide</span>"  
                try:
                    if  float(x_array[2])<0 or float(x_array[2])>200:
                        result+="<span style='margin-left: 20px'>  ☛Ca minimum est hors des limites</span>"
                except:
                    result +="<span>   ☛Ca minimum  ne peut être converti en nombre </span>"
                try:
                    if  float(x_array[3])<0 or float(x_array[3])>200:
                        result+="<span style='margin-left: 20px'>  ☛Mg minimum est hors des limites</span>"
                except:
                    result +="<span>   ☛Mg minimum  ne peut être converti en nombre </span>"                               
                try:
                    if  float(x_array[4])<0 or float(x_array[4])>100:
                        result+="<span style='margin-left: 20px'>  ☛Na minimum est hors des limites</span>"
                except:
                    result +="<span>   ☛Na minimum  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[5])<0 or float(x_array[5])>500:
                        result+="<span style='margin-left: 20px'>  ☛Cl minimum est hors des limites</span>"
                except:
                    result +="<span>   ☛Cl minimum  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[6])<0 or float(x_array[6])>500:
                        result+="<span style='margin-left: 20px'>  ☛SO4 minimum est hors des limites</span>"
                except:
                    result +="<span>   ☛SO4 minimum  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[7])<0 or float(x_array[7])>500:
                        result+="<span style='margin-left: 20px'>  ☛alcalinité minimum est hors des limites</span>"
                except:
                    result +="<span>   ☛alcalinité minimum  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[8])<0 or float(x_array[8])>200:
                        result+="<span style='margin-left: 20px'>  ☛Ca maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛Ca maximum  ne peut être converti en nombre </span>"
                try:
                    if  float(x_array[9])<0 or float(x_array[9])>200:
                        result+="<span style='margin-left: 20px'>  ☛Mg maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛Mg maximum  ne peut être converti en nombre </span>"                               
                try:
                    if  float(x_array[10])<0 or float(x_array[10])>100:
                        result+="<span style='margin-left: 20px'>  ☛Na maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛Na maximum  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[11])<0 or float(x_array[11])>500:
                        result+="<span style='margin-left: 20px'>  ☛Cl maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛Cl maximum  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[12])<0 or float(x_array[12])>500:
                        result+="<span style='margin-left: 20px'>  ☛SO4 maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛SO4 axiimum  ne peut être converti en nombre </span>" 
                try:
                    if  float(x_array[13])<0 or float(x_array[13])>500:
                        result+="<span style='margin-left: 20px'>  ☛alcalinité maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛alcalinité maximum  ne peut être converti en nombre </span>"                           
            case "styles":
                if x_array[1]=='':
                    result="<span style='margin-left: 20px'>  ☛Le nom est vide</span>"
                if x_array[2]=='':
                    result+="<span style='margin-left: 20px'>  ☛Famille est vide</span>"
                try:
                    if  float(x_array[3])<1.0 or float(x_array[3])>1.999:
                        result+="<span style='margin-left: 20px'>  ☛OG minimun est hors des limites</span>"
                except:
                    result +="<span>   ☛OG minimun  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[4])<1.0 or float(x_array[4])>1.999:
                        result+="<span style='margin-left: 20px'>  ☛FG minimun est hors des limites</span>"
                except:
                    result +="<span>   ☛FG minimun  ne peut être converti en nombre </span>"

                try:
                    if  float(x_array[5])<2 or float(x_array[5])>15.9:
                        result+="<span style='margin-left: 20px'>  ☛ABV minimun est hors des limites</span>"
                except:
                    result +="<span>   ☛FG minimun  ne peut être converti en nombre </span>"     

                try:
                    if  float(x_array[6])<0 or float(x_array[6])>99:
                        result+="<span style='margin-left: 20px'>  ☛IBU minimun est hors des limites</span>"
                except:
                    result +="<span>   ☛IBU minimun  ne peut être converti en nombre </span>"   

                try:
                    if  float(x_array[7])<0 or float(x_array[7])>1.9:
                        result+="<span style='margin-left: 20px'>  ☛BU vs GU minimun est hors des limites</span>"
                except:
                    result +="<span>   ☛BU vs GU minimun  ne peut être converti en nombre </span>"   

                try:
                    if  float(x_array[8])<0 or float(x_array[8])>99:
                        result+="<span style='margin-left: 20px'>  ☛Couleur minimun est hors des limites</span>"
                except:
                    result +="<span>   ☛Couleur minimun  ne peut être converti en nombre </span>"    

                try:
                    if  float(x_array[9])<60 or float(x_array[9])>99:
                        result+="<span style='margin-left: 20px'>  ☛Atténuation  minimun est hors des limites</span>"
                except:
                    result +="<span>   ☛Atténuation  minimun  ne peut être converti en nombre </span>"  

                try:
                    if  float(x_array[10])<1 or float(x_array[10])>82:
                        result+="<span style='margin-left: 20px'>  ☛Niveau de carbonation  minimun est hors des limites</span>"
                except:
                    result +="<span>   ☛Niveau de carbonation  minimun  ne peut être converti en nombre </span>"        
                try:
                    if  float(x_array[11])<1 or float(x_array[11])>5.0:
                        result+="<span style='margin-left: 20px'>  ☛Niveau de carbonation  minimun est hors des limites</span>"
                except:
                    result +="<span>   ☛Niveau de carbonation  minimun  ne peut être converti en nombre </span>" 

                try:
                    if  float(x_array[12])<1 or float(x_array[12])>1.999:
                        result+="<span style='margin-left: 20px'>  ☛OG maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛OG maximum  ne peut être converti en nombre </span>"  

                try:
                    if  float(x_array[13])<0 or float(x_array[13])>15.9:
                        result+="<span style='margin-left: 20px'>  ☛ABV maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛ABV maximum  ne peut être converti en nombre </span>" 

                try:
                    if  float(x_array[14])<0 or float(x_array[14])>99:
                        result+="<span style='margin-left: 20px'>  ☛IBU maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛IBU maximum  ne peut être converti en nombre </span>" 

                try:
                    if  float(x_array[15])<0 or float(x_array[15])>1.9:
                        result+="<span style='margin-left: 20px'>  ☛BU versus GU maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛BU versus GU maximum  ne peut être converti en nombre </span>" 

                try:
                    if  float(x_array[16])<0 or float(x_array[16])>99:
                        result+="<span style='margin-left: 20px'>  ☛Couleur maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛Couleur maximum  ne peut être converti en nombre </span>" 

                try:
                    if  float(x_array[17])<60 or float(x_array[17])>99:
                        result+="<span style='margin-left: 20px'>  ☛Atténuation maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛Atténuation maximum  ne peut être converti en nombre </span>"  

                try:
                    if  float(x_array[18])<1 or float(x_array[18])>5.0:
                        result+="<span style='margin-left: 20px'>  ☛Niveau de carbonation maximum est hors des limites</span>"
                except:
                    result +="<span>   ☛Niveau de carbonation maximum  ne peut être converti en nombre </span>" 

                try:
                    if  float(x_array[3])>float(x_array[11]):
                        result+="<span style='margin-left: 20px'>  ☛OG min. > OG max</span>"
                except:
                    pass                 
                try:
                    if  float(x_array[4])>float(x_array[12]):
                        result+="<span style='margin-left: 20px'>  ☛FG min. > FG max</span>"
                except:
                    pass
                           
                try:
                    if  float(x_array[5])>float(x_array[13]):
                        result+="<span style='margin-left: 20px'>  ☛ABV min. > ABV max</span>"
                except:
                    pass
                try:
                    if  float(x_array[6])>float(x_array[14]):
                        result+="<span style='margin-left: 20px'>  ☛IBU min. > IBU max</span>"
                except:
                    pass
                try:
                    if  float(x_array[7])>float(x_array[15]):
                        result+="<span style='margin-left: 20px'>  ☛BUvsGU min. > BUvsGU max</span>"
                except:
                    pass               
                try:
                    if  float(x_array[8])>float(x_array[16]):
                        result+="<span style='margin-left: 20px'>  ☛Couleur min. > Couleur max</span>"
                except:
                    pass                
                try:
                    if  float(x_array[8])>float(x_array[17]):
                        result+="<span style='margin-left: 20px'>  ☛Atténuation min. > Atténuation max</span>"
                except:
                    pass                
                try:
                    if  float(x_array[8])>float(x_array[17]):
                        result+="<span style='margin-left: 20px'>  ☛Niveau de carbonation min. > Niveau de carbonation max</span>"
                except:
                    pass
        if result =="":
            return "OK"
        else:       
            return result        

    #---
    def do_import_miscs(self):
        #read raw data

        if not self.check_encoding():
            return 
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        cpt=0
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
                cpt+=1
                x_array=line.split('⎈')
                print(x_array)
                if len(x_array) != 4:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 5. Avez-vous sélectionné le bon fichier ?</span>')
                    return    
                check=self.check_import(x_array)
               
                if check != "OK":
                    self.ui.textEdit.append('<span style="color:red;">Ligne '+str(cpt)+' : Un (ou plusieurs) champ(s) de cette ligne est(sont) inacceptable(s) ! </span>')
                    self.ui.textEdit.append(check )   
                    self.ui.textEdit.append('-----')

                else: 


                    id=None
                    name=x_array[1]
                    category=x_array[2]
                    unit=x_array[3]
                    notes=''
                    
                    misc=Misc(id,name,category,unit,notes)
                    result=add_misc(misc)
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+'<span style="color:red;"> échouée !</span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break

    #---------------------------------------------------------------------------------------
    def do_import_rests(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        cpt=0
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
                cpt+=1
                x_array=line.split('⎈')

                if len(x_array) != 5:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 5. Avez-vous sélectionné le bon fichier ?</span>')
                    return    
                check=self.check_import(x_array)
               
                if check != "OK":
                    self.ui.textEdit.append('<span style="color:red;">Ligne '+str(cpt)+' : Un (ou plusieurs) champ(s) de cette ligne est(sont) inacceptable(s) ! </span>')
                    self.ui.textEdit.append(check )   
                    self.ui.textEdit.append('-----')

                else: 


                    id=None
                    name=x_array[1]
                    temperature=x_array[2]
                    duration=x_array[3]
                    
                    rest=Rest(id,name,temperature, duration,None)#None before description is for thickness_reference
                    result=add_rest(rest)
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+'<span style="color:red;"> échouée !</span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break

    #---------------------------------------------------------------------------------------------------------
    def do_import_fermentables(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        cpt=0
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                cpt+=1
                x_array=line.split('⎈')
                #check the format of the file
                if len(x_array) !=11:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 11.</span>')
                    return
                check=self.check_import(x_array)
                if check != "OK":
                    self.ui.textEdit.append('<span style="color:red;">Ligne '+str(cpt)+' : Un (ou plusieurs) champ(s) de cette ligne est(sont) inacceptable(s) ! </span>')
                    self.ui.textEdit.append(check )   
                    self.ui.textEdit.append('-----')
                else:
                    id=None
                    brand=x_array[1].upper()#ensure upper case
                    name=x_array[2]
                    form=x_array[3]
                    category=x_array[4]
                    color=x_array[5]
                    potential=x_array[6]
                    raw_ingredient=x_array[7]
                    version=x_array[8]
                    link=x_array[9]
                    # [:-1] removes the linefeed at the end of the last field
                    notes=x_array[10][:-1]
                    #check brand exists
                    fb=find_fbrand_by_name(brand)
                    if fb ==None:
                        self.ui.textEdit.append('Importation de '+name+' de marque '+brand+ '<span style="color:red;"> échouée, cette marque n\'est pas dans la liste de vos marques; peut-êre les orthographes diffèrent-elles !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        fermentable=Fermentable(id,brand,name,form,category,color,potential,raw_ingredient,version,link,notes)
                        result=add_fermentable(fermentable)
                        if(result =='OK'):
                            self.ui.textEdit.append('Importation de '+name+' de marque '+brand+ ' <span style="color:green;">réussie !</span>')
                            self.ui.textEdit.append('-----')
                        else:
                            self.ui.textEdit.append('Importation de '+name+' de marque '+brand+ '<span style="color:blue;"> ignoré !</span>') 
                            self.ui.textEdit.append(result)
                            self.ui.textEdit.append('-----')
                if(end):
                    
                    break

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------   
    def do_import_fermentable_brands(self):
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding='utf-8')
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
                print(line)
                x_array=line.split('⎈')
                print('len x_array is '+str(len(x_array)))
                if len(x_array) != 3:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 3. Avez-vous sélectionné le bon fichier ?</span>')
                    self.ui.textEdit.append('-----')
                    return
                id=None
                name=x_array[1].upper()
                # [:-1] removes the linefeed at the end of the last field
                country_code=x_array[2][:-1]
                print('country code is '+(country_code))

                #check if country exists
                c=find_country_by_code(country_code)
                if c ==None:
                    self.ui.textEdit.append('Importation de '+name+' de code pays '+country_code+ '<span style="color:red;"> échouée, ce pays n est pas dans la liste de vos pays; peut-êre les orthographes diffèrent-elles !</span>')
                    self.ui.textEdit.append('-----')
                else:
                    fermentable_brand=FBrand(id,name,country_code)
                    result=add_fbrand(fermentable_brand)
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+' code '+country_code+ ' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+' code '+country_code+ '<span style="color:red;"> ignorée ! </span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break

    #-------------------------------------------------------------------------------------------
    def do_import_hops(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
                x_array=line.split('⎈')
                if len(x_array) != 12:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 3. Avez-vous sélectionné le bon fichier ?</span>')
                    self.ui.textEdit.append('-----')
                    return                
                id=None
                supplier=x_array[1]
                crop_year=x_array[2]
                country_code=x_array[3]
                name=x_array[4]
                form=x_array[5]
                purpose=x_array[6]
                alpha=x_array[7]
                aromas=x_array[8]
                alternatives=x_array[9]
                link=x_array[10]
                notes=x_array[11]
                #check if supplier exists
                hs=find_hsupplier_by_name(supplier)
                if hs==None:
                    self.ui.textEdit.append('Importation de '+name+' du fournisseur  '+supplier+ ' <span style="color:red;">échouée, ce fournisseur n\'exsite pas dans vos listes.!</span>')
                    self.ui.textEdit.append('-----')
                else:
                    hop=Hop(id,supplier,crop_year,country_code,name,form,purpose,alpha,aromas,alternatives,link,notes)
                    result=add_hop(hop)
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+' du fournisseur  '+supplier+ ' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+' du fournisseur '+supplier+ '<span style="color:blue;"> ignorée !</span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break

    #--------------------------------------------------------------------------------------------------------------------------
    def do_import_hop_suppliers(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        char=None
        end=False
        line=''
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
              
                x_array=line.split('⎈')
                if len(x_array) != 2:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 3. Avez-vous sélectionné le bon fichier ?</span>')
                    self.ui.textEdit.append('-----')
                    return
                id=None
                name=x_array[1][:-1].upper()
                # [:-1] removes the linefeed at the end of the last field
           
                hs=HSupplier(id,name)
                result=add_hsupplier(hs)
                if(result =='OK'):
                    self.ui.textEdit.append('Importation de '+name+' <span style="color:green;">réussie !</span>')
                    self.ui.textEdit.append('-----')
                else:
                    self.ui.textEdit.append('Importation de '+name+' <span style="color:blue;"> ignorée ! </span>') 
                    self.ui.textEdit.append(result)
                    self.ui.textEdit.append('-----')
                if(end):
                    break         
    #-------------------------------------------------------------------------------------------------------------------------

    def do_import_yeasts(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
              
     
                x_array=line.split('⎈')
                #check the format of the file
                if len(x_array) !=19:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 19. Avez-vous pris le bon fichier ?</span>')
                    return                
                id=None 
                brand=x_array[1]
                name=x_array[2]        
                #this is with mysql
                #manufacture_date=x_array[3]        
                #expiration_date=x_array[4]  
                #QtCore.QDate.fromString(str(date_from_db),'yyyy-MM-dd')  
                manufacture_date=date.fromisoformat(x_array[3])
                expiration_date=date.fromisoformat(x_array[4])
                pack_unit=x_array[5]  
                cells_per_pack=x_array[6]  
                form=x_array[7]  
                target=x_array[8]  
                floculation=x_array[9]  
                sedimentation=x_array[10]  
                abv_tolerance=x_array[11]  
                temp_min=x_array[12]  
                temp_ideal_min=x_array[13]  
                temp_ideal_max=x_array[14]  
                temp_max=x_array[15]  
                attenuation=x_array[16]
                link=x_array[17]  
                notes=x_array[18] 
                yb=find_ybrand_by_name(brand) 
                if yb  ==None:
                    self.ui.textEdit.append('Importation de '+name+' de marque '+brand+ '<span style="color:red;"> échouée, cette marque n\'est pas dans la liste de vos marques; peut-êre les orthographes diffèrent-elles !</span>')
                    self.ui.textEdit.append('-----')
                else:
                    yeast=Yeast(id,brand,name,manufacture_date,expiration_date,pack_unit,cells_per_pack,form,target,floculation,sedimentation,abv_tolerance,temp_min,temp_ideal_min,temp_ideal_max,temp_max,attenuation,link,notes)
                    result=add_yeast(yeast)
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+' du fbricant  '+brand+ ' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+' du fabricant '+brand+ '<span style="color:blue;"> ignorée !</span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break
    #----------------------------------------------------------------------------------------------------------
    def do_import_styles(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        cpt=0
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                cpt+=1
                x_array=line.split('⎈')
                if len(x_array) != 19:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 5. Avez-vous sélectionné le bon fichier ?</span>')
                    return    
                check=self.check_import(x_array)
               
                if check != "OK":
                    self.ui.textEdit.append('<span style="color:red;">Ligne '+str(cpt)+' : Un (ou plusieurs) champ(s) de cette ligne est(sont) inacceptable(s) ! </span>')
                    self.ui.textEdit.append(check )   
                    self.ui.textEdit.append('-----')

                else: 
                    id=None
                    name=x_array[1]
                    family=x_array[2]
                    og_min=x_array[3]
                    fg_min=x_array[4]
                    abv_min=x_array[5]

                    ibu_min=x_array[6]
                    bu_vs_gu_min=x_array[7]
                    srm_min=x_array[8]
                    app_att_min=x_array[9]
                    co2_min=x_array[10] 
                    og_max=x_array[11]
                    fg_max=x_array[12]
                    abv_max=x_array[13]

                    ibu_max=x_array[14]
                    bu_vs_gu_max=x_array[15]
                    srm_max=x_array[16]
                    app_att_max=x_array[17]
                    co2_max=x_array[18]
                
                    style=Style(id, name,family,og_min,fg_min,abv_min,ibu_min,bu_vs_gu_min,srm_min,app_att_min,co2_min,og_max,fg_max,abv_max,ibu_max,bu_vs_gu_max,srm_max,app_att_max,co2_max)
                    result=add_style(style)
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+' de famille  '+family+ ' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+' de famille'+family+ '<span style="color:red;"> échouée !</span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break

    def do_import_target_waters(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        cpt=0
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
                cpt+=1
                x_array=line.split('⎈')
                if len(x_array) != 14:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 14. Avez-vous sélectionné le bon fichier ?</span>')
                    return
                check=self.check_import(x_array)
               
                if check != "OK":
                    self.ui.textEdit.append('<span style="color:red;">Ligne '+str(cpt)+' : Un (ou plusieurs) champ(s) de cette ligne est(sont) inacceptable(s) ! </span>')
                    self.ui.textEdit.append(check )   
                    self.ui.textEdit.append('-----')
                else:
                
                    id=None
                    name=x_array[1]
                    ca_min=x_array[2]
                    mg_min=x_array[3]
                    na_min=x_array[4]
                    cl_min=x_array[5]

                    so4_min=x_array[6]
                    alca_min=x_array[7]
                
                    ca_max=x_array[8]
                    mg_max=x_array[9]
                    na_max=x_array[10]
                    cl_max=x_array[11]

                    so4_max=x_array[12]
                    alca_max=x_array[13]
                
                
                    watertarget=WaterTarget(id, name,ca_min,mg_min,na_min,cl_min,so4_min,alca_min,ca_max,mg_max,na_max,cl_max,so4_max,alca_max)  
                    result=add_water_target (watertarget) 
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+ ' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+ '<span style="color:blue;"> ignorée !</span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break 
    def do_import_source_waters(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        cpt=0
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
                cpt+=1
                x_array=line.split('⎈')
                if len(x_array) != 9:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 8. Avez-vous sélectionné le bon fichier ?</span>')
                    return  
   
                check=self.check_import(x_array)
               
                if check != "OK":
                    self.ui.textEdit.append('<span style="color:red;">Ligne '+str(cpt)+' : Un (ou plusieurs) champ(s) de cette ligne est(sont) inacceptable(s) ! </span>')
                    self.ui.textEdit.append(check )   
                    self.ui.textEdit.append('-----')

                else:              
                    id=None
                    name=x_array[1]
                    ca=x_array[2]
                    mg=x_array[3]
                    na=x_array[4]
                    cl=x_array[5]

                    so4=x_array[6]
                    alca=x_array[7]
                    ph=x_array[8]
            
                
                
                    watersource=Water(id, name,ca,mg,na,cl,so4,alca,ph)  
                    result=add_water_source (watersource) 
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+ ' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+ '<span style="color:blue;"> ignorée !</span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break 
    #-------------------------------------------------------------------------------------------------------------
    def do_import_equipment_profiles(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        cpt=0
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
               
                cpt+=1
                x_array=line.split('⎈')
        
                if len(x_array) != 25:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 18. Avez-vous sélectionné le bon fichier ?</span>')
                    return    
                check=self.check_import(x_array)
               
                if check != "OK":
                    self.ui.textEdit.append('<span style="color:red;">Ligne '+str(cpt)+' : Un (ou plusieurs) champ(s) de cette ligne est(sont) inacceptable(s) ! </span>')
                    self.ui.textEdit.append(check )   
                    self.ui.textEdit.append('-----')

                else:            
                    id=None
                    name=x_array[1]
                    etype=x_array[2]
                    hop_absorption=x_array[3]
                    hop_absorption_reduction_coeff=x_array[4]
                    grain_absorption=x_array[5]
                    altitude=x_array[6]

                    mash_tun_capacity=x_array[7]
                    mash_tun_retention=x_array[8]
                    mash_tun_undergrain=x_array[9]
                    mash_tun_thermal_losses=x_array[10]
                    mash_tun_heat_capacity_equiv=x_array[11]
                    mash_thickness=x_array[12]
                    mash_efficiency= x_array[13]

                    kettle_capacity=x_array[14]
                    kettle_retention=x_array[15]
                    kettle_diameter=x_array[16]
                    kettle_steam_exit_diameter=x_array[17]
                    kettle_evaporation_rate=x_array[18]
                    kettle_heat_slope=x_array[19]

                    fermenter_capacity=x_array[20]
                    fermenter_retention=x_array[21]
                    cooler_type=x_array[22]
                    cooler_slope=x_array[23]
                    cooler_flow_rate=x_array[24]
                
                    equipment=Equipment(id, name, etype, hop_absorption,hop_absorption_reduction_coeff,grain_absorption, altitude, mash_tun_capacity, mash_tun_retention,mash_tun_undergrain,\
            mash_tun_thermal_losses,mash_tun_heat_capacity_equiv,mash_thickness,mash_efficiency, \
            kettle_capacity,kettle_retention, kettle_diameter,kettle_steam_exit_diameter, kettle_evaporation_rate, kettle_heat_slope,\
            fermenter_capacity, fermenter_retention, cooler_type,cooler_slope,cooler_flow_rate) 
                    result=add_equipment (equipment) 
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+ ' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+ '<span style="color:blue;"> ignorée !</span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break 

    #check file encoding
    def check_encoding(self):
        #read raw data
        self.ui.textEdit.setHtml("")
        fileObj = open(self.filename, 'rb')
        rawdata=fileObj.read()
        fileObj.close()
        encoding = chardet.detect(rawdata)['encoding']
        print('encoding is '+encoding)
        if encoding != "utf-8":
            print('<p style="color:red;">L\'encodage du fichier est '+encoding+' Nous n\'acceptons que des fichiers encodé utf-8. Abandon !</p>')
            self.ui.textEdit.setHtml('<p style="color:red;">L\'encodage du fichier est '+encoding+' Nous n\'acceptons que des fichiers encodé utf-8. Abandon !</p>')
            return  False
        else:
            return True          
    #---------------------------------------------------------------------------------------------------------------

    def do_import_countries(self):
        #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
              
                x_array=line.split('⎈')
                
                if len(x_array) != 3:
                    self.ui.textEdit.append('<span style="color:red;">Votre fichier est mal formé. Le nombre de champs doit être de 3. Avez-vous sélectionné le bon fichier ?</span>')
                    return
                id=None
                name=x_array[1]
                country_code=x_array[2].lower().strip()
            
            
                country=Country(id, name,country_code)
                result=add_country(country)
                if(result =='OK'):
                    self.ui.textEdit.append('Importation de '+name+' de code  '+country_code+ ' <span style="color:green;">réussie !</span>')
                    self.ui.textEdit.append('-----')
                else:
                    self.ui.textEdit.append('Importation de '+name+' de code '+country_code+ '<span style="color:red;"> échouée !</span>') 
                    self.ui.textEdit.append(result)
                    self.ui.textEdit.append('-----')
                if(end):
                    break
                
    def do_import_ybrands(self):
         #read raw data
        if not self.check_encoding():
            return
        fileObj = open(self.filename, 'r',encoding="utf-8")
        #lines = fileObj.readlines()
        char=None
        end=False
        line=''
        stop_char='♆'
        while True:
            line=''
            while True:
                char=fileObj.read(1)
                if(char ==stop_char):
                    break
                if not char:
                    break
                line += char
            if not char:
                #print('Fin de fichier')
                end=True #we do not break here to allow the last line treatement
            if(line != '')  : #to avoid the first empty line  
                #print(line)
                #print('-----------')
                x_array=line.split('⎈')
                id=None
                name=x_array[1]
                country_code=x_array[2][:-1].lower()
                #check if country exists
                c=find_country_by_code(country_code)
                if c ==None:
                    self.ui.textEdit.append('Importation de '+name+' de code pays '+country_code+ '<span style="color:red;"> échouée, ce pays n est pas dans la liste de vos pays; peut-êre les orthographes diffèrent-elles !</span>')
                    self.ui.textEdit.append('-----')  
                else:              
            
                    ybrand=YBrand(id, name,country_code)
                    result=add_ybrand(ybrand)
                    print('RESULT IS '+result)
                    if(result =='OK'):
                        self.ui.textEdit.append('Importation de '+name+' de code  '+country_code+ ' <span style="color:green;">réussie !</span>')
                        self.ui.textEdit.append('-----')
                    else:
                        self.ui.textEdit.append('Importation de '+name+' de code '+country_code+ '<span style="color:blue;"> ignorée !</span>') 
                        self.ui.textEdit.append(result)
                        self.ui.textEdit.append('-----')
                if(end):
                    break    