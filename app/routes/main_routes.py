from flask import Blueprint, render_template, flash, send_from_directory, current_app, abort
import os

main = Blueprint('main_routes', __name__)


@main.route('/', methods=['GET'], strict_slashes=False)
def index():
	return render_template('index.html')


@main.route('/uploads/recipe_images/<filename>')
def uploaded_file(filename):
	"""Serve uploaded recipe images from local storage"""
	try:
		upload_method = current_app.config.get('UPLOAD_METHOD', 'local')
		
		# Only serve local files if using local upload method
		if upload_method != 'local':
			abort(404)
			
		# Security: ensure filename is safe
		if '..' in filename or filename.startswith('/'):
			abort(404)
			
		recipe_image_folder = current_app.config['RECIPE_IMAGE_FOLDER']
		
		# Check if file exists
		file_path = os.path.join(recipe_image_folder, filename)
		if not os.path.exists(file_path):
			abort(404)
			
		return send_from_directory(recipe_image_folder, filename)
		
	except Exception as e:
		current_app.logger.error(f"Error serving uploaded file {filename}: {e}")
		abort(404)