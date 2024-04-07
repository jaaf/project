from sqlalchemy import Column, Index, Integer, String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata

class WaterTarget(Base):
    __tablename__="water_targets"
    
    id = Column("id",Integer, primary_key=True,autoincrement=True)
    name= Column('name',String(50),unique=True)
    ca_min=Column('ca_min',Float)
    ca_min=Column('ca_min',Float)
    mg_min=Column('mg_min',Float)
    na_min=Column('na_min',Float)
    cl_min=Column('cl_min',Float)
    so4_min=Column('so4_min',Float)
    alca_min=Column('alca_min',Float)
    ca_max=Column('ca_max',Float)
    ca_max=Column('ca_max',Float)
    mg_max=Column('mg_max',Float)
    na_max=Column('na_max',Float)
    cl_max=Column('cl_max',Float)
    so4_max=Column('so4_max',Float)
    alca_max=Column('alca_max',Float)

 

                     
    
    def __init__(self,id, name,ca_min,mg_min,na_min,cl_min,so4_min,alca_min,ca_max,mg_max,na_max,cl_max,so4_max,alca_max):
        self.id=id
        self.name= name
        self.ca_min=ca_min
        self.mg_min=mg_min
        self.na_min=na_min
        self.cl_min=cl_min
        self.so4_min=so4_min
        self.alca_min=alca_min
        self.ca_max=ca_max
        self.mg_max=mg_max
        self.na_max=na_max
        self.cl_max=cl_max
        self.so4_max=so4_max
        self.alca_max=alca_max
        

    def __repr__(self):
        return f"{self.id}, {self.name}, ca_min: {self.ca_min} ca_max:{self.ca_max}"

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_water(water):
    try:
        with session as sess:
            result =(sess.query(WaterTarget).filter(WaterTarget.name == water.name).first())
            if (result == None):
                sess.add(water)
                sess.commit()
                return 'OK'  
            else:
                return 'Cette eau existe déjà !'    
    except Exception as err:
        return str(err)

def update_water(water):

   
    try:
        with session as sess:
            result =(sess.query(WaterTarget).filter(WaterTarget.id == water.id).first())  
       
            if(result!= None):
                result.name= water.name
                result.ca_min=  water.ca_min
                result.mg_min= water.mg_min
                result.na_min= water.na_min
                result.cl_min= water.cl_min
                result.so4_min= water.so4_min
                result.alca_min= water.alca_min
                result.ca_max=  water.ca_miax= water.mg_max
                result.na_max= water.na_max
                result.cl_max= water.cl_max
                result.so4_max= water.so4_max
                result.alca_max= water.alca_max
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no water   with id = {water.id}!")   
    except Exception as err:
          return str(err)

def delete_water(id):
    try:
        with session as sess:
            result= (sess.query(WaterTarget).filter(WaterTarget.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            
    except Exception as err:
        
        return (str(err))     

def all_water():
    with session as sess:
        result=(sess.query(WaterTarget).all())      
    return result        


def find_water_by_id(id):
   
    with session as sess:
        result = (sess.query(WaterTarget).filter(WaterTarget.id == id).first())
        return result

def find_water_by_name(name):
    with session as sess:
        result =(sess.query(WaterTarget).filter(WaterTarget.name == name).first())     
        return result   
    
              
   
