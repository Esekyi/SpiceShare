from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.comment import Comment
from app.models.instruction import Instruction
from app import db


def create_recipe(data, user_id, ingredients, comments, instructions, send_url):
	"""
	Create a new recipe and save it to the database.
	
	:param data: A dictionary containing recipe data.
	:param ingredients: A list of ingredients to associate with the recipe.
    :param comments: A list of comments to associate with the recipe.
	:param user_id: The ID of the user creating the recipe.
	:return: The newly created Recipe object.
	"""
	try:
		new_recipe = Recipe(
			title=data['title'],
			description=data['description'],
			instructions=data['instructions'],
			prep_time=int(data.get('prep_time', 0)),  # Default to 0 if not provided
			cook_time=int(data.get('cook_time', 0)),  # Default to 0 if not provided
			servings=int(data.get('servings', 0)),  # Default to 0 if not provided
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

		# Handle comments
		for comment_text in comments:
			if comment_text: # not tolerating empty comments
				comment = Comment(
					text=comment_text,
					user_id=user_id,
					recipe_id=new_recipe.id
				)
				db.session.add(comment)

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


def get_all_recipes():
    return Recipe.query.all()


def get_recipe_by_id(recipe_id):
	return Recipe.query.get(recipe_id)


def delete_recipe(recipe):
    db.session.delete(recipe)
