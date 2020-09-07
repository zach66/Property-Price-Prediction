import logging 
import yaml
import pandas as pd
import numpy as np
import logging
from copy import copy


# Logging
logger = logging.getLogger('generate-feature')

#Function for selecting categories
def AssignCat(col, num_cats=5):
    """ train model return model object and print model R square
    Args:s
        col: dataframe column
        num_cats: redunce number of categories in that column/variable to this number
    Returns:
        col['new'].values:  new column with values of only 5 (default) classes (pandas series)
    """

    if len(col.value_counts().keys()) < num_cats:
        num_cats = len(col.value_counts().keys())
    
    if num_cats <= 1:
        logger.warning("num_cats must be greater than 2. Origianl column returned")
        return col.values

    cats =  pd.DataFrame(col.value_counts().nlargest(num_cats - 1))
    cats['row_num'] = [str(x+1) for x in range(len(cats))]
    cats['name'] = cats.index.values
    col = pd.DataFrame({'val': col.values})
    col = pd.merge(col, cats, how='left', left_on='val', right_on='name')
    col['new'] = col['row_num'].fillna(str(num_cats))
    
    return col['new'].values


# Functions for generating new features all return pandas.core.series.Series
def building_class(df):
    if 'BUILDING CLASS CATEGORY' not in df :
        logger.warning("New feature can't be generated. Empty frame returned")
        return None
    
    # reduce to 5 categories
    df['bc'] = AssignCat(df['BUILDING CLASS CATEGORY'])
    return  df['bc'] 

def residential(df):
    if 'RESIDENTIAL UNITS' not in df :
        logger.warning("New feature can't be generated. Empty frame returned")
        return None
    
    # log transform
    df['res_unit_log'] = df['RESIDENTIAL UNITS'].apply(lambda x: 0 if x == 0 else np.log(x))
    return df['res_unit_log'] 

def commercial(df):
    if 'COMMERCIAL UNITS' not in df :
        logger.warning("New feature can't be generated. Empty frame returned")
        return None
    
    # log transform
    df['com_unit_log'] = df['COMMERCIAL UNITS'].apply(lambda x: 0 if x == 0 else np.log(x)) 
    return df['com_unit_log']

def total(df):
    if 'TOTAL UNITS' not in df :
        logger.warning("New feature can't be generated. Empty frame returned")
        return None
    
    # log transform
    df['tot_unit_log'] = df['TOTAL UNITS'].apply(lambda x: 0 if x == 0 else np.log(x))
    return df['tot_unit_log']

def land(df):
    if 'land' not in df :
        logger.warning("New feature can't be generated. Empty frame returned")
        return None
    
    # log transform
    df['land_log'] = np.log(df['land'])
    return df['land_log']

def gross(df):
    if 'gross_sqft' not in df :
        logger.warning("New feature can't be generated. Empty frame returned")
        return None
    
    # log transform
    df['gross_sqft_log'] = np.log(df['gross_sqft'])
    return df['gross_sqft_log']
 
# wrapper 
def featurize(df, features=None):
    """ train model return model object and print model R square
    Args:s
        df: cleaned dataframe
        features: new features
    Returns:
        df_for_model:  datafram with additional features for modelling
    """

    # Check if input is pandas dataframe
    if not isinstance(df, pd.DataFrame):
        logger.error("Parameter %s is not a DataFrame object.", df)
    
    # Check none input df
    if df is None:
        logger.warning("Input dataframe is empty. Empty frame returned")
        return None

    # Check none input features
    if features is None:
        logger.warning("No new feature need generated. Original frame returned")
        return df

    logger.info('Create/transform new feature: %s', features)
    
    data = copy(df)

    new_features=[]
    try:
        for col in features:
            if col == 'bc':
                new_features.append(building_class(df))
            
            elif col == 'res_unit_log':
                new_features.append(residential(df))
            
            elif col == 'com_unit_log':
                new_features.append(commercial(df))
            
            elif col == 'tot_unit_log':
               new_features.append(total(df))
            
            elif col == 'land_log':
                new_features.append(land(df))
            
            elif col == 'gross_sqft_log':
                new_features.append(gross(df))
            
            else:
                logger.error('New feature %s can not be generated', col)

    except Exception as err:
        logger.error("Error occurred while generating/transforming new features:%s", err)
  
    
    logger.info("Successfully created %i new features: %s", len(features), features)
    
    # Combine new features with original cleaned dataframe
    df_new_feature = pd.concat(new_features,axis=1)
    df_for_model = pd.concat([data,df_new_feature],axis=1).reset_index(drop=True)

    return df_for_model
