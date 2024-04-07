
'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from PyQt6.QtWidgets import QLabel,QHBoxLayout,QVBoxLayout,QWidget,QFrame,QPushButton,QGroupBox

from database.profiles.equipment import all_equipment, update_equipment,Equipment, add_equipment,delete_equipment, find_equipment_by_id
from PyQt6.QtCore import QTimer


class LevelIndicator(QWidget):
    def __init__(self,pad,w,h,decimals,parent=None) :
        super().__init__(parent)
        self.pad=pad #le padding around the optimal range in percentage of the total display
        self.w=w # the width of the graphicalBox 
        self.decimals=decimals#the number of decimal places for values displayed 
     
        self.main_frame=QFrame()
        if(h<16 ):
            self.h=16
        else:
            self.h=h  
      
        self.h=h # the height of the graphicBox
        #forcing for test
        self.h=18
      
        
        self.pix_pad=int(self.w*pad/100) # the padding in px
        self.fontSize='8px'
        self.fontFamily="Carlita Sans"
    
        #self.min=self.pad
        #self.max=100-2*self.pad
        #the horizontal group box in which the 3 ranges are displayed 
        self.graphicBox=QFrame()
        self.graphicBox.setMaximumWidth(self.w)
        self.graphicBox.setMinimumWidth(self.w)
        self.setMaximumWidth(self.w+48) # including the label before the graphicBox
        #self.graphicBox.setObjectName("External")  # Changed here...
        #self.graphicBox.setStyleSheet("QGroupBox#External { border: 2px solid red;}") 
        self.graphicBox.setStyleSheet("font-size:"+self.fontSize+";")
        self.layout=QHBoxLayout()
        #the part of the bar under min value
        self.lowLine=QFrame()
        self.lowLine.setStyleSheet("background-color:lightgray;")
        self.lowLine.setMinimumHeight(self.h)
        self.lowLine.setMinimumWidth(self.pix_pad)
        self.lowLine.setMaximumWidth(self.pix_pad)
        #the part of the bar above the max value
        self.highLine=QFrame()
        self.highLine.setMinimumHeight(self.h)
        self.highLine.setMinimumWidth(self.pix_pad)
        self.highLine.setMaximumWidth(self.pix_pad)
        self.highLine.setStyleSheet("background-color:lightgray")
        #the part of the bar for the optimal range
        self.mediumLine=QFrame()
        self.mediumLine.setStyleSheet("background-color:lightgreen")
        self.mediumLine.setMinimumHeight(self.h)
        self.mediumLine.setMinimumWidth(self.w-(2*self.pix_pad))
        self.mediumLine.setMaximumWidth(self.w-(1*self.pix_pad))
        self.layout.addWidget(self.highLine)
        self.layout.insertWidget(0,self.mediumLine)
        self.layout.insertWidget(0,self.lowLine)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.graphicBox.setLayout(self.layout)
        self.graphicBox.setMinimumHeight(self.h)
        self.graphicBox.setMaximumHeight(self.h)
        self.globalLayout=QHBoxLayout()
        self.label=QLabel('Text')
        self.label.setMaximumWidth(48)
        self.label.setMinimumWidth(48)
        self.globalLayout.addWidget(self.graphicBox)
        self.globalLayout.insertWidget(0,self.label)
        self.globalLayout.setContentsMargins(2,0,0,0)
        self.main_frame.setLayout(self.globalLayout) 
        self.main_frame.setObjectName("MyFrame")
        self.main_frame.setStyleSheet("QFrame#MyFrame { border: 2px solid #ddd;}")
        self.overallLayout=QVBoxLayout()
        self.overallLayout.setContentsMargins(0,0,0,0)
        self.overallLayout.addWidget(self.main_frame)
        self.setLayout(self.overallLayout)
        #the mark for the actual value
        self.mark = QLabel()
        #self.mark.name='square'
        self.mark.resize(5, self.h)
        self.mark.setStyleSheet('background-color:blue;') #will be changed depending of where the value is
       
        self.mark.move(0,10) 
        self.mark.setParent(self.graphicBox)

        self.aMin_label=QLabel('')
        self.aMin_label.setStyleSheet("font-size:"+self.fontSize+"; color:blue;padding:0")
        self.aMin_label.resize(48,10)
        self.aMin_label.setParent(self.graphicBox)

        self.aMax_label=QLabel('')
        self.aMax_label.setStyleSheet('font-size:'+self.fontSize+';padding:0;color:blue')
        self.aMax_label.resize(32,10)
        self.aMax_label.setParent(self.graphicBox)

        self.amin_label=QLabel('')  
        self.amin_label.setStyleSheet('font-size:'+self.fontSize+';padding:0;color:blue')
        self.amin_label.resize(32,10)
        self.amin_label.setParent(self.graphicBox)

        self.amax_label=QLabel('')
        self.amax_label.setStyleSheet('font-size:'+self.fontSize+';padding:0;color:blue')
        self.amax_label.resize(32,10)
        self.amax_label.setParent(self.graphicBox)
    
        self.av_label=QLabel('')
        self.av_label.resize(32,10)
        self.av_label.setParent(self.graphicBox)
    
 
    def setText(self,astring):
        #the title of the level indicator (what it is displaying)
        self.label.setText(astring)    


    def setValue(self,av):
        #pass the actual value usable after a first setValues has been done;
        if(self.amin and self.amax):
            self.setValues(self.amin,self.amax,av)


    def setValues(self,amin,amax,av):
        container_width=self.graphicBox.width()
        #pmin pmax pv values on the percentage scale
        #amin amax av  actual values
        # we have pv= pmin +((av-amin)/(amax-amin)*(pmax -pmin))
        self.amin=amin
        self.amax=amax
        self.pixmin=int(container_width*self.pad/100)
        self.pixmax=int(container_width*(100-self.pad)/100)
        pv=float(self.pad)+((av-self.amin)/(self.amax - self.amin))*(100-2*self.pad)
      
        #pMax maximum displayable value en percentage scale
        r=(100-2*self.pad)/self.pad
        #aMax maximum actual value displayable  (i.e. the value at the end of the bar)
        aMax=self.amax+ (self.amax-self.amin)/r#3 is 60/20
      
        #aMin minimum actual value displayable
        aMin=self.amin-((self.amax-self.amin)/r) 
        
        self.aMin_label.setText(str(round(aMin,self.decimals)))
        self.aMin_label.move(8,0)

        self.aMax_label.setText(str(round(aMax,self.decimals)))
        self.aMax_label.move(int(container_width-37),0)
        
        self.amin_label.setText(str(round(amin,self.decimals)))
        self.amin_label.move(self.pixmin,0)
      

        self.amax_label.setText(str(round(amax,self.decimals)))
        self.amax_label.move(self.pixmax-32,0)
        
        self.av_label.setText(str(round(av,self.decimals)))
        mark_pos=(container_width/100*pv)-5
        if(mark_pos>=container_width-5):
            mark_pos=container_width-5
            self.mark.setStyleSheet("background-color:red")
            self.av_label.setStyleSheet("font-size:"+self.fontSize+";padding:0;color:red")
            self.av_label.move(int(mark_pos-30),self.h-10)
            self.mark.move(int(mark_pos-5),0)
        elif (mark_pos<0):
            mark_pos=0
            self.mark.setStyleSheet("background-color:red") 
            self.av_label.setStyleSheet("font-size:"+self.fontSize+";padding:0;color:red")
            self.av_label.move(int(mark_pos+8),self.h-10)
            self.mark.move(0,0)
        elif (mark_pos<self.pixmin) :
            self.mark.setStyleSheet("background-color:coral") 
            self.av_label.setStyleSheet("font-size:"+self.fontSize+";padding:0;color:coral")
            self.av_label.move(int(mark_pos+6),self.h-10)
            self.mark.move(int(mark_pos-5),0)
        elif    (mark_pos>self.pixmax):
            self.mark.setStyleSheet("background-color:coral") 
            self.av_label.setStyleSheet("font-size:"+self.fontSize+";padding:0;color:coral")
            self.av_label.move(int(mark_pos-32),self.h-10) 
            self.mark.move(int(mark_pos-5),0)
        else:
            self.mark.setStyleSheet("background-color:green") 
            self.av_label.setStyleSheet("font-size:"+self.fontSize+";padding:0;color:green;font-weight:bold")
            self.av_label.move(int(mark_pos+6),self.h-10)
            self.mark.move(int(mark_pos-5),0)
        if(av==0):
            self.mark.setStyleSheet('font-size:'+self.fontSize+';background-color:lightgray')
        #self.mark.setStyleSheet("background-color: magenta")
       
        

    def reset(self):
        self.mark.setStyleSheet('font-size:'+self.fontSize+';background-color:blue')
        self.mark.move(8,0)
        self.amin_label.setText('')
        self.amax_label.setText('')
        self.aMax_label.setText('')
        self.aMin_label.setText('')
        self.av_label.setText('')

