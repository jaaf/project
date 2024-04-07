from sqlalchemy import Column, Index, Integer, String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata

class Water(Base):
    __tablename__="waters"
    
    id = Column("id",Integer, primary_key=True)
    name= Column('name',String(50),unique=True)
    ca=Column('ca',Float)
    mg=Column('mg',Float)
    na=Column('na',Float)
    cl=Column('cl',Float)
    so4=Column('so4',Float)
    alca=Column('alca',Float)
    pH=Column('pH',Float)

    __table_args__=(UniqueConstraint('name', name='_name_uc'),
                     )

                     
    
    def __init__(self,id, name,ca,mg,na,cl,so4,alca,pH):
        self.id=id
        self.name= name
        self.ca=ca
        self.mg=mg
        self.na=na
        self.cl=cl
        self.so4=so4
        self.alca=alca
        self.pH=pH

        

    def __repr__(self):
        return f"{self.id}, {self.name},{self.ca} , {self.mg}"

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_water(water):
    try:
        with session as sess:
            result =(sess.query(Water).filter(Water.name == water.name).first())
            if (result == None):
                sess.add(water)
                sess.commit()
                return 'OK'  
            else:
                return 'Cette eau existe déjà !'     
    except Exception as err:
        return str(err)

def update_water(water):

    #print('in update water , water received')
    #print(water)
    try:
        with session as sess:
            result =(sess.query(Water).filter(Water.id == water.id).first())  
            #print('water found by index')
            #print(result)
            if(result!= None):
                result.name= water.name
                result.ca=  water.ca
                result.mg= water.mg
                result.na= water.na
                result.cl= water.cl
                result.so4= water.so4
                result.alca= water.alca
                result.pH=water.pH
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
            result= (sess.query(Water).filter(Water.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            
    except Exception as err:
        
        return (str(err))     

def all_water():
    with session as sess:
        result=(sess.query(Water).all())      
    return result        


def find_water_by_id(id):
    with session as sess:
        result = (sess.query(Water).filter(Water.id == id).first())
        return result
        
              
   
