from sqlalchemy import Column, Index, Integer, Date,String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session

from database.orm_base import metadata
import datetime

class Brew(Base):
    __tablename__="brews"
    
    id = Column("id",Integer, primary_key=True,autoincrement=True)
    name= Column('name',String(50))
    equipment=Column('equipment',Text)
    batch_volume=Column('batch_volume',Float)
    brew_date=Column('brew_date',Date,default=datetime.date.today())
    rtype=Column('rtype',String(25))
    style=Column('style',String(50))
    bitterness=Column('bitterness',Float)
    og=Column('og',Float)
    abv=Column('abv',Float)
    color=Column('color',Float)
    boil_time=Column('boil_time',Float)
    fermentables=Column('fermentables',Text)
    hops=Column('hops',Text)
    yeasts=Column('yeasts',Text)
    miscs=Column('miscs',Text)
    rests=Column('rests',Text)
    grain_temperature=Column('grain_temperature',Float)
    additions_temperature=Column('additions_temperature',Float)
    temperature_method=Column('temperature_method',String(25))
    base_water=Column('base_water',Text) 
    dilution_water=Column('dilution_water',Text)
    dilution=Column('dilution',Integer)
    style_water=Column('style_water',Text)
    target_water=Column('target_water',Text)
    water_for_sparge=Column('water_for_sparge',String(50))
    salt_additions=Column('salt_additions',Text)
    water_adjustment_state=Column('water_adjustment_state',String(50))
    pH_adjuster_enabled =Column('pH_adjuster_enabled',Integer)
    pH_target=Column('pH_target',Float)
    acid_agent=Column('acid_agent',String(25))
    launched=Column('launched',Integer)
    feedback=Column('feedback',Text)

  

    __table_args__=(UniqueConstraint('name', 'brew_date',name='_name_date_uc'),)

    def __repr__(self):
        return f"[{self.id}, {self.name} ,{self.launched},{self.feedback}"

    
    def __init__(self,id,name,equipment,batch_volume,brew_date,rtype,style,bitterness,og,abv,color,boil_time,fermentables,hops,yeasts,miscs,rests,\
                 grain_temperature, additions_temperature, temperature_method,base_water,dilution_water,dilution,\
    style_water, target_water,water_for_sparge,salt_additions,water_adjustment_state,pH_adjuster_enabled,pH_target,acid_agent,launched,feedback):
        self.id=id
        self.name= name
        self.equipment=equipment
        self.batch_volume=batch_volume
        self.brew_date=brew_date
        self.rtype=rtype
        self.style=style
        self.bitterness=bitterness
        self.og=og
        self.abv=abv
        self.color=color
        self.boil_time=boil_time
        self.fermentables=fermentables
        self.hops=hops
        self.yeasts=yeasts
        self.miscs=miscs
        self.rests=rests
        self.grain_temperature=grain_temperature
        self.additions_temperature=additions_temperature
        self.temperature_method=temperature_method
        self.base_water=base_water
        self.dilution_water=dilution_water
        self.dilution=dilution
        self.style_water=style_water
        self.target_water=target_water
        self.water_for_sparge=water_for_sparge
        self.salt_additions=salt_additions
        self.water_adjustment_state=water_adjustment_state
        self.pH_adjuster_enabled=pH_adjuster_enabled
        self.pH_target=pH_target
        self.acid_agent=acid_agent
        self.launched=launched
        self.feedback=feedback
        
#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_brew(brew):
    print("IN add_brew ")
    try:
        with session as sess:
            sess.add(brew)
            sess.commit()
            print('my breww id in add_brew '+str(brew.id))
            return brew.id      
    except Exception as err:
       
        return 'Error'+str(err)

#-------------------------------------------------------------------------
def update_brew(brew): 
    print("IN updat_brew")
    try:
        with session as sess:
            result =(sess.query(Brew).filter(Brew.id == brew.id).first())  
            if(result!= None):
                result.name= brew.name
                result.rtype=brew.rtype
                result.brew_date=brew.brew_date
                result.style=brew.style
                result.equipment=brew.equipment
                result.batch_volume=brew.batch_volume
                result.bitterness=brew.bitterness
                result.og=brew.og
                result.abv=brew.abv
                result.color=brew.color
                result.boil_time=brew.boil_time
                result.fermentables=brew.fermentables
                result.hops=brew.hops
                result.yeasts=brew.yeasts
                result.miscs=brew.miscs
                result.rests=brew.rests
                result.grain_temperature=brew.grain_temperature
                result.additions_temperature=brew.additions_temperature
                result.temperature_method=brew.temperature_method
                result.base_water=brew.base_water
                result.dilution_water=brew.dilution_water
                result.dilution=brew.dilution
                result.style_water=brew.style_water
                result.target_water=brew.target_water
                result.water_for_sparge=brew.water_for_sparge
                result.salt_additions=brew.salt_additions
                result.water_adjustment_state=brew.water_adjustment_state
                result.pH_adjuster_enabled=brew.pH_adjuster_enabled
                result.pH_target=brew.pH_target
                result.acid_agent=brew.acid_agent
                result.launched=brew.launched
                result.feedback=brew.feedback
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no session   with id = {session.id}!")   
    except Exception as err:
          return "Il y a une erreur" +str(err)

def delete_brew(id):
    try:
        with session as sess:
            result= (sess.query(Brew).filter(Brew.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            
    except Exception as err:
        
        return (str(err))     

def all_brew():
    with session as sess:
        result=(sess.query(Brew).all())      
    return result        


def find_brew_by_id(id):
    with session as sess:
        result = (sess.query(Brew).filter(Brew.id == id).first())
        return result

def find_brew_by_name(name):
    with session as sess:
        result = (sess.query(Brew).filter(Brew.name == name).first())
        return result

def find_brew_by_name_and_date(name, date):
    with session as sess:
        result = (sess.query(Brew).filter(Brew.name == name,Brew.brew_date==date).first())
        return result