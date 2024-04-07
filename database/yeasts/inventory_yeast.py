from sqlalchemy import Column, Date,Index, Integer, Boolean,String, TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint
from database.orm_base import Base
from database.db_connection import engine, session
from database.orm_base import metadata
import datetime

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
   

