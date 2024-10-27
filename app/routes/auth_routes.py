from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models.user import User
from app.services.recaptcha_service import verify_recaptcha

"""Route for basic authentication"""

auth_bp = Blueprint('auth', __name__)


def is_safe_url(target):
	"""Check if the target URL is safe for redirection."""
	from urllib.parse import urlparse, urljoin
	# Allow relative URLs
	if target.startswith('/'):
		return True
	safe = urlparse(target).scheme in ['http', 'https'] and \
	       urljoin(request.host_url, target) == target
	return safe

@auth_bp.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
	"""Login authentication handler"""


	# Check if the user is already authenticated
	if current_user.is_authenticated:
		return redirect(url_for('user_routes.user_profile', user_id=current_user.id))

	if request.method == 'POST':
		email = request.form.get("email").strip().lower()
		password = request.form["password"]
		next_page = request.form.get("next")
		remember_me = request.form.get('remember_me')

		recaptcha_response = request.form.get('g-recaptcha-response')
		if not recaptcha_response or not verify_recaptcha(recaptcha_response):
			flash("CAPTCHA verification failed. Please try again.", "error")
			return redirect(url_for('auth.login'))

		# Convert checkbox to boolean
		remember = True if remember_me == "on" else False

		user = User.query.filter_by(email=email).first()

		if user and check_password_hash(user.password_hash, password):
			login_user(user, remember=remember)

			if next_page and is_safe_url(next_page):
				return redirect(next_page)
			else:
				flash('logged in', 'success')
				return redirect(url_for('main.index'))

		flash('Invalid Credentials', 'warning')

	return render_template('user_auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
	"""logout handler"""
	logout_user()
	flash("You've been logged out succesfully!",'success')
	return redirect(url_for('auth.login'))

