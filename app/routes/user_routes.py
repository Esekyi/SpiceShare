"""User services routes"""
from flask import Blueprint, jsonify, request, flash, redirect, url_for
from app import db
from app.services.user_services import get_all_users, delete_user, get_user_by_id, update_user
from flask_login import login_required, current_user

# user routes blueprint
bp = Blueprint('user_routes', __name__)

@bp.route('/users', methods=['GET'])
def list_users():
    """get all users in db"""
    users = get_all_users()
    return jsonify([user.username for user in users])


@bp.route('/user/<uuid:user_id>', methods=["GET"])
@login_required
def get_user(user_id):
    """get a specific user by id"""
    user = get_user_by_id(str(user_id))
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('main.index'))
    return jsonify({"username": user.username, "email": user.email})


@bp.route('/user/<uuid:user_id>/edit', methods=["POST"])
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
        update_user(user, email=new_email,
                    password_hash=data.get('password_hash'))
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_routes.get_user', user_id=user_id))

    else:
        flash('You are not authorized to edit this profile.', 'danger')
        return redirect(url_for('main.index'))


@bp.route('/user/<uuid:user_id>/delete', methods=['POST'])
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
