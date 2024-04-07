'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from SignalObject import SignalObject


class MyStandardItem(QtGui.QStandardItem):
    def __init__(self,text,data=None,parent=None):
        super(MyStandardItem,self).__init__(text)
        if data is not None:
            self.data=data
        else:
            self.data=None
        
        

    def get_data(self):
        return self.data
    
class CheckableComboBox(QtWidgets.QComboBox):
    
    closedPopup = QtCore.pyqtSignal()

    def __init__(self,parent=None):
        super(CheckableComboBox, self).__init__(parent)
        
        self.setView(QtWidgets.QListView(self))
        self.view().pressed.connect(self.handleItemPressed)
        self._changed = False
        self.setModel(QtGui.QStandardItemModel(self))
        self.closeOnLineEditClick=False
        firstItem = MyStandardItem("Cocher pour activer")
        firstItem.setBackground(QtGui.QBrush(QtGui.QColor(200, 200, 200)))
        firstItem.setSelectable(False)
        firstItem.setCheckable(False)
        firstItem.setEditable
        self.model().appendRow(firstItem) 
 
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)
        self._changed=True

    def checkedItems(self):
        l = []
        for i in range(self.model().rowCount()):
            it = self.model().item(i)
            if it.checkState() == Qt.CheckState.Checked:
                if it.data is not None:
                    l.append(it.get_data())
                else:    
                    l.append(it.text())
        return l

    def hidePopup(self):
        if not self._changed:
            print('emitting')
            self.closedPopup.emit()
            super(CheckableComboBox, self).hidePopup()
            QtCore.QTimer.singleShot(0, lambda: self.setCurrentIndex(0))
        self._changed=False
    