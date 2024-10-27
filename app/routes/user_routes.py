"""User services routes"""
from flask import Blueprint, jsonify, request, flash, redirect, url_for, render_template
from app import db
from app.services.user_services import get_all_users, delete_user, get_user_by_id, update_user_details, create_user, get_user_by_email, get_user_by_username, is_valid_username
from app.services.recipe_service import get_recipes_by_user
from app.services.recaptcha_service import verify_recaptcha
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
from app.services.email_service import send_custom_email

# user routes blueprint
bp = Blueprint('user_routes', __name__)

@bp.route('/users', methods=['GET'], strict_slashes=False)
@login_required
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


@bp.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():

    if request.method == 'POST':

        data = request.form
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email').strip().lower()
        password = data.get('password')
        confirm_password = request.form.get('confirm_password')
        recaptcha_response = request.form.get('g-recaptcha-response')

        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            flash("CAPTCHA verification failed. Please try again.", "error")
            return redirect(url_for('user_routes.register'))

        if not first_name or not last_name or not username or not email or not password or not confirm_password:
            flash('All fields are required', 'error')
            return redirect(url_for('user_routes.register'))

        existing_user = get_user_by_email(email)
        existing_username = get_user_by_username(username)
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('user_routes.register'))

        if existing_username:
            flash("Username already exists.", 'error')
            return redirect(url_for('user_routes.register'))

        if not is_valid_username(username):
            flash(
                'Username should be at least 6 characters long must contain only letters, numbers, and underscores, with no spaces.', 
                'error')
            return redirect(url_for('user_routes.register'))

        try:
            if password == confirm_password:
                new_user = create_user(first_name, last_name, username, email, password)

                send_custom_email(
                    subject="Welcome to SpiceShare!",
                    recipients=[new_user.email],
                    template_name='email/welcome_email.html',
                    context={'first_name': new_user.first_name}
                )
                flash('Registration successful, proceed to login!', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('Password and confirm password do not match', 'error')

        except Exception as e:
            db.session.rollback()
            flash(f'An error occured during registeration. Please try again', 'error')
            return redirect(url_for('user_routes.register'))

    if current_user.is_authenticated:
        return redirect(url_for('user_routes.user_profile', user_id=current_user.id))
    return render_template('user_auth/register.html')


@bp.route('/user/<uuid:user_id>/edit', methods=["POST"], strict_slashes=False)
@login_required
def edit_user(user_id):
    """Update user details by id (only handles POST requests)"""
    user = get_user_by_id(str(user_id))

    if current_user.id != user.id:
        flash('You are not authorized to edit this profile', 'error')
        return redirect(url_for('user_routes.user_profile', user_id=current_user.id))

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

    if check_password_hash(user.password_hash, old_password):
        if new_password == confirm_password:
            update_user_details(user.id, first_name, last_name, new_password)
            flash('Profile updated successfully', 'success')
        else:
            flash('New Password and confirm password do not match', 'error')
    else:
        flash('Old password is incorrect', 'error')

    return redirect(url_for('user_routes.user_profile', user_id=user_id))





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
    

@bp.route('/user/<uuid:user_id>/profile', methods=['GET'], strict_slashes=False)
@login_required
def user_profile(user_id):
    user = get_user_by_id(user_id)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 9))

    if user != current_user:
        flash("You are not authorized to view page", 'danger')
        return redirect(url_for('index'))
    
    paginated_user_recipes = get_recipes_by_user(user.id, page, per_page)
    return render_template('user_auth/user_profile.html', recipes=paginated_user_recipes['items'], user=user, total_items=paginated_user_recipes['total_items'],
                           total_pages=paginated_user_recipes['total_pages'],
                           current_page=paginated_user_recipes['current_page'],
                           per_page=per_page
                           )
