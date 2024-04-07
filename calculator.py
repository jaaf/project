'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from database.profiles.equipment import Equipment,find_equipment_by_id
from BrewUtils import BrewUtils
import math
import os

class Calculator:

    @classmethod
    def original_gravity(cls,dlg):
        #calculated only when not og_as_target
        if(not dlg.og_as_target and dlg.end_sugar>0 and dlg.end_water_mass>0 ):
            #dlg.og=BrewUtils.og_from_sugar_and_volume(dlg.end_sugar, dlg.batch_volume+dlg.equipment.kettle_retention)
            dlg.og=BrewUtils.og_from_sugar_and_water_mass(dlg.end_sugar,dlg.end_water_mass)
            dlg.ui.calculatedOGEdit.setText(str(round(dlg.og,3)))
            dlg.og_indicator.setValue(round(dlg.og,3))
            cls.beer_forecast_abv(dlg)
            
        else:
            dlg.og=1.0    

    #-------------------------------------------------------------------------------------------------    
    @classmethod
    def end_water_mass(cls,dlg):
        if(dlg.og_as_target and dlg.og and dlg.batch_volume>0 and dlg.equipment):
            dlg.end_water_mass=BrewUtils.water_mass_from_SG_and_volume(dlg.og,(dlg.batch_volume+dlg.equipment.kettle_retention))
            cls.preboil_water_mass(dlg)
        else:
            if(not dlg.og_as_target and dlg.batch_volume>=0 and dlg.end_sugar>=0 and dlg.equipment):
                dlg.end_water_mass=BrewUtils.water_from_sugar_and_volume(dlg.end_sugar,dlg.batch_volume+dlg.equipment.kettle_retention)
                cls.preboil_water_mass(dlg)
                cls.original_gravity(dlg)
            else:
                dlg.end_water_mass=0   

    #-----------------------------------------------------------------------------------------------------------------------
    @classmethod
    def boil_evaporation(cls,dlg):
        if  dlg.equipment and dlg.boil_time>0:
            dlg.boil_evaporation=dlg.equipment.kettle_evaporation_rate/60*dlg.boil_time
            cls.preboil_water_mass(dlg)
        else:
            dlg.boil_evaporation=0    

    #-----------------------------------------------------------------------------------------------------------------------
    @classmethod
    def preboil_gravity(cls, dlg):
        if(dlg.end_sugar>0 and dlg.preboil_water_mass>0):
            #this counter infinite loop is no longer necessary
            #if dlg.preboil_gravity>=1.0:
            #    old_preboil_gravity=dlg.preboil_gravity
            #else:
            #    old_preboil_gravity=1.0

            platos= dlg.end_sugar /(dlg.end_sugar + dlg.preboil_water_mass)*100
            dlg.preboil_gravity = 1 + platos / (258.6 - (platos / 258.2) * 227.1)
            dlg.ui.preboilGravityEdit.setText( str(round(dlg.preboil_gravity,3)))
            cls.utilisation_gravity_factor(dlg)
            cls.hot_max_wort_volume(dlg)
            #if abs(old_preboil_gravity-dlg.preboil_gravity)>0.001:
            #    cls.mash_sugar(dlg)


    #----------------------------------------------------------------------
    @classmethod
    def end_sugar(cls,dlg):
        #the sugar that is in the postboil wort
        if(dlg.og_as_target and dlg.og>1.00 and dlg.equipment):
            #here volume is batch + retention
            dlg.end_sugar=BrewUtils.sugar_mass_from_SG_and_volume(dlg.og,(dlg.batch_volume+dlg.equipment.kettle_retention))
            cls.total_fermentable_mass(dlg)
            #cls.end_water_mass(dlg)
            cls.preboil_gravity(dlg)
       
        else:  
            if(not dlg.og_as_target and dlg.mash_sugar>=0 and dlg.boil_sugar>=0)  :
                dlg.end_sugar=dlg.mash_sugar + dlg.boil_sugar
                cls.end_water_mass(dlg)
                cls.original_gravity(dlg)
                cls.preboil_gravity(dlg)
            else:    
                dlg.end_sugar=0  
    
    #--------------------------------------------------------------------------
    @classmethod
    def mash_sugar(cls,dlg):
        #called from cls.end_sugar or when fermentables updated or added
        cls.boil_sugar(dlg)#compute boil_sugar
        if(dlg.og_as_target and dlg.end_sugar>=0 and dlg.boil_sugar>=0):
            #print('sugars are end '+str(dlg.end_sugar)+ '  and boil '+str(dlg.boil_sugar))
            dlg.mash_sugar=dlg.end_sugar-dlg.boil_sugar
            #print('mash sugar is '+str(dlg.mash_sugar))
            #cls.total_fermentable_mass(dlg)
            cls.hot_after_sparge_wort_volume(dlg)
        else:
            if(not dlg.og_as_target and dlg.equipment ):
                dlg.mash_sugar=0
                for item in dlg.fermentable_selector.destination_model.items:
                    if(item.usage == 'empâtage'):
                        dlg.mash_sugar += item.quantity * item.fermentable.potential /100 * dlg.equipment.mash_efficiency/100
                cls.end_sugar(dlg)
                cls.hot_after_sparge_wort_volume(dlg)
                   
            else:
                dlg.mash_sugar=0

    #---------------------------------------------------------------
    @classmethod
    def boil_sugar(cls,dlg):
        #the sugar from non mashed fermentables
       
        dlg.boil_sugar=0
        for item in dlg.fermentable_selector.destination_model.items:
            if item.usage == "trempage" :#and item.fermentable.form != 'Extrait liquide' and item.fermentable.form !='Extrait sec'):
                dlg.boil_sugar+=item.quantity * item.steep_potential/100
            if item.usage == "ébullition" :#and (item.fermentable.form == 'Extrait liquide' or item.fermentable.form !='Extrait sec)')):
                dlg.boil_sugar += item.quantity * item.fermentable.potential/100
        if(dlg.og_as_target ):
            pass#cls.mash_sugar(dlg) 
        else:
            cls.end_sugar(dlg)   

    #---------------------------------------------------------------
    @classmethod 
    def beer_average_color(cls,dlg):
        try:
            total_MCU=0
            for item in dlg.fermentable_selector.destination_model.items:
                total_MCU+=(4.23*item.fermentable.color*item.quantity)/dlg.batch_volume
            color=2.99*(total_MCU**0.6859)
            dlg.color=color
        except:
            pass

    #----------------------------------------------------------------------------------------------------------
    @classmethod
    def mash_average_potential(cls,dlg):
        
        if dlg.equipment:
            sigma=0
            mass=0
            items=dlg.fermentable_selector.destination_model.items
            if(items!=[]):
                for item in items:
                    if item.usage == "empâtage":
                        
                        sigma+=(item.quantity * item.fermentable.potential)
                        mass+=item.quantity
                try: #risk division by 0
                    #print("####################### sigma is "+str(sigma) +" and mass is "+str(mass))
                    dlg.mash_average_potential=sigma/mass
                  
                    #print("###############################in calculator mash_average_potential is "+str(dlg.mash_average_potential))
                except: 
                    dlg.mash_average_potential=0
                    #return     
            else:
                dlg.mash_average_potential=0
        else:
            dlg.mash_average_potential=0 
    #-------------------------------------------------------------------------------------------------------------
    @classmethod
    def weighted_average_potential(cls,dlg):
        #takes into account all type of fermentable, mashed, steeped and boiled
        cls.mash_average_potential(dlg)
        if dlg.equipment:
            sigma=0
            mass=0
            items=dlg.fermentable_selector.destination_model.items
            if(items!=[]):
                for item in items:
                    if item.usage == "empâtage":
                        
                        sigma+=(item.quantity * item.fermentable.potential)*dlg.equipment.mash_efficiency/100
                    if item.usage == "trempage" : #and item.fermentable.form!='Extrait liquide' and item.fermentable.form != 'Extrait sec':
                        sigma+=item.quantity * item.steep_potential
                    #if item.fermentable.form == 'Extrait liquide' or item.fermentable ==  'Extrait sec':
                    if item.usage=='ébullition':
                        sigma+=item.quantity * item.fermentable.potential  

                    mass+=item.quantity
                try: #risk division by 0
                    dlg.weighted_average_potential=sigma/mass
                except: 
                    dlg.weighted_average_potential=0
                    #return     
            else:
                dlg.weighted_average_potential=0

            cls.total_fermentable_mass(dlg)
            cls.total_mash_fermentable_mass(dlg)
            
        else:
            dlg.weighted_average_potential=0    
    #--------------------------------------------------------------------------------------------------------------
    @classmethod
    def total_fermentable_mass(cls,dlg):
        if(dlg.og_as_target and dlg.end_sugar>0 and dlg.weighted_average_potential>0 and dlg.equipment):
            try:
                dlg.total_fermentable_mass=dlg.end_sugar /dlg.weighted_average_potential*100
            except:
                dlg.total_fermentable_mass=0    
            cls.fermentable_true_values(dlg) 
            return
        else:
            if(not dlg.og_as_target ):
                dlg.total_fermentable_mass=0
                #all kind of malts, mashed, steeped and boiled
                for item in dlg.fermentable_selector.destination_model.items:
                    dlg.total_fermentable_mass += item.quantity  
                cls.mash_sugar(dlg)  
                cls.mash_water_mass(dlg) 
                cls.beer_average_color(dlg)
            
            else:
                dlg.total_fermentable_mass=0   

    #---------------------------------------------------------------------------------------------------------------
    @classmethod
    def total_mash_fermentable_mass(cls,dlg):
        if dlg.og_as_target and dlg.total_fermentable_mass>0:
            mass=0
            for item in dlg.fermentable_selector.destination_model.items:
                if item.usage == 'empâtage':
                    mass +=item.quantity
            dlg.total_mash_fermentable_mass=mass  #print('total_mash_fermentable_mass '+str(dlg.total_mash_fermentable_mass)+'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            cls.mash_fermentables_absorbed_water(dlg)
            cls.mash_water_mass(dlg)  
            cls.mash_max_volume(dlg)
        else:
            if not dlg.og_as_target:
                mass=0
                for item in dlg.fermentable_selector.destination_model.items:
                    if item.usage == 'empâtage':
                        mass +=item.quantity
                dlg.total_mash_fermentable_mass=mass  #print('total_mash_fermentable_mass '+str(dlg.total_mash_fermentable_mass))
                cls.mash_fermentables_absorbed_water(dlg)
                cls.mash_water_mass(dlg)
        cls.compute_rests(dlg)

    #-------------------------------------------------------------------------------------------------------------
    @classmethod
    def total_boil_steeped_mass(cls,dlg): #if dlg.og_as_target and dlg.total_fermentable_mass>0:
        mass=0
        for item in dlg.fermentable_selector.destination_model.items:
            if item.usage == 'trempage' :
                mass += item.quantity
        
        dlg.total_boil_steeped_mass=mass
        cls.preboil_water_mass(dlg)

    #--------------------------------------------------------------------------------------------------------------
    @classmethod
     #called from cls.mash_sugar with og as target
    def fermentable_true_values(cls,dlg):
        #print('in fermentable_true_values')
        if(dlg.weighted_average_potential>0 and dlg.mash_sugar>=0 and dlg.total_fermentable_mass>0 and dlg.equipment):
            #print('really in fermentable_true_values')
            total_initial_quantity =0
            #calculate total initial quantity
            for item in dlg.fermentable_selector.destination_model.items:
                total_initial_quantity += item.quantity 
            if(total_initial_quantity>0):        
                #calculate fraction for each fermentable        
                for item in dlg.fermentable_selector.destination_model.items:
                    item.initial_fraction=item.quantity/total_initial_quantity
                #calculate true values    
                for item in    dlg.fermentable_selector.destination_model.items: 
                    item.quantity = dlg.total_fermentable_mass * item.initial_fraction
                    item.quantity_display=round(item.quantity,2)
                #update view    
               
                dlg.fermentable_selector.destination_model.set_initialized(True)  
                dlg.fermentable_selector.destination_model.layoutChanged.emit()   
                dlg.ui.targetOGCheckBox.setDisabled(False) 
                #print('true values calculated') ,
                cls.beer_color(dlg)    
                cls.total_mash_fermentable_mass(dlg)
                cls.total_boil_steeped_mass(dlg)
                cls.mash_sugar(dlg)
            else:
                pass    
        else:
            #print('Could not calculate true fermentables amount')     
            pass  
    #---------------------------------------------------------------------------------------
    @classmethod
    def beer_color(cls,dlg):
        if dlg.batch_volume>0:
            MCU=0
            for item in  dlg.fermentable_selector.destination_model.items:
                MCU += (item.fermentable.color *4.23 * item.quantity)/dlg.batch_volume

            color=2.939 * MCU**0.6859
            dlg.ui.colorEdit.setText(str(round(color,0)))   
            dlg.color_indicator.setValue(color)
    #--------------------------------------------------------------------------------------
    @classmethod
    def beer_forecast_abv(cls, dlg):
        #att is attenuation of the yeast expressed like 0.80
        #csm is the quantity of sugar added per liter for bottle carbonation
        #cwm the quantity of water to dilute the carbonation sugar per liter

        #molecular mass of CO2=44,098 , molecular mass of alcool Ethanol is 46,088
        #when 1 g of CO2 is produced and evacuated, we have 1/44,098*46,088=1,04512 g of alcool produced
        #OG -FG represent the quantity of CO2 lost 
        #(OG - FG) *1.04678 represent the quantity (mass) of alcool produced
        # thus ABM is (OG -FG)*1.04678 /FG
        # ABV =ABM /0.789
        att=0
        for item in dlg.yeast_selector.destination_model.items:
            if item.yeast.attenuation/100 >att:
                att=item.yeast.attenuation/100       
        if dlg.og>1:
            OP=BrewUtils.SG_to_Plato(dlg.og)#original platos
            OSugar=OP*dlg.og*1000/100 #g of sugar per liter of wort
            OWater=(dlg.og*1000)-OSugar #g of water per liter of wort
            #the following are estimation they will fixed in feedback
            NSugar=OSugar+6 #new sugar mass per liter after adding carbonation sugar(estimation 6 g/l)
            NWater=OWater+45 #new water mass per liter after adding carbonation sugar(estimation 45 ml/l )
            NP=(NSugar/(NSugar+NWater))*100#new platos after adding carbonation sugar
            NOG=BrewUtils.Plato_to_Sg(NP) #new original gravity
            FG=((NOG-1)*(1-att))+1
            ABV =((NOG-FG)*1.047 /FG /0.789)*100
            dlg.abv=ABV
            dlg.abv_indicator.setValue(dlg.abv)
            dlg.ui.abvEdit.setText(str(round(ABV,1)))
            cls.beer_color(dlg)
        #---------------------------------------------------------------------------------------
    @classmethod
    def mash_fermentables_absorbed_water(cls,dlg):
        #print('in mash_fermentables_absorbed_water')
        if(dlg.og_as_target and dlg.total_fermentable_mass>0 and dlg.equipment):
            dlg.mash_fermentables_absorbed_water=dlg.total_mash_fermentable_mass * dlg.equipment.grain_absorption
            #print('mash_fermentables_absorbed_water '+str(dlg.mash_fermentables_absorbed_water))
            cls.total_water_mass(dlg)
        else:
            if(not dlg.og_as_target and dlg.equipment and dlg.total_mash_fermentable_mass>0):
                dlg.mash_fermentables_absorbed_water=dlg.total_mash_fermentable_mass * dlg.equipment.grain_absorption
                cls.total_water_mass(dlg)
            else:    
                dlg.mash_fermentables_absorbed_water=0  
                #print('Could not calculate mash_fermentable_absorbed_water') 
        #print('mash_fermentables_absorbed_water '+str(dlg.mash_fermentables_absorbed_water))

    #--------------------------------------------------------------------------------------------
    @classmethod
    def boil_added_sugar_mass(cls,dlg):
        sugar_mass=0
        for item in dlg.fermentable_selector.destination_model.items:
            if item.fermentable.category =='Sucre':
                sugar_mass += item.quantity * item.fermentable.potential/100
        return sugar_mass        
   

    @classmethod
    def hot_max_wort_volume(cls, dlg):
        
        if dlg.preboil_water_mass>=0 and dlg.preboil_gravity and dlg.total_boil_steeped_mass>=0 and dlg.mash_sugar>0:
            boil_sugar=cls.boil_added_sugar_mass(dlg)
            volume_before_steep=BrewUtils.volume_from_water_and_sugar(dlg.preboil_water_mass,(dlg.mash_sugar+boil_sugar))*1.04
            dlg.hot_max_wort_volume=volume_before_steep+(dlg.total_boil_steeped_mass*0.67)

            dlg.ui.hotMaxWortVolumeEdit.setText(str(round(dlg.hot_max_wort_volume,2)))
            if dlg.feedbackDialog:
                dlg.feedbackDialog.ui.expectedBeforeBoilVolumeEdit.setText(str(round(dlg.hot_max_wort_volume,2)))


    #------------------------------------------------------------------------------------------------
    @classmethod
    def hot_after_sparge_wort_volume(cls,dlg):
        if dlg.preboil_water_mass>=0 and dlg.mash_sugar>=0: 
            volume=BrewUtils.volume_from_water_and_sugar(dlg.preboil_water_mass,dlg.mash_sugar)*1.04
            dlg.ui.hotAfterSpargeWortVolumeEdit.setText(str(round(volume,2)))
            if dlg.feedbackDialog is not None :
                dlg.feedbackDialog.ui.expectedAfterSpargeVolumeEdit.setText(str(round(volume,2))) 
            cls.after_sparge_gravity(dlg)

    #------------------------------------------------------------------------------------------------
    @classmethod
    def mash_max_volume(cls, dlg):
        if dlg.mash_water_mass and dlg.total_mash_fermentable_mass:
            volume=dlg.mash_water_mass *1.04 +dlg.total_mash_fermentable_mass*0.67
            dlg.ui.mashMaxVolumeEdit.setText(str(round(volume,2)))

    @classmethod
    def after_sparge_gravity(cls,dlg):
        if dlg.preboil_water_mass>=0 and dlg.mash_sugar>=0:
            gravity=BrewUtils.og_from_sugar_and_water_mass(dlg.mash_sugar,dlg.preboil_water_mass)
            dlg.ui.afterSpargeGravityEdit.setText(str(round(gravity,3)))
            if dlg.feedbackDialog:
                dlg.feedbackDialog.ui.expectedAfterSpargeGravityEdit.setText(str(round(gravity,3)))
        else:
            pass    
    #------------------------------------------------------------------------------------------------

    @classmethod
    def mash_hop_absorbed_water(cls,dlg):
        if dlg.equipment!=0:
            for item in dlg.hop_selector.destination_model.items:
                hop_mass=0
                if item.usage =="à l'empâtage":
                    hop_mass+=item.quantity
            dlg.mash_hop_absorbed_water=hop_mass*dlg.equipment.hop_absorption/1000
            cls.mash_water_mass(dlg)
        else:
            dlg.mash_hop_absorbed_water=0
                 

    #------------------------------------------------------------------------------------------------
    @classmethod
    def preboil_water_mass(cls,dlg):
        if(dlg.og_as_target and dlg.end_water_mass>=0 and dlg.hop_absorbed_water>=0 and dlg.total_boil_steeped_mass>=0 and dlg.equipment and dlg.boil_time):
            evaporation= dlg.equipment.kettle_evaporation_rate * dlg.boil_time /60
            steeped_absorption=dlg.total_boil_steeped_mass*dlg.equipment.grain_absorption 
            dlg.preboil_water_mass=dlg.end_water_mass + evaporation + steeped_absorption+dlg.hop_absorbed_water
            dlg.ui.coldPreboilWaterVolumeEdit.setText(str(round(dlg.preboil_water_mass,2)))
            cls.total_water_mass(dlg)
            cls.preboil_gravity(dlg)
            cls.hot_after_sparge_wort_volume(dlg)
        else:
            if(not dlg.og_as_target and dlg.end_water_mass>0 and dlg.hop_absorbed_water>=0 and dlg.total_boil_steeped_mass>=0 and dlg.boil_time>0 and dlg.equipment):
                steeped_absorption=dlg.total_boil_steeped_mass*dlg.equipment.grain_absorption
                evaporation= dlg.equipment.kettle_evaporation_rate * dlg.boil_time /60
                dlg.preboil_water_mass=dlg.end_water_mass + dlg.hop_absorbed_water +steeped_absorption+evaporation
                cls.total_water_mass(dlg)
                cls.preboil_gravity(dlg)
                cls.hot_after_sparge_wort_volume(dlg)
            else:  
                dlg.preboil_water_mass=0 
    
    #------------------------------------------------------------------------------------
    @classmethod
    def total_water_mass(cls,dlg):
        if(dlg.og_as_target and dlg.preboil_water_mass>0 and dlg.mash_fermentables_absorbed_water>=0):
            dlg.total_water_mass=dlg.preboil_water_mass+dlg.mash_fermentables_absorbed_water
            cls.sparge_water_mass(dlg)
        else:
            if(not dlg.og_as_target and dlg.mash_fermentables_absorbed_water>=0 and dlg.preboil_water_mass>=0):
                dlg.total_water_mass=dlg.preboil_water_mass+dlg.mash_fermentables_absorbed_water
                cls.sparge_water_mass(dlg)
            else:
                dlg.total_water_mass=0

    #----------------------------------------------------------------------------------------
    @classmethod
    def mash_water_mass(cls,dlg):
        if(dlg.og_as_target and dlg.total_fermentable_mass>=0 and dlg.mash_hop_absorbed_water>=0  and dlg.equipment):
            dlg.mash_water_mass=dlg.mash_hop_absorbed_water + dlg.equipment.mash_tun_undergrain + (dlg.equipment.mash_thickness * dlg.total_mash_fermentable_mass)
            dlg.ui.coldMashWaterVolumeEdit.setText(str(round(dlg.mash_water_mass,2)))
            cls.sparge_water_mass(dlg)
            cls.mash_max_volume(dlg)
        else:
            if(not dlg.og_as_target and dlg.total_mash_fermentable_mass>=0  and dlg.mash_hop_absorbed_water>=0 and dlg.equipment):
                dlg.mash_water_mass= dlg.total_mash_fermentable_mass * dlg.equipment.mash_thickness +dlg.equipment.mash_tun_undergrain +dlg.mash_hop_absorbed_water
                dlg.ui.coldMashWaterVolumeEdit.setText(str(round(dlg.mash_water_mass,2)))
                cls.sparge_water_mass(dlg)
                cls.mash_max_volume(dlg)
            else:
                dlg.mash_water_mass=0 

    @classmethod
    def sparge_water_mass(cls,dlg):
        #print('in sparge_water_mass')
        if(dlg.og_as_target and dlg.total_water_mass>=0 and dlg.mash_water_mass>=0):
            dlg.sparge_water_mass=dlg.total_water_mass - dlg.mash_water_mass
            
            dlg.ui.coldSpargeWaterVolumeEdit.setText(str(round(dlg.sparge_water_mass,2)))
        else:
            if(not dlg.og_as_target and dlg.mash_water_mass>=0 and dlg.total_water_mass>=0):
                dlg.sparge_water_mass=dlg.total_water_mass - dlg.mash_water_mass
                dlg.ui.coldSpargeWaterVolumeEdit.setText(str(round(dlg.sparge_water_mass,2)))
            else:
                dlg.sparge_water_mass=0

    @staticmethod
    def end_boil_Volume_hot(dlg):
        if (dlg.batch_volume>=0 and dlg.equipment):
            dlg.end_boil_volume_hot=(dlg.batch_volume +dlg.equipment.fermenter_retention)*1.04
            dlg.ui.hotPostboilWortVolumeEdit.setText(str(round(dlg.end_boil_volume_hot,1)))

    #IBU 
    @classmethod
    def utilisation_gravity_factor (cls, dlg):
        if (dlg.bitterness_as_target and  dlg.preboil_gravity and dlg.og):
            gravity=(dlg.preboil_gravity +dlg.og)/2
            dlg.utilisation_gravity_factor = 1.65 * 0.000125 ** (gravity - 1)
            cls.ibu_before_scaling(dlg)
        if not dlg.bitterness_as_target and dlg.preboil_gravity and dlg.og: 
            gravity=(dlg.preboil_gravity +dlg.og)/2
            dlg.utilisation_gravity_factor = 1.65 * 0.000125 ** (gravity - 1)  
            cls.bitterness(dlg)

    @classmethod
    def utilisation_time_factor (cls, t):
        return (1 - math.exp(-0.04 * (float(t))) )/ 4.15
    #---------------------------------------------------------------------------------------
    @classmethod
    def ibu_before_scaling(cls,dlg):
        dlg.ibu_before_scaling=cls.bitterness(dlg)
        cls.total_hop_mass(dlg)

    #---------------------------------------------------------------------------------------
    @classmethod
    def weighted_average_ibu_yield(cls, dlg):
        #utilisation is the product of 2 factors and is a number like 0.14 i.e less than 1, and alpha (the percentage like 12 for 12% of alpha acids)
        #yield is utilisation * alpha
        # and BU are givem by BU = mass [g] * alpha * utilisation * 10 / volume [l]
        # or                  BU = mass [g] * yield               * 10 / volume [l]
        if dlg.bitterness_as_target and dlg.utilisation_gravity_factor  and dlg.boil_time>0:
            cls.ibu_before_scaling(dlg)
            sigma=0
            mass=0
            items=dlg.hop_selector.destination_model.items
            if items!=[]:
                for item in items:
                    mass += item.quantity
                    match item.usage:
                        case "à l'empâtage":
                            sigma += item.quantity * item.utilisation *item.hop.alpha

                            
                        case "au premier moût":
                            sigma += item.quantity * dlg.utilisation_gravity_factor * cls.utilisation_time_factor(dlg.boil_time) *item.multiplicator * item.hop.alpha
                        case "à l'ébullition":
                            sigma += item.quantity * dlg.utilisation_gravity_factor * cls.utilisation_time_factor(item.minutes) * item.hop.alpha   
                        case "hopstand"   :
                            match item.hopstant_method:
                                case 'Basique':
                                    sigma += item.quantity *  item.utilisation *item.hop.alpha
                                #case 'Integration'
                        case "au fermenteur":
                            sigma += item.quantity * item.utilisation *item.hop.alpha
                   
            dlg.weighted_average_ibu_yield=sigma/mass
            cls.total_hop_mass(dlg)

    #-------------------------------------------------------------------------------------
      
    #---------------------------------------------------------------------------------------     
    @classmethod
    def total_hop_mass(cls,dlg):
        if(dlg.bitterness_as_target and  dlg.bitterness and dlg.equipment and  dlg.batch_volume and dlg.ibu_before_scaling): 
            mass_before_scaling=0
            items=dlg.hop_selector.destination_model.items 
            for item in items:
                mass_before_scaling += item.quantity
            dlg.total_hop_mass=mass_before_scaling * dlg.bitterness / dlg.ibu_before_scaling
            cls.hop_true_values(dlg)
        if(not dlg.bitterness_as_target ) :
            mass=0
            items=dlg.hop_selector.destination_model.items  
            for item in items:
                mass += item.quantity
            dlg.total_hop_mass=mass
            cls.hop_true_values(dlg)    
    #---------------------------------------------------------------------------------------     
    @classmethod
    def hop_absorbed_water(cls,dlg):
        #this is a convergent recursive calculation  
        #we loop because change in water absorbed triggers a change in preboil volume and preboil gravity
        #and preboil gravity changes hop quantity calculated
        
        
        if(dlg.bitterness_as_target and dlg.equipment):
            k=dlg.equipment.hop_absorption_reduction_coeff
            if(dlg.og and dlg.preboil_gravity and dlg.equipment ):
                #due to variable declaration in BrewWidget initial diff is 10
                diff= dlg.hop_absorbed_water - dlg.old_hop_absorbed_water
                dlg.old_hop_absorbed_water=dlg.hop_absorbed_water
                if (diff>0.02 or diff <-0.02) and dlg.hop_water_cpt<100: #protection agains infinite loop
                    water_mass=0# the mass that is removed from boil or retained by false bottom
                    
                    items=dlg.hop_selector.destination_model.items
                    if items!=[]:
                        for item in items: 
                            if item.usage!= 'au fermenteur'and item.usage!="à l'empâtage"  :
                                #when loose absorption replaces equivalent volume of kettle retention
                                if item.loose:
                                    water_mass=dlg.equipment.hop_absorption*k*item.quantity /1000#part retained by false bottom
                                else:
                                    water_mass=dlg.equipment.hop_absorption * item.quantity /1000 #removed in mesh bag

                    dlg.hop_absorbed_water=water_mass#only the removed hops part 
                
                    dlg.hop_water_cpt += 1#to prevent infinite loop
                    #loop because change in water absorbed triggers a change in preboil volume and preboil gravity
                    cls.preboil_water_mass(dlg)
                    

                else:#exit the loop
                    
                    dlg.old_hop_absorbed_water=10
                    dlg.hop_water_cpt=0   
                    #do not loop as diff is small enough
                    
        else:#bittereness not a target
            
            dlg.old_hop_absorbed_water=10
            dlg.hop_water_cpt=0 
            if dlg.equipment != None:
                k=dlg.equipment.hop_absorption_reduction_coeff
                water_mass=0
                items=dlg.hop_selector.destination_model.items
                if items!=[]:
                    for item in items: 
                        if item.usage!= 'au fermenteur'and item.usage!="à l'empâtage"  :
                                #when loose absorption replaces equivalent volume of kettle retention
                                if item.loose:
                                    water_mass=dlg.equipment.hop_absorption*k*item.quantity /1000#part retained by false bottom
                                else:
                                    water_mass=dlg.equipment.hop_absorption * item.quantity /1000 #removed in mesh bag

                dlg.hop_absorbed_water=water_mass#only the removed hops part 
                cls.preboil_water_mass(dlg)  
               
    #---------------------------------------------------------------------------------------
    @classmethod
    def hop_true_values(cls,dlg):
        if  dlg.total_hop_mass !=0 and dlg.total_hop_mass>=0:
            items=dlg.hop_selector.destination_model.items
            total_initial_quantity=0
            for item in items:
                total_initial_quantity += item.quantity
            #calculate fraction for each hop
            for item in items:
                if(total_initial_quantity>0):
                    item.fraction=item.quantity / total_initial_quantity
                else: item.fraction=0    
            #calculate true values
            for item in items:
                item.quantity=dlg.total_hop_mass *item.fraction 
                item.quantity_display=round(item.quantity,0)
            #update view
            dlg.hop_selector.destination_model.set_initialized(True)  
            dlg.hop_selector.destination_model.layoutChanged.emit()   
            dlg.ui.targetIBUCheckBox.setDisabled(False)  
            
            cls.hop_absorbed_water(dlg)
          
        else:
            cls.print_debug('Could not calculate true hops amount')  
    #-------------------------------------------------------------------------------------------
    @classmethod
    def effective_area(cls,wort_diameter, steam_exit_diameter):
        wort_area=wort_diameter * wort_diameter *math.pi /4
        steam_exit_area=steam_exit_diameter * steam_exit_diameter * math.pi /4
        ea=(wort_area *  steam_exit_area  )**(1/2)
        return ea
    #---------------------------------------------------------------------------------------------
    @classmethod
    def natural_time_to_temp(cls,dlg,T0,T,volume):
        #calculate the time to naturally reach the temperature T starting from T0
        #TO initial temp, T temp to reach
        temp=T0
        time=0
        time_step=0.01
        boil_kelvin=100 - (28.8888 * dlg.equipment.altitude) / 9144 +273.15 #kelvin
    
        effective_area= cls.effective_area(dlg.equipment.kettle_diameter, dlg.equipment.kettle_steam_exit_diameter)
        b=   (0.0002925 * effective_area / volume) + 0.00538
        cpt=0
        while temp>T and cpt<12000:
            temp=(53.7 * math.exp(-1.0 * b * time)) +boil_kelvin -53.7
            time += time_step
            cpt += 1
        return time   
    
    #----------------------------------------------------------------------------------------------
   


    #----------------------------------------------------------------------------------------------
    @classmethod
    def calculate_residual_ibu(cls,dlg,AA0,duration,usage):
        if(dlg.equipment ):
            residual_AA=cls.residual_AA(dlg,AA0,duration,usage)
            return cls.residual_IBU_from_integration(dlg,residual_AA)
    #----------------------------------------------------------------------------------------------
    @classmethod
    def residual_IBU_from_integration(cls,dlg,AA0):
        #set to the boil temperature. Will be calculated otherwise if one hop use hopstand ("hors flamme")
        #the volume of wort at end of boil
        end_boil_volume=dlg.batch_volume+dlg.equipment.fermenter_retention
        AA=AA0#initial alpha acids
        d_AA_concentration=0 # the derivative functioni.e. Δ_AA_concentration / Δt
        AA_concentration = AA0 /end_boil_volume
        d_iso_AA_concentration=0 # the derivative function i.e. Δ_iso_AA_concentration / Δt
        iso_AA_concentration=0
        
        
        hs_celcius=100 -(28.8888 * dlg.equipment.altitude) /9144 #boil temperature not Kelvin
        time_step=0.1
        hs_duration=0
        hs_kelvin=0
        hopstand=False
        emptying_time=None
        items = dlg.hop_selector.destination_model.items
        #check if hop stand is performed
        for item in items:
            if(item.usage == 'hors flamme'):
                hs_kelvin=item.temperature+273.15
                hs_duration = item.minutes
                hopstand=True
                break
        match dlg.equipment.cooler_type:
            case "Contre-courant":
                emptying_time=(dlg.batch_volume+dlg.equipment.kettle_retention)*1.04/dlg.equipment.cooler_flow_rate
                
        #this is the initial temperature
        boil_kelvin=100 -(28.8888 * dlg.equipment.altitude) /9144 +273.15 #boil temperatureK
        #time to reach Hopsand temperature
        time_to_HS=(boil_kelvin - hs_kelvin)/dlg.equipment.cooler_slope
        
        #the natural cooling time constant
        b=   ((0.0002925 * cls.effective_area(dlg.equipment.kettle_capacity, dlg.equipment.kettle_steam_exit_diameter)) / end_boil_volume) + 0.00538
        #print('b is '+str(b))
        time=0
        Δt=None
        Δt2=None
        heating=True
        current_kelvin=boil_kelvin

        while time<300 and current_kelvin>70+273.15:#limit to five hours and 70 °C
    
            if(time<time_to_HS):
                #print('firt cooling')
                current_kelvin =boil_kelvin - dlg.equipment.cooler_slope * time

            if time >= time_to_HS and time<=time_to_HS+hs_duration:
                if(heating ==True ): #heating indicates the hopstand temperature is regulated
                    current_kelvin= hs_kelvin

                else:
                    #the natural curve is shifted to the letf
                    #print('natural cooling during hop stand')
                    if Δt == None: #calculate once only
                        Δt=  cls.natural_time_to_temp(dlg,boil_kelvin,hs_kelvin,end_boil_volume)-time_to_HS
                        #print('delta_time '+str(Δt))
                    #b=   ((0.0002925 * cls.effective_area(dlg.equipment.kettle_capacity, dlg.equipment.kettle_steam_exit_diameter)) / end_boil_volume )+ 0.00538   
                    #print('b is '+str(b))
                    temp_K =53.7 * math.exp(-1.0 * b * (time + Δt)) +boil_kelvin -53.7 #the shifted curve
                    current_kelvin = temp_K


            if(time >time_to_HS +hs_duration):
                #Forced cooling at this point
                if(dlg.equipment.cooler_type == 'Contre-courant'):
                    current_volume=end_boil_volume-(dlg.equipment.cooler_flow_rate * (time-time_to_HS - hs_duration))
                    #when using counter-flow cooler the volume of wort decreases while the kettles is emptied thus b is not constant
                    b=   ((0.0002925 * cls.effective_area(dlg.equipment.kettle_capacity, dlg.equipment.kettle_steam_exit_diameter)) / current_volume )+ 0.00538   
                    if Δt2 == None: #calculate once only
                        Δt2=  cls.natural_time_to_temp(dlg,boil_kelvin,current_kelvin,current_volume)-time_to_HS-hs_duration
                    
                    #the natural curve is shifted to the letf heating is off kettle is being emptyied 
                    temp_K =(53.7 * math.exp(-1.0 * b * (time + Δt2))) +boil_kelvin -53.7
                    current_kelvin= temp_K

                if (dlg.equipment.cooler_type == 'Immersion'):
                    #kettle is not being emptyied i.e. volume is constant
                    
                    current_kelvin= current_kelvin -dlg.equipment.cooler_slope * (time_step)
            
            k1=k1 = 7.9 * math.pow(10.0, 11.0) * math.exp(-11858.0 / current_kelvin)
            k2 = 4.1 * math.pow(10.0, 12.0) * math.exp(-12994.0 / current_kelvin)
            
            d_AA_concentration = -1.0 * k1 * AA_concentration
            AA_concentration = AA_concentration + d_AA_concentration * time_step
            if (AA_concentration < 0) :
                AA_concentration = 0
            d_iso_AA_concentration= k1 * AA_concentration - k2 * iso_AA_concentration 
            iso_AA_concentration = iso_AA_concentration + d_iso_AA_concentration * time_step

            if iso_AA_concentration < 0 :
                iso_AA_concentration = 0
            
            time += time_step
            #print(str(current_kelvin -273.15) + ' at '+ str(time))
       
        #we have exited the loop
        return iso_AA_concentration        
        
    @classmethod
    def HS_IBU_from_integration(cls,dlg,AA0,loose):
        #this calculation supposes that the hop is added when the hopstand temperature is reached
        #set to the boil temperature. Will be calculated otherwise if one hop use hopstand ("hors flamme")
        #the volume of wort at end of boil
        end_boil_volume=dlg.batch_volume+dlg.equipment.fermenter_retention
        AA=AA0#initial alpha acids
        d_AA_concentration=0 # the derivative functioni.e. Δ_AA_concentration / Δt
        AA_concentration = AA0 /end_boil_volume
        d_iso_AA_concentration=0 # the derivative function i.e. Δ_iso_AA_concentration / Δt
        iso_AA_concentration=0
        
        
       
        time_step=0.1
        hs_duration=0
        hopstand=False
        emptying_time=None
        items = dlg.hop_selector.destination_model.items
        #check if hop stand is performed
        for item in items:
            if(item.usage == 'hors flamme'):
                hs_kelvin=item.temperature+273.15
                hs_duration = item.minutes
                hopstand=True
                break
        
        match dlg.equipment.cooler_type:
            case "Contre-courant":
                emptying_time=(dlg.batch_volume+dlg.equipment.kettle_retention)*1.04/dlg.equipment.cooler_flow_rate
        #this is the initial temperature
        boil_kelvin=100 -(28.8888 * dlg.equipment.altitude) /9144 +273.15 #boil temperatureK

        #time to reach Hopsand temperature
        time_to_HS=0 #hop is added when hopstand temperature is reached
        
        #the natural cooling time constant
        b=   ((0.0002925 * cls.effective_area(dlg.equipment.kettle_capacity, dlg.equipment.kettle_steam_exit_diameter)) / end_boil_volume) + 0.00538
        time=0
        Δt=None
        Δt2=None
        heating=True
        current_kelvin=boil_kelvin

        while time<300 and current_kelvin>70+273.15:#limit to five hours and 70 °C

            if  time<=hs_duration:
                if(heating ==True ): #heating indicates the hopstand temperature is regulated
                    current_kelvin= hs_kelvin

                else:
                    #the natural curve starts at time =0
                    temp_K =53.7 * math.exp(-1.0 * b * (time )) +boil_kelvin -53.7 #the shifted curve
                    current_kelvin = temp_K


            if time >hs_duration:
                if loose:
                #Forced cooling at this point
                    if(dlg.equipment.cooler_type == 'Contre-courant'):
                        current_volume=end_boil_volume-(dlg.equipment.cooler_flow_rate * (time- hs_duration))
                        #when using counter-flow cooler the volume of wort decreases while the kettles is emptied thus b is not constant
                        b=   ((0.0002925 * cls.effective_area(dlg.equipment.kettle_capacity, dlg.equipment.kettle_steam_exit_diameter)) / current_volume )+ 0.00538   
                        if Δt2 == None: #calculate once only
                            Δt2=  cls.natural_time_to_temp(dlg,boil_kelvin,current_kelvin,current_volume)-hs_duration
                        
                        #the natural curve is shifted to the letf heating is off kettle is being emptyied 
                        temp_K =(53.7 * math.exp(-1.0 * b * (time + Δt2))) +boil_kelvin -53.7
                        current_kelvin= temp_K

                    if (dlg.equipment.cooler_type == 'Immersion'):
                        #kettle is not being emptyied i.e. volume is constant
                        
                        current_kelvin= current_kelvin -dlg.equipment.cooler_slope * (time_step)
                else:
                    break   
            
            k1=k1 = 7.9 * math.pow(10.0, 11.0) * math.exp(-11858.0 / current_kelvin)
            k2 = 4.1 * math.pow(10.0, 12.0) * math.exp(-12994.0 / current_kelvin)
            
            d_AA_concentration = -1.0 * k1 * AA_concentration
            AA_concentration = AA_concentration + d_AA_concentration * time_step
            if (AA_concentration < 0) :
                AA_concentration = 0
            d_iso_AA_concentration= k1 * AA_concentration - k2 * iso_AA_concentration 
            iso_AA_concentration = iso_AA_concentration + d_iso_AA_concentration * time_step

            if iso_AA_concentration < 0 :
                iso_AA_concentration = 0
            
            time += time_step
            #print(str(current_kelvin -273.15) + ' at '+ str(time))
       
        #we have exited the loop
        return iso_AA_concentration 
    #------------------------------------------------------------------------------------------
    @classmethod
    def current_boiling_volume_cold(cls,dlg,time):
        #print('time in current_boiling_volume is '+str(time))
        if dlg.preboil_water_mass>0 and dlg.equipment:
            return dlg.preboil_water_mass - (dlg.equipment.kettle_evaporation_rate * time /60 )#division by 100 is because time is in cents of minute


        else: return None

    #--------------------------------------------------------------------------------------------
    @classmethod
    def residual_AA(cls,dlg,AA0,boil_time,usage):
        volume=0
        time_step=0.01
        preboil_time=0
        boil_time=boil_time
        temp=0
        time=0
        cpt=0
        AA=AA0 #les alpha acides en absolue
        d_AA_concentration=0
        AA_concentration = AA0 / dlg.preboil_water_mass

        if usage == "au premier moût":
            preboil_time=20 /dlg.equipment.kettle_heat_slope*dlg.preboil_water_mass
          
        if(usage == "à l'ébullition"):
            preboil_time=0
        while time< preboil_time+boil_time and cpt<3000:#cpt limité à 5 heures
            if time<preboil_time:
                temp=80 +( dlg.equipment.kettle_heat_slope * time /dlg.preboil_water_mass) +273.15
            else:
                temp=100+273.15
                
            volume=cls.current_boiling_volume_cold(dlg,time -preboil_time)#only ebullition time
            k1 = 7.9 * math.pow(10.0, 11.0) * math.exp(-11858.0 / temp)
            
            k2 = 4.1 * math.pow(10.0, 12.0) * math.exp(-12994.0 / temp)
            d_AA_concentration = -1.0 * k1 * AA_concentration
            AA_concentration = AA_concentration + d_AA_concentration * time_step
            if (AA_concentration < 0) :
                AA_concentration = 0
            
            time=time+time_step
            cpt=cpt+1 #a way to limit the loop even if data is wrong 
        AA = AA_concentration * volume

        return AA

    #----------------------------------------------------------------------------------------------------------------------
    @classmethod
    def bitterness(cls,dlg):
        if  dlg.utilisation_gravity_factor and dlg.batch_volume and dlg.equipment:  
            items = dlg.hop_selector.destination_model.items
            ibu=0
            for item in items:
                match item.usage:
                    case "à l'empâtage":
                        item.ibu =item.multiplicator * item.quantity * item.hop.alpha * dlg.utilisation_gravity_factor * cls.utilisation_time_factor(60)  *10 / (dlg.batch_volume+dlg.equipment.kettle_retention)
                        ibu+=item.ibu

                    case "au premier moût":
                        item.ibu= item.multiplicator *item.quantity * item.hop.alpha * dlg.utilisation_gravity_factor * cls.utilisation_time_factor(dlg.boil_time) * 10 / (dlg.batch_volume+dlg.equipment.kettle_retention)
                        if item.loose:
                            AA0=item.quantity * item.hop.alpha  /100 *1000 #  1000 for g to mg
                            #print ('AA0 is '+str(AA0))
                            loose_ibu=cls.calculate_residual_ibu(dlg,AA0,float(dlg.boil_time),"au premier moût")
                            item.ibu += loose_ibu
                        ibu +=item.ibu

                    case "à l'ébullition":
                        item.ibu = item.quantity * item.hop.alpha * dlg.utilisation_gravity_factor * cls.utilisation_time_factor(item.minutes) * 10 / (dlg.batch_volume+dlg.equipment.kettle_retention)
                        if item.loose:
                            AA0=item.quantity * item.hop.alpha  /100 *1000 #  1000 for g to mg
                            loose_ibu=cls.calculate_residual_ibu(dlg,AA0,float(item.minutes),"à l'ébullition")
                            item.ibu += loose_ibu 
                        ibu += item.ibu

                    case "hors flamme":
                        item.ibu=cls.HS_IBU_from_integration(dlg, item.quantity * item.hop.alpha /100 *1000,item.loose)#  1000 for g to mg
                        ibu += item.ibu
                        
            if(not dlg.bitterness_as_target):
                dlg.ui.calculatedIBUEdit.setText(str(round(ibu,0))) 
                dlg.ibu_indicator.setValue(ibu)
                dlg.bitterness=ibu 
                dlg.ibu_indicator.setValue(ibu)

            else:    
                dlg.ibu_indicator.setValue(ibu)
                return ibu
          

    #-----------------------------------------------------------------------------------------------------------------------------
    @classmethod
    def boil_temperature_kelvin(cls,dlg):
        if(dlg.equipment ):
            dlg.boil_temperature_kelvin=100 -(28.8888 * dlg.equipment.altitude) /9144 +273.15
            dlg.rest_selector.ui.boilTemperatureEdit.setText(str(round(dlg.boil_temperature_kelvin - 273.15,1)))
            cls.malovicki_factor(dlg)
    #-----------------------------------------------------------------------------------------------------------------------------
    @classmethod
    def malovicki_factor(cls,dlg):
        #this factor correct the Tinseth equation depending on altitude but also on temperature
        #as it decreases during hopstand
        if dlg.boil_temperature_kelvin :
            dlg.malovicki_factor = 239000000000 * math.exp(-9773 / dlg.boil_temperature_kelvin)

  
    #--------------------------------------------------------------------------------------------------------------------------   
    def print_debug_color(dlg):
        if (dlg.color ):
            cls.print_debug ('color is '+str(dlg.color))        

        
    @classmethod
    def print_debug(self,text):
        debug=False
        if debug:
            print(text)

    @classmethod
    def interpol (cls,T, Tmax, Tmin, rho_Tmax, rho_Tmin) :
        K = (Tmax - Tmin) / (rho_Tmin - rho_Tmax);
        return rho_Tmax + (Tmax - T) / K;

    @classmethod
    def rho(cls,T):
    #water density
    #http://www.atomer.fr/1/1-densite-eau.html
        if T < 20:
            #for safety but this case never happens
            return 0.998205;
        
        if (T >= 20 and T < 30) :
            return cls.interpol(T, 30, 20, 0.995649, 0.998205)
        
        if (T >= 30 and T < 40) :
            return cls.interpol(T, 40, 30, 0.99222, 0.995649)
        
        if (T >= 40 and T < 50) :
            return cls.interpol(T, 50, 40, 0.98803, 0.99222)
        
        if (T >= 50 and T < 60) :
            return cls.interpol(T, 60, 50, 0.9832, 0.98803)
        
        if (T >= 60 and T < 70) :
            return cls.interpol(T, 70, 60, 0.97778, 0.9832)
        
        if (T >= 70 and T < 80) :
            return cls.interpol(T, 80, 70, 0.97182, 0.97778)
        
        if (T >= 80 and T < 90) :
            return cls.interpol(T, 90, 80, 0.96535, 0.97182)
        
        if (T >= 90 and T < 100) :
            return cls.interpol(T, 100, 90, 0.9584, 0.96535)
      
        if (T > 100) :
            #if this happens, it will be close to 100
            return 0.9584
    

    @classmethod
    def reset_computation(cls,dlg):
        for r in dlg.rest_selector.destination_model.items:
            r.water_mass=None
            r.addition_temperature=None
            r.addition=None#cold
            r.addition_hot=None
            r.fraction=None
    
    @classmethod
    def print_computation_results(cls,dlg):
        for r in dlg.rest_selector.destination_model.items:
            #if r.water_mass is not None:
            try:
                water_mass=str(round(r.water_mass,2))
            except:
                water_mass=str(None)   
            try:
                addition_hot=str(round(r.addition_hot,2)) 
            except:
                addition_hot=str(None)
            try:
                addition_temperature=str(round(r.addition_temperature,1))
            except:
                addition_temperature=str(None)   
            #print(r.name+'   '+water_mass+'/'+addition_hot+'/'+addition_temperature) 

    @classmethod
    def compute_rests(cls,dlg):
        cls.reset_computation(dlg)
        match dlg.temperature_method:
            case 'Chauffage':
                cls.compute_strike_temperature(dlg)
            case 'Infusion':
                cls.compute_infusion_rests(dlg)
            case 'Décoction':
                cls.compute_decoction_rests(dlg)
    @classmethod
    def compute_strike_temperature(cls,dlg):
        #This is for the case the mash tun use heating
        #in such a case, the mash tun is supposed pre-heated when the grain is added
        if not dlg.grain_temperature or dlg.temperature_method == 'Infusion':
            #this is for 'Chauffage' and 'Décoction
            return False
        if dlg.temperature_method == 'Décoction' and dlg.equipment.type == 'Brew in a Bag':
            return False
        
        #the equivalent grain mass   
        G = dlg.total_mash_fermentable_mass # masse du grain
        C = dlg.equipment.mash_tun_heat_capacity_equiv # equivalent grain de la cuve
        M = dlg.mash_water_mass # mas d'eau
        Tg = dlg.grain_temperature
        T = dlg.rest_selector.destination_model.items[0].temperature #target temperature
        #calculation in Celcius
        try:
            dlg.rest_selector.destination_model.items[0].addition_temperature= round(T + (0.4 *G*(T-Tg)/(M+0.4*C)),1) #first_temperature =T2 + 0.4 * Mg * ((T2 - T1) / M2)
            dlg.rest_selector.destination_model.items[0].addition=round(M/cls.rho(20),1)
            dlg.rest_selector.destination_model.items[0].addition_hot=round(M/cls.rho(T),1)
            dlg.rest_selector.destination_model.items[0].water_mass=round(M,1)
            cls.print_computation_results(dlg)
        except:
            pass
       
        return True #calculation done
    
    '''@classmethod
    def compute_strike_temperature_initial(cls,dlg):
        #Initial state Mg * Tg with Mg = grain equivalent of grain+mash_tun capacity
        #Addition M2 * Tw with M2 mass of water in final state and Tw the water strike temperature
        #Final state (M2+0.4 * Mg)*T2  wit T2 target temperature o.4 is the coeff for grain capacity vs water capacity
        # we can write (0.4* Mg * Tg) + (M2 * Tw)=(M2 +0.4 Mg)*T2
        #0.4*Mg*Tg+M2*Tw  =  M2*T2+0.4*Mg*T2 i.e. M2 *Tw =M2 * T2 + 0.4 * Mg *T2-0.4 *Mg *Tg
        # thus Tw = T2 +0.4 * (Mg/M2) *(T2 -Tg) 
        #this is for decoction and heating temperature transition
        #i.e. all mash water is added at once
        if not dlg.grain_temperature or dlg.temperature_method == 'Infusion':
            #this is for 'Chauffage' and 'Décoction
            return False
        if dlg.temperature_method == 'Décoction' and dlg.equipment.type == 'Brew in a Bag':
            return False
        
        #the equivalent grain mass   
        Mg = dlg.total_mash_fermentable_mass+dlg.equipment.mash_tun_heat_capacity_equiv
        M2 = dlg.mash_water_mass
        T1 = dlg.grain_temperature
        T2 = dlg.rest_selector.destination_model.items[0].temperature
        #calculation in Celcius
        dlg.rest_selector.destination_model.items[0].addition_temperature= round(T2 + 0.4 * Mg * ((T2 - T1) / M2),1)  
        dlg.rest_selector.destination_model.items[0].addition=round(M2/cls.rho(20),1)
        dlg.rest_selector.destination_model.items[0].addition_hot=round(M2/cls.rho(T2),1)
        dlg.rest_selector.destination_model.items[0].water_mass=round(M2,1)
        cls.print_computation_results(dlg)

        return True #calculation done'''

    @classmethod
    def delta_mass(cls,Tw, T1, T2, M2, Mg):
        temp_k = (T2 - T1) / (Tw - T1)
        print('tempp_k is '+str(temp_k))
        return (M2 + 0.4 * Mg) * temp_k

    #----INFUSION-------------------------------------------------------------------------------------------------
    @classmethod
    def compute_infusion_rests(cls,dlg):
        #in the case of infusion, the mash tun and the grain are supposed to be at the room temperature
        if not dlg.grain_temperature or not dlg.additions_temperature or dlg.temperature_method != 'Infusion':
            print('short return '+str(dlg.grain_temperature)+'/'+str(dlg.additions_temperature)+'/'+dlg.temperature_method)
            return
        rests=dlg.rest_selector.destination_model.items
        deltaMass = None
        first = None
        temp_hour_drift=dlg.equipment.mash_tun_thermal_losses
        T1=None #previous rest temperature
        T2=None #the rest temperature
        M1=None #the previous rest water mass
        M2=None #the rest water mass
        Tw=dlg.additions_temperature #temperature of the various water additions
        #grain and mash tun are supposed to have the same temperature, thus we confuse them as grain
        Mg=dlg.total_mash_fermentable_mass + dlg.equipment.mash_tun_heat_capacity_equiv
        
        rho20=cls.rho(20)
        Tg=dlg.grain_temperature

        #first we need to identify the rest for which mash_thickness is defined
        
        for key in range(len(rests)):
            if float(rests[key].temperature) > dlg.additions_temperature:
                #should add an alarm
                return
            #print(rests[key])
            if rests[key].thickness_reference:

                reference = key
                #print('reference is '+str(first))
                rests[reference].water_mass =dlg.mash_water_mass
                #then we calculate this rest and the previous added water at Tw °C
                #and we loop down till the first rest
                for i in reversed(range(reference+1)):
                    #print('i in reverse loop is '+str(i))
                    if i==0:
                        break
                    #we start form a little less than the previous rest's temperature (due to thermal losses)
                    T1=rests[i-1].temperature - (rests[i-1].duration /60/2*temp_hour_drift)
                    #print('T1 is '+str(T1))
                    # we aim at a little more than the rest's temperature to anticipate thermal losses
                    T2=rests[i].temperature +(rests[i].duration /60/2*temp_hour_drift)
                    #print('T2 is '+str(T2))
                    M2=rests[i].water_mass
                    deltaMass=cls.delta_mass(Tw, T1, T2, M2, Mg)
                    #print('deltaMass is '+str(deltaMass))
                    rests[i-1].water_mass=M2-deltaMass
                    rests[i].addition=round(deltaMass /rho20,2) #cold volume
                    rests[i].addition_hot=round(deltaMass / cls.rho(Tw),2)
                    rests[i].addition_temperature = round(Tw,1)
                #print('rests[1].water_mass is '+str(rests[1].water_mass))

                #first rest temperature i.e. strike temperature
                #print("Dealing with rest 0")
                M2=rests[0].water_mass 
                #we aim at a little more than the rest's temperature
                T2=rests[0].temperature +(rests[0].duration / 60 / 2 * temp_hour_drift)
                T1 = Tg
                M1 = 0
                #We do not use the compute_strike_temperature method because in this case 
                #grain and mash tun have the same initial temperature
                first_temperature =T2 + 0.4 * Mg * ((T2 - T1) / M2)
                print("first temp is "+str(first_temperature))
                rests[0].addition=round(rests[0].water_mass / rho20,2)
                rests[0].addition_hot=round(rests[0].water_mass / cls.rho(first_temperature),2)
                rests[0].addition_temperature=round(first_temperature,1)
                
                #now we loop up till the last rest startinf from reference rest
                for i in range(reference , len(rests)-1):
                    #print('i in last loop is '+str(i))
                    #last is len(rests)-1
                    T1=rests[i].temperature - (rests[i].duration / 60 / 2 * temp_hour_drift)
                    T2=rests[i+1].temperature + (rests[i+1].duration / 60 / 2 * temp_hour_drift)
                    M1=rests[i].water_mass
                    deltaMass=((M1 + 0.4 * Mg) * (T2 - T1)) / (Tw - T2)
                    rests[i + 1].water_mass = M1 + deltaMass
                    rests[i + 1].addition = round(deltaMass / rho20,2);
                    rests[i + 1].addition_hot = round(deltaMass / cls.rho(Tw),2)
                   
                    rests[i + 1].addition_temperature = round(Tw,1)

                total_volume=0
                for rest in rests:
                    total_volume+=rest.addition
                if total_volume>dlg.mash_water_mass + dlg.sparge_water_mass*1.05:
                    pass #to set an alarm

                break #break the loop whent the reference rest has been done
        cls.print_computation_results(dlg)
                       
        
    @classmethod
    def compute_decoction_rests(cls,dlg):
        print('compute decoction rests')
        cls.reset_computation(dlg)  
        if not dlg.temperature_method =='Décoction' or not dlg.grain_temperature:
            return
        rests=dlg.rest_selector.destination_model.items
        temp_hour_drift = dlg.equipment.mash_tun_thermal_losses
        R= dlg.equipment.mash_thickness
        K= (R + 0.4) / (R + 1); #provides the mash heat capacity as Cm=K * Cw where Cw is water capacity
        m=dlg.equipment.mash_tun_heat_capacity_equiv #tun heat capacity in grain mass equiv
        M=dlg.mash_water_mass + dlg.total_mash_fermentable_mass
        for i in range(len(rests)-1):
            Tw = dlg.boil_temperature_kelvin-273.5
            T1 = rests[i].temperature -(rests[i].duration / 60 / 2 * temp_hour_drift)
            T2 = rests[i+1].temperature+(rests[i + 1].duration / 60 / 2 * temp_hour_drift)
            fraction =((1 + m / (K * M)) * (T2 - T1)) / (Tw - T1)
            rests[i].fraction=round(fraction,2)

