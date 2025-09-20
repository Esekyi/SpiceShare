from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from app.config import Config
from flask_login import LoginManager
from uuid import UUID
import os
from build import build_css
from flask_mail import Mail
from typing import Optional, Any, TYPE_CHECKING

# Only import User for type checking, not at runtime
if TYPE_CHECKING:
    from app.models.user import User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'You Must Login to Access This Page!'
login_manager.login_message_category = 'error'

# initializing db extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()

def create_app() -> Flask:
	# if not os.environ.get('FLASK_DEBUG'):
	# 	build_css()

	app = Flask(__name__)
	app.config.from_object(Config)
	
	# Set maximum file upload size
	app.config['MAX_CONTENT_LENGTH'] = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)

	# initialize these ext
	db.init_app(app)
	migrate.init_app(app,db)
	login_manager.init_app(app)
	csrf.init_app(app)
	mail.init_app(app)

	# register blueprint
	from app.routes import user_routes, recipe_routes, auth_routes, category_routes, main_routes,search_routes,email_routes, api
	app.register_blueprint(user_routes.bp)
	app.register_blueprint(recipe_routes.bp)
	app.register_blueprint(auth_routes.auth_bp)
	app.register_blueprint(main_routes.main)
	app.register_blueprint(search_routes.search_bp)
	app.register_blueprint(email_routes.email)
	app.register_blueprint(category_routes.cat_bp, url_prefix='/api')
	app.register_blueprint(api.api, url_prefix='/api/v1')
	
	# Exempt API routes from CSRF protection
	csrf.exempt(api.api)
	csrf.exempt(category_routes.cat_bp)

	# Register custom template filters
	register_template_filters(app)

    # Custom Error Handlers
	register_error_handlers(app)


	return app

@login_manager.user_loader
def load_user(user_id: str) -> Optional['User']:
	from app.models.user import User
	try:
		user_uuid = UUID(user_id)
		return User.query.get(user_uuid)
	except ValueError:
		return None
	

def register_error_handlers(app: Flask) -> None:
    """Registers custom error pages."""

    @app.errorhandler(404)
    def not_found_error(error: Any) -> tuple:
        return render_template('error.html', error_code=404, error_message="Page Not Found"), 404
	
    @app.errorhandler(500)
    def internal_error(error: Any) -> tuple:
        return render_template('error.html', error_code=500, error_message="Internal Server Error"), 500

    @app.errorhandler(403)
    def forbidden_error(error: Any) -> tuple:
        return render_template('error.html', error_code=403, error_message="Forbidden"), 403

    @app.errorhandler(400)
    def bad_request_error(error: Any) -> tuple:
        return render_template('error.html', error_code=400, error_message="Bad Request"), 400


def register_template_filters(app: Flask) -> None:
	"""Register custom Jinja2 template filters."""
	
	@app.template_filter('recipe_image_url')
	def recipe_image_url_filter(image_filename: str) -> str:
		"""Generate the appropriate URL for a recipe image based on upload method."""
		from app.services.image_service import get_image_url
		return get_image_url(image_filename)
