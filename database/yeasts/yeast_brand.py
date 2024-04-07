from sqlalchemy import Column, Index, Integer, String, TIMESTAMP, text,CHAR

from database.orm_base import Base
from database.db_connection import engine, session
from database.orm_base import metadata

class YBrand(Base):
    __tablename__="ybrands"
    
    id = Column("id",Integer, primary_key=True)
    name= Column('name',String(50), unique=True)
    country_code = Column("country_code", String(2))


                     
    
    def __init__(self,id, name, country_code):
        self.id=id
        self.name=name
        self.country_code=country_code

    def __repr__(self):
        return f"{self.id} {self.name} {self.country_code} "

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_ybrand(ybrand):
    try:
        with session as sess:
            result =(sess.query(YBrand).filter(YBrand.name == ybrand.name).first())
            if (result == None):
                sess.add(ybrand)
                sess.commit()
                return 'OK'
            else:
                #print(f"the brand {ybrand.name }  already exists! Nothing done!")
                return 'duplicate'
    except Exception as err:
        #print('An exception arose while attempting to add a yeast brand', err)
        return str(err)

def update_ybrand(ybrand):
    try:
        with session as sess:
            result =(sess.query(YBrand).filter(YBrand.id == ybrand.id).first())  
            if(result!= None):
                result.name=ybrand.name
                result.country_code=ybrand.country_code
                sess.add(result)
                sess.commit()
              
    except Exception as err:
        pass
           #print('An error arose when attempting to update a yeast brand',err)

def delete_ybrand(id):
    with session as sess:
        result= (sess.query(YBrand).filter(YBrand.id == id).first())
        if(result != None):
            sess.delete(result) 
            sess.commit()      
            

def all_ybrand():
    with session as sess:
        result=(sess.query(YBrand).all())      
    return result          

def find_ybrand_by_id(id):
    with session as sess:
        result=(sess.query(YBrand).filter(YBrand.id == id).first())   
        return result

def find_ybrand_by_name(name):
   with session as sess:
       result =   (sess.query(YBrand).filter(YBrand.name == name).first())  
       return result
       
       
         
