from sqlalchemy import Column, Index, Integer, Date,String, Text,TIMESTAMP, text,CHAR,ForeignKey,Float,UniqueConstraint


from database.orm_base import Base
from database.db_connection_local  import engine,session

from database.orm_base import metadata

class Setting(Base):
    __tablename__="settings"
    
    id = Column("id",Integer, primary_key=True)
    name=Column("Name",String(25))
    val=Column('Value',String(25))

    def __init__(self,id, name,val):
        self.id=id
        self.name=name
        self.val=val

#the following will create the table if it does not exist
metadata.create_all(bind=engine)

def add_setting(setting):
    try:
        with session as sess:
            sess.add(setting)
            sess.commit()
            return 'OK'       
    except Exception as err:
       
        return str(err)

def update_setting(setting): 
    try:
        with session as sess:
            result =(sess.query(Setting).filter(Setting.id == setting.id).first())  
            if(result!= None):
                result.name= setting.name
                result.val=setting.val
                sess.add(result)
                sess.commit()
                return 'OK'
            else:
                return (f"There is no setting   with id = {setting.id}!")   
    except Exception as err:
          return "Il y a une erreur" +str(err)
    
def all_setting():
    with session as sess:
        result=(sess.query(Setting).all())      
    return result        


def find_setting_by_id(id):
    with session as sess:
        result = (sess.query(Setting).filter(Setting.id == id).first())
        return result