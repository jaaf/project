from sqlalchemy import Column, Date,Index, Integer, String, Boolean,Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata
import datetime

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
                return 'Cette marque de levure existe déjà.'
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
       
       
         

class Yeast(Base):
    __tablename__="yeasts"
    
    id = Column("id",Integer, primary_key=True)
    brand= Column('brand',String(50), ForeignKey("ybrands.name"))
    name= Column('name',String(50))
    manufacture_date=Column('manufacture_date',Date)
    expiration_date=Column('expiration_date',Date)
    pack_unit=Column('pack_unit',String(25))
    cells_per_pack=Column('cells_per_pack',Float)
    form = Column('form',String(10))
    target=Column('target',String(10))
    floculation=Column('floculation',String(10))
    sedimentation=Column('sedimentation', String(10))
    abv_tolerance=Column('abv_tolerance', Float)
    temp_min =Column('temp_min',Float)
    temp_ideal_min =Column('temp_ideal_min',Float)
    temp_ideal_max =Column('temp_ideal_max',Float)
    temp_max =Column('temp_max',Float)
    attenuation=Column('attenuation',Float)
    link=Column('link',String(255))
    notes=Column('notes', Text)

    __table_args__=(UniqueConstraint('name', 'brand','pack_unit', name='_name_brand_unit_uc'), )

                     
    
    def __init__(self,id, brand,name,manufacture_date,expiration_date,pack_unit,cells_per_pack,form,target,floculation, sedimentation, abv_tolerance,\
        temp_min,temp_ideal_min,temp_ideal_max,temp_max,attenuation,link,notes):
        self.id=id
        self.brand=brand
        self.name=name
        self.manufacture_date=manufacture_date
        self.expiration_date=expiration_date  
        self.pack_unit=pack_unit
        self.cells_per_pack=cells_per_pack        
        self.form=form
        self.target=target
        self.floculation=floculation
        self.sedimentation=sedimentation
        self.abv_tolerance=abv_tolerance
        self.temp_min=temp_min
        self.temp_ideal_min=temp_ideal_min
        self.temp_ideal_max=temp_ideal_max
        self.temp_max=temp_max
        self.attenuation=attenuation
        self.link=link
        self.notes=notes

    def __repr__(self):
        return f"[{self.id}, {self.brand}, {self.name}] "

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_yeast(yeast):
    try:
        with session as sess:
            sess.add(yeast)
            sess.commit()
            return 'OK'       
    except Exception as err:
        if('Duplicate entry' in str(err)):
            return f'Entrée en double: le doublet (nom : {yeast.name} , marque : {yeast.brand} ) existe déjà!' 
        else:
            return str(err)

def update_yeast(yeast):

    #print('in update yeast , yeast received')
    #print(yeast)
    try:
        with session as sess:
            result =(sess.query(Yeast).filter(Yeast.id == yeast.id).first())  
            #print('yeast found by index')
            #print(result)
            if(result!= None):
                result.brand=yeast.brand
                result.name=yeast.name
                result.manufacture_date=yeast.manufacture_date
                result.expiration_date=yeast.expiration_date  
                result.pack_unit=yeast.pack_unit
                result.cells_per_pack=yeast.cells_per_pack        
                result.form=yeast.form
                result.target=yeast.target
                result.floculation=yeast.floculation
                result.sedimentation=yeast.sedimentation
                result.abv_tolerance=yeast.abv_tolerance
                result.temp_min=yeast.temp_min
                result.temp_ideal_min=yeast.temp_ideal_min
                result.temp_ideal_max=yeast.temp_ideal_max
                result.temp_max=yeast.temp_max
                result.attenuation=yeast.attenuation
                result.link=yeast.link
                result.notes=yeast.notes
                #print('yeast after update')
                #print(result)
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no yeast   with id = {yeast.id}!")   
    except Exception as err:
          return str(err)

def delete_yeast(id):
    try:
        with session as sess:
            result= (sess.query(Yeast).filter(Yeast.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            
    except Exception as err:
        if('foreign key constraint fails' in str(err)):
            return ("La levure ne peut être supprimée car elle est toujours utilisée dans l'inventaire")
        #print('an exception was raised : '+str(err))
        return (str(err))     

def all_yeast():
    with session as sess:
        result=(sess.query(Yeast).all())      
    return result        


def find_yeast_by_id(id):
    with session as sess:
        result = (sess.query(Yeast).filter(Yeast.id == id).first())
        return result
        
              
class InventoryYeast(Base):
    __tablename__="inventory_yeasts"
    
    id = Column("id",Integer, primary_key=True)
    yeast_id= Column('yeast_id',Integer, ForeignKey("yeasts.id"))
    quantity= Column('quantity',Float)
    cost = Column('cost',Float)
    purchase_date=Column('purchase_date',Date)
    frozen= Column('frozen', Boolean)
    
    def __init__(self,id, yeast_id,quantity,cost,purchase_date,frozen=False):
        self.id=id
        self.yeast_id=yeast_id
        self.quantity=quantity
        self.cost=cost
        self.purchase_date=purchase_date
        self.frozen=frozen
      

    def __repr__(self):
        return f"[{self.id}, {self.yeast_id}] ,({self.quantity} kg, {self.cost} €, {self.purchase_date}, {self.frozen})"
        
#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_inventory_yeast(inventory_yeast):
    
    try:
        with session as sess:
            sess.add(inventory_yeast)
            sess.commit()
            return 'OK'       
    except Exception as err:
        return str(err)
        
def update_inventory_yeast(inventory_yeast):
    try:
        with session as sess:
            result =(sess.query(InventoryYeast).filter(InventoryYeast.id == inventory_yeast.id).first())  
            if(result!= None):
                result.fermentable_id=inventory_yeast.yeast_id
                result.quantity=inventory_yeast.quantity
                result.cost=inventory_yeast.cost
                result.purchase_date=inventory_yeast.purchase_date
                result.frozen=inventory_yeast.frozen
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no inventory yeast   with id = {inventory_yeast.id}!")   
    except Exception as err:
           return str(err)
#----------------------------------------------------------------------------------          
def delete_inventory_yeast(id):
    try:
        with session as sess:
            result= (sess.query(InventoryYeast).filter(InventoryYeast.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
                
    except Exception as err:
        return (str(err))    
                
#--------------------------------------------------------------------------------------
def all_inventory_yeast():
    with session as sess:
        result=(sess.query(InventoryYeast).all())      
    return result        
   


