import logging 
import yaml
import pandas as pd
import numpy as np
import logging
from copy import copy

# Logging
logger = logging.getLogger('clean-data')

# Functions for clean 'SALE PRICE', 'LAND SQUARE FEET', 'GROSS SQUARE FEET' and 'YEAR BUILT'
# all return dataframe
def year_clean(df):
    if 'YEAR BUILT' not in df :
        logger.warning("YEAR BUILT not existed. Original frame returned")
        return df
    
    df['year'] = df['YEAR BUILT']
    
    #Impute median where year = 0
    year_median = df['year'][df['year'] != 0].median()
    
    #Date cannot before 1764
    df['year'] = df['year'].apply(lambda x: x if x >= 1764 else year_median)
    
    return  df

def land_clean(df):
    if 'LAND SQUARE FEET' not in df :
        logger.warning("LAND SQUARE FEET not existed. Original frame returned")
        return df
    
    #Impute mean for missing and values
    df['land'] =  pd.to_numeric(df['LAND SQUARE FEET'], errors='coerce')   
    
    #use median for 0 and nulls
    land_median = df['land'][df['land']!=0].median()
    df['land'] = df['land'].fillna(land_median)
    df['land'] = df['land'].apply(lambda x: x if x > 0 else land_median)
    
    return df

def gross_clean(df):
    if 'GROSS SQUARE FEET' not in df :
        logger.warning("GROSS SQUARE FEET not existed. Original frame returned")
        return df
    
    df['gross_sqft'] =  pd.to_numeric(df['GROSS SQUARE FEET'], errors='coerce')
    
    #use median for 0 and nulls
    gross_sqft_median = df['gross_sqft'][df['gross_sqft']!=0].median()
    df['gross_sqft'] = df['gross_sqft'].fillna(gross_sqft_median)
    df['gross_sqft'] = df['gross_sqft'].apply(lambda x: x if x > 0 else gross_sqft_median)
    
    return df

def price_clean(df):
    if 'SALE PRICE' not in df :
        logger.warning("SALE PRICE not existed. Original frame returned")
        return df

    # Some values which represent missing values: '-'
    df['price'] = pd.to_numeric(df['SALE PRICE'], errors='coerce')

    # Remove Nan values
    df = df[df['price'].isnull()==0]

    # Remove records with price = 0 
    df = df[df['price'] != 0]

    # Log transform
    df['price'] = df['price'].apply(np.log)
    
    price_avg = df['price'].mean()
    price_stdev = np.std(df['price'])

    #Remove outliers: 3 stdevs from mean
    df =  df[df['price'] >= price_avg - price_stdev * 3]
    df =  df[df['price'] <= price_avg + price_stdev * 3]

    return df

# wrapper
def clean(df, columns=None):
    """ data cleaning for columns: 'SALE PRICE', 'LAND SQUARE FEET', 'GROSS SQUARE FEET' and 'YEAR BUILT' """
    
    # Check if input is pandas dataframe
    if not isinstance(df, pd.DataFrame):
        logger.error("Parameter %s is not a DataFrame object.", df)

    # Check none input
    if df is None:
        logger.warning("Input dataframe is empty. Empty frame returned")
        return None

    if columns is None:
        logger.warning("No columns need to be cleaned. Original frame returned")
        return df

    logger.info('Cleaning the data')
    
    try:
        for col in columns:
            if col == 'SALE PRICE':
                df = price_clean(df)
            
            elif col == 'LAND SQUARE FEET':
                df = land_clean(df)

            elif col == 'GROSS SQUARE FEET':
                df = gross_clean(df)
            
            elif col == 'YEAR BUILT':
                df = year_clean(df)
            
            else:
                logger.warning('Column %s not existed to be cleaned', col)
    
    except Exception as err:
        logger.error("Error occurred while cleaning data:%s", err)

    
    logger.info("Successfully cleaned %i columns: %s", len(columns), columns)
    
    df = df.reset_index(drop=True)

    return df


