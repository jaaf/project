from sqlalchemy import Column, Date,Index, Integer, Boolean,String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint
from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#AS IT SEEMS THAT SQLALCHEMY TRY TO CREATE TABLES IN ALPHABETHIC ORDER WE MUST PLACE INVENTORY MISC AFTER MISC and not in a separate file
#---------------------------------------------------------------------------------------------------------------
class Misc(Base):
    __tablename__="miscs"
    
    id = Column("id",Integer, primary_key=True)
    name= Column('name',String(50))
    category= Column('category',String(25))
    unit=Column('unit',String(10))
    notes=Column('notes', Text)

    __table_args__=(UniqueConstraint('name', name='_name_uc'),
                     )

                     
    
    def __init__(self,id, name,category,unit, notes):
        self.id=id
        self.name=name
        self.category=category
        self.unit=unit
        self.notes=notes

    def __repr__(self):
        return f"{self.id}, {self.name},  {self.category} "

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_misc(misc):
    try:
        with session as sess:
            sess.add(misc)
            sess.commit()
            return 'OK'       
    except Exception as err:
        if('Duplicate entry' in str(err)):
            return f'Entrée en double:  (nom : {misc.name}  ) existe déjà!' 
        else:
            return str(err)

def update_misc(misc):

    #print('in update misc , misc received')
    #print(misc)
    try:
        with session as sess:
            result =(sess.query(Misc).filter(Misc.id == misc.id).first())  
            #print('misc found by index')
            #print(result)
            if(result!= None):
                result.name=misc.name
                result.category=misc.category
                result.unit=misc.unit
                result.notes=misc.notes
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no misc   with id = {misc.id}!")   
    except Exception as err:
          return str(err)

def delete_misc(id):
    try:
        with session as sess:
            result= (sess.query(Misc).filter(Misc.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            
    except Exception as err:
        if('foreign key constraint fails' in str(err)):
            return ("L'ingrédient divers ne peut être supprimé car il est encore utilisé dans l'inventaire")
        #print('an exception was raised : '+str(err))
        return (str(err))     

def all_misc():
    with session as sess:
        result=(sess.query(Misc).all())      
    return result        


def find_misc_by_id(id):
    with session as sess:
        result = (sess.query(Misc).filter(Misc.id == id).first())
        return result
        
              
   
class InventoryMisc(Base):
    __tablename__="inventory_miscs"
    
    id = Column("id",Integer, primary_key=True)
    misc_id= Column('misc_id',Integer, ForeignKey("miscs.id"))
    quantity= Column('quantity',Float)
    cost = Column('cost',Float)
    purchase_date=Column('purchase_date',Date)
    frozen= Column('frozen', Boolean)
    
    def __init__(self,id, misc_id,quantity,cost,purchase_date,frozen=False):
        self.id=id
        self.misc_id=misc_id
        self.quantity=quantity
        self.cost=cost
        self.purchase_date=purchase_date
        self.frozen=frozen
      

    def __repr__(self):
        return f"[{self.id}, {self.misc_id}] ,({self.quantity} kg, {self.cost} €, {self.purchase_date}, {self.frozen})"
        
#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_inventory_misc(inventory_misc):
    
    try:
        with session as sess:
            sess.add(inventory_misc)
            sess.commit()
            return 'OK'       
    except Exception as err:
        return str(err)
        
def update_inventory_misc(inventory_misc):
    try:
        with session as sess:
            result =(sess.query(InventoryMisc).filter(InventoryMisc.id == inventory_misc.id).first())  
            if(result!= None):
                result.misc_id=inventory_misc.misc_id
                result.quantity=inventory_misc.quantity
                result.cost=inventory_misc.cost
                result.purchase_date=inventory_misc.purchase_date
                result.frozen=inventory_misc.frozen
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no inventory misc   with id = {inventory_misc.id}!")   
    except Exception as err:
           return str(err)
#----------------------------------------------------------------------------------          
def delete_inventory_misc(id):
    try:
        with session as sess:
            result= (sess.query(InventoryMisc).filter(InventoryMisc.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
               
    except Exception as err:
        return (str(err))    
                
#--------------------------------------------------------------------------------------
def all_inventory_misc():
    with session as sess:
        result=(sess.query(InventoryMisc).all())      
    return result        
   

