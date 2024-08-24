from app.models.user import User
from app import db

def get_all_users():
	return User.query.all()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def create_user(username, email, password_hash):
	new_user = User(username=username, email=email, password_hash=password_hash)
	return new_user


def update_user(user, email=None, password_hash=None):
    if email:
        user.email = email
    if password_hash:
        user.password_hash = password_hash
    db.session.commit()


def delete_user(user):
    db.session.delete(user)
    db.session.commit()
