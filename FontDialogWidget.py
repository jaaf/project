from FontDialogWidgetBase import Ui_FontDialog as fontDlg
from PyQt6 import QtCore,QtWidgets
from PyQt6.QtWidgets import QDialog,QWidget
from database.commons.settings import Setting,all_setting, update_setting, add_setting, find_setting_by_id
from dateUtils import DateUtils
from PyQt6.QtCore import Qt,QRegularExpression,QTimer
from database.commons.country import all_country,find_country_by_code
from PyQt6.QtGui import QDoubleValidator,QRegularExpressionValidator,QIntValidator
from PyQt6 import QtGui
import sys, datetime
from HelpMessage import HelpMessage
from SignalObject import SignalObject
from BrewWidget import Communication

'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

class FontDialogWidget(QDialog):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui =fontDlg()
        self.ui.setupUi(self)
        self.id=id
       
        self.parent=parent
        settings=all_setting()
        self.ui.comboBox.addItem('8')
        self.ui.comboBox.addItem('9')
        self.ui.comboBox.addItem('10')
        self.ui.comboBox.addItem('11')
        self.ui.comboBox.addItem('12')
        self.ui.comboBox.addItem('13')
        self.ui.comboBox.addItem('14')
        self.ui.comboBox.addItem('15')
        self.ui.comboBox.addItem('16')
        
        self.ui.comboBox.addItem('17')
        self.ui.comboBox.addItem('18')
        settings=all_setting()
        print('settings all')
        print(settings)
        
        val='11'
        self.currentId=None
        for item in settings:
            if item.name=='Font Size':


                val=item.val
                self.currentId=item.id
        print('using val '+str(val))
        self.ui.comboBox.setCurrentText(val)   

        self.ui.saveButton.clicked.connect(self.save)   
        

    def save(self):
        name='Font Size'
        val=self.ui.comboBox.currentText() 
        result=None
        if not self.currentId:
            result=add_setting(Setting(None,name,val))
        else:
            result=update_setting(Setting(self.currentId,name,val))   
        self.close()    
        




