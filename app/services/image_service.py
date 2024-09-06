import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from flask import current_app
import uuid
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # logging level to DEBUG



def upload_image_to_s3(image, folder='recipes'):
	"""Upload image to S3 bucket and retrieve the given image URL"""

	aws_access_key_id = current_app.config['S3_ACCESS_KEY_ID']
	aws_secret_access_key = current_app.config['S3_SECRET_ACCESS_KEY']
	region_name = current_app.config['S3_REGION']
	bucket_name = current_app.config['S3_BUCKET_NAME']
	try:

		# Generating a random and unique filename for image
		filename = secure_filename(image.filename)
		unique_filename = f"{uuid.uuid4().hex}.{filename.rsplit('.', 1)[1].lower()}"

		# Init the S3 client
		s3_client = boto3.client(
			's3',
			aws_access_key_id=aws_access_key_id,
			aws_secret_access_key=aws_secret_access_key,
			region_name=region_name
		)

		# Upload the file to S3
		s3_client.upload_fileobj(
			image,
			bucket_name,
			f"{folder}/{unique_filename}",
			ExtraArgs={
				"ACL": "public-read",
				"ContentType": image.content_type
			}
		)

		# Return URL of uploaded image
		# image_url = f"{current_app.config['S3_URL']}{folder}/{unique_filename}"
		return unique_filename
	

	except NoCredentialsError:
		logging.error("AWS credentials not available")
		raise ValueError("AWS credentials not available")
	except ClientError as e:
		logging.error(f"Failed to upload image: {e}")
		raise ValueError(f"Failed to upload image: {e}")
	except Exception as e:
		logging.error(f"An unexpected error occurred: {e}")
		raise ValueError(f"An unexpected error occurred: {e}")


def delete_image_from_s3(image_filename, folder='recipes'):
	"""
    Deletes an image from the S3 bucket.

    :param image_filename: The filename of the image to be deleted.
    :return: True if the file was deleted, False if the file was not found or deletion failed.
    """

	aws_access_key_id = current_app.config['S3_ACCESS_KEY_ID']
	aws_secret_access_key = current_app.config['S3_SECRET_ACCESS_KEY']
	region_name = current_app.config['S3_REGION']
	bucket_name = current_app.config['S3_BUCKET_NAME']

	try:
		s3_client = boto3(
			's3',
			aws_access_key_id=aws_access_key_id,
			aws_secret_access_key=aws_secret_access_key,
			region_name=region_name
		)


		# Delete the file from S3
		response = s3_client.delete_object(
            Bucket=bucket_name,
            Key=f"{folder}/{image_filename}"
        )

		if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 204:
			return True
		else:
			return False


	except ClientError as e:
		logging.error(f"Failed to delete image: {e}")
		return False
	except Exception as e:
		logging.error(f"An unexpected error occurred: {e}")
		return False
