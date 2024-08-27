from app import db
from app.models.category import Category


def get_all_categories():
	categories = Category.query.all()
	return categories
