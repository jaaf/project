from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import sessionmaker, scoped_session
from database.orm_base import Base
from cryptography.fernet import Fernet
from PyQt6.QtWidgets import QMessageBox
#from os import path
from pathlib import Path

import sys
from getpass import getpass
from shutil import which
import logging
import logging.handlers as handlers

import sqlite3
from pathlib import Path

#THIS IS PARSED BEFORE main.py
#Creating a logger
home_path=Path.home()
logger = logging.getLogger("ROOT")
if sys.platform.startswith('linux'):
    p=home_path/".biere"
else:
    p=home_path/"AppData/Local/.biere"
p.mkdir(mode=0o777,parents=True,exist_ok=True)

filename=(p/"bière.log").resolve()

logging.basicConfig( filemode='a', level=logging.DEBUG,
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s",
    datefmt="le %d %m %Y à %H:%M:%S",
)
formatter = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s",
    datefmt="le %d %m %Y à %H:%M:%S")

logHandler = handlers.RotatingFileHandler(filename, maxBytes=5000, backupCount=2)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

print("Home dir is "+str(home_path.resolve()))


if sys.platform.startswith('linux'):
    p=home_path/".biere"/"cred"
    p.mkdir(mode=0o777,parents=True,exist_ok=True)
    path_to_cred=(home_path/".biere"/"cred").resolve() #a string
else:
    p=home_path/"AppData/Local/.biere/cred"
    p.mkdir(mode=0o777,parents=True,exist_ok=True)
    path_to_cred=Path(p.resolve())

try:
    with open(path_to_cred/'key.bin','rb') as fileObj : 
        for line in fileObj:
            key=line
        fileObj.close() 
except Exception:
    #we could not get a key , create a new one and save it          
    key=Fernet.generate_key()
    with open(path_to_cred/'key.bin','wb') as fileObj: 
        fileObj.write(key)
        fileObj.close()

choice=''
try: #check is a db choice has already been done

    with open(path_to_cred/'db-choice.txt','r') as fileObj:
        for line in fileObj:
            choice=line
        fileObj.close()
        print("Le choix de la base de données a déjà été fait. il s'agit de  "+choice)
except Exception as e:
    choice=input("""
    Bienvenue dans Bière.\n
    Vous avez le choix entre une base de données mysql ou sqlite. Indiquez votre choix en tapant mysql ou sqlite\n """) 
    while choice != "mysql" and choice != 'sqlite':
        choice=input("Vous avez saisi "+str(choice)+" .Ce doit être mysq ou sqlite. Veuillez saisir votre choix à nouveau.\n")
    with open(path_to_cred/'db-choice.txt','w') as fileObj:
            fileObj.write(choice)
            fileObj.close()    
            
logger.info("Application démarée")

if choice =='mysql':
    logger.info("L'application utilise une base de données "+choice)
    try:
        #try to retrieve database name
        with open(path_to_cred/'dbname.bin','rb') as fileObj:
            for line in fileObj:
                encrypted_dbname=line
            fileObj.close()
        dbname=Fernet(key).decrypt(encrypted_dbname).decode('utf-8')  

    except Exception as e:
        #we could not retrieve the dbname
        dbname=getpass("Merci de saisir le nom de la base de données\n")
        encrypted_dbname=Fernet(key).encrypt(dbname.encode('utf-8'))
        with open(path_to_cred/'dbname.bin','wb') as fileObj:
            fileObj.write(encrypted_dbname)
        fileObj.close()  


    try:
        #try to retrieve a previously saved password
        with open(path_to_cred/'password.bin','rb') as fileObj:
            for line in fileObj:
                encrypted_password=line
            fileObj.close()
        
        password=Fernet(key).decrypt(encrypted_password).decode('utf-8')
        #print(password)
    except Exception as e:
        #we could not retrieve a password create one and save it
        password=getpass("Merci de saisir le mot de passe de l’utilisateur biere@localhost \n")
        encrypted_password=Fernet(key).encrypt(password.encode('utf-8'))
        with open(path_to_cred/'password.bin','wb') as fileObj:
            fileObj.write(encrypted_password)
        fileObj.close()
    #check mysql server is installed

    cmd = "mysql"
    if not which(cmd) :
        
        print("Vous n’avez pas installé de serveur mysql. L’application ne peut fonctionner sans ce serveur. Merci de l’installer avant de continuer")
    while not which(cmd):
        pass
    

    db_url="mysql+pymysql://biere:"+password+"@localhost:3306/"+dbname
    #db_url="sqlite:////home/jaaf/db1"
    try:
        if not database_exists(db_url):
            create_database(db_url)
    except Exception as e:
        end=False
        #try a new password until success
        
        while end==False:
            #print("Le nom de la base de donnée "+dbname+" ou le mot de passe est erroné. ")
            dbname=getpass("""
Bière n’a pu se connecter à la basse de données\n. 
Il peut y avoir plusieurs raisons à cela : base de données non créée, utilisateur biere@localhost non créé, mot de passe erroné.\n
Corrigez cela et réessayez sion vous allez boucler sur ces demandes. Merci de saisir à nouveau le nom de la base de donnée\n""")
            encrypted_dbname=Fernet(key).encrypt(dbname.encode('utf-8'))
            with open(path_to_cred/'dbname.bin','wb') as fileObj:
                fileObj.write(encrypted_dbname)
            fileObj.close()
            password=getpass("Merci de saisir le mot de passe de l’utilisateur biere@localhost de la base de données\n")
            encrypted_password=Fernet(key).encrypt(password.encode('utf-8'))
            with open(path_to_cred/'password.bin','wb') as fileObj:
                fileObj.write(encrypted_password)
            fileObj.close() 
            
            db_url="mysql+pymysql://biere:"+password+"@localhost:3306/"+dbname
            try:
                if not database_exists(db_url):
                    create_database(db_url)  
                end=True 
            except:
                print('Connexion au serveur de base de données refusée. Vérifiez le mot de passe et le nom de la base!')  
    print ("Vous travaillez avec une base de données mysql dont le nom est "+dbname)
    
if choice =='sqlite':
    logger.info("L'application utilise une base de données "+choice)
    print('le choix est '+choice)
    try:
    #try to retrieve database name
        with open(path_to_cred/'dbname.bin','rb') as fileObj:
            for line in fileObj:
                encrypted_dbname=line
            fileObj.close()
        dbname=Fernet(key).decrypt(encrypted_dbname).decode('utf-8')  

    except Exception as e:
        #we could not retrieve the dbname
        dbname=input("Merci de saisir le nom de la base de données\n")
        encrypted_dbname=Fernet(key).encrypt(dbname.encode('utf-8'))
        with open(path_to_cred/'dbname.bin','wb') as fileObj:
            fileObj.write(encrypted_dbname)
        fileObj.close()  

    if sys.platform.startswith("linux"):   
        db_url="sqlite:///"+str(home_path/".biere"/dbname)
    else:
        db_url="sqlite:///"+str(home_path/"AppData/Local/.biere"/dbname)
        
        
    print ("Vous travaillez avec une base de données sqlite dont le nom est "+dbname)



engine = create_engine(db_url)#,pool_size=5,pool_recycle=3600)
Session =sessionmaker(bind=engine,expire_on_commit=False)
session =Session()


