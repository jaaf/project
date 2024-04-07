from sqlalchemy import Column, Index, Integer, String, TIMESTAMP, text,CHAR

from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata

class HSupplier(Base):
    __tablename__="hsuppliers"
    
    id = Column("id",Integer, primary_key=True)
    name= Column('name',String(50), unique=True)
   


                     
    
    def __init__(self,id, name):
        self.id=id
        self.name=name

    def __repr__(self):
        return f"{self.id} {self.name}  "

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_hsupplier(hsupplier):
    try:
        with session as sess:
            result =(sess.query(HSupplier).filter(HSupplier.name == hsupplier.name).first())
            if (result == None):
                sess.add(hsupplier)
                sess.commit()
                return 'OK'
            else:
                #print(f"the supplier {hsupplier.name }  already exists! Nothing done!")
                return 'Ce vendeur existe déjà.'
    except Exception as err:
        #print('An exception arose while attempting to add a hop supplier', err)
        return str(err)

def update_hsupplier(hsupplier):
    try:
        with session as sess:
            result =(sess.query(HSupplier).filter(HSupplier.id == hsupplier.id).first())  
            if(result!= None):
                result.name=hsupplier.name
                sess.add(result)
                sess.commit()
              
    except Exception as err:
        pass
           #print('An error arose when attempting to update a hop supplier',err)

def delete_hsupplier(id):
    with session as sess:
        result= (sess.query(HSupplier).filter(HSupplier.id == id).first())
        if(result != None):
            sess.delete(result) 
            sess.commit()      
             

def all_hsupplier():
    with session as sess:
        result=(sess.query(HSupplier).all())      
    return result          

def find_hsupplier_by_id(id):
    with session as sess:
        result=(sess.query(HSupplier).filter(HSupplier.id == id).first())   
        return result

def find_hsupplier_by_name(name):
   with session as sess:
       result =   (sess.query(HSupplier).filter(HSupplier.name == name).first())  
       return result
       
       
         
