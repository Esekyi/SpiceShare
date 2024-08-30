from app.models.user import User
from app import db
from werkzeug.security import generate_password_hash

def get_all_users():
	return User.query.all()


def get_user_by_id(user_id):
    return User.query.get_or_404(user_id)


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


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


def update_user(user, email=None, password=None, first_name=None, last_name=None):
    if email:
        user.email = email
    if password:
        password_hash = generate_password_hash(password)
        user.password_hash = password_hash
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    db.session.commit()


def delete_user(user):
    db.session.delete(user)
    db.session.commit()
