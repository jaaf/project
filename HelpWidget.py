'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from HelpWidgetBase import Ui_helpWidget as hw
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QPushButton,QSpacerItem,QSizePolicy,QTextEdit
from PyQt6 import QtCore
from PyQt6.QtCore import Qt,QRegularExpression,QTimer,QSize
from database.fermentables.fermentable_brand import all_fbrand, find_fbrand_by_name
from PyQt6 import QtGui
import copy
import jsonpickle
from database.profiles.rest import Rest
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator,QIntValidator
from pathlib import Path

class HelpWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =hw()
        self.ui.setupUi(self)
        self.ui.groupBox.setTitle("Sommaire")
        self.this_file_path=Path(__file__).parent
        
        self.resize(QSize(1600,800))
        self.vl=QVBoxLayout()
        self.Introduction=QPushButton('Introduction')
        self.Installation=QPushButton('Variantes d’installation')
        self.sqlite2mysql=QPushButton("Basculer de sqlite\nvers mysql")
        self.mysql2sqlite=QPushButton("Bascule de mysql \nvers sqlite")
        self.Interface=QPushButton("Présentation de l'interface")
        self.Selector=QPushButton("Principe des saisies d'ingrédients\n dans une recette")
        self.Recipe=QPushButton("Notion de recette dans Bière")
        self.Brew=QPushButton("Notion de session de brassage")
        self.vl.addWidget(self.Introduction)
        self.vl.addWidget(self.Installation)
        self.vl.addWidget(self.sqlite2mysql)
        self.vl.addWidget(self.mysql2sqlite)
        self.vl.addWidget(self.Interface)
        self.vl.addWidget(self.Selector)
        self.vl.addWidget(self.Recipe)
        self.vl.addWidget(self.Brew)
        self.vl.addStretch()
        self.ui.groupBox.setMaximumWidth(200)
        self.ui.groupBox.setLayout(self.vl)
        self.set_connections()
        
        

    def set_connections(self):
        self.Introduction.clicked.connect(lambda: self.show_chapter('Introduction')) 
        self.Installation.clicked.connect(lambda: self.show_chapter("Installation"))
        self.sqlite2mysql.clicked.connect(lambda: self.show_chapter("Basculer de sqlite vers mysql"))
        self.mysql2sqlite.clicked.connect(lambda: self.show_chapter("Basculer de mysql vers sqlite"))
        self.Interface.clicked.connect(lambda: self.show_chapter('Interface')) 
        self.Selector.clicked.connect(lambda: self.show_chapter('Selector'))
        self.Recipe.clicked.connect(lambda: self.show_chapter('Recipe'))
        self.Brew.clicked.connect(lambda: self.show_chapter('Brew'))

    def show_chapter(self,what):
        print(self.this_file_path)
   
        filename=(self.this_file_path/"help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
        full_what=what+".html"
        filename=(self.this_file_path/"help/GeneralHelp/"/full_what).resolve()
          
        text=open(filename,'r',encoding="utf-8").read()
        self.ui.textEdit.setHtml(prepend+text) 
