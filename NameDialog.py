'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from NameDialogBase import Ui_Dialog as theDlg
from PyQt6.QtWidgets import QDialog,QLabel,QHBoxLayout,QVBoxLayout,QWidget,QFrame,QPushButton,QGroupBox,QFileDialog,QMessageBox
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from pathlib import Path
import shutil
from database.brews.brew import (Brew, add_brew, all_brew, delete_brew,
                                 find_brew_by_id, find_brew_by_name, find_brew_by_name_and_date,
                                 update_brew)

from datetime import date
import chardet,os
#from help.RecipeHelp import recipe_help


class NameDialog(QDialog):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =theDlg()
        self.ui.setupUi(self)
        self.parent=parent
        self.date=date.today()
        self.name=ModuleNotFoundError
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.tryButton.clicked.connect(self.test_name)
        self.ui.nameEdit.textChanged.connect(self.update_name)

    def update_name(self):
        self.name=self.ui.nameEdit.text()

    def set_name(self,name):
        self.ui.nameEdit.setText(name)

    def set_intro(self,intro):
        self.ui.introEdit.setText(intro)   
    
    def set_date(self,date):
        self.date=date

    def test_name(self):   
        self.ui.messageEdit.setText("")
        
        name=self.ui.nameEdit.text()
        if len(name) >50:
            self.ui.messageEdit.setText("Ce nom est trop long. Il doit compter moins de 50 caractères")
            return

    
        result=find_brew_by_name_and_date(name,self.date)
        if  result is not None:
            
            self.ui.messageEdit.setText("Ce couple (nom, et date d’aujourd’hui) existe déjà ! Merci d’en essayer un autre")
        else:
            
            self.accept()

