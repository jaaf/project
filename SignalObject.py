'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''


from PyQt6.QtCore import QObject,pyqtSignal

class SignalObject(object)    :
    #a python object to pass information in the calculate signal
    def __init__(self,name, value):
        self.name=name
        self.value=value

    def __repr__(self):
        return 'name is : '+self.name+ ' and value is '+str(self.value)  

