from sqlalchemy import Column, Index, Integer, String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session
from database.orm_base import metadata

class Style(Base):
    __tablename__="styles"
    
    id = Column("id",Integer, primary_key=True)
    name= Column('name',String(50),unique=True)
    family=Column('family',String(50))
    og_min=Column('og_min',Float)
    fg_min=Column('fg_min',Float)
    abv_min=Column('abv_min',Float)
    ibu_min=Column('ibu_min',Float)
    bu_vs_gu_min=Column('bu_vs_gu_min',Float)
    srm_min=Column('srm_min',Float)
    app_att_min=Column('app_att_min',Float)
    co2_min=Column('co2_min',Float)
    og_max=Column('og_max',Float)
    fg_max=Column('fg_max',Float)
    abv_max=Column('abv_max',Float)
    ibu_max=Column('ibu_max',Float)
    bu_vs_gu_max=Column('bu_vs_gu_max',Float)
    srm_max=Column('srm_max',Float)
    app_att_max=Column('app_att_max',Float)
    co2_max=Column('co2_max',Float)


                     
    
    def __init__(self,id, name,family,og_min,fg_min,abv_min,ibu_min,bu_vs_gu_min,srm_min,app_att_min,co2_min,og_max,fg_max,abv_max,ibu_max,bu_vs_gu_max,srm_max,app_att_max,co2_max):
        self.id=id
        self.name= name
        self.family=family
        self.og_min=og_min
        self.fg_min=fg_min
        self.abv_min=abv_min
        self.ibu_min=ibu_min
        self.bu_vs_gu_min=bu_vs_gu_min
        self.srm_min=srm_min
        self.app_att_min=app_att_min
        self.co2_min=co2_min
        self.og_max=og_max
        self.fg_max=fg_max
        self.abv_max=abv_max
        self.ibu_max=ibu_max
        self.bu_vs_gu_max=bu_vs_gu_max
        self.srm_max=srm_max
        self.app_att_max=app_att_max
        self.co2_max=co2_max
        

    def __repr__(self):
        return f"{self.id}, {self.name} , {self.family}"

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_style(style):
    try:
        with session as sess:
            sess.add(style)
            sess.commit()
            return 'OK'       
    except Exception as err:
        return str(err)

def update_style(style):

    #print('in update style , style received')
    #print(style)
    try:
        with session as sess:
            result =(sess.query(Style).filter(Style.id == style.id).first())  
            #print('style found by index')
            #print(result)
            if(result!= None):
                result.name= style.name
                result.family=style.family
                result.og_min=style.og_min
                result.fg_min=style.fg_min
                result.abv_min=style.abv_min
                result.ibu_min=style.ibu_min
                result.bu_vs_gu_min=style.bu_vs_gu_min
                result.srm_min=style.srm_min
                result.app_att_min=style.app_att_min
                result.co2_min=style.co2_min
                result.og_max=style.og_max
                result.fg_max=style.fg_max
                result.abv_max=style.abv_max
                result.ibu_max=style.ibu_max
                result.bu_vs_gu_max=style.bu_vs_gu_max
                result.srm_max=style.srm_max
                result.app_att_max=style.app_att_max
                result.co2_max=style.co2_max
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no style   with id = {style.id}!")   
    except Exception as err:
          return str(err)

def delete_style(id):
    try:
        with session as sess:
            result= (sess.query(Style).filter(Style.id == id).first())
            if(result != None):
                sess.delete(result) 
                sess.commit()  
                return 'OK'    
            
    except Exception as err:
        
        return (str(err))     

def all_style():
    with session as sess:
        result=(sess.query(Style).all())      
    return result        


def find_style_by_id(id):
    with session as sess:
        result = (sess.query(Style).filter(Style.id == id).first())
        return result

def find_style_by_name(name):
    with session as sess:
        result= (sess.query(Style).filter(Style.name == name).first())   
        return result
   
