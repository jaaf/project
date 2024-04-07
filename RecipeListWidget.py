'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from database.recipes.recipe import all_recipe
from ListModels import RecipeListModel
from PyQt6.QtWidgets import QListView,QVBoxLayout,QHBoxLayout,QPushButton,QWidget,QLabel,QComboBox,QCheckBox,QLineEdit,QFrame
from PyQt6 import QtCore,QtWidgets
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon,QFont
from RecipeWidget import RecipeWidget
from HelpMessage import HelpMessage
from pathlib import Path


class RecipeListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent
        self.icon_path=self.parent.icon_path
        self.icon_size=QSize(32,32)
        self.newButton=QPushButton()
        self.sortButton=QPushButton()
        self.listView=QListView()
        self.selection=None
        self.recipeWidget=None
        self.this_file_path=Path(__file__).parent
        

    def setup_gui(self): 

        #create a toolbar
        self.sortCombo=QComboBox()
        self.sortCombo.addItem("")
        self.sortCombo.addItem('Nom-Style-Type')
        self.sortCombo.addItem("Style-Type-Nom")
        self.sortCombo.addItem("Type-Style-Nom")
        self.sortButton.setIcon(QIcon(self.icon_path+'sort-list-alt-svgrepo-com.svg'))
        self.sortButton.setIconSize(self.icon_size)
        self.sortButton.setMaximumSize(40,40)
        toolbarLayout=QHBoxLayout()

        #FILTERS
        self.filterLayout=QHBoxLayout()

        self.typeFilterLayout=QVBoxLayout()
        self.typeFilter=QCheckBox("Filtrer type")
        self.typeFilterEdit=QLineEdit()
        self.typeFilterLayout.addWidget(self.typeFilter)
        self.typeFilterLayout.addWidget(self.typeFilterEdit)


        self.nameFilterLayout=QVBoxLayout()
        self.nameFilter=QCheckBox("Filtrer noms")
        self.nameFilterEdit=QLineEdit()
        self.nameFilterLayout.addWidget(self.nameFilter)
        self.nameFilterLayout.addWidget(self.nameFilterEdit)

        self.styleFilterLayout=QVBoxLayout()
        self.styleFilter=QCheckBox("Filtrer styles")
        self.styleFilterEdit=QLineEdit()
        self.styleFilterLayout.addWidget(self.styleFilter)
        self.styleFilterLayout.addWidget(self.styleFilterEdit)

        self.nameFilterLayout.setSpacing(0)
        self.styleFilterLayout.setSpacing(0)
        self.typeFilterLayout.setSpacing(0)
        self.filterButton=QPushButton()
        self.filterButton.setIcon(QIcon(self.icon_path+'filter-slash-svgrepo-com.svg'))
        self.filterButton.setIconSize(self.icon_size)
        self.filterButton.setToolTip("Appliquer les filtres")
        self.filterLayout.addWidget(self.filterButton)
        self.filterLayout.addLayout(self.nameFilterLayout)
        self.filterLayout.addLayout(self.styleFilterLayout)
        self.filterLayout.addLayout(self.typeFilterLayout)
        self.filterHelpButton=QPushButton("?")
        self.filterHelpButton.resize(24,24)
        self.filterHelpButton.setMaximumWidth(24)
        self.filterHelpButton.setToolTip("Obtenir de l'aide sur le filtrage")
        self.filterHelpButton.setStyleSheet("background-color:green;color:white")
        self.filterLayout.addWidget(self.filterHelpButton)

        self.hide_sub_filter("name")
        self.hide_sub_filter("style")
        self.hide_sub_filter("type")
        self.newButton.setIcon(QIcon(self.icon_path+'add-square-svgrepo-com.svg'))
        self.newButton.setIconSize(self.icon_size)
        self.newButton.setMaximumSize(40,40)
        self.newButton.setToolTip('Ajouter une recette')
        self.sortButton.setIcon(QIcon(self.icon_path+'sort-list-alt-svgrepo-com.svg'))
        self.sortButton.setIconSize(self.icon_size)
        self.sortButton.setMaximumSize(40,40)
        self.sortButton.setToolTip('Trier les recettes')
        spacerItem = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        spacerItemSmall = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        toolbarLayout.addItem(spacerItem)

        self.filterFrame=QFrame()
        self.filterFrame.setLayout(self.filterLayout)
        self.filterFrame.setStyleSheet("background-color:honeydew;")
        toolbarLayout.addWidget(self.filterFrame)
        toolbarLayout.addWidget(self.sortButton)
        toolbarLayout.addWidget(self.sortCombo)
        toolbarLayout.addWidget(self.newButton)
        toolbarLayout.setSpacing(20)

        #create a title bar
        titlebarLayout=QHBoxLayout()
        self.titleLabel=QLabel()
        self.titleLabel.setText('LISTE DES RECETTES')
        title_font=QFont()
        title_font.setPointSize(int(self.font().pointSize()*1.3))
        title_font.setWeight(700)
        self.titleLabel.setFont(title_font)
        spacerItem = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        titlebarLayout.addWidget(self.titleLabel) 
        titlebarLayout.addItem(spacerItem)

        #setting the model for list view
        listLayout=QVBoxLayout()
        self.recipes=all_recipe()
        self.recipes.sort(key=lambda x: (x.id,x.name))
        self.model=RecipeListModel(recipes=self.recipes)
        font=QFont("Liberation Mono")
        #font=self.font().setStyle(QFont.styleItalic)
        self.listView.setFont(font)
        self.listView.setModel(self.model)
        self.listView.setSpacing(8)
        listLayout.addWidget(self.listView)

        #compose widget layout
        mainLayout=QVBoxLayout()
        mainLayout.addLayout(toolbarLayout)
        mainLayout.addLayout(titlebarLayout)
        mainLayout.addLayout(listLayout)
        self.setLayout(mainLayout)
     
        #set connections
        self.newButton.clicked.connect(self.new_recipe)
        self.listView.clicked.connect(self.select_recipe)
        self.sortCombo.currentTextChanged.connect(lambda: self.sort_list(self.sortCombo.currentText()))
        self.nameFilter.stateChanged.connect(self.name_filter_changed)
        self.styleFilter.stateChanged.connect(self.style_filter_changed)
        self.typeFilter.stateChanged.connect(self.type_filter_changed)
        self.filterButton.clicked.connect(self.apply_filters)
        self.filterHelpButton.clicked.connect(self.show_contextual_help)

    def show_contextual_help(self):
        helpPopup=HelpMessage() 
        filename=(self.this_file_path/"help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
        helpPopup.set_title('À propos du filtrage ')
        filename=(self.this_file_path/"help/BrewListFilterHelp.html").resolve()
        text=open(filename,'r',encoding="utf-8").read()
        helpPopup.set_message(prepend+text)
        helpPopup.exec()

    def apply_filters(self):
        items=self.recipes
        filtered=list(filter(lambda x: \
                                (self.nameFilterEdit.text().upper() in x.name.upper() or not self.nameFilter.isChecked()) and \
                                (self.typeFilterEdit.text().upper() in x.rtype.upper( ) or not self.typeFilter.isChecked()) and \
                                    (self.styleFilterEdit.text().upper() in x.style.upper() or not self.styleFilter.isChecked()),items))
        self.model.recipes=filtered
        self.sort_list(self.sortCombo.currentText())

    def type_filter_changed(self):
        if self.typeFilter.isChecked():
            self.show_sub_filter("type")
        else:
            self.hide_sub_filter("type")
            
    def style_filter_changed(self):
        print("in style_filter_changed")
        if self.styleFilter.isChecked():
            self.show_sub_filter("style")
        else:
            self.hide_sub_filter("style")  

    def name_filter_changed(self):
        if self.nameFilter.isChecked():
            self.show_sub_filter("name")
        else:
            self.hide_sub_filter("name")        

    def hide_sub_filter(self,mode):
        match mode:
            case "type":
                self.typeFilterEdit.setVisible(False)
                self.typeFilterEdit.setText("")

            case "name":
                self.nameFilterEdit.setVisible(False)
                self.nameFilterEdit.setText("")
            case "style":
                self.styleFilterEdit.setVisible(False)    
                self.styleFilterEdit.setText("")    

    def show_sub_filter(self,mode):
        print('show again')
        match mode:
            case "type":
                self.typeFilterEdit.setVisible(True)
            case "name":
                self.nameFilterEdit.setVisible(True)
            case "style":
                print("style")
                self.styleFilterEdit.setVisible(True)   

    def sort_list(self, mode):
        #self.source_list.sort(key=lambda x: (x.brand,x.name,x.version))
        match mode:
            case "":
                self.model.recipes.sort(key=lambda x: (x.id))
            case 'Nom-Style-Type':
                self.model.recipes.sort(key=lambda x: (x.name,x.style,x.rtype))
            case "Style-Type-Nom":
                self.model.recipes.sort(key=lambda x: (x.style,x.rtype,x.name))
            case "Type-Style-Nom":
                self.model.recipes.sort(key=lambda x: (x.rtype,x.style,x.name))
        self.model.layoutChanged.emit()   
    

    def select_recipe(self):
        #print('LIST VIEW CLICKED')
        indexes = self.listView.selectedIndexes()
        if indexes:
            index=indexes[0]
            self.selection=self.model.recipes[index.row()]
            self.recipeWidget=RecipeWidget(self.selection.id,self)
            stackIndex=self.parent.swapWidget('recipe',self.recipeWidget)
            self.parent.stackedWidget.setCurrentIndex(stackIndex)

   
    def new_recipe(self):
        self.recipeWidget=RecipeWidget(None,self)#we pass the parent i.e. RecipeListWidget as parent sans Id
        stackIndex=self.parent.swapWidget('recipe',self.recipeWidget)

        #print('stackIndex is '+str(stackIndex))
        #self.recipeWidget.setCurrentStackIndex(stackIndex)#pass the index to the recipe editor 
        self.parent.stackedWidget.setCurrentIndex(stackIndex)
     

