# MSiA 423 Project: House Sale Price Prediction 
- **Author: Zach Zhu**    
- **QA: Joe Zhang**

- [Charter](#Charter)
- [Backlog](#Backlog)
## Directory structure 

```
├── README.md                         <- You are here
├── app
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app   
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│   ├── config_s3.env                 <- Configurations for S3
│   ├── config_db.env                 <- Configurations for database
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── model/                        <- Model pipeline output
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a  stakeholder 
│
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── develop/                      <- Current notebooks being used in development.
setup. 
│
│
├── src/                              <- Source data for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts for model pipeline
├── requirements.txt                  <- Python package dependencies 
├── test.py                           <- Python scripts to run unit tests
├── run-unit-tests.sh                 <- Bash scripts to run unit tests 
├── run-pipeline.sh                   <- Bash scripts to run model pipeline
├── Dockerfile_bash                   <- Dockerfile for building image to run model pipeline and unit tests 
├── Dockerfile                        <- Dockerfile for building image to load data to S3 and create RDS

```


# 1. Run the model pipeline 

## 1. Configuration 

**insturctors and TA have been added to the S3 policy**
**Only set your AWS Key credential to get access to my S3 bucket**

```bash
cd 2020-msia423-zhu-zach-PropertyPricePrediction    
export AWS_ACCESS_KEY_ID=<your AWS access key>
export AWS_SECRET_ACCESS_KEY=<AWS secret access key>
```

## 2. Build the image 

```bash
 docker build -f Dockerfile_bash -t house .
```

## 3. Execute the pipeline 

Note: we only mount the data folder here because if we were to mount the current directory, the container would access our local version of `run-pipeline.sh`, which on Windows computers, will not be formatted correctly. Also, it would require `chmod +x run-pipeline.sh` to be run locally. 

```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(pwd)/data",target=/app/data/ house run-pipeline.sh
```

# 2. Run unit tests for all functions

## Build the image 

if you have already built the image in the [Run the model pipeline], you can skip this step, we use the same imgae `house`

```bash
 docker build -f Dockerfile_bash -t house .
```

## Execute to run tests

```bash
docker run --mount type=bind,source="$(pwd)/data",target=/app/data/ house run-unit-tests.sh
``` 


# 3. Run the Flask app 

## 1. Configure database

The app will query from dabase, whether local or RDS 

**If you use local sqlite**: Set `SQLALCHEMY_DATABASE_URI` to your local sqlite string, default is `sqlite:///data/house_sale.db`

```bash
cd 2020-msia423-zhu-zach-PropertyPricePrediction 
export SQLALCHEMY_DATABASE_URI=sqlite:///data/house_sale.db
```


**If you use RDS**: Set `SQLALCHEMY_DATABASE_URI` to be the format '{dialect}://{user}:{pw}@{host}:{port}/{db}' and **VERIFY THAT YOU ARE ON THE NORTHWESTERN VPN BEFORE YOU CONTINUE ON**

```bash
cd 2020-msia423-zhu-zach-PropertyPricePrediction 
export SQLALCHEMY_DATABASE_URI='{dialect}://{user}:{pw}@{host}:{port}/{db}'
```
* Set `user` to the "master username" that you used to create the database server
* Set `MYSQL_PASSWORD` to the "master password" that you used to create the database server
* Set `host` to be the RDS instance endpoint from the console
* Set `port` to be `3306` or other port
* Set `db` your database name

## 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
PORT = 1996  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile 
APP_NAME = "house-price"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

## 3. Build the image 

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f app/Dockerfile -t houseapp .
```

This command builds the Docker image, with the tag `houseapp`, based on the instructions in `app/Dockerfile` and the files existing in this directory.
 
## 4. Run the container 

To run the app, run from this directory: 

```bash
docker run -t -i -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(pwd)"/data,target=/app/data -p 1996:1996 --name myapp houseapp
```
You should now be able to access the app at http://0.0.0.0:1996/ in your browser.

This command runs the `houseapp` image as a container named `myapp` and forwards the port 1996 from container to your laptop so that you can access the flask app exposed through that port. 

If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 1996` line in `app/Dockerfile`)

## 5. Kill the container 

Once finished with the app, you will need to kill the container. To do so, you could either enter `Ctrl C`, or:

```bash
docker kill myapp
```

where `myapp` is the name given in the `docker run` command.




# Mid-project Pull Request (PR) and checkpoint

## 1.Data Ingestion

### Get data from kaggle
The dataset can be downloaded from [Kaggle](https://www.kaggle.com/new-york-city/nyc-property-sales).
The dataset is a csv file around 13MB curretntly stored in 2020-msia423-zhu-zach-PropertyPricePrediction/data/external/nyc-rolling-sales.csv. You can choose to change the directory and the file name as you want.


### S3 set-up
#### Configuration and environment variables
Edit your config file accordingly
```bash
cd 2020-msia423-zhu-zach-PropertyPricePrediction    
vi config/config_s3.env
```
* Set `S3_BUCKET_NAME` to the S3 bucket name that you created in AWS.
* Set `RAW_DATA_FILENAME` to the name of the downloaded file from Kaggle. 
* Set `RAW_DATA_PATH` to the local directory you store your data.
* Set `ACCESS_KEY` to your AWS access key. 
* Set `SECRET_KEY` to your AWS secret access key.

#### Build the docker image
Return to the root directory
```bash
docker build -f Dockerfile -t db .
```

#### Store data into S3
Run from the command line
```bash
docker run --env-file=config/config_s3.env db src/data_to_s3.py
```


### Connecting AWS RDS from your computer 

_Note: You will need to be on the Northwestern VPN._

Edit your mysql config file accordingly 

```bash
vi .mysqlconfig
```

* Set `MYSQL_USER` to the "master username" that you used to create the database server
* Set `MYSQL_PASSWORD` to the "master password" that you used to create the database server
* Set `MYSQL_HOST` to be the RDS instance endpoint from the console
* Set `MYSQL_PORT` to be `3306`
* Set `DATABASE_NAME` your database name
 

Set the environment variables in your `~/.bashrc`

```bash
echo 'source .mysqlconfig' >> ~/.bashrc
source ~/.bashrc
```

**VERIFY THAT YOU ARE ON THE NORTHWESTERN VPN BEFORE YOU CONTINUE ON**

Use the MySQL Docker image to start a MySQL client and connect to your database. (More information on the MySQL Docker image can be found [here](https://hub.docker.com/_/mysql))

```bash
docker run 
-it # `docker run` option - interactive session, attach to the container after it starts \
--rm # `docker run` option - remove the container after it exits \
mysql:latest # Docker image and version \
mysql # command we are passing to entrypoint of container \
-h${MYSQL_HOST} # host used by command `mysql` \
-u${MYSQL_USER} # username used by command `mysql` \
-p${MYSQL_PASSWORD}  # password used by command `mysql` 
```

You can run the Docker container by using the `run_mysql_client.sh` script.

```bash
sh run_mysql_client.sh
```

Submit SQL commands!

![](figures/term_1.png)


#### Query data
* For instructor, use `MYSQL_USER=msia423instructor` and `MYSQL_PASSWORD=zzm7646` to query the table. 
* For QA, you use `MYSQL_USER=msia423qa` and `MYSQL_PASSWORD=zzm7646` to query the table. 


###2.Database set-up

Build the provided Docker image (if you have already built the imaage in the [S3 set-up](#S3), you can skip this step )

```bash
docker build -f Dockerfile -t db .
```


#### If you want to create a local SQLite database

```bash
vi config/config_db.env
```
* set `SQLALCHEMY_DATABASE_URI` to `sqlite:///data/house_sale.db`

Run it!
```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data --env-file config/config_db.env db src/create_db.py
```
![](figures/term_2.png)


#### Create tables in AWS RDS
**VERIFY THAT YOU ARE ON THE NORTHWESTERN VPN BEFORE YOU CONTINUE ON**

Edit your mysql config file accordingly
```bash
vi config/config_db.env
```

* Set `MYSQL_USER` to the "master username" that you used to create the database server
* Set `MYSQL_PASSWORD` to the "master password" that you used to create the database server
* Set `MYSQL_HOST` to be the RDS instance endpoint from the console
* Set `MYSQL_PORT` to be `3306`
* Set `DATABASE_NAME` your database name

Run it!
```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data --env-file config/config_db.env db src/create_db.py 
```

![](figures/term_3.png)

You can use the MySQL client again to see that a table has been added and data generated.

```bash
sh run_mysql_client.sh
```

![](figures/term_4.png)





## Project Repo
<!-- toc -->

- [Directory structure](#directory-structure)
- [Running the app](#running-the-app)
  * [1. Initialize the database](#1-initialize-the-database)
    + [Create the database with a single song](#create-the-database-with-a-single-song)
    + [Adding additional songs](#adding-additional-songs)
    + [Defining your engine string](#defining-your-engine-string)
      - [Local SQLite database](#local-sqlite-database)
  * [2. Configure Flask app](#2-configure-flask-app)
  * [3. Run the Flask app](#3-run-the-flask-app)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Build the image](#1-build-the-image)
  * [2. Run the container](#2-run-the-container)
  * [3. Kill the container](#3-kill-the-container)

<!-- tocstop -->

## Charter
### Vision
After six years of robust house price growth, the U.S. housing market is cooling. Despite this, 19 of the 20 major U.S. cities continued to experience moderate house price hikes, according to Standard and Poor’s in 2019. Demand remains strong, and for investors, real estate continues to be recognized as a great long-term **investment** option. To most new grads, purchasing a property would be a very first tough investment decision to make. However, as **sale price** being the most crucial factor to be considered in investment, there are barely no handy tools for individual investors to perform prediction on property sale value. By leveraging machine learning techniques to **predict reasonable/value-based price of a property**, this project aims to deliver a easy-to-use tool that empower investment firms and individual investors to make the best decisions. 

### Mission
The tool will be designed as a user-friendly web-based application where users will be prompted to provide property information with a regression model to output the forecasted property price and important property features. The model will be trained on history sales data that contains every building or building unit (apartment, etc.) sold in the New York City property market over a 12-month period from September 2016 to September 2017. The dataset is obtained from [Kaggle](https://www.kaggle.com/new-york-city/nyc-property-sales). 
> - *Due to inflation and market volatility, the dataset need to be updated according to time for future use*
> - *App users may need extra explanations and assistance as there are multiple features of a property may not be well-defined and easy to obtain from the market.*

The application intends to provide additional information for investors to consider, should not be used as a robust investment strategy, and the prediction may not be accurate enough to reflect the real sale of the market.

### Success Criteria

- **Machine Learning Criteria:** 
The R square(**R^2**) will be deployed to select the best regression model, and the best model should yield a R^2 greater than **0.5**.

- **Business Success Criteria:**
 The deliverables will be considered successful from a business standpoint if more than **20%** of the customers return to pay for the application after first month trial and the average monthly rating from customers is greater than **4.2 on a 5.0 scale**. In the long-run, the success will be deemed as the application does help investors choose better properties to invest and optimize the value based house pricing. 
 
## Backlog

**Initiative 1:**  Model Development

-   Epic 1: Data cleaning and exploratory data analysis
    -   Story 1: Explore variables
    -   Story 2: Identify outliers and missing values
    -   Story 3: Analyze relationships between variables
    -   Story 4: Data transformation and feature engineering
    -   Story 5: Output dataframe for modelling        
-   Epic 2: Model building
    -   Story 1: Split train-test datasets
    -   Story 2: Select best model based on MSE metric
    -   Story 3: Feature importance
    -   Story 4: Improve model to get potential lift in prediction

    
**Initiative 2:**  Application development

-   Epic 1:  Create **S3**  bucket to store raw source data
-   Epic 2:  Construct relational database
-   Epic 3:  Develop Web App (Flask) backend
     -  Story 1: Construct Docker 
    -   Story 2: Integrate app with supervised model
-   Epic 4:  Develop Web App (Flask) frontend
    -   Story 1: Create landing and result page 
    -   Story 2: Design interactive survey
    -   Story 3: Design web style and layout
-   Epic 5: Test and optimization
    -   Story 1: Test and fix bugs
    -   Story 2: Launch application


### Backlog

**Size of story**.
-   The magnitude of work planned. 
    -   0 points - quick chore
    -   1 point ~ 1 hour (small)
    -   2 points ~ 1/2 day (medium)
    -   4 points ~ 1 day (large)
    -   8 points - big and needs to be broken down more when it comes to execution (okay as placeholder for future work though)
    

### Backlog

- Initiative1.epic1.story1 (2 of story points) - PLANNED  
- Initiative1.epic1.story2 (1 of story points) - PLANNED  
- Initiative1.epic1.story3 (0 of story points) - PLANNED  
- Initiative1.epic1.story4 (1 of story points) - PLANNED
- Initiative1.epic1.story5 (0 of story points) - PLANNED
- Initiative1.epic2.story1 (0 of story points) - PLANNED  
- Initiative1.epic2.story2 (4 of story points) - PLANNED  
- Initiative1.epic2.story3 (0 of story points) - PLANNED
- Initiative1.epic2.story4 (2 of story points) - PLANNED

### Icebox

-   Initiative1.Epic2.Story4
-   Initiative1.Epic3.Story1
-   Initiative1.Epic3.Story2

-   Initiative2.Epic1
-   Initiative2.Epic2
-   Initiative2.Epic3.Story1
-   Initiative2.Epic3.Story2
-   Initiative2.Epic4.Story1
-   Initiative2.Epic4.Story2
-   Initiative2.Epic4.Story3
-   Initiative2.Epic5.Story1
