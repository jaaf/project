
'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from FeedbackWidgetBase import Ui_Form as feedback_ui
from PyQt6 import QtCore
from PyQt6.QtCore import  Qt
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget,QCheckBox,QGroupBox,QPushButton,QHBoxLayout,QVBoxLayout,QLineEdit,QLabel,QListView
from HelpMessage import HelpMessage
from BrewUtils import BrewUtils
from FeedbackObject import FeedbackObject
import jsonpickle
from pathlib import Path

class FeedbackWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent) 
        self.parent=parent 
        self.ui =feedback_ui()
        self.ui.setupUi(self)
        self.note_list=[]
        self.note_model=NoteModel(notes=self.note_list)
        self.ui.listView.setModel(self.note_model)
        self.note_selection=None
        self.ui.deleteButton.setVisible(False)
        self.ui.updateButton.setVisible(False)
        self.this_file_path=Path(__file__).parent
        
        

        app = QtWidgets.QApplication.instance()
        #as use of setStyleSheet prevents correct font propagation. Prepend all style with this prefix to fix this issue
        self.font_style_prefix='font:'+str(app.font().pointSize())+'pt '+app.font().family()+';'
        #don't understand why font is not correctly propagated though is is for hop and yeasts
        self.setFont(app.font())
        self.ui.additionalBoilTimeHelpButton.setStyleSheet(self.font_style_prefix+'background-color:red; color:white; font-weight:bold;')
        self.ui.additionalWaterHelpButton.setStyleSheet(self.font_style_prefix+"background-color: green; color:white;") 
        self.ui.afterSpargeGravityHelpButton.setStyleSheet(self.font_style_prefix+"background-color: green; color:white;")
        self.ui.beforeBoilVolumeHelpButton.setStyleSheet(self.font_style_prefix+"background-color: green; color:white;")
        self.ui.listView.setStyleSheet("QListView{border: 2px solid green;}""QListView::item:selected{border: 3px solid red;color:blue;background-color:white}""QListView::item{border-bottom:2px solid gray}")

        #connections
        self.ui.additionalBoilTimeHelpButton.clicked.connect(lambda:self.show_contextual_help('additional_boil_time'))
        self.ui.additionalWaterHelpButton.clicked.connect(lambda:self.show_contextual_help('additional_water'))
        self.ui.afterSpargeGravityHelpButton.clicked.connect(lambda:self.show_contextual_help('after_sparge_gravity'))
        self.ui.beforeBoilVolumeHelpButton.clicked.connect(lambda:self.show_contextual_help('before_boil_volume'))

        
        self.ui.observedAfterSpargeGravityEdit.textChanged.connect(self.calculated_mash_efficiency)
        self.ui.observedAfterSpargeVolumeEdit.textChanged.connect(self.calculated_mash_efficiency)
        self.ui.addButton.clicked.connect(self.add_note)
        self.ui.listView.clicked.connect(self.select_note)
        self.ui.deleteButton.clicked.connect(self.delete_note)
        self.ui.updateButton.clicked.connect(self.update_note)
            #------------------------------------------------------------------


                #------------------------------------------------------------------------------
    def select_note(self):
        #select an item in the source (public) list for addition to the destination list
        old_selection=self.note_selection
        indexes =self.ui.listView.selectedIndexes()
        if indexes:
            index=indexes[0] 
            self.note_selection=self.note_model.notes[index.row()]
            if (old_selection==self.note_selection):  
                self.clear_selection()   
                
            else:
                self.load_note()
                self.ui.addButton.setVisible(False)
                self.ui.deleteButton.setVisible(True)
                self.ui.updateButton.setVisible(True)
        else:
            self.clear_selection() 
         
        try:
            print(self.note_selection.content)
        except:
            pass
        #self.adapt_form()        
    #----------------------------------------------------------------------------------------
    def clear_selection(self):
 
                self.note_selection=None
                self.ui.listView.clearSelection() 
                self.clear_note()
                #self.reset_form()
                #to delete the inverted highlight background on the last selected item
                self.ui.listView.clearFocus()
    def load_note(self): 
        self.ui.noteTitleEdit.setText(self.note_selection.title)
        self.ui.noteContentEdit.setText(self.note_selection.content)
    def clear_note(self):
        self.ui.noteContentEdit.setText("")
        self.ui.noteTitleEdit.setText("")
        self.ui.addButton.setVisible(True)
        self.ui.deleteButton.setVisible(False)
        self.ui.updateButton.setVisible(False)
        pass
    def show_contextual_help(self,what):
        helpPopup=HelpMessage()
        filename=(self.this_file_path/"help/Head.html").resolve()
        prepend=open(filename,'r',encoding="utf-8").read()
       
        match what:
            case 'additional_boil_time':
                helpPopup.set_title("Temps d'ébullition additionnel")
                filename=(self.this_file_path/'help/AdditionalBoilTimeHelp.html').resolve()
                
            case 'additional_water':
                helpPopup.set_title('Eau correctrice additionnelle')
                filename=(self.this_file_path/"help/AdditionalWaterHelp.html").resolve()

            case 'after_sparge_gravity':
                helpPopup.set_title("Densité après rinçage")
                filename=(self.this_file_path/"help/AfterSpargeGravityHelp.html").resolve()

            case 'before_boil_volume':
                helpPopup.set_title("Volume maximum du môut avant ébullition")
                filename=(self.this_file_path/"help/BeforeBoilVolumeHelp.html").resolve()

        text=open(filename,'r',encoding="utf-8").read()
        helpPopup.set_message(prepend+text)
        helpPopup.exec()

        #-----------------------------------------------------------------------

    def observed_sugar(self):
        try:
            #le volume est pris froid
            sugar= BrewUtils.sugar_mass_from_SG_and_volume(float(self.ui.observedAfterSpargeGravityEdit.text()),float(self.ui.observedAfterSpargeVolumeEdit.text())/1.04)
        except:
            sugar=None
        print('in observed_sugar returning '+str(sugar))
        return sugar 
   
     
    
    #-------------------------------------------------------------------------
    def calculated_mash_efficiency(self):
     
        sugar=self.observed_sugar()
        if sugar:
            self.calculated_grain_absorption()
            #potential includes expected mash efficiency
            potential=self.parent.mash_average_potential#/(self.parent.equipment.mash_efficiency/100)
            
            print('potential is '+str(potential))

            mass=self.parent.total_mash_fermentable_mass
            print('mass is '+str(mass))
            observed_efficiency=sugar *100/(potential*mass/100)
            self.ui.observedMashEfficiencyEdit.setText(str(round(observed_efficiency,1)))
      
        
    def calculated_grain_absorption(self):
        grain_mass=self.parent.total_mash_fermentable_mass
        mash_and_sparge_water_mass=self.parent.mash_water_mass+self.parent.sparge_water_mass
        #we use the cold volume
        preboil_water_mass=BrewUtils.water_mass_from_SG_and_volume(float(self.ui.observedAfterSpargeGravityEdit.text()),float(self.ui.observedAfterSpargeVolumeEdit.text())/1.04)
        grain_absorption=(mash_and_sparge_water_mass-preboil_water_mass)/grain_mass
        self.ui.observedGrainAbsorptionEdit.setText(str((round(grain_absorption,2))))

    def init_note_list(self,list):
        self.note_list=list
        self.note_model.notes=list
        self.note_model.layoutChanged.emit()

    def add_note(self):
        title=self.ui.noteTitleEdit.text()
        content=self.ui.noteContentEdit.toPlainText() 
        note=Note(title,content)
        self.note_list.append(note)
        self.note_model.notes.append(note)
        self.note_model.layoutChanged.emit()

    def delete_note(self):
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            del self.note_model.notes[index.row()]
            self.note_model.layoutChanged.emit()
            self.clear_note()

    def update_note(self):
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            selection =self.note_model.notes[index.row()]
            selection.title=self.ui.noteTitleEdit.text()
            selection.content=self.ui.noteContentEdit.toPlainText()
            self.note_model.layoutChanged.emit()
            self.clear_selection()
    def read_observed(self):
        
        after_sparge_wort_volume=self.ui.observedAfterSpargeVolumeEdit.text()
        after_sparge_gravity=self.ui.observedAfterSpargeGravityEdit.text()
        additional_water=self.ui.observedAddedWaterEdit.text()
        additional_boil_time=self.ui.observedAdditionalBoilTime.text()
        after_boil_wort_volume=self.ui.observedAferBoilVolumeEdit.text()
        after_boil_gravity=self.ui.observedOriginalGravityEdit.text()
        notes=jsonpickle.encode(self.note_model.notes)
        self.fbo=FeedbackObject(after_sparge_wort_volume,after_sparge_gravity,additional_water,additional_boil_time,after_boil_wort_volume,after_boil_gravity,notes)
        return jsonpickle.encode(self.fbo)

class Note(object):
    def __init__(self,title,content):
        self.title=title
        self.content=content

class NoteModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, notes=None, **kwargs):
        super(NoteModel,self).__init__(*args, **kwargs)
        self.notes = notes or []
            
    def rowCount(self,index):
        return len(self.notes)      
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        
        if (role ==Qt.ItemDataRole.DisplayRole):
            n =self.notes[index.row()] 
            return str(n.title)+'\n '+str(n.content)+"\n --------------------------------------------------"
        