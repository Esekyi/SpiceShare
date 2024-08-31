from flask import Blueprint, jsonify, request
from app.services.recipe_service import get_all_recipes

api = Blueprint('api', __name__)

def serialize_recipe(recipe):
    """Convert a Recipe object to a dictionary."""
    return {
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'image_url': recipe.image_url,
        'created_at': recipe.created_at.isoformat(),  # Convert datetime to string if needed
        'view_count': recipe.view_count
    }

@api.route('/recipes', methods=['GET'], strict_slashes=False)
def recipes():
	page = int(request.args.get('page', 1))
	per_page = int(request.args.get('per_page', 3))
	try:
		paginated_recipes = get_all_recipes(page, per_page)
		serialized_recipes = [serialize_recipe(recipe) for recipe in paginated_recipes['items']]
		return jsonify({
			'recipes': serialized_recipes,
			'total_items': paginated_recipes['total_items'],
			'total_pages': paginated_recipes['total_pages'],
			'current_page': paginated_recipes['current_page']
			})
	except ValueError as e:
		return jsonify({'error': str(e)}), 400

