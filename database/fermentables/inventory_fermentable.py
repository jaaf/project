from sqlalchemy import Column, Index, Integer, Boolean,String, Date,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint
from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata
import datetime

class InventoryFermentable(Base):
    __tablename__="inventory_fermentables"
    
    id = Column("id",Integer, primary_key=True)
    fermentable_id= Column('fermentable_id',Integer, ForeignKey("fermentables.id"))
    quantity= Column('quantity',Float)
    cost = Column('cost',Float)
    purchase_date=Column('purchase_date',Date,default=datetime.date.today())
    frozen= Column('frozen', Boolean)
    
    def __init__(self,id, fermentable_id,quantity,cost,purchase_date,frozen=False):
        self.id=id
        self.fermentable_id=fermentable_id
        self.quantity=quantity
        self.cost=cost
        self.purchase_date=purchase_date
        self.frozen=frozen
      

    def __repr__(self):
        return f"[{self.id}, {self.fermentable_id}] ,({self.quantity} kg, {self.cost} €, {self.purchase_date}, {self.frozen})"
        
#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_inventory_fermentable(inventory_fermentable):
    
    try:
        with session as sess:
            sess.add(inventory_fermentable)
            sess.commit()
            return 'OK'       
    except Exception as err:
        return str(err)
        
def update_inventory_fermentable(inventory_fermentable):
    #print('before update')
    #print('id : '+str(inventory_fermentable.id))
    #print('fermentable_id : '+str(inventory_fermentable.fermentable_id))
    #print('quantity : '+str(inventory_fermentable.quantity))
    #print('cost : '+str(inventory_fermentable.cost))
    #print('purchase_date : '+str(inventory_fermentable.purchase_date))
    #print('frozen : '+str(inventory_fermentable.frozen))
    print(str(inventory_fermentable.id))
    print(str(inventory_fermentable.fermentable_id))
    try:
        with session as sess:
            result =(sess.query(InventoryFermentable).filter(InventoryFermentable.id == inventory_fermentable.id).first())  
            if(result!= None):
                result.fermentable_id=inventory_fermentable.fermentable_id
                result.quantity=inventory_fermentable.quantity
                result.cost=inventory_fermentable.cost
                result.purchase_date=inventory_fermentable.purchase_date
                result.frozen=inventory_fermentable.frozen
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no inventory fermentable   with id = {str(inventory_fermentable.id)}!")   
    except Exception as err:
           return str(err)
           
def delete_inventory_fermentable(id):
    try:
        with session as sess:
            result= (sess.query(InventoryFermentable).filter(InventoryFermentable.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()
                return 'OK'      
                
    except Exception as err:
        return (str(err))            

def all_inventory_fermentable():
    with session as sess:
        result=(sess.query(InventoryFermentable).all())      
    return result        
   

