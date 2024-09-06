from app.models.user import User
from app import db
from werkzeug.security import generate_password_hash
def get_all_users():
	return User.query.all()


def get_user_by_id(user_id):
    return User.query.get_or_404(user_id)


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def create_user(first_name, last_name, username, email, password):
    password_hash = generate_password_hash(password)
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password_hash=password_hash
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user


def update_user_details(user_id, first_name, last_name, new_password=None):
    """Update user's profile information."""
    user = get_user_by_id(user_id)
    if user:
        user.first_name = first_name
        user.last_name = last_name
        if new_password:
            user.password_hash = generate_password_hash(new_password)
        db.session.commit()
    return user


def delete_user(user):
    db.session.delete(user)
    db.session.commit()

def is_valid_username(username):
    """Check if the username is valid: no spaces, only _, can include numbers, and must be at least 6 characters long."""
    return len(username) >= 6 and (username.isalnum() or '_' in username)
