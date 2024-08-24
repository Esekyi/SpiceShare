from app.models.user import User

def get_all_users():
	return User.query.all()

def create_user(username, email):
	user = User(username=username, email=email)
	return user
