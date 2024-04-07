'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from MoveInitFilesDialogBase import Ui_Form as theDlg
from PyQt6.QtWidgets import QDialog,QLabel,QHBoxLayout,QVBoxLayout,QWidget,QFrame,QPushButton,QGroupBox,QFileDialog,QMessageBox
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from pathlib import Path
import shutil



import chardet,os
#from help.RecipeHelp import recipe_help
from SignalObject import SignalObject

class MoveInitFilesDialog(QDialog):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =theDlg()
        self.ui.setupUi(self)
        self.Dpath=None
        
        #connectins
        self.ui.pushButton.clicked.connect(self.select_file)
        self.ui.pushButton_2.clicked.connect(self.copy_files)
       
    def select_file(self):
        dir_name=QFileDialog.getExistingDirectory(self,'Sélectionnez un répertoire')
        if dir_name:
            self.Dpath=Path(dir_name) 
        self.ui.textEdit.setText(str(self.Dpath))
        
    def copy_files(self):
        #print("DEST PATH IS "+str(self.Dpath))
        #print("concat with "+str(Path(r"\base-data")))
        #source_dir=path.abspath(path.join(path.dirname(__file__),'base-data'))
        cwd=Path.cwd()
        source_path=Path(cwd,"base-data")
        
        dest_path=Path(self.Dpath,Path("base-data"))
     
        print(str(source_path))
        print(str(dest_path))
        try:
            shutil.copytree(source_path.resolve(),dest_path.resolve())
            self.set_message("success","Les fichiers ont été copiés dans "+str(dest_path.resolve()))
        except Exception as e:
            self.set_message("failure","Une erreur s’est produite! \n "+str(e))

    def set_message(self,style,text,time=500):
        print(text)
        if style =="success":
            messagePopup=QMessageBox(QMessageBox.Icon.Information,style,text,QMessageBox.StandardButton.Ok,self,Qt.WindowType.FramelessWindowHint)
            messagePopup.setStyleSheet("background-color:green;color: white;font-weight:bold")
        else:
             messagePopup=QMessageBox(QMessageBox.Icon.Critical,style,text,QMessageBox.StandardButton.Ok,self,Qt.WindowType.FramelessWindowHint)
             messagePopup.setStyleSheet("background-color:red;color: white;font-weight:bold")
        messagePopup.exec()

