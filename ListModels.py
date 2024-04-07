'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from PyQt6 import QtCore,QtGui
from PyQt6.QtCore import Qt
from dateUtils import DateUtils

from database.fermentables.fermentable_brand import all_fbrand, find_fbrand_by_name
from database.fermentables.fermentable import all_fermentable, update_fermentable,Fermentable, add_fermentable,delete_fermentable, find_fermentable_by_id
from database.hops.hop_suppliers import all_hsupplier, find_hsupplier_by_name
from database.hops.hop import all_hop, update_hop,Hop, add_hop,delete_hop, find_hop_by_id
from database.hops.inventory_hop import all_inventory_hop, InventoryHop, add_inventory_hop, delete_inventory_hop, update_inventory_hop
from database.yeasts.yeast import all_inventory_yeast, InventoryYeast, add_inventory_yeast, delete_inventory_yeast, update_inventory_yeast
from database.yeasts.yeast import all_yeast, update_yeast,Yeast, add_yeast,delete_yeast, find_yeast_by_id
from database.yeasts.yeast import all_ybrand, find_ybrand_by_name
from database.miscs.misc import all_misc, update_misc,Misc, add_misc,delete_misc, find_misc_by_id
from database.miscs.misc import all_inventory_misc, InventoryMisc, add_inventory_misc, delete_inventory_misc, update_inventory_misc
from PyQt6.QtGui  import QFont

class RecipeListModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, recipes=None, **kwargs):
        super(RecipeListModel,self).__init__(*args, **kwargs)
        self.recipes = recipes or []  
 
        
    def data(self,index,role):
        r =self.recipes[index.row()] 
        if (role ==Qt.ItemDataRole.DisplayRole):
            return self.str_normalize(r.name.upper(),50)  +" "+self.str_normalize(r.style,50)+ " "+r.rtype
     
     #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
       
        s.strip()
        while (len(s)<l):
           s+=' ' 
        return s       
       
                      
    def rowCount(self,index):
        return len(self.recipes)


class BrewListModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, brews=None, **kwargs):
        super(BrewListModel,self).__init__(*args, **kwargs)
        self.brews = brews or []  
        
        
 
        
    def data(self,index,role):
        b =self.brews[index.row()] 
        if (role ==Qt.ItemDataRole.DisplayRole):
            return (self.str_normalize(DateUtils.FrenchDate(b.brew_date),20)+ ' '+self.str_normalize(b.name.upper(),50)+ ' '+self.str_normalize(b.style,50))
     
                
                      
    def rowCount(self,index):
        return len(self.brews)
        
    
    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s 

    '''         ##############################################################################################################
    # ############################################################################################################       
class FermentableModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, fermentables=None, **kwargs):
        super(FermentableModel,self).__init__(*args, **kwargs)
        self.fermentables = fermentables or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            f =self.fermentables[index.row()] 
            fname=self.str_normalize(f.name,15)
            fbrand=self.str_normalize(str(f.brand),20)
            return str(f.id)+' '+fname+' '+f.version +' [' +fbrand+' ]  '+'\n ('+f.form+', '+f.category+', '+str(f.color)+' EBC, '+str(f.potential)+'%, '+f.raw_ingredient+')'\
            +'\n——————————————————————————————————————————————————————————————————————————————————————————'
        if (role == Qt.ItemDataRole.DecorationRole):
            f=self.fermentables[index.row()]
            fb=find_fbrand_by_name(f.brand)
            filename='./w20/'+fb.country_code+'.png'
            return QtGui.QImage(filename)
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.fermentables)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

###########################################################################################################
# #########################################################################################################  
     
class InventoryFermentableModel(QtCore.QAbstractListModel):
    def __init__(    self, *args, inventory_fermentables=None, **kwargs):
        super(InventoryFermentableModel,self).__init__(*args, **kwargs)
        self.inventory_fermentables = inventory_fermentables or []
           
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            invf =self.inventory_fermentables[index.row()] 
            f=find_fermentable_by_id(invf.fermentable_id)
            fname=self.str_normalize(f.name,15)
            fbrand=self.str_normalize(str(f.brand),20)
            
            return fname+' '+f.version +' produit par ' +fbrand+'  '+'\n'+ \
            'QUANTITÉ : '+str(invf.quantity)+' kg'+ ' COÛT : '+str(invf.cost) + ' — Id public: '+str(invf.fermentable_id)+ ' acheté le '+DateUtils.FrenchDate(invf.purchase_date)+' '\
            '\n ('+f.form+', '+f.category+', '+str(f.color)+' EBC, '+str(f.potential)+'%, '+f.raw_ingredient+')'\
            +'\n——————————————————————————————————————————————————————————————————————————————————————————'
            #return '['+str(invf.id)+', '+f.name+' from '+f.brand+'], \n Quantity = '+str(invf.quantity)+' kg, '+'Cost = '+str(invf.cost)
        if (role == Qt.ItemDataRole.DecorationRole):
            invf =self.inventory_fermentables[index.row()] 
            f=find_fermentable_by_id(invf.fermentable_id)
            fb=find_fbrand_by_name(f.brand)
            filename='./w20/'+fb.country_code+'.png'
            return QtGui.QImage(filename)  
                
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       
                
    def rowCount(self,index):
        return len(self.inventory_fermentables)           
                     
    def FrenchDate(self,date_from_db) :
        adate=  adate=QtCore.QDate.fromString(str(date_from_db),'yyyy-MM-dd')   
        loc=QtCore.QLocale("fr_FR")
        return loc.toString(adate,'dd MMMM yyyy')     


'''
             
 ##############################################################################################################
 # ############################################################################################################     
   
