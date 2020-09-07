import boto3
import os
import logging.config

# Logging
logging_config = "config/logging/local.conf"
logging.config.fileConfig(logging_config)
logger = logging.getLogger('upload_to_S3')


if __name__ == "__main__":
	
	try:
		session = boto3.Session(
	    aws_access_key_id=os.environ.get("ACCESS_KEY"),
	    aws_secret_access_key=os.environ.get("SECRET_KEY"),)

		s3 = session.resource("s3")
		bucket = s3.Bucket(os.environ.get("S3_BUCKET_NAME"))

		#upload file to s3 
		bucket.upload_file(os.environ.get("RAW_DATA_PATH"), os.environ.get("S3_DATA_PATH"))
		logger.info("Successfully upload data to S3 bucket")

	except Exception as err:
		logger.error("Error occurred while uploading file to S3 bucket")