import logging 
import yaml
import pandas as pd
import numpy as np
import logging

# For modeling
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

# Logging
logger = logging.getLogger('train-model')

methods = dict(rf=RandomForestRegressor)

def train(df, target_column="price", initial_features=None, method='rf', test_size=0.3, random_state_split=66, **kwargs):
    """ train model return model object and print model R square
    Args:
        df: dataframe including additional features
        target_column: target column name (dependent variable)
        initial_features: features for training model
        method: Type of model to train ('logistic')
        test_size: Test set size for training model
        random_state: Seed for spliting train and test 
         **kwargs: Keyword arguments for sklearn.ensemble.RandomForestRegressor. Please see sklearn documentation
            for all possible options:
            https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
    
    Returns:
        model: model object 
        df_metric: metric saved in a dataframe
    """
    
    # Check if input is pandas dataframe
    if df is None:
        logger.warning("Input dataframe is empty. Empty frame returned")
        return None, None

    if initial_features is None:
        logger.warning("No features to train the model. Empty frame returned")
        return None, None

    if not isinstance(df, pd.DataFrame):
        logger.error("Parameter %s is not a DataFrame object.", df)


    logger.info('Training a %s model', method) 
    
    # Generate features
    X = df[initial_features]
    Y = df[target_column]
    
    try: 
        # Split data into test and train
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_size, random_state=random_state_split)

         # Instantiate model
        model = methods[method](**kwargs)

        # Train the model on training data
        model.fit(X_train, Y_train)

    except Exception as err:
        logger.error("Error occurred while training the model: %s", err)

    # Use the forest's predict method on the test data
    y_hat = model.predict(X_test)

    df_metric = pd.DataFrame(data={'R square': [r2_score(Y_test, y_hat)]})
  
    return model, df_metric
