from fpdf import FPDF
from database.brews.brew import (Brew, add_brew, all_brew, delete_brew,
                                 find_brew_by_id, find_brew_by_name, 
                                 update_brew)
from database.profiles.equipment import (Equipment, add_equipment,
                                         all_equipment, delete_equipment,
                                         find_equipment_by_name,
                                         update_equipment)
from dateUtils import DateUtils
from PyQt6.QtWidgets import QFileDialog
import jsonpickle,os
from pathlib import Path


class  PDFWriter (FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.lm=10
        self.rm=10
        self.bm=10
        self.set_left_margin(self.lm)
        self.set_right_margin(self.rm)
        self.lh=4
        self.font_name=""
      
        #try embedded fonts first
        try:
            self.add_font('DejaVuSans','','.\/base-data/fonts/DejaVuSans/DejaVuSans.ttf',uni=True)
            self.add_font('DejaVuSans','B','.\/base-data/fonts/DejaVuSans/DejaVuSans-Bold.ttf',uni=True)
            self.add_font('DejaVuSans','BI','.\/base-data/fonts/DejaVuSans/\DejaVuSans-BoldOblique.ttf',uni=True)
            self.font_name="DejaVuSans"

        except Exception as e:
            print(e)
            try:
                self.add_font('LinLibertine','','.\/base-data/fonts/LinuxLibertine/LinLibertine_Rah.ttf',uni=True)
                self.add_font('LinLibertine','B','.\/base-data/Fonts/LinuxLibertine/LinLibertine_RBah.ttf',uni=True)
                self.add_font('LinLibertine','BI','.\/base-data/fonts/LinuxLibertine/LinLibertine_RBIah.ttf',uni=True)
                self.font_name="LinLibertine"
            except Exception as e:
                print(e)    
                try:
                    self.add_font('LinBiolinum','','.\/base-data/fonts/LinuxLibertine/LinBiolinum_Rah.ttf',uni=True)
                    self.add_font('LinBiolinum','B','.\/base-data/fonts/LinuxLibertine/LinBiolinum_RBah.ttf',uni=True)
                    self.add_font('LinBiolinum','BI','.\/base-data/fonts/LinuxLibertine/LinLibertine_RBIah.ttf',uni=True)
                    self.font_name="LinBiolinum"                    

                except Exception as e:
                    print(e)
                    #try system fonts
                    try:
                        self.add_font('DejaVuSans','',r'C:\Windows\Fonts\DejaVuSans.ttf',uni=True)
                        self.add_font('DejaVuSans','B',r'C:\Windows\Fonts\DejaVuSans-Bold.ttf',uni=True)
                        self.add_font('DejaVuSans','BI',r'C:\Windows\Fonts\DejaVuSans-BoldOblique.ttf',uni=True)
                        self.font_name="DejaVuSans"
                    except Exception as e:
                        print(e)
                        try:

                            self.add_font('Arial','',r'C:\Windows\Fonts\arial.ttf',uni=True)
                            self.add_font('Arial','B',r'C:\Windows\Fonts\arialbd.ttf',uni=True)
                            self.add_font('Arial','BI',r'C:\Windows\Fonts\arialbi.ttf',uni=True)
                            self.font_name="Arial"
                        except Exception as e:
                            
                            print(e)
                    
                            self.add_font('Verdana','',r'C:\Windows\Fonts\verdana.ttf',uni=True)
                            self.add_font('Verdana','B',r'C:\Windows\Fonts\verdanab.ttf',uni=True)
                            self.add_font('Verdana','BI',r'C:\Windows\Fonts\verdanaz.ttf',uni=True)
                            self.font_name="Verdana"
                            
                #if exception still occurs the calling program will catch it

        print("chosen font : "+self.font_name)
        self.set_font(self.font_name,'',8)
        self.nb_page=1
        
    #--------------------------------------------------------------------------------------------------------------
    def create_header(self,name,date,page=""):
        self.set_font(self.font_name,"B",10)
        self.cell(170,10,"Brassage du "+date+" — "+name,border="LTB",  new_x="RIGHT",new_y="TOP",align='L')  
        self.cell(20,10,"Page "+page,border="TRB", new_x="LEFT",new_y="NEXT",align='L')
        self.set_font(self.font_name,"",8)
        self.set_y(self.get_y()+self.lh)

    #--------------------------------------------------------------------------------------------------------------
    def create_subtitle(self,text):
        self.set_font(self.font_name,"BI",10)
        self.cell(0,10,text,  new_x="LEFT",new_y="NEXT",align='L')  
        self.set_font(self.font_name,"",8)

    #--------------------------------------------------------------------------------------------------------------
    def create_fermentable_table(self,pos_x,pos_y,list,place="l",show_title=False):
        self.set_font(self.font_name,"B",8) 
        self.set_xy(pos_x,pos_y)
        lh=4
        self.cell(40,lh,"Fermentables", border=0,new_y="NEXT",align="L")
        self.set_x(pos_x)
        self.set_font(self.font_name,'',8)
        current_y=pos_y+self.lh #one line for title
        for item in list:
            self.cell(40,lh,item.fermentable.name.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(30,lh,item.fermentable.brand.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(12,lh,str(round(item.quantity,2))+"kg",border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(30,lh,"Rendement : "+str(item.fermentable.potential)+"%",border=0,new_x="RIGHT",new_y="TOP",align="L")
            
            self.cell(33,lh,"Pourcentage : "+str(round(item.initial_fraction*100,2))+"%",border=0,new_x="RIGHT",new_y="TOP",align="L")
            #after last column
            current_y+=lh
            self.set_xy(pos_x,current_y)

    #--------------------------------------------------------------------------------------------------------------
    def create_hop_table(self,pos_x,pos_y,list,place="l",show_title=False):
        self.set_font(self.font_name,"B",8) 
        self.set_xy(pos_x,pos_y)
        lh=4
        self.cell(40,lh,"Houblons", border=0,new_y="NEXT",align="L")
        self.set_x(pos_x)
        self.set_font(self.font_name,'',8)
        current_y=pos_y+self.lh #one line for title
        for item in list:
            self.cell(40,lh,item.hop.name.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(30,lh,item.hop.supplier.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(12,lh,str(round(item.quantity,0))+"g",border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(30,lh, "AA : "+ str(item.hop.alpha)+"%",border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(33,lh,"Pourcentage : "+str(round(item.fraction*100,2))+"%",border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(20,lh,item.hop.form,border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(20,lh,item.hop.purpose,border=0,new_x="RIGHT",new_y="TOP",align="L")
            #after last column
            current_y+=lh
            self.set_xy(pos_x,current_y)

    #--------------------------------------------------------------------------------------------------------------
    def create_yeast_table(self,pos_x,pos_y,list,place="l",show_title=False):
        self.set_font(self.font_name,"B",8) 
        self.set_xy(pos_x,pos_y)
        lh=4
        self.cell(40,lh,"Levures", border=0,new_y="NEXT",align="L")
        self.set_x(pos_x)
        self.set_font(self.font_name,'',8)
        current_y=pos_y+self.lh #one line for title
        for item in list:
            self.cell(40,lh,item.yeast.name.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(30,lh,item.yeast.brand.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(40,lh,str(round(item.quantity,0))+" "+item.yeast.pack_unit,border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(30,lh, "Att : "+ str(item.yeast.attenuation)+"%",border=0,new_x="RIGHT",new_y="TOP",align="L")
            #after last column
            current_y+=lh
            self.set_xy(pos_x,current_y)  

    #--------------------------------------------------------------------------------------------------------------
    def create_misc_table(self,pos_x,pos_y,list,place="l",show_title=False):
        self.set_font(self.font_name,"B",8) 
        self.set_xy(pos_x,pos_y)
        lh=4
        self.cell(40,lh,"Ingrédients divers", border=0,new_y="NEXT",align="L")
        self.set_x(pos_x)
        self.set_font(self.font_name,'',8)
        current_y=pos_y+self.lh #one line for title
        for item in list:
            self.cell(40,lh,item.misc.name.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(30,lh,item.misc.category,border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(40,lh,str(round(item.quantity,0))+" "+item.misc.unit,border=0,new_x="RIGHT",new_y="TOP",align="L")
            #after last column
            current_y+=lh
            self.set_xy(pos_x,current_y) 

    #--------------------------------------------------------------------------------------------------------------
    def create_rest_table(self,pos_x,pos_y,list,place="l",show_title=False):
        self.set_font(self.font_name,"B",8) 
        self.set_xy(pos_x,pos_y)
        lh=4
        self.cell(40,lh,"Programme d'empâtage", border=0,new_y="NEXT",align="L")
        self.set_x(pos_x)
        self.set_font(self.font_name,'',8)
        current_y=pos_y+self.lh #one line for title
        for item in list:
            self.cell(40,lh,item.name.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(12,lh,str(item.temperature)+"°C",border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(12,lh,str(round(item.duration,0))+"min.",border=0,new_x="RIGHT",new_y="TOP",align="L")
            #after last column
            current_y+=lh
            self.set_xy(pos_x,current_y)        

    #--------------------------------------------------------------------------------------------------------------
    def create_recipe_table(self,pos_x,pos_y,title,list,place="l",show_title=False,wide=False,header_line=False):
        self.set_font(self.font_name,"B",8) 
        self.set_xy(pos_x,pos_y)
        lh=4
        self.cell(40,lh,title, border=0,new_y="NEXT",align="L")
        self.set_x(pos_x)
        self.set_font(self.font_name,'',8)
        current_y=pos_y+self.lh #one line for title
        for item in list:
            if wide:
                self.cell(40,lh,item.name.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            else:
                self.cell(30,lh,item.name.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(10,lh,str(item.value),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(10,lh,str(item.unit),border=0,new_x="RIGHT",new_y="TOP",align="L")
            #after last column
            current_y+=lh
            self.set_xy(pos_x,current_y)

    #--------------------------------------------------------------------------------------------------------------
    def create_result_table(self,pos_x,pos_y,title,list,place="l",show_title=False,wide=False,header_line=False):
        self.set_font(self.font_name,"B",8) 
        self.set_xy(pos_x,pos_y)
        lh=4
        self.cell(40,lh,title, border=0,new_y="NEXT",align="L")
        self.set_x(pos_x)
        self.set_font(self.font_name,'',8)
        current_y=pos_y+self.lh #one line for title
        if header_line:
            self.set_font(self.font_name,"B",8)
            self.cell(50,lh,"",border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(15,lh,"Prévu",border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(15,lh,"Observé",border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(10,lh,"Unité",border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.set_font(self.font_name,'',8)
            #after last column
            current_y+=lh
            self.set_xy(pos_x,current_y)
        for item in list:
            if wide:
                self.cell(40,lh,item.name.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            else:
                self.cell(50,lh,item.name.lower().capitalize(),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(15,lh,str(item.expected),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(15,lh,str(item.observed),border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.cell(10,lh,str(item.unit),border=0,new_x="RIGHT",new_y="TOP",align="L")
            #after last column
            current_y+=lh
            self.set_xy(pos_x,current_y)       

    #--------------------------------------------------------------------------------------------------------------
    def create_notes_table(self,pos_x,pos_y,list,place="l",show_title=False):
        self.set_xy(pos_x,pos_y)
        current_y=self.get_y()
        lh=4
        
        for item in list:
            self.set_font(self.font_name,"B",8)
            self.multi_cell(30,lh,item.title,border=0,new_x="RIGHT",new_y="TOP",align="L")
            self.set_font(self.font_name,"",8)
            self.multi_cell(160,lh,item.content,border=0,new_x="RIGHT",new_y="NEXT",align="L")
            n=self.get_num_of_lines_in_multicell(item.content,160) 
            print("number of lines is "+str(n))
            current_y+=self.lh*(n+1)
            self.set_y(current_y)

    #--------------------------------------------------------------------------------------------------------------
    def create_v_space(self,value):
        self.cell(0,value,"",0,new_x="LMARGIN",new_y="NEXT")

    #--------------------------------------------------------------------------------------------------------------
    def prepare_tables(self,brew,brewWidget):
        #prepare the data to display in tables
        #Données recette
        self.recipe_data=[]
        self.recipe_data2=[]
        class RecipeLine(object):
            def __init__(self,name,value,unit):
                self.name=name
                self.value=value
                self.unit=unit
        class ResultLine(object):
            def __init__(self,name, expected , observed, unit):
                self.name =name
                self.expected=expected
                self.observed=observed
                self.unit=unit

        a=RecipeLine('Type de brassage',brew.rtype,'')
        self.recipe_data.append(a)
        b=RecipeLine('Couleur',brew.color,'EBC')
        self.recipe_data.append(b)
        c=RecipeLine('Carbonation','','Vol.')
        self.recipe_data.append(c)

        a1=RecipeLine('Volume fermenteur',brew.batch_volume,'litres')
        self.recipe_data2.append(a1)
        b1=RecipeLine("Densité d'origine",brew.og,'SG')
        self.recipe_data2.append(b1)
        c1=RecipeLine("Temps d'ébullition",brew.boil_time,'minutes')
        self.recipe_data2.append(c1)
        d1=RecipeLine("Alcool en volume",str(round(brew.abv,1)),'%')
        self.recipe_data2.append(d1)

        #Données d’équipement
        
        equipment=jsonpickle.decode(brew.equipment)

        self.equipment_data1=[]
        a=RecipeLine("Type d'équipement",equipment.type,"")
        self.equipment_data1.append(a)
        b=RecipeLine("Absorption par le grain",equipment.grain_absorption,"l/kg")
        self.equipment_data1.append(b)
        c=RecipeLine("Absorption par le houblon",equipment.hop_absorption,"l/kg")
        self.equipment_data1.append(c)
        c=RecipeLine("Coeff. réducteur vrac",equipment.hop_absorption_reduction_coeff,"")
        self.equipment_data1.append(c)
        c=RecipeLine("Altitude",equipment.altitude,"m")
        self.equipment_data1.append(c)
   

        self.equipment_data2=[]
        a=RecipeLine("Efficacité d'empâtage",equipment.mash_efficiency,"%")
        self.equipment_data2.append(a)
        a=RecipeLine("Finesse d'empâtage",equipment.mash_thickness,"%")
        self.equipment_data2.append(a)
        a=RecipeLine("Volume sous grain",equipment.mash_tun_undergrain,"l")
        self.equipment_data2.append(a)
        a=RecipeLine("Capacité calo. equiv. grain",equipment.mash_tun_heat_capacity_equiv,"kg")
        self.equipment_data2.append(a)
        a=RecipeLine("Rétention",equipment.mash_tun_retention,"l")
        self.equipment_data2.append(a)

        self.equipment_data3=[]
        a=RecipeLine("Taux d'évaporation",equipment.kettle_evaporation_rate,"l/h")
        self.equipment_data3.append(a)
        a=RecipeLine("Rétention",equipment.kettle_retention,"l")
        self.equipment_data3.append(a)
        a=RecipeLine("Diamètre cuve",equipment.kettle_diameter,"cm")
        self.equipment_data3.append(a)
        a=RecipeLine("Diamètre orifice couvercle",equipment.kettle_steam_exit_diameter,"cm")
        self.equipment_data3.append(a)
        a=RecipeLine("Vitesse de chauffe",equipment.kettle_heat_slope,"°C/l.min")
        self.equipment_data3.append(a)

        self.equipment_data4=[]
        a=RecipeLine("Rétention ",equipment.fermenter_retention,"l")
        self.equipment_data4.append(a)
        a=RecipeLine("Type de refroidisseur ",equipment.cooler_type,"")
        self.equipment_data4.append(a)
        a=RecipeLine("Vitesse de refroidissement ",equipment.cooler_slope,"°C/min.")
        self.equipment_data4.append(a)
        a=RecipeLine("Vitesse de vidage ",equipment.cooler_flow_rate,"l")
        self.equipment_data4.append(a)

      
 
        #FEEDBACK
        self.feedback_data=[]
        a=ResultLine("Eau d'empâtage",str(round(brewWidget.mash_water_mass,2)),"---","l")
        self.feedback_data.append(a)
        a=ResultLine("Eau de rinçage",str(round(brewWidget.sparge_water_mass,2)),"---","l")
        self.feedback_data.append(a)
        a=ResultLine("Volume du moût après rinçage",brewWidget.ui.hotAfterSpargeWortVolumeEdit.text(),brewWidget.brew_feedback.after_sparge_wort_volume,"l")
        self.feedback_data.append(a)
        a=ResultLine("Densité après rinçage",brewWidget.ui.afterSpargeGravityEdit.text(),brewWidget.brew_feedback.after_sparge_gravity,"l")
        self.feedback_data.append(a)
        #these 2 observed fields are calculated in the FeedbackDialog
        a=ResultLine("Efficacité de l'empâtage",brewWidget.equipment.mash_efficiency,brewWidget.feedbackDialog.ui.observedMashEfficiencyEdit.text(),"%")
        self.feedback_data.append(a)
        a=ResultLine("Absorption du grain",brewWidget.equipment.grain_absorption,brewWidget.feedbackDialog.ui.observedGrainAbsorptionEdit.text(),"l/kg")
        self.feedback_data.append(a)
        a=ResultLine("Vol. max. avant ébullition",brewWidget.ui.hotMaxWortVolumeEdit.text(),"","l")
        self.feedback_data.append(a)
        a=ResultLine("Eau correctrice ajoutée","0",brewWidget.brew_feedback.additional_water,"l")
        self.feedback_data.append(a)
        a=ResultLine("Temps d'ébullition additionnel","0",brewWidget.brew_feedback.additional_boil_time,"l")
        self.feedback_data.append(a)
        #from calculator
        a=ResultLine("Volume du moût après ébullition",brewWidget.ui.hotPostboilWortVolumeEdit.text(),brewWidget.brew_feedback.after_boil_wort_volume,"l")
        self.feedback_data.append(a)
        a=ResultLine("Densité après ébullition",str(round(brew.og,3)),brewWidget.brew_feedback.after_boil_gravity,"l")
        self.feedback_data.append(a)

    #--------------------------------------------------------------------------------------------------------------
    #  function which calculates the number of lines inside multicel
    def get_num_of_lines_in_multicell(self, message,cell_w):
        # divide the string in words
        n=0
        lines=message.splitlines()
        for l in lines:
            words = l.split(" ")
            line = ""
            n += 1
            for word in words:
         
                line += word + " "
                line_width = self.get_string_width(line)
                # In the next if it is necessary subtract 1 to the WIDTH
                if line_width > cell_w - 1:
                    # the multi_cell() insert a line break
                    n += 1
                    # reset of the string
                    line = word + " "

        return n
        
 
    #--------------------------------------------------------------------------------------------------------------
    def save_dialog(self):
        dialog=QFileDialog()
        dialog.setDirectory(os.getcwd())
        dialog.setNameFilter("File (*.pdf)")
        if dialog.exec():
            filename=dialog.selectedFiles()
            if filename: 
                print(filename[0]+".pdf")
                self.output(filename[0]+".pdf")
               
    #--------------------------------------------------------------------------------------------------------------
    def print_brew(self,brewWidget,destination_path):
        print("destination path in PDFWriter is "+destination_path)
        
        brew=find_brew_by_id(brewWidget.id)
        self.prepare_tables(brew,brewWidget)
        fermentables=brewWidget.fermentable_selector.destination_model.items
        hops=brewWidget.hop_selector.destination_model.items
        yeasts=brewWidget.yeast_selector.destination_model.items
        miscs=brewWidget.misc_selector.destination_model.items
        rests=brewWidget.rest_selector.destination_model.items

        
        self.create_header(brew.name,DateUtils.FrenchDate(brew.brew_date),str(self.nb_page))
        self.nb_page+=1
        self.create_subtitle("Données de la recette")
        
        
        #side by side tables 
        self.create_v_space(2)
        start=self.get_y()
        self.create_recipe_table(self.lm,start,"Généralités recette",self.recipe_data,place="l",show_title=True)
        end1=self.get_y()
        self.create_recipe_table(self.lm+63,start,"Généralités recette",self.recipe_data2,place="r",show_title=True)
        end2=self.get_y()
        self.create_rest_table(self.lm+127,start,rests,place="l",show_title=True)
        end3=self.get_y()
        self.set_y(max(end1,end2,end3)) #use the longer table

        #alone table
        self.create_v_space(2)
        start=self.get_y()
        self.create_fermentable_table(self.lm,self.get_y(),fermentables,place="l",show_title=True)

        #alone table
        self.create_v_space(2)
        start=self.get_y()
        self.create_hop_table(self.lm,start,hops,place="l",show_title=True)

        #alone table
        self.create_v_space(2)
        start=self.get_y()
        self.create_yeast_table(self.lm,start,yeasts,place="l",show_title=True)

        #alone table
        self.create_v_space(2)
        start=self.get_y()
        self.create_misc_table(self.lm,start,miscs,place="l",show_title=True)

    
        #alone table
        self.create_v_space(2)
        start=self.get_y()
    
        self.line(self.lm,start,self.lm+190,start)
        self.create_subtitle("Données de l'équipement ")

        #side by side tables 
        self.create_v_space(2)
        start=self.get_y() 
        
        self.create_recipe_table(self.lm,start,"Généralités",self.equipment_data1,place="l",show_title=True,wide=True)
        end1=self.get_y()
        self.create_recipe_table(self.lm+95,start,"Cuve d'empâtage",self.equipment_data2,place="l",show_title=True,wide=True)
        end2=self.get_y()
        self.set_y(max(end1,end2)) #use the longer table


        #side by side tables
        self.create_v_space(2)
        start=self.get_y()
        self.create_recipe_table(self.lm+95,start,"fermenteur et refroidisseur",self.equipment_data4,place="l",show_title=True,wide=True)
        end1=self.get_y()
        self.create_recipe_table(self.lm,start,"Bouilloire",self.equipment_data3,place="l",show_title=True,wide=True)
        end2=self.get_y()
        self.set_y(max(end1,end2)) #use the longer table
            
        self.create_v_space(2)
        start=self.get_y()
        self.line(self.lm,start,self.lm+190,start)
        
        nb_line=3
        nb_line+=len(self.feedback_data)
        if (nb_line*self.lh)+self.get_y()>277:
            self.add_page() 
            self.create_header(brew.name,DateUtils.FrenchDate(brew.brew_date),str(self.nb_page))
            self.nb_page+=1
            
        self.create_subtitle("Résultats ")
        #alone table
        self.create_v_space(1)
        start=self.get_y()
        self.create_result_table(self.lm,self.get_y(),"Résultats",self.feedback_data,place="l",show_title=True,header_line=True)
        self.create_v_space(2)
        self.create_v_space(2)
        start=self.get_y()
        self.line(self.lm,start,self.lm+190,start)

        nb_line=3 #for the header and first line
        list=jsonpickle.decode(brewWidget.brew_feedback.notes)
        for item in list:
            n=self.get_num_of_lines_in_multicell(item.content,160)
            nb_line+=n+1
        if (nb_line*self.lh)+self.get_y()>277:
            self.add_page()
            self.create_header(brew.name,DateUtils.FrenchDate(brew.brew_date),str(self.nb_page))
            self.nb_page+=1
        
        self.create_subtitle("Notes de session ")
        self.create_notes_table(self.lm,self.get_y(),jsonpickle.decode(brewWidget.brew_feedback.notes) )
        #self.save_dialog(
        #print font name
        self.set_xy(170,271)
        self.set_font(self.font_name,"",6)
        self.cell(20,5,self.font_name)
    
        self.output(destination_path)
    

      