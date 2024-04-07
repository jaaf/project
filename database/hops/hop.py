from sqlalchemy import Column, Index, Integer, String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata

class Hop(Base):
    __tablename__="hops"
    
    id = Column("id",Integer, primary_key=True)
    supplier= Column('supplier',String(50))
    crop_year=Column('crop_year',String(4))
    country_code=Column('country_code',String(2))
    name= Column('name',String(50))
    form = Column('form',String(10))
    purpose =Column('purpose',String(10))
    alpha =Column('alpha',Float)
    aromas = Column('aromas',String(255))
    alternatives=Column('alternatives',String(255))
    link=Column('link',String(255))
    notes=Column('notes', Text)

    __table_args__=(UniqueConstraint('name', 'supplier','crop_year', name='_name_supplier_crop_uc'),
                     )

                     
    
    def __init__(self,id, supplier,crop_year,country_code,name, form,purpose,alpha,aromas,alternatives,link,notes):
        
        self.id=id
        self.supplier=supplier
        self.crop_year=crop_year
        self.country_code=country_code         
        self.name=name
        self.form=form
        self.purpose=purpose
        self.alpha=alpha
        self.aromas=aromas
        self.alternatives=alternatives
        self.link=link
        self.notes=notes

    def __repr__(self):
        return f"[{self.id}, {self.supplier}, {self.crop_year}, {self.name} , {self.form}, {self.purpose}, {self.aromas},  {self.alternatives}, {self.link}, {self.notes}] "

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_hop(hop):
    try:
        with session as sess:
            sess.add(hop)
            sess.commit()
            return 'OK'       
    except Exception as err:
        if('Duplicate entry' in str(err)):
            return f'Entrée en double: le triplet (nom : {hop.name} , supplier : {hop.supplier} , année de récolte : {hop.crop_year}) existe déjà!' 
        else:
            return str(err)

def update_hop(hop):

    #print('in update hop , hop received')
    #print(hop)
    try:
        with session as sess:
            result =(sess.query(Hop).filter(Hop.id == hop.id).first())  
            #print('hop found by index')
            #print(result)
            if(result!= None):
                result.name=hop.name
                result.supplier=hop.supplier
                result.crop_year=hop.crop_year
                result.country_code=hop.country_code
                result.form=hop.form
                result.purpose=hop.purpose
                result.alpha=hop.alpha
                result.aromas=hop.aromas
                result.alternatives=hop.alternatives
                result.link=hop.link
                result.notes=hop.notes
                #print('hop after update')
                #print(result)
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no hop   with id = {hop.id}!")   
    except Exception as err:
          return str(err)

def delete_hop(id):
    try:
        with session as sess:
            result= (sess.query(Hop).filter(Hop.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            else:
                pass
                #print(f"There is no hop with id= {id} to delete!") 
    except Exception as err:
        if('foreign key constraint fails' in str(err)):
            print(str(err))
            return ("Le houblon ne peut être supprimé car il est encore utilisé dans l'inventaire")
        #print('an exception was raised : '+str(err))
        return (str(err))     

def all_hop():
    with session as sess:
        result=(sess.query(Hop).all())      
    return result        


def find_hop_by_id(id):
    with session as sess:
        result = (sess.query(Hop).filter(Hop.id == id).first())
        return result
        
              
   
