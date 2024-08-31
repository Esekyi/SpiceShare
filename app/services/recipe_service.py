from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.comment import Comment
from app.models.instruction import Instruction
from app import db
import random

from app.services.pagination_service import paginate


def create_recipe(data, user_id, ingredients, instructions, send_url):
	"""
	Create a new recipe and save it to the database.
	
	:param data: A dictionary containing recipe data.
	:param ingredients: A list of ingredients to associate with the recipe.
    :param comments: A list of comments to associate with the recipe.
	:param user_id: The ID of the user creating the recipe.
	:return: The newly created Recipe object.
	"""
	try:
		oven_temp = int(data.get('oven_temp')) if data.get('oven_temp') else 60,
		prep_time = int(data.get('prep_time')) if data.get('prep_time') else 0
		cook_time = int(data.get('cook_time')) if data.get('cook_time') else 0
		servings = int(data.get('servings')) if data.get('servings') else 0

		new_recipe = Recipe(
			title=data['title'],
			description=data['description'],
			oven_temp=oven_temp,
			prep_time=prep_time,  # Default to 0 if not provided
			cook_time=cook_time,  # Default to 0 if not provided
			servings=servings,  # Default to 0 if not provided
			category_id=data['category_id'],
            user_id=user_id,
			image_url=send_url
		)
		db.session.add(new_recipe)
		db.session.flush()  # Flush pending transaction to get the recipe ID before committing

		# Handle ingredients
		for ingredient_name in ingredients:
			if ingredient_name:  # not tolerating any empty ingredient
				ingredient = Ingredient(
					name=ingredient_name,
					recipe_id=new_recipe.id
				)
				db.session.add(ingredient)

		# Handle each instruction
		for i, instruction in enumerate(instructions):
			if instruction:
				new_instruction = Instruction(
					step_number=i + 1,
					name=instruction,
					recipe_id=new_recipe.id
				)
				db.session.add(new_instruction)


		db.session.commit() # comit all changes to different tables
		return new_recipe

	except Exception as e:
		db.session.rollback()
		raise Exception(f"Failed to create recipe: {str(e)}")


def get_all_recipes(page=1, per_page=3):
	"""Get all recipes with pagination.

    Args:
        page (int): The current page number.
        per_page (int): The number of recipes per page.

    Returns:
        dict: A dictionary containing paginated recipes and pagination info.
    """

	recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
	return paginate(recipes, page, per_page)


def get_recipe_by_id(recipe_id):
	return Recipe.query.get_or_404(recipe_id)


def delete_recipe(recipe):
    db.session.delete(recipe)


def get_most_viewed_recipes(limit=5):
	"""
	Check through Recipe table and get the most viewed recipes - 
	sorted from descending on the view count field. limit of recipes needed
	:param int limit, 0"""
	return Recipe.query.order_by(Recipe.view_count.desc()).limit(limit).all()


def get_random_recipes_with_images(limit=3):
	recipes_with_image = Recipe.query.filter(
		Recipe.image_url != None, Recipe.image_url != '').all()
	if len(recipes_with_image) > limit:
		return random.sample(recipes_with_image, limit)
	return recipes_with_image
