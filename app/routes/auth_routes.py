from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models.user import User
from app import db

"""Route for basic authentication"""

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
	"""Login authentication handler"""
	if request.method == 'POST':
		email = request.form["email"]
		password = request.form["password"]
		user = User.query.filter_by(email=email).first()

		if user and check_password_hash(user.password_hash, password):
			login_user(user)
			return redirect(url_for('main.profile'))

		flash('Invalid Credentials', 'warning')

	return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
	"""logout handler"""
	logout_user()
	return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=["GET", "POST"])
def register():
	if request.method == "POST":
		pass

	return render_template('register.html')
