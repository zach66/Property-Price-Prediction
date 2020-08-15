import traceback
from flask import render_template, request, redirect, url_for
import logging.config
from flask import Flask
import pandas as pd
import numpy as np
import pickle
from flask_sqlalchemy import SQLAlchemy
from src.create_db import House

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Test log')

# Initialize the database
db = SQLAlchemy(app)


@app.route('/')
def index():
    """Main view that lists house records in the database.
    Create view into index page that uses data queried from House database and
    inserts it into the 2020-msia423-zhu-zach-PropertyPricePrediction/templates/index.html template.
    Returns: rendered html template
    """
 
    try:
        records = db.session.query(House).all()
        logger.debug("Index page accessed")
        return render_template('index.html', records=records)
    except:
        traceback.print_exc()
        logger.warning("Not able to display records, error page returned")
        return render_template('error.html')


@app.route('/predict', methods=['POST'])
def predict_entry():
    """View that process a POST with new song input
    :return: redirect to index page
    """
    
    # Read data from form input
    try:
        bo=request.form["bo"]
        lot=request.form["lot"]
        block=request.form["block"]
        bc=request.form["bc"]
        tax=request.form["tax"]
        ru=request.form["ru"]              
        cu=request.form["cu"]               
        tu=request.form["tu"]                   
        land=request.form["land"]
        gross=request.form["gross"]
        yr=request.form["year"]

    
        # Change some variables to "1" if input is 0, since log transformation is required later
        if ru =="0":
            ru = "1"
        if cu == "0":   
            cu = "1"
        if tu == "0":  
            tu = "1"
        if land == "0": 
            land = "1"
        if gross == "0": 
            gross = "1"

        # Create test dataframe for predicting
        test = pd.DataFrame([[int(bo),int(lot),int(block),int(bc),int(tax),np.log(int(ru)),
                     np.log(int(cu)),np.log(int(tu)),np.log(float(land)),
                     np.log(float(gross)),int(yr)]],
                    columns=["BOROUGH","LOT","BLOCK","bc","TAX CLASS AT TIME OF SALE",
                             "res_unit_log","com_unit_log","tot_unit_log", "land_log", 
                             "gross_sqft_log","year"])
        
        # Load model pickle file
        try:
            file = open('data/model/model.pkl', 'rb')
            model = pickle.load(file)
            file.close()
        except:
            logger.error("Model object can't be loaded!")
        
        # Make prediciton
        prediction = float(round(np.exp(model.predict(test))[0],2))
         
        # Store user input as well as prediction into data
        record = House(BOROUGH=str(bo), BUILDING_CLASS_CATEGORY=str(bc),
                       BLOCK=int(block), LOT=int(lot),RESIDENTIAL_UNITS=int(ru),
                       COMMERCIAL_UNITS=int(cu), TOTAL_UNITS=int(tu),
                       LAND_SQUARE_FEET=float(land),GROSS_SQUARE_FEET=float(gross),
                       YEAR_BUILT=int(yr),TAX_CLASS_AT_TIME_OF_SALE=str(tax),PREDICTED_SALE_PRICE=prediction)
        
        db.session.add(record)
        db.session.commit()
        logger.info("New record added!")

        return redirect(url_for('index'))

    except:
        logger.warning("Not able to display prediction, error page returned")
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])