class HopModel(QtCore.QAbstractListModel):
    #a model for the public QListView
    def __init__(    self, *args, hops=None, **kwargs):
        super(HopModel,self).__init__(*args, **kwargs)
        self.hops = hops or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            h =self.hops[index.row()] 
            hname=self.str_normalize(h.name,15)
            hsupplier=self.str_normalize(str(h.supplier),20)
            return str(h.id)+' '+hname+' '+h.crop_year +' vendu par ' +hsupplier+'   '+'\n ('+h.form+', '+h.purpose+', '+str(h.alpha)+' %)'\
            +'\n——————————————————————————————————————————————————————————————————————————————————————————'
        if (role == Qt.ItemDataRole.DecorationRole):
            h=self.hops[index.row()]
            filename='./w20/'+h.country_code+'.png'
            return QtGui.QImage(filename)
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.hops)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

###########################################################################################################
###########################################################################################################    
#     
class InventoryHopModel(QtCore.QAbstractListModel):
    #a model for the inventory QListView
    def __init__(    self, *args, inventory_hops=None, **kwargs):
        super(InventoryHopModel,self).__init__(*args, **kwargs)
        self.inventory_hops = inventory_hops or []
           
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            invh =self.inventory_hops[index.row()] 
            h=find_hop_by_id(invh.hop_id)
            if h is not None:
                hname=self.str_normalize(h.name,15)
                hsupplier=self.str_normalize(str(h.supplier),20)
                hid=self.str_normalize(str(h.id),3)
                return  hname+' '+h.crop_year +' acheté chez ' +hsupplier+'   '+'\n'+ \
                'QUANTITÉ : '+str(invh.quantity)+' kg'+ ' COÛT : '+str(invh.cost) +' — Id public : '+hid+ ' acheté le '+DateUtils.FrenchDate(invh.purchase_date)+\
                '\n ('+h.form+', '+h.purpose+', '+str(h.alpha)+' % )'\
                +'\n——————————————————————————————————————————————————————————————————————————————————————————'
            return "Houblon d'inventaire d'ID "+str(invh.id)+" pointant sur le houblon public d'ID "+str(invh.hop_id)+" qui n'existe plus en liste publique \n"\
            + " Cette situation ne devrait jamais se produire. "\
            +'\n——————————————————————————————————————————————————————————————————————————————————————————'
            #return '['+str(invf.id)+', '+f.name+' from '+f.brand+'], \n Quantity = '+str(invf.quantity)+' kg, '+'Cost = '+str(invf.cost)
        if (role == Qt.ItemDataRole.DecorationRole):
            invh =self.inventory_hops[index.row()] 
            h=find_hop_by_id(invh.hop_id)

            filename='./w20/'+h.country_code+'.png'
            return QtGui.QImage(filename)  
                
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       
                
    def rowCount(self,index):
        return len(self.inventory_hops)           
                     
##############################################################################################################
 # ############################################################################################################     
   
