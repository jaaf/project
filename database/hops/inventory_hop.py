from sqlalchemy import Column, Date,Index, Integer, Boolean,String, TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint
from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata
import datetime

class InventoryHop(Base):
    __tablename__="inventory_hops"
    
    id = Column("id",Integer, primary_key=True)
    hop_id= Column('hop_id',Integer, ForeignKey("hops.id"))
    quantity= Column('quantity',Float)
    cost = Column('cost',Float)
    purchase_date=Column('purchase_date',Date)
    frozen= Column('frozen', Boolean)
    
    def __init__(self,id, hop_id,quantity,cost,purchase_date,frozen=False):
        self.id=id
        self.hop_id=hop_id
        self.quantity=quantity
        self.cost=cost
        self.purchase_date=purchase_date
        self.frozen=frozen
      

    def __repr__(self):
        return f"[{self.id}, {self.hop_id}] ,({self.quantity} kg, {self.cost} €, {self.purchase_date}, {self.frozen})"
        
#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_inventory_hop(inventory_hop):
    
    try:
        with session as sess:
            sess.add(inventory_hop)
            sess.commit()
            return 'OK'       
    except Exception as err:
        return str(err)
        
def update_inventory_hop(inventory_hop):
    try:
        with session as sess:
            result =(sess.query(InventoryHop).filter(InventoryHop.id == inventory_hop.id).first())  
            if(result!= None):
                result.hop_id=inventory_hop.hop_id
                result.quantity=inventory_hop.quantity
                result.cost=inventory_hop.cost
                result.purchase_date=inventory_hop.purchase_date
                result.frozen=inventory_hop.frozen
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no inventory hop   with id = {inventory_hop.id}!")   
    except Exception as err:
           return str(err)
#----------------------------------------------------------------------------------          
def delete_inventory_hop(id):
    try:
        with session as sess:
            result= (sess.query(InventoryHop).filter(InventoryHop.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
                 
    except Exception as err:
        return (str(err))    
                
#--------------------------------------------------------------------------------------
def all_inventory_hop():
    with session as sess:
        result=(sess.query(InventoryHop).all())      
    return result        
   

