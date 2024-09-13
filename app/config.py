import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import timedelta


# loading environment variables from .env file
load_dotenv()

class Config:
	SECRET_KEY = os.getenv('SECRET_KEY') or 'with_this_you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = os.getenv(
		'DATABASE_URL') or 'postgresql://spiceshare:fudf2024@localhost/spiceshare_db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SECURE = True
	REMEMBER_COOKIE_DURATION = timedelta(days=14)


    # AWS S3 configuration
	S3_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
	S3_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
	S3_REGION = os.getenv('AWS_REGION')
	S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
	S3_URL = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/"


	# Flask-mail
	MAIL_SERVER = os.getenv('MAIL_SERVER')
	MAIL_PORT = os.getenv('MAIL_PORT')
	MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
	MAIL_USE_SSL =  os.getenv('MAIL_USE_SSL')
	MAIL_USERNAME = os.getenv('MAIL_USERNAME')
	MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
	MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')