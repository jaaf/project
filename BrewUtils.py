'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

'''

class BrewUtils():

    @staticmethod
    def SG_to_Plato(val):
        return (-1 * 616.868 + 1111.14 * val - 630.272 * val ** 2 + 135.997 * val ** 3)

    @staticmethod
    def Plato_to_Sg(val):
        return 1 + (val / (258.6 - ((val / 258.2) * 227.1)))
    
    @staticmethod
    def water_mass_from_SG_and_volume(SG,volume): 
        #volume at 20°C
        platos=(-1 * 616.868 + 1111.14 * SG - 630.272 * SG ** 2 + 135.997 * SG ** 3)
        total_mass=volume * SG
        return (total_mass *(100 - platos))/100

    @staticmethod
    def water_mass_from_platos_and_volume(platos,volume):
        #volume at 20°C
        SG= 1 + platos / (258.6 - (platos / 258.2) * 227.1)
        total_mass=volume * SG
        return (total_mass *(100 - platos))/100
    
   
    @staticmethod
    def sugar_mass_from_SG_and_volume(SG,volume):

        platos=(-1 * 616.868 + 1111.14 * SG - 630.272 * SG ** 2 + 135.997 * SG ** 3)
        #print("in sugar_masss_from_sg_and_volume"+"SG is "+str(SG) +" volume is "+str(volume) + " and platos is" +str(platos))
        total_mass=volume * SG
        return (total_mass *platos)/100

    @staticmethod
    def water_mass_from_SG_and_volume(SG,volume):
        platos=(-1 * 616.868 + 1111.14 * SG - 630.272 * SG ** 2 + 135.997 * SG ** 3)
        total_mass=volume * SG
        return total_mass * (100-platos)/100
    
    @staticmethod
    def volume_from_water_and_SG(water,SG):
        plato=BrewUtils.SG_to_Plato(SG)
        sugar=water*(plato/(100-plato))
        mass=water+sugar
        volume=mass/SG
        return volume
    
    @staticmethod
    def volume_from_water_and_sugar(water,sugar):
        plato=(sugar/(water+sugar))*100
        SG=BrewUtils.Plato_to_Sg(plato)
        volume=((water+sugar)/SG)
        return volume

    @staticmethod
    def water_from_gravity_and_sugar(SG,sugar):
        platos=BrewUtils.SG_to_Plato(SG)
        try:
            water=sugar(100-platos)/platos
        except: return None
        return water
            
    @staticmethod
    def water_from_sugar_and_volume(sugar,volume):
        water=volume/2
        sg=0
        ecart=1
        cpt=0
        while (cpt<100 and (ecart>0.0001 or ecart<0.0001)):
            platos=sugar*100 /(sugar +water)
            sg=(1 + platos/ (258.6 - (platos / 258.2) * 227.1))
            total_mass=sg*volume
            ecart=water-total_mass+sugar
            water=total_mass-sugar
            cpt +=1
        #print ('WATER MASS CALCULATED  '+str(water)+' - end cpt:' +str(cpt))
        return water

    @staticmethod
    def og_from_sugar_and_volume(sugar,volume):
        water=volume/2
        sg=0
        ecart=1
        cpt=0
        while (cpt<100 and (ecart>0.001 or ecart<0.001)):
            platos=sugar*100 /(sugar +water)
            sg=(1 + platos/ (258.6 - (platos / 258.2) * 227.1))
            total_mass=sg*volume
            ecart=water-total_mass+sugar
            water=total_mass-sugar
            cpt +=1
        #print ('water mass calculated '+str(water))
        return sg

    @staticmethod
    def og_from_sugar_and_water_mass(sugar,water_mass)  :
        platos=sugar /(sugar+water_mass)*100
        
        return   1 + platos / (258.6 - (platos / 258.2) * 227.1)



    #----------------------------------------------------------------------------------
    @staticmethod         
    def find_fermentable_in_list(id,list):
        for rf in list:
            if(rf.fermentable.id ==id):
                return rf
        return False          

    #-----------------------------------------------------------------------------------
    @staticmethod 
    def are_equal_fermentables(bf_list1,bf_list2):
        if len(bf_list1) != len(bf_list2):
            #print('are not equal fermentable 1')
            return False
        index=0
        while index<len(bf_list1):    
            bf1=bf_list1[index]
            bf2=bf_list2[index]
              
            #quantity may slightly change because of calculations
            if (round(bf1.quantity,3) != round(bf2.quantity,3)): 
                #print('are not equal fermentable 3 : '+str(bf1.quantity) + ' | '+str(bf2.quantity))
                return False
            if (bf1.usage!=bf2.usage):
                #print('are not equal fermentable 4')
                return False    
            if (bf1.steep_potential!=bf2.steep_potential): 
                #print('are not equal fermentable 5')
                return False 
            if (bf1.diph != bf2.diph):
                return False
            if (bf1.buffering_capacity != bf2.buffering_capacity):
                return False
            index +=1    
        return True      
   
    #----------------------------------------------------------------------------------
    @staticmethod         
    def find_hop_in_list(id,list):
        for rh in list:
            if(rh.hop.id ==id):
                return rh
        return False          

    #-----------------------------------------------------------------------------------
    @staticmethod 
    def are_equal_hops(bh_list1,bh_list2):
        if len(bh_list1) != len(bh_list2): 
            #print('are not equal hops 1')
            return False
        index =0    
        while index<len(bh_list1):
            bh1=bh_list1[index]
            bh2=bh_list2[index]
            if (bh1.quantity != bh2.quantity): 
                #print('are not equal hops 3 : '+str(abs(bh1.quantity-bh2.quantity)))
                return False
            if (bh1.usage!=bh2.usage): 
                #print('are not equal hops 4')
                return False    
            if (bh1.utilisation!=bh2.utilisation): 
                #print('are not equal hops 5')
                return False 
            if (bh1.multiplicator!=bh2.multiplicator): 
                #print('are not equal hops 6')
                return False 
            if (bh1.minutes!=bh2.minutes): 
                #print('are not equal hops 7')
                return False 
            if (bh1.hours!=bh2.hours): 
                #print('are not equal hops 8')
                return False 
            if (bh1.days!=bh2.days): 
                #print('are not equal hops 9')
                return False 
            '''
            if (bh1.hopstand_method!=bh2.hopstand_method): 
                #print('are not equal hops 10')
                return False 
            '''    
            if (bh1.loose!=bh2.loose): 
                #print('are not equal hops 11')
                return False 
            index+=1               
        return True      

    #----------------------------------------------------------------------------------
    @staticmethod         
    def find_yeast_in_list(id,list):
        for ry in list:
            if(ry.yeast.id ==id):
                return ry
        return False          

    #-----------------------------------------------------------------------------------
    @staticmethod 
    def are_equal_yeasts(by_list1,by_list2):
        if len(by_list1) != len(by_list2):
            return False
        for by1 in by_list1:
           
            by2=BrewUtils.find_yeast_in_list(by1.yeast.id,by_list2)
            if not by2:
                return False
            else:    
                if(by1.quantity!=by2.quantity):
                    return False
                
              
                #brew_yeast.yeast cannot be changed in recipe 
                #thus ignore it
        #print('yeasts are equal')        
        return True  

    #----------------------------------------------------------------------------------
    @staticmethod         
    def find_misc_in_list(id,list):
        for rm in list:
            if(rm.misc.id ==id):
                return rm
        return False          

    #-----------------------------------------------------------------------------------
    @staticmethod 
    def are_equal_miscs(bm_list1,bm_list2):
        if len(bm_list1) != len(bm_list2):
            return False
        for bm1 in bm_list1:
           
            bm2=BrewUtils.find_misc_in_list(bm1.misc.id,bm_list2)
            if not bm2:
                return False
            else:    
                if(bm1.quantity!=bm2.quantity):
                    return False
                if (bm1.reference_volume!=bm2.reference_volume):
                    return False    
                if (bm1.usage!=bm2.usage):
                    return False  
                #brew_misc.misc cannot be changed in recipe 
                #thus ignore it
        #print('miscs are equal')        
        return True      
    

    #-----------------------------------------------------------------------------------
    @staticmethod 
    def are_equal_rests(br_list1,br_list2):
        if len(br_list1) != len(br_list2):
            return False
        for br1 in br_list1:
           
            br2=BrewUtils.find_rest_in_list(br1.id,br_list2)
            if not br2:
                return False
            else: 
                if (br1.temperature!=br2.temperature):
                    return False    
                if (br1.duration!=br2.duration):
                    return False  
                #other properties cannot be changed in recipe 
                #thus ignore them 
        #print('rests are equal')        
        return True       

    #----------------------------------------------------------------------------------
    @staticmethod         
    def find_rest_in_list(id,list):
        for rr in list:
            if(rr.id ==id):
                return rr
                
        return False          

     #---------------------------------------------------------------------------------
    @staticmethod
    def are_equal_brew_commons(brew1,brew2):
     
        reason=''
        are_equal=True
        if(  brew1.id != brew2.id):
            reason +='\n➨l\'identifiant a changé'
            are_equal= False
       
        if  (brew1.name != brew2.name):
            reason += '\n➨le nom a changé' 
            are_equal= False
      
        if  (str(brew1.brew_date) != str(brew2.brew_date)):
            reason +='\n➨la date de brassage a changé'
            are_equal= False
        
        if  (brew1.rtype != brew2.rtype):
            reason +='\n➨de type de recette a changé' 
            are_equal= False
        
        if  (brew1.style != brew2.style):
            reason +='\n➨le style a changé'
           
            are_equal= False 
    
        if  (brew1.batch_volume != brew2.batch_volume):
            reason +='\n➨le volume du lot a changé' 
            are_equal= False
            
        
        if  (float(brew1.bitterness) != float(brew2.bitterness)):
            reason +='\n➨l\'amertume a changé' 
            are_equal= False
       
        if  (float(brew1.og) != float(brew2.og)):
            reason +='\n➨la densité d\'origine a changé' 
            are_equal= False
            #print((float(brew1.og)))
            #print((float(brew2.og)))
        
        if  (float(brew1.abv) != float(brew2.abv)):
            reason +='\n➨al\'ABV a changé' 
            are_equal= False
        if  (float(brew1.color) != float(brew2.color)):
            reason +='\n➨la couleur a changé' 
            are_equal= False
        if  (float(brew1.boil_time )!= float(brew2.boil_time)):
            reason +='\n➨le temps d\'ébullition a changé' 
            are_equal= False
        if brew1.pH_adjuster_enabled != brew2.pH_adjuster_enabled:
            reason += "\n Ajustement du pH En service/Hors service changé"
            are_equal=False
        if float(brew1.pH_target) != float(brew2.pH_target):
            reason += '\n➨la cible de pH a changé' 
            are_equal=False
        if brew1.acid_agent != brew2.acid_agent:
            reason += '\n➨l\'agent d\'accidification a changé' 
            are_equal=False
    
        return [are_equal,reason] 
                
    #---------------------------------------------------------------------------------
    @staticmethod
    def are_equal_recipe_commons(recipe1,recipe2):
        #print(str(recipe1.id) +'  '+str(recipe2.id))
        #print(str(recipe1.name) +'  '+str(recipe2.name))
        #print(str(recipe1.author) +'  '+str(recipe2.author))
        #print(str(recipe1.rtype) +'  '+str(recipe2.rtype))
        #print(str(recipe1.style) +'  '+str(recipe2.style))
        #print(str(recipe1.bitterness) +'  '+str(recipe2.bitterness))
        #print(str(recipe1.og) +'  '+str(recipe2.og))
        #print(str(recipe1.abv) +'  '+str(recipe2.abv))
        #print(str(recipe1.color) +'  '+str(recipe2.color))
        #print(str(recipe1.boil_time) +'  '+str(recipe2.boil_time))
       
        if(recipe1.id != recipe2.id):
           return False
       
        if(recipe1.name != recipe2.name):
            return False
      
        if(recipe1.author != recipe2.author):
            return False
        
        if(recipe1.rtype != recipe2.rtype):
            return False
        
        if(recipe1.style != recipe2.style):
            return False
        
        if(float(recipe1.bitterness) != float(recipe2.bitterness)):
            return False
       
        if(float(recipe1.og) != float(recipe2.og)):
            return False
        
        if(float(recipe1.abv) != float(recipe2.abv)):
            return False
        if(float(recipe1.color) != float(recipe2.color)):
            return False
        if(float(recipe1.boil_time )!= float(recipe2.boil_time)):
            return False
        
        return True 
          