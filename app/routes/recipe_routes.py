from flask import Blueprint, request, url_for, render_template, jsonify, flash, redirect
from app import db
from app.services.recipe_service import get_all_recipes, get_recipe_by_id, create_recipe
from app.services.validation_service import validate_recipe_data
from app.services.category_sevice import get_all_categories
from app.services.image_service import upload_image_to_s3
from flask_login import login_required, current_user

bp = Blueprint('recipe_routes', __name__)


@bp.route('/recipes/create', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def add_recipe():
    if request.method == 'POST':
        data = request.form.to_dict()  # ensuring form data comes as to dictionary.
        ingredients = request.form.getlist('ingredients[]')
        comments = request.form.getlist('comments[]')
        instructions = request.form.getlist('instructions[]')
        image = request.files.get('image')

        errors = validate_recipe_data(data)
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('recipe_routes.add_recipe'))        


        image_url = None
        if image:
            try:
                image_url = upload_image_to_s3(image)
            except ValueError as e:
                flash(str(e), 'danger')
                return redirect(url_for('recipe_routes.add_recipe'))


        try:
            send_url = image_url if image_url is not None else ''
            create_recipe(data, comments, ingredients, instructions, send_url, user_id=current_user.id)
            flash("Recipe created successfully!", 'success')
            return redirect(url_for('recipe_routes.list_recipes'))

        except Exception as e:
            # Rollback db session in case of an error
            db.session.rollback()
            flash(
                f"An error occurred while creating the recipe: {str(e)}", "error")
            return redirect(url_for('recipe_routes.add_recipe'))


    categories = get_all_categories()
    return render_template('recipes/create.html', categories=categories)


@bp.route('/recipes', methods=['GET'], strict_slashes=False)
def list_recipes():
    recipes = get_all_recipes()
    return render_template('recipes/list.html', recipes=recipes)


@bp.route('/recipes/<uuid:recipe_id>', methods=['GET'], strict_slashes=False)
def view_recipe(recipe_id):
    pass


@bp.route('/recipes/<uuid:recipe_id>/edit', methods=['PUT'], strict_slashes=False)
@login_required
def edit_recipe(recipe_id):
    pass


@bp.route('/recipes/<uuid:recipe_id>/delete', methods=['DELETE'], strict_slashes=False)
@login_required
def remove_recipe(recipe_id):
    pass
