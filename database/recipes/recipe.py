from sqlalchemy import Column, Index, Integer, String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata
import jsonpickle

class Recipe(Base):
    __tablename__="recipes"
    
    id = Column("id",Integer, primary_key=True)
    name= Column('name',String(50))
    author=Column('author',String(50))
    rtype=Column('rtype',String(25))
    style=Column('style',String(50))
    bitterness=Column('bitterness',Float)
    og=Column('og',Float)
    abv=Column('abv',Float)
    color=Column('color',Float)
    boil_time=Column('boil_time',Float)
    fermentables=Column('fermentables',Text)
    hops=Column('hops',Text)
    yeasts=Column('yeasts',Text)
    miscs=Column('miscs',Text)
    rests=Column('rests',Text)

  

    __table_args__=(UniqueConstraint('name', 'author',name='_name_author_uc'),)

                     
    
    def __init__(self,id, name,author,rtype,style,bitterness,og,abv,color,boil_time,fermentables,hops,yeasts,miscs,rests):
        self.id=id
        self.name= name
        self.author=author
        self.rtype=rtype
        self.style=style
        self.bitterness=bitterness
        self.og=og
        self.abv=abv
        self.color=color
        self.boil_time=boil_time
        self.fermentables=fermentables
        self.hops=hops
        self.yeasts=yeasts
        self.miscs=miscs
        self.rests=rests
        

    def __repr__(self):
        return f"{self.id}, {self.name} , {self.author} ,\n FERMENTABLES {self.fermentables}"

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_recipe(recipe):
    try:
        with session as sess:
            sess.add(recipe)
            sess.commit()
            return 'OK'       
    except Exception as err:
        return str(err)

def update_recipe(recipe):
    try:
        with session as sess:
            result =(sess.query(Recipe).filter(Recipe.id == recipe.id).first())  
            if(result!= None):
                result.name= recipe.name
                result.author=recipe.author
                result.rtype=recipe.rtype
                result.style=recipe.style
                result.bitterness=recipe.bitterness
                result.og=recipe.og
                result.abv=recipe.abv
                result.color=recipe.color
                result.boil_time=recipe.boil_time
                result.fermentables=recipe.fermentables
                result.hops=recipe.hops
                result.yeasts=recipe.yeasts
                result.miscs=recipe.miscs
                result.rests=recipe.rests
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no recipe   with id = {recipe.id}!")   
    except Exception as err:
          return str(err)

def delete_recipe(id):
    try:
        with session as sess:
            result= (sess.query(Recipe).filter(Recipe.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            else:
                pass
                #print(f"There is no recipe with id= {id} to delete!") 
    except Exception as err:
        
        return (str(err))     

def all_recipe():
    with session as sess:
        result=(sess.query(Recipe).all())      
    return result        


def find_recipe_by_id(id):
    with session as sess:
        result = (sess.query(Recipe).filter(Recipe.id == id).first())
        return result

def find_recipe_by_name(name):
    with session as sess:
        result = (sess.query(Recipe).filter(Recipe.name == name).first())
        return result
