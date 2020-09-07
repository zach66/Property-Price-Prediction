import os
import logging.config
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import Column, Integer, String, MetaData, Float
import argparse

# Logging
logging_config = 'config/logging/local.conf'
logging.config.fileConfig(logging_config)
logger = logging.getLogger('create_db')

Base = declarative_base()  

class House(Base):
    """Create a data model for the user input and model output """
    __tablename__ = 'House_Info'
    id = Column(Integer, primary_key=True, nullable=True)
    BOROUGH = Column(String(100), unique=False, nullable=True)
    BUILDING_CLASS_CATEGORY = Column(String(100), unique=False, nullable=True)
    BLOCK = Column(Integer, unique=False, nullable=True)
    LOT = Column(Integer, unique=False, nullable=True)
    RESIDENTIAL_UNITS = Column(Integer, unique=False, nullable=True)                
    COMMERCIAL_UNITS = Column(Integer, unique=False, nullable=True)                  
    TOTAL_UNITS = Column(Integer, unique=False, nullable=True)                       
    LAND_SQUARE_FEET = Column(Float, unique=False, nullable=True)
    GROSS_SQUARE_FEET = Column(Float, unique=False, nullable=True)
    YEAR_BUILT = Column(Integer, unique=False, nullable=True)
    TAX_CLASS_AT_TIME_OF_SALE = Column(String(100), unique=False, nullable=True)
    PREDICTED_SALE_PRICE = Column(Float, unique=False, nullable=True) 
    
    def __repr__(self):
        return '<House {}>'.format(self.id)

def create_db(engine_string): 
    '''Creates database
    Args: 
        engine_string (string): engine string 
    Returns:
        none
    '''
    try: 
        engine = sql.create_engine(engine_string)
        Base.metadata.create_all(engine)
        logger.info("Database created successfully")
    except: 
        logger.error("Database not successfully created")

    
        
if __name__ == "__main__":

    conn_type = "mysql+pymysql"
    user = os.environ.get("MYSQL_USER")
    password = os.environ.get("MYSQL_PASSWORD")
    host = os.environ.get("MYSQL_HOST")
    port = os.environ.get("MYSQL_PORT")
    database = os.environ.get("MYSQL_DATABASE")
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

    if SQLALCHEMY_DATABASE_URI is not None:
        engine_string = SQLALCHEMY_DATABASE_URI
    
    elif host is None:
        engine_string = 'sqlite:///data/house_sale.db'
    
    else:
        #AWS RDS
        engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)
      
    create_db(engine_string)