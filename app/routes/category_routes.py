from flask import Blueprint, request, url_for, render_template, jsonify, flash, redirect
from app.services.category_service import CategoryService

cat_bp = Blueprint('category_routes', __name__)


@cat_bp.route('/categories', methods=['POST'], strict_slashes=False)
def create_category():
	data = request.json
	name = data.get('name')
	description = data.get('description')

	if not name:
		return jsonify({'error': 'Category name is required'}), 400

	try:
		new_category = CategoryService.create_category(name, description)
		return jsonify({
			'message': 'Category created successfully',
			'category': {
				'id': new_category.id,
				'name': new_category.name,
				'description': new_category.description
			}
		}), 201
	except ValueError as e:
		return jsonify({'error': str(e)}), 400
