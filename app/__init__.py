from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_login import LoginManager
from app.models.user import User
from uuid import UUID

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# initializing db extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
	app = Flask(__name__)
	app.config.from_object(Config)

	# initialize these ext
	db.init_app(app)
	migrate.init_app(app,db)
	login_manager.init_app(app)

	# register blueprint
	from app.routes import user_routes, recipe_routes, auth_routes
	app.register_blueprint(user_routes.bp)
	app.register_blueprint(recipe_routes.bp)
	app.register_blueprint(auth_routes.auth_bp)


	return app

@login_manager.user_loader
def load_user(user_id):
	try:
		user_uuid = UUID(user_id)
		return User.query.get(user_uuid)
	except ValueError:
		return None