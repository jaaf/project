'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from ConfirmationDialogBase import Ui_ConfirmationDialog
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QPixmap


class ConfirmationDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui =Ui_ConfirmationDialog()
        self.ui.setupUi(self)

        self.ui.confirmButton.clicked.connect(self.close_confirm)
        self.ui.cancelButton.clicked.connect(self.close_cancel)
    
    def setIcon(self,icon):
        pixmap=QPixmap(icon)
        self.ui.iconLabel.setPixmap(pixmap)

    def setTitle(self,title):
        self.ui.titleLabel.setText(title)

    def setMessage(self,message):
        self.ui.textEdit.setHtml(message)  
        self.ui.textEdit.setMinimumWidth(900)
        self.ui.textEdit.setMinimumHeight(400)

    def setConfirmButtonText(self,text):
        self.ui.confirmButton.setText(text) 

    def setCancelButtonText(self,text):
        self.ui.cancelButton.setText(text)       

    def close_confirm(self):
        self.accept()

    def close_cancel(self):
        self.reject()    