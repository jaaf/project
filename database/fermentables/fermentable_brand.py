from sqlalchemy import Column, Index, Integer, String, TIMESTAMP, text,CHAR

from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata

class FBrand(Base):
    __tablename__="fbrands"
    
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

def add_fbrand(fbrand):
    try:
        with session as sess:
            result =(sess.query(FBrand).filter(FBrand.name == fbrand.name).first())
            if (result == None):
                sess.add(fbrand)
                sess.commit()
                return 'OK'
            else:
                #print(f"the brand {fbrand.name }  already exists! Nothing done!")
                return 'cette marque existe probablement déjà  '
    except Exception as err:
        #print('An exception arose while attempting to add a fermentable brand', err)
        return str(err)

def update_fbrand(fbrand):
    try:
        with session as sess:
            result =(sess.query(FBrand).filter(FBrand.id == fbrand.id).first())  
            if(result!= None):
                result.name=fbrand.name
                result.country_code=fbrand.country_code
                sess.add(result)
                sess.commit()
             
    except Exception as err:
        pass
           #print('An error arose when attempting to update a fermentable brand',err)

def delete_fbrand(id):
    try:
        with session as sess:
            result= (sess.query(FBrand).filter(FBrand.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()    
                return "OK"  
    except Exception as e:
        return (str(e))       

def all_fbrand():
    with session as sess:
        result=(sess.query(FBrand).all())      
    return result          

def find_fbrand_by_id(id):
    with session as sess:
        result=(sess.query(FBrand).filter(FBrand.id == id).first())   
        return result

def find_fbrand_by_name(name):
    with session as sess:
       result =   (sess.query(FBrand).filter(FBrand.name == name).first())  
       return result
       
       
         
