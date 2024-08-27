import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from flask import current_app
import uuid
from werkzeug.utils import secure_filename


def upload_image_to_s3(image, folder='recipes'):
	"""Upload image to S3 bucket and retrieve the given image URL"""
	try:
		# Generating a random and unique filename for image
		filename = secure_filename(image.filename)
		unique_filename = f"{uuid.uuid4().hex}_{filename}"

		# Init the S3 client
		s3_client = boto3.client(
			's3',
			aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
			aws_secret_access_key=current_app.config['S3_SECRET_KEY'],
			region_name=current_app.config['S3_REGION']
		)

		# Upload the file to S3
		s3_client.upload_fileobj(
			image,
			current_app.config['S3_BUCKET'],
			f"{folder}/{unique_filename}",
			ExtraArgs={
				"ACL": "public-read",
				"ContentType": image.content_type
			}
		)

		# Return URL of uploaded image
		image_url = f"{current_app.config['S3_URL']}{folder}/{unique_filename}"
		return image_url
	

	except NoCredentialsError:
		raise ValueError("AWS credentials not available")
	except ClientError as e:
		raise ValueError(f"Failed to upload image: {e}")
