from app import db
from app.models.recipe import Recipe
from app.models.category import Category
from app.models.ingredient import Ingredient
from app.models.instruction import Instruction
from app.models.user import User


def search_recipes(query):
	"""
    Search for recipes based on a query string.
    The query can match recipe names, ingredients, author or categories.
    """
	query = f"%{query.lower()}%"

	# Search by title
	recipes_by_title = Recipe.query.filter(Recipe.title.ilike(query)).all()

	# Search by description
	recipes_by_description = Recipe.query.filter(
		Recipe.description.ilike(query)).all()

	# Search by ingredients
	recipes_by_ingredient = db.session.query(Recipe).join(
		Ingredient).filter(Ingredient.name.ilike(query)).all()

	# Search by category name
	recipes_by_category = db.session.query(Recipe).join(
		Category).filter(Category.name.ilike(query)).all()

	# Search by author (first name, last name or username)
	author_recipes = db.session.query(Recipe).join(User).filter(
		(User.first_name.ilike(query)) |
		(User.last_name.ilike(query)) |
		(User.username.ilike(query))
	).all()

	# calling a set function on it to remove duplicates
	all_recipes = set(recipes_by_title + recipes_by_category +
	                  recipes_by_description + recipes_by_ingredient + author_recipes)

	return list(all_recipes)
