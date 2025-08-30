import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from flask import current_app, url_for
import uuid
import os
from werkzeug.utils import secure_filename
from PIL import Image
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
		s3_client = boto3.client(
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


# ===============================
# LOCAL IMAGE UPLOAD FUNCTIONS
# ===============================

def allowed_file(filename):
	"""Check if the uploaded file has an allowed extension"""
	allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def upload_image_locally(image, folder='recipe_images'):
	"""
	Upload image to local filesystem
	
	:param image: FileStorage object from request.files
	:param folder: Subfolder within uploads directory
	:return: Unique filename of uploaded image
	"""
	try:
		# Validate file
		if not image or not image.filename:
			raise ValueError("No image file provided")
		
		if not allowed_file(image.filename):
			raise ValueError("File type not allowed. Please upload PNG, JPG, JPEG, GIF, or WebP images.")
		
		# Generate unique filename
		filename = secure_filename(image.filename)
		file_extension = filename.rsplit('.', 1)[1].lower()
		unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
		
		# Create upload directory if it doesn't exist
		upload_path = current_app.config['RECIPE_IMAGE_FOLDER']
		os.makedirs(upload_path, exist_ok=True)
		
		# Full file path
		file_path = os.path.join(upload_path, unique_filename)
		
		# Save the original image
		image.save(file_path)
		
		# Optimize image (resize if too large, compress)
		optimize_image(file_path)
		
		logging.info(f"Image uploaded locally: {unique_filename}")
		return unique_filename
		
	except Exception as e:
		logging.error(f"Failed to upload image locally: {e}")
		raise ValueError(f"Failed to upload image: {e}")


def optimize_image(file_path, max_width=1200, max_height=800, quality=85):
	"""
	Optimize uploaded image by resizing and compressing
	
	:param file_path: Path to the image file
	:param max_width: Maximum width in pixels
	:param max_height: Maximum height in pixels
	:param quality: JPEG quality (1-100)
	"""
	try:
		with Image.open(file_path) as img:
			# Convert RGBA to RGB if necessary (for JPEG compatibility)
			if img.mode in ('RGBA', 'LA', 'P'):
				img = img.convert('RGB')
			
			# Calculate new dimensions while maintaining aspect ratio
			width, height = img.size
			if width > max_width or height > max_height:
				ratio = min(max_width / width, max_height / height)
				new_width = int(width * ratio)
				new_height = int(height * ratio)
				img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
			
			# Save optimized image
			img.save(file_path, optimize=True, quality=quality)
			
		logging.debug(f"Image optimized: {file_path}")
	except Exception as e:
		logging.error(f"Failed to optimize image {file_path}: {e}")
		# Don't raise error - optimization is not critical


def delete_image_locally(image_filename, folder='recipe_images'):
	"""
	Delete image from local filesystem
	
	:param image_filename: Name of the image file to delete
	:param folder: Subfolder within uploads directory
	:return: True if deleted successfully, False otherwise
	"""
	try:
		upload_path = current_app.config['RECIPE_IMAGE_FOLDER']
		file_path = os.path.join(upload_path, image_filename)
		
		if os.path.exists(file_path):
			os.remove(file_path)
			logging.info(f"Image deleted locally: {image_filename}")
			return True
		else:
			logging.warning(f"Image not found for deletion: {image_filename}")
			return False
		
	except Exception as e:
		logging.error(f"Failed to delete image locally: {e}")
		return False


# ===============================
# UNIFIED IMAGE UPLOAD FUNCTIONS
# ===============================

def upload_image(image, folder='recipes'):
	"""
	Unified image upload function that uses either local or S3 storage
	based on the UPLOAD_METHOD configuration
	
	:param image: FileStorage object from request.files
	:param folder: Folder name for organization (used differently for local vs S3)
	:return: Unique filename of uploaded image
	"""
	upload_method = current_app.config.get('UPLOAD_METHOD', 'local')
	
	if upload_method == 's3':
		return upload_image_to_s3(image, folder)
	else:
		return upload_image_locally(image, 'recipe_images')


def delete_image(image_filename, folder='recipes'):
	"""
	Unified image deletion function that uses either local or S3 storage
	based on the UPLOAD_METHOD configuration
	
	:param image_filename: Name of the image file to delete
	:param folder: Folder name for organization
	:return: True if deleted successfully, False otherwise
	"""
	upload_method = current_app.config.get('UPLOAD_METHOD', 'local')
	
	if upload_method == 's3':
		return delete_image_from_s3(image_filename, folder)
	else:
		return delete_image_locally(image_filename, 'recipe_images')


def get_image_url(image_filename):
	"""
	Generate the appropriate URL for an image based on upload method
	
	:param image_filename: Name of the image file
	:return: Full URL to access the image
	"""
	if not image_filename:
		return None
		
	upload_method = current_app.config.get('UPLOAD_METHOD', 'local')
	
	if upload_method == 's3':
		# S3 URL format
		bucket_name = current_app.config['S3_BUCKET_NAME']
		region = current_app.config['S3_REGION']
		return f"https://{bucket_name}.s3.{region}.amazonaws.com/recipes/{image_filename}"
	else:
		# Local URL format - will be served by Flask route
		return url_for('main_routes.uploaded_file', filename=image_filename)
