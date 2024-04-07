from sqlalchemy import Column, Index, Integer, String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata


class Equipment(Base):
    __tablename__="equipments"
    
    id = Column("id",Integer, primary_key=True)
    name= Column('name',String(50),unique=True)
    type= Column('type',String(25))
    hop_absorption=Column('hop_absorption',Float)
    hop_absorption_reduction_coeff=Column('hop_reduction_absorption_coeff',Float)
    grain_absorption=Column('grain_absorption',Float)
    altitude=Column('altitude',Float)

    mash_tun_capacity=Column('mash_tun_capacity',Float)
    mash_tun_retention=Column('mash_tun_retention',Float)
    mash_tun_undergrain=Column('mash_tun_undergrain',Float)
    mash_tun_thermal_losses=Column('mash_tun_thermal_losses',Float)
    mash_tun_heat_capacity_equiv=Column('mash_tun_heat_capacity_equiv',Float)
    mash_thickness=Column('mash_thickness',Float)
    mash_efficiency=Column('mash_efficiency',Float)

    kettle_capacity=Column('kettle_capacity',Float)
    kettle_retention=Column('kettle_retention',Float)
    kettle_diameter=Column('kettle_diameter',Float)
    kettle_steam_exit_diameter=Column('kettle_steam_exit_diameter',Float)
    kettle_evaporation_rate=Column('kettle_evaporation_rate',Float)
    kettle_heat_slope=Column('kettle_heat_slope',Float)

    fermenter_capacity=Column('fermenter_capacity',Float)
    fermenter_retention=Column('fermenter_retention',Float)

    cooler_type=Column('cooler_type',String(25))
    cooler_slope=Column('cooler_slope',Float)
    cooler_flow_rate=Column('cooler_flow_rate',Float)

    __table_args__=(UniqueConstraint('name', name='_name_uc'),
                     )

                     
    
    def __init__(self,id, name, type, hop_absorption,hop_absorption_reduction_coeff,grain_absorption, altitude, mash_tun_capacity, mash_tun_retention,mash_tun_undergrain,\
        mash_tun_thermal_losses,mash_tun_heat_capacity_equiv,mash_thickness,mash_efficiency, \
        kettle_capacity,kettle_retention, kettle_diameter,kettle_steam_exit_diameter, kettle_evaporation_rate, kettle_heat_slope,\
        fermenter_capacity, fermenter_retention, cooler_type,cooler_slope,cooler_flow_rate):
        self.id=id
        self.name= name
        self.type= type
        self.hop_absorption=hop_absorption
        self.hop_absorption_reduction_coeff=hop_absorption_reduction_coeff
        self.grain_absorption=grain_absorption
        self.altitude=altitude

        self.mash_tun_capacity=mash_tun_capacity
        self.mash_tun_retention=mash_tun_retention
        self.mash_tun_undergrain=mash_tun_undergrain
        self.mash_tun_thermal_losses=mash_tun_thermal_losses
        self.mash_tun_heat_capacity_equiv=mash_tun_heat_capacity_equiv
        self.mash_thickness=mash_thickness
        self.mash_efficiency=mash_efficiency

        self.kettle_capacity=kettle_capacity
        self.kettle_retention=kettle_retention
        self.kettle_diameter=kettle_diameter
        self.kettle_steam_exit_diameter=kettle_steam_exit_diameter
        self.kettle_evaporation_rate=kettle_evaporation_rate
        self.kettle_heat_slope=kettle_heat_slope

        self.fermenter_capacity=fermenter_capacity
        self.fermenter_retention=fermenter_retention

        self.cooler_type=cooler_type
        self.cooler_slope=cooler_slope
        self.cooler_flow_rate=cooler_flow_rate

    def __repr__(self):
        return f"{self.id}, {self.name}, {self.type}"

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_equipment(equipment):
    try:
        with session as sess:
            result =(sess.query(Equipment).filter(Equipment.name == equipment.name).first())
            if result == None:
                sess.add(equipment)
                sess.commit()
                return 'OK'
            else:
                return 'Un équipement de même nom existe déjà !'       
    except Exception as err:
        return str(err)

def update_equipment(equipment):

    #print('in update equipment , equipment received')
    #print(equipment)
    try:
        with session as sess:
            result =(sess.query(Equipment).filter(Equipment.id == equipment.id).first())  
            #print('equipment found by index')
            #print(result)
            if(result!= None):
                result.name= equipment.name
                result.type=  equipment.type
                result.hop_absorption= equipment.hop_absorption
                result.hop_absorption_reduction_coeff=equipment.hop_absorption_reduction_coeff
                result.grain_absorption= equipment.grain_absorption
            
                result.altitude= equipment.altitude

                result.mash_tun_capacity= equipment.mash_tun_capacity
                result.mash_tun_retention=equipment.mash_tun_retention
                result.mash_tun_undergrain= equipment.mash_tun_undergrain
                result.mash_tun_thermal_losses= equipment.mash_tun_thermal_losses
                result.mash_tun_heat_capacity_equiv= equipment.mash_tun_heat_capacity_equiv
                result.mash_thickness= equipment.mash_thickness
                result.mash_efficiency= equipment.mash_efficiency

                result.kettle_capacity= equipment.kettle_capacity
                result.kettle_retention= equipment.kettle_retention
                result.kettle_diameter= equipment.kettle_diameter
                result.kettle_steam_exit_diameter= equipment.kettle_steam_exit_diameter
                result.kettle_evaporation_rate=equipment.kettle_evaporation_rate
                result.kettle_heat_slope=equipment.kettle_heat_slope

                result.fermenter_capacity= equipment.fermenter_capacity
                result.fermenter_retention= equipment.fermenter_retention

                result.cooler_type= equipment.cooler_type
                result.cooler_slope= equipment.cooler_slope
                result.cooler_flow_rate= equipment.cooler_flow_rate
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no equipment   with id = {equipment.id}!")   
    except Exception as err:
          return str(err)

def delete_equipment(id):
    try:
        with session as sess:
            result= (sess.query(Equipment).filter(Equipment.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            
    except Exception as err:
        
        return (str(err))     

def all_equipment():
    with session as sess:
        result=(sess.query(Equipment).all())      
    return result        


def find_equipment_by_id(id):
    with session as sess:
        result = (sess.query(Equipment).filter(Equipment.id == id).first())
        return result
        
             
def find_equipment_by_name(name):
    with session as sess:
        result = (sess.query(Equipment).filter(Equipment.name == name).first())
        return result
          
