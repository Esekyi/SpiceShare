"""User services routes"""
from flask import Blueprint, jsonify, request, flash, redirect, url_for, render_template
from app import db
from app.services.user_services import get_all_users, delete_user, get_user_by_id, update_user, create_user, get_user_by_email
from flask_login import login_required, current_user

# user routes blueprint
bp = Blueprint('user_routes', __name__)

@bp.route('/users', methods=['GET'], strict_slashes=False)
def list_users():
    """get all users in db"""
    users = get_all_users()
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "name": user.first_name + ' ' + user.last_name,
            "email": user.email
        })
    return jsonify(user_list)


@bp.route('/user/<uuid:user_id>', methods=["GET"], strict_slashes=False)
@login_required
def get_user(user_id):
    """get a specific user by id"""
    user = get_user_by_id(str(user_id))
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('main.index'))
    return jsonify({"username": user.username, "email": user.email})


@bp.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    if request.method == 'POST':
        data = request.form
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not first_name or not last_name or not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('user_routes.register'))

        existing_user = get_user_by_email(email)
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('user_routes.register'))

        try:
            create_user(first_name, last_name, password, email, username)
            flash('Registration successful, proceed to login!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occured during registeration. Please try again', 'error')
            return redirect(url_for('user_routes.register'))

    return render_template('user_auth/register.html')


@bp.route('/user/<uuid:user_id>/edit', methods=["POST"], strict_slashes=False)
@login_required
def edit_user(user_id):
    """Update user details by id"""
    user = get_user_by_id(str(user_id))
    if user and user.id == current_user.id:
        data = request.form
        new_email = data.get('email')

        # run a quick db check to see if email already exist
        all_users = get_all_users()
        if any(u.email == new_email and u.id != user.id for u in all_users):
            flash('Email already in use', 'danger')
            return redirect(url_for('user_routes.get_user', user_id=user_id))

        update_user(
            user,
            email=new_email,
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )

        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_routes.get_user', user_id=user_id))

    else:
        flash('You are not authorized to edit this profile.', 'danger')
        return redirect(url_for('main.index'))


@bp.route('/user/<uuid:user_id>/delete', methods=['POST'], strict_slashes=False)
@login_required
def delete_user_profile(user_id):

    user = get_user_by_id(user_id)
    if user and user.id == current_user.id:
        delete_user(user)
        flash('Profile deleted succesfully.', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('You are not authorized to delete this profile.', 'danger')
        return redirect(url_for('main.index'))