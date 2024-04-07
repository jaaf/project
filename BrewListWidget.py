
'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''
from database.brews.brew import all_brew
from ListModels import BrewListModel
from PyQt6.QtWidgets import QListView,QVBoxLayout,QHBoxLayout,QPushButton,QWidget,QLabel,QDateEdit,QCheckBox,QLineEdit,QLabel,QFrame,QComboBox
from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon,QPalette,QFont
from BrewWidget import BrewWidget
from datetime import date
from HelpMessage import HelpMessage



class BrewListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent
        self.icon_path=self.parent.icon_path
 
        self.icon_size=QSize(32,32)
        self.sortButton=QPushButton()
        self.listView=QListView()
        self.selection=None
        
        self.brewWidget=None

        #set connections
        self.listView.clicked.connect(self.select_brew)

    def setup_gui(self):  


        #create a toolbar
        toolbarLayout=QHBoxLayout()
        #FILTERS
        self.filterLayout=QHBoxLayout()
        self.dateFilterLayout=QVBoxLayout()
        self.dateSubFilterLayout=QHBoxLayout()
        self.dateFilter=QCheckBox("Filtrer dates")
        self.startDateEdit=QDateEdit()
        self.startDateEdit.setCalendarPopup(True)
        self.endDateEdit=QDateEdit()
        self.endDateEdit.setDate(date.today())
        self.endDateEdit.setCalendarPopup(True)
        self.duLabel=QLabel("du")
        self.dateSubFilterLayout.addWidget(self.duLabel)
        self.dateSubFilterLayout.addWidget(self.startDateEdit)
        self.auLabel=QLabel("au")
        self.dateSubFilterLayout.addWidget(self.auLabel)
        self.dateSubFilterLayout.addWidget(self.endDateEdit)
        self.dateFilterLayout.addWidget(self.dateFilter)
        self.dateFilterLayout.addLayout(self.dateSubFilterLayout)

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
        self.dateFilterLayout.setSpacing(0)
        self.dateSubFilterLayout.setSpacing(2)
        self.filterButton=QPushButton()
        self.filterButton.setIcon(QIcon(self.icon_path+'filter-slash-svgrepo-com.svg'))
        self.filterButton.setIconSize(self.icon_size)
        self.filterButton.setToolTip("Appliquer les filtres")
        self.filterLayout.addWidget(self.filterButton)
        self.filterLayout.addLayout(self.nameFilterLayout)
        self.filterLayout.addLayout(self.styleFilterLayout)
        self.filterLayout.addLayout(self.dateFilterLayout)
        self.filterHelpButton=QPushButton("?")
        self.filterHelpButton.resize(24,24)
        self.filterHelpButton.setMaximumWidth(24)
        self.filterHelpButton.setToolTip("Obtenir de l'aide sur le filtrage")
        self.filterHelpButton.setStyleSheet("background-color:green;color:white")
        self.filterLayout.addWidget(self.filterHelpButton)

        self.hide_sub_filter("name")
        self.hide_sub_filter("style")
        self.hide_sub_filter("date")

        self.sortCombo=QComboBox()
        self.sortCombo.addItem("")
        self.sortCombo.addItem('Date-Nom-Style')
        self.sortCombo.addItem("Nom-Date-Style")
        self.sortCombo.addItem("Style-Date-Nom")
        self.sortButton.setIcon(QIcon(self.icon_path+'sort-list-alt-svgrepo-com.svg'))
        self.sortButton.setIconSize(self.icon_size)
        self.sortButton.setMaximumSize(40,40)
        self.sortButton.setToolTip('Trier les sessions')
        spacerItem = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        spacerItemSmall = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        toolbarLayout.addItem(spacerItem)
        
        #toolbarLayout.addLayout(self.filterLayout)
        self.filterFrame=QFrame()
        self.filterFrame.setLayout(self.filterLayout)
        self.filterFrame.setStyleSheet("background-color:honeydew;")
        toolbarLayout.addWidget(self.filterFrame)
        toolbarLayout.addWidget(self.sortButton)
        toolbarLayout.addWidget(self.sortCombo)
        toolbarLayout.setSpacing(20)

        #create a title bar
        titlebarLayout=QHBoxLayout()
        self.titleLabel=QLabel()
        self.titleLabel.setText('LISTE DES SESSIONS DE BRASSAGE')
        title_font=QFont()
        title_font.setPointSize(int(self.font().pointSize()*1.3))
        title_font.setWeight(700)
        self.titleLabel.setFont(title_font)
        spacerItem = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        titlebarLayout.addWidget(self.titleLabel) 
        titlebarLayout.addItem(spacerItem)


        #setting the model for list view
        listLayout=QVBoxLayout()
        self.brews=all_brew()
        self.brews.sort(key=lambda x: x.brew_date)
        self.model=BrewListModel(brews=self.brews)
        font=QFont("Liberation Mono")
        #font=self.font().setStyle(QFont.styleItalic)
        self.listView.setFont(font)
        self.listView.setModel(self.model)
        self.listView.setSpacing(8)
        listLayout.addWidget(self.listView)

        #compose the widget layout
        mainLayout=QVBoxLayout()
        mainLayout.addLayout(toolbarLayout)
        mainLayout.addLayout(titlebarLayout)
        mainLayout.addLayout(listLayout)
        #listLayout.setContentsMargins(30,30,30,30)
        self.setLayout(mainLayout)

        self.sortCombo.currentTextChanged.connect(lambda: self.sort_list(self.sortCombo.currentText()))
        self.dateFilter.stateChanged.connect(self.date_filter_changed)
        self.nameFilter.stateChanged.connect(self.name_filter_changed)
        self.styleFilter.stateChanged.connect(self.style_filter_changed)
        self.filterButton.clicked.connect(self.apply_filters)
        self.filterHelpButton.clicked.connect(self.show_contextual_help)

    def show_contextual_help(self):
        helpPopup=HelpMessage() 
        filename="help/Head.html"
        prepend=open(filename,'r',encoding="utf-8").read()
        helpPopup.set_title('À propos du filtrage ')
        filename="help/BrewListFilterHelp.html"
        text=open(filename,'r',encoding="utf-8").read()
        helpPopup.set_message(prepend+text)
        helpPopup.exec()

    def apply_filters(self):
        items=self.brews
        filtered=list(filter(lambda x: \
                             (x.brew_date>self.startDateEdit.date() and x.brew_date<=self.endDateEdit.date() or not self.dateFilter.isChecked()) and \
                                (self.nameFilterEdit.text().upper() in x.name.upper() or not self.nameFilter.isChecked()) and \
                                    (self.styleFilterEdit.text().upper() in x.style.upper() or not self.styleFilter.isChecked()),items))
        self.model.brews=filtered
        self.sort_list(self.sortCombo.currentText())

    def date_filter_changed(self):
        if self.dateFilter.isChecked():
            self.show_sub_filter("date")
        else:
            self.hide_sub_filter("date")
            
    def style_filter_changed(self):
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
            case "date":
                self.startDateEdit.setVisible(False)
                
                self.endDateEdit.setVisible(False)
                self.endDateEdit.setDate(date.today())
                self.duLabel.setVisible(False)
                self.auLabel.setVisible(False)

            case "name":
                self.nameFilterEdit.setVisible(False)
                self.nameFilterEdit.setText("")
            case "style":
                self.styleFilterEdit.setVisible(False)    
                self.styleFilterEdit.setText("")    

    def show_sub_filter(self,mode):
        match mode:
            case "date":
                self.startDateEdit.setVisible(True)
                self.endDateEdit.setVisible(True)
                self.duLabel.setVisible(True)
                self.auLabel.setVisible(True)
            case "name":
                self.nameFilterEdit.setVisible(True)
            case "style":
                self.styleFilterEdit.setVisible(True)    

    def sort_list(self, mode):
        #self.source_list.sort(key=lambda x: (x.brand,x.name,x.version))
        match mode:
            case "":
                self.model.brews.sort(key=lambda x: (x.id))
            case 'Date-Nom-Style':
                self.model.brews.sort(key=lambda x: (x.brew_date,x.name,x.style))
            case "Nom-Date-Style":
                self.model.brews.sort(key=lambda x: (x.name,x.brew_date,x.style))
            case "Style-Date-Nom":
                self.model.brews.sort(key=lambda x: (x.style,x.brew_date,x.name))
        self.model.layoutChanged.emit()   

    def select_brew(self):
        indexes = self.listView.selectedIndexes()
        if indexes:
            index=indexes[0]
            self.selection=self.model.brews[index.row()]
            self.brewWidget=BrewWidget(self.selection.id,None,self)
            self.parent.brewTabWidget.addTab(self.brewWidget,self.brewWidget.nameEdit.text())
            stackIndex=self.parent.swapWidget('brew',self.parent.brewTabWidget)# ('brew',self.brewWidget)
            self.parent.stackedWidget.setCurrentIndex(stackIndex)
           

    def edit_brew(self):
        self.dlg=BrewWidget(self.selection.id,self)
        self.dlg.show()

    def delete_brew(self):
        pass    

    def new_brew(self):#not used at the moment
        self.brewWidget=BrewWidget(None,self.parent)#we pass the parent i.e. MainWindow as parent
        self.brewWidget.show() 
        self.model.brews=all_brew()  
        self.model.layoutChanged.emit()
      