class YeastModel(QtCore.QAbstractListModel):
    #a model for the public QListView
    def __init__(    self, *args, yeasts=None, **kwargs):
        super(YeastModel,self).__init__(*args, **kwargs)
        self.yeasts = yeasts or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            y =self.yeasts[index.row()] 
            yname=self.str_normalize(y.name,15)
            ybrand=self.str_normalize(str(y.brand),20)
            return str(y.id)+' '+y.name+' produit par ' +ybrand+'\n '+y.pack_unit+' pour '+y.target
        if (role == Qt.ItemDataRole.DecorationRole):
            y=self.yeasts[index.row()]
            yb=find_ybrand_by_name(y.brand)
            filename='./w20/'+yb.country_code+'.png'
            return QtGui.QImage(filename)
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.yeasts)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

###########################################################################################################
###########################################################################################################    
#     
class InventoryYeastModel(QtCore.QAbstractListModel):
    #a model for the inventory QListView
    def __init__(    self, *args, inventory_yeasts=None, **kwargs):
        super(InventoryYeastModel,self).__init__(*args, **kwargs)
        self.inventory_yeasts = inventory_yeasts or []
           
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            invy =self.inventory_yeasts[index.row()] 
            y=find_yeast_by_id(invy.yeast_id)
            if y is not None:
                yname=self.str_normalize(y.name,15)
                ybrand=self.str_normalize(str(y.brand),20)
                yid=self.str_normalize(str(y.id),3)
                return  yname+' de ' +ybrand+'   '+'\n'+ \
                'QUANTITÉ : '+str(invy.quantity)+' '+y.pack_unit+ ' COÛT : '+str(invy.cost) +' € \nId public : '+yid+ ' acheté le '+DateUtils.FrenchDate(invy.purchase_date)
            return "Levure d'inventaire d'Id "+str(invy.id)+" pointant sur la levure publique d'ID "+str(invy.yeast_id)+" qui n'est plus en liste publique.\n"\
            +" Cette situation ne devrait jamais se produire"
            #return '['+str(invf.id)+', '+f.name+' from '+f.brand+'], \n Quantity = '+str(invf.quantity)+' kg, '+'Cost = '+str(invf.cost)
        if (role == Qt.ItemDataRole.DecorationRole):
            invy =self.inventory_yeasts[index.row()] 
            y=find_yeast_by_id(invy.yeast_id)
            if y is not None:
                b=find_ybrand_by_name(y.brand)

                filename='./w20/'+b.country_code+'.png'
                return QtGui.QImage(filename)  
                
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       
                
    def rowCount(self,index):
        return len(self.inventory_yeasts)           
                     
##############################################################################################################
 # ############################################################################################################     
   
class MiscModel(QtCore.QAbstractListModel):
    #a model for the public QListView
    def __init__(    self, *args, miscs=None, **kwargs):
        super(MiscModel,self).__init__(*args, **kwargs)
        self.miscs = miscs or []
        self.im=QtGui.QImage('./au.png')     
        
    #---------------------------------------------------------------------------------    
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            m =self.miscs[index.row()] 
            mname=self.str_normalize(m.name,15)
            return str(m.id)+' '+mname+' '+' unité : '+m.unit
     
          
    #---------------------------------------------------------------------------------                 
    def rowCount(self,index):
        return len(self.miscs)

    #---------------------------------------------------------------------------------  
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       

###########################################################################################################
###########################################################################################################    
#     
class InventoryMiscModel(QtCore.QAbstractListModel):
    #a model for the inventory QListView
    def __init__(    self, *args, inventory_miscs=None, **kwargs):
        super(InventoryMiscModel,self).__init__(*args, **kwargs)
        self.inventory_miscs = inventory_miscs or []
           
    def data(self,index,role):
        if (role ==Qt.ItemDataRole.DisplayRole):
            invy =self.inventory_miscs[index.row()] 
            y=find_misc_by_id(invy.misc_id)
            yname=self.str_normalize(y.name,15)
            yid=self.str_normalize(str(y.id),3)
            return  yname+'   '+'\n'+ \
            'QUANTITÉ : '+str(invy.quantity)+' '+y.unit+ ' COÛT : '+str(invy.cost) +' € — Id public : '+yid+ ' acheté le '+DateUtils.FrenchDate(invy.purchase_date)
            #return '['+str(invf.id)+', '+f.name+' from '+f.brand+'], \n Quantity = '+str(invf.quantity)+' kg, '+'Cost = '+str(invf.cost)
        
                
    def str_normalize(self, s,l):
        while (len(s)<l):
           s+=' ' 
        return s       
                
    def rowCount(self,index):
        return len(self.inventory_miscs)           
                     
