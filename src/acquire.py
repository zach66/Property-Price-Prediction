import boto3
import os
import logging
import pandas as pd
import logging


# Logging
logger = logging.getLogger('acquire-from-S3')

def acquire(S3_BUCKET_NAME=None, S3_DATA_PATH=None, DOWNLOAD_FILE_PATH=None):
    """Acquire raw data 

    Args:
        S3_BUCKET_NAME: the S3 bucket name that you created in AWS.
        LOCAL_file_PATH: the name of the downloaded file from S3.
        S3_DATA_PATH: the S3 directory you store your data.
        ACCESS_KEY: your AWS access key.
        SECRET_KEY: your AWS secret access key.

    Returns:
        df: raw data (pandas dataframe)
    """
    logger.info('Acquiring data from %s', S3_BUCKET_NAME)

    try:
        # Create a new s3 session
        session = boto3.Session(aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), 
                                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

        s3 = session.resource("s3")
        bucket = s3.Bucket(S3_BUCKET_NAME)

        # Download file to s3 
        bucket.download_file(S3_DATA_PATH, DOWNLOAD_FILE_PATH)
        logger.info("Successfully download data from S3 bucket")
    
    except Exception as err:
        logger.error("Error occurred while downloading file from S3 bucket: %s", err)
  
    df = pd.read_csv(DOWNLOAD_FILE_PATH)
    df = df.iloc[:, ~ df.columns.str.contains('^Unnamed')]

    return df