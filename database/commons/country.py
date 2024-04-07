from sqlalchemy import Column, Index, Integer, String, TIMESTAMP, text,CHAR

from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata

class Country(Base):
    __tablename__="countries"
    
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

def add_country(country):
    try:
        with session as sess:
            result =(sess.query(Country).filter(Country.name == country.name).first())
            if (result == None):
                sess.add(country)
                sess.commit()
                return 'OK'
            else:
                #print(f"the country {country.name }  already exists! Nothing done!")
                return 'duplicate'
    except Exception as err:
        #print('An exception arose while attempting to add a country', err)
        return str(err)

def update_country(country):
    try:
        with session as sess:
            result =(sess.query(Country).filter(Country.id == country.id).first())  
            if(result!= None):
                result.name=country.name
                result.country_code=country.country_code
                sess.add(result)
                sess.commit()
              
    except Exception as err:
        pass
           #print('An error arose when attempting to update a  country',err)

def delete_country(id):
    with session as sess:
        result= (sess.query(Country).filter(Country.id == id).first())
        if(result != None):
            sess.delete(result) 
            sess.commit()      
             

def all_country():
    with session as sess:
        result=(sess.query(Country).all())      
    return result          

def find_country_by_id(id):
    with session as sess:
        result=(sess.query(Country).filter(Country.id == id).first())   
        return result

def find_country_by_name(name):
   with session as sess:
       result =   (sess.query(Country).filter(Country.name == name).first())  
       return result

def find_country_by_code(code):
    with session as sess:
       result =   (sess.query(Country).filter(Country.country_code == code).first())  
       return result       
         
