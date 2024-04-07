'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from PyQt6 import QtGui,QtWidgets
from PyQt6.QtWidgets import QPushButton,QDialog,QHBoxLayout,QVBoxLayout,QTextEdit,QLabel,QTextBrowser
from pathlib import Path
class HelpMessage(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.title=QLabel()
        self.body=QTextBrowser()
        self.body.setOpenExternalLinks(True)
        buttonLayout=QHBoxLayout()
        #horizontalSpacer=QtWidgets.QSpacerItem(10,10,QtWidgets.QSizePolicy.maximum,QtWidgets.QSizePolicy.expanding)
        #buttonLayout.addItem(horizontalSpacer)
        self.closeButton=QPushButton('Fermer')
        buttonLayout.addWidget(self.closeButton)

        mainLayout=QVBoxLayout()
        mainLayout.addWidget(self.title)
        mainLayout.addWidget(self.body)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        self.resize(800,400)
        self.closeButton.clicked.connect(self.close)
        self.this_file_path=Path(__file__).parent

    def set_title(self, title):
        self.title.setText(title)
        self.title.setStyleSheet('font-size:18px; font-weight:600;')
        
    def set_message(self,message):
        filename=(self.this_file_path/"help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
        self.body.setHtml(prepend+message) 
          

    def close(self):
        self.accept()
