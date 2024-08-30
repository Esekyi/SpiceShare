from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models.user import User
from app import db

"""Route for basic authentication"""

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
	"""Login authentication handler"""
	# Check if the user is already authenticated
	if current_user.is_authenticated:
		return redirect(url_for('user_routes.user_profile', user_id=current_user.id))

	if request.method == 'POST':
		email = request.form["email"]
		password = request.form["password"]
		user = User.query.filter_by(email=email).first()

		if user and check_password_hash(user.password_hash, password):
			login_user(user)
			next_page = request.args.get('next')
			if next_page:
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

