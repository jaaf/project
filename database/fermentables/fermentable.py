from sqlalchemy import Column, Index, Integer, String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata

class Fermentable(Base):
    __tablename__="fermentables"
    
    id = Column("id",Integer, primary_key=True)
    brand= Column('brand',String(50))
    name= Column('name',String(50))
    form = Column('form',String(25))
    category =Column('category',String(50))
    color =Column('color',Float)
    potential = Column('potential',Float)
    raw_ingredient=Column('raw_ingredient',String(30))
    version=Column('version',String(10))
    link=Column('link',String(255))
    notes=Column('notes', Text)
    

    __table_args__=(UniqueConstraint('name', 'brand','version', name='_name_brand_version_uc'),
                     )

                     
    
    def __init__(self,id, brand,name, form,category,color,potential,raw_ingredient, version, link,notes):
        self.id=id
        self.brand=brand
        self.name=name
        self.form=form
        self.category=category
        self.color=color
        self.potential=potential
        self.raw_ingredient=raw_ingredient
        self.version=version
        self.link=link
        self.notes=notes

    def __repr__(self):
        return f"[{self.id}, {self.name} ,{self.brand},{self.version}, {self.form}, {self.category}, {self.color},  {self.potential}, {self.raw_ingredient}, {self.link}] "

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_fermentable(fermentable):
    try:
        with session as sess:
            sess.add(fermentable)
            sess.commit()
            return 'OK'       
    except Exception as err:
        if('Duplicate entry' in str(err)):
            return f'Entrée en double: le triplet (nom : {fermentable.name} , marque : {fermentable.brand} , version : {fermentable.version}) existe déjà!' 
        else:
            return str(err)

def update_fermentable(fermentable):
    try:
        with session as sess:
            result =(sess.query(Fermentable).filter(Fermentable.id == fermentable.id).first())  
            if(result!= None):
                result.name=fermentable.name
                result.brand=fermentable.brand
                result.version=fermentable.version
                result.form=fermentable.form
                result.category=fermentable.category
                result.color=fermentable.color
                result.potential=fermentable.potential
                result.raw_ingredient=fermentable.raw_ingredient
                result.link=fermentable.link
                result.notes=fermentable.notes
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no fermentable   with id = {fermentable.id}!")   
    except Exception as err:
          return str(err)

def delete_fermentable(id):
    try:
        with session as sess:
            result= (sess.query(Fermentable).filter(Fermentable.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            else:
                pass
                #print(f"There is no fermentable with id= {id} to delete!") 
    except Exception as err:
        if('foreign key constraint fails' in str(err)):
            print(str(err))
            return ('The fermentable could not be deleted because it is used in inventory')
            #print('an exception was raised : '+str(err))
        return (str(err))     

def all_fermentable():
    with session as sess:
        result=(sess.query(Fermentable).all())      
    return result        


def find_fermentable_by_id(id):
    with session as sess:
        result = (sess.query(Fermentable).filter(Fermentable.id == id).first())
        return result
        
'''              
def find_fermentable(brand,form):
    with session as sess:
        if(brand !='' and form!=''):
            result=(sess.query(Fermentable).filter(Fermentable.brand ==brand, Fermentable.form==form).all())
        if (brand !='' and form ==''): 
            result=(sess.query(Fermentable).filter(Fermentable.brand ==brand).all())
    return result      
'''
@staticmethod
def are_equal(f1,f2):
    if f1.name!=f2.name:
        return False
    if f1.version!=f2.version:
        return False
    if f1.form!=f2.form:
        return False
    if f1.category!=f2.category:
        return False
    if f1.color!=f2.color:
        return False
    if f1.potential!=f2.potential:
        return False
    if f1.raw_ingredient!=f2.raw_ingredient:
        return False
    if f1.link!=f2.link:
        return False
    if f1.notes!=f2.notes:
        return False
    return True                                   

