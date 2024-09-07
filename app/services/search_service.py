from app import db
from app.models.recipe import Recipe
from app.models.category import Category
from app.models.ingredient import Ingredient
from app.models.instruction import Instruction
from app.models.user import User
from app.services.pagination_service import paginate
from sqlalchemy import or_


def search_recipes(query, page=1, per_page=10):
	"""
    Search for recipes based on a query string.
    The query can match recipe names, ingredients, author or categories.
    """
	query = f"%{query.lower()}%"


	recipes = Recipe.query.join(Ingredient).join(Category).join(User).filter(
		or_(
			Recipe.title.ilike(query),
			Recipe.description.ilike(query),
			Ingredient.name.ilike(query),
			Category.name.ilike(query),
			User.first_name.ilike(query),
			User.last_name.ilike(query),
			User.username.ilike(query)
		)
	).distinct()


	return paginate(recipes.all(), page, per_page)
