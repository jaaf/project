
'''
copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

import sys
from PyQt6 import QtWidgets
from PyQt6 import QtGui
from PyQt6.QtGui import QPalette,QColor,QFont
from MainWindow import MainWindow
from database.commons.settings import Setting,all_setting, update_setting, add_setting, find_setting_by_id
import logging
import datetime
from pathlib import Path
from database.db_connection_local import logger




#Creating a handler
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
                #Will call default excepthook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        #Create a critical level log message with info from the except hook.
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
#Assign the excepthook to the handler
sys.excepthook = handle_unhandled_exception


now=datetime.datetime.now()
print('logger initialized')
app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
print("Le style des fenêtres est "+app.style().objectName())
print("La plateforme est "+sys.platform)
logger.info("Le style des fenêtres est "+app.style().objectName())
logger.info("La plateforme est "+sys.platform)
screen_resolution = QtGui.QGuiApplication.primaryScreen().availableGeometry()

#window.resize(w,h)
new_font = QFont()
new_font.setFamily('Carlito Sans') 

settings=all_setting()
for item in settings:
    if item.name=='Font Size':
        new_font.setPointSize(int(item.val))
    else:    
        new_font.setPointSize(11)

app.setFont( new_font )
print("initializing mainwindow")
window = MainWindow()
print("resizing")
window.resize(1280,720)
window.show()
app.exec()
logger.info('Application terminée par bouton de fermeture \n\n')


