import os
from werkzeug.utils import secure_filename

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'with_this_you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = os.environ.get(
		'DATABASE_URL') or 'postgresql://spiceshare:fudf2024@localhost/spiceshare_db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	UPLOAD_FOLDER = 'app/static/uploads'
	ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
