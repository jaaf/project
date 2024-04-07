from sqlalchemy import Column, Index, Integer, String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata

class Rest(Base):
    __tablename__="rests"
    
    id = Column("id",Integer, primary_key=True)
    name= Column('name',String(50),unique=True)
    temperature=Column('temperature',Float)
    duration=Column('duration',Float)
    thickness_reference=Column('thickness_reference',Integer)


  
                     
    
    def __init__(self,id, name,temperature,duration,thickness_reference):
        self.id=id
        self.name= name
        self.temperature=temperature
        self.duration=duration
        self.thickness_reference=thickness_reference
        
        

    def __repr__(self):
        return f"{self.id}, {self.name}"

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_rest(rest):
    try:
        with session as sess:
            sess.add(rest)
            sess.commit()
            return 'OK'       
    except Exception as err:
        return str(err)

def update_rest(rest):
    try:
        with session as sess:
            result =(sess.query(Rest).filter(Rest.id == rest.id).first())  
            #print('water found by index')
            #print(result)
            if(result!= None):
                result.name= rest.name
                result.temperature=  rest.temperature
                result.duration= rest.duration
                result.thickness_reference=rest.thickness_reference
             
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no rest   with id = {rest.id}!")   
    except Exception as err:
          return str(err)

def delete_rest(id):
    try:
        with session as sess:
            result= (sess.query(Rest).filter(Rest.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            
    except Exception as err:
        
        return (str(err))     

def all_rest():
    with session as sess:
        result=(sess.query(Rest).all())      
    return result        


def find_rest_by_id(id):
    with session as sess:
        result = (sess.query(Rest).filter(Rest.id == id).first())
        return result
        
              
   
