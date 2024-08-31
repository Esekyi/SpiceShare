from flask import Blueprint, request, url_for, render_template, flash, redirect
from app import db
from app.services.recipe_service import get_all_recipes, get_recipe_by_id, create_recipe, get_most_viewed_recipes
from app.services.validation_service import validate_recipe_data
from app.services.category_service import CategoryService
from app.services.image_service import upload_image_to_s3
from flask_login import login_required, current_user
from app.models.user import User
import os

bp = Blueprint('recipe_routes', __name__)

# s3_url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3{os.getenv('AWS_REGION')}.amazonaws.com/"


@bp.route('/recipes/create', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def add_recipe():
    if request.method == 'POST':
        data = request.form.to_dict()  # ensuring form data comes as to dictionary.
        ingredients = request.form.getlist('ingredients[]')
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
                flash("Image was uploaded", "success")
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('recipe_routes.add_recipe'))


        try:
            send_url = image_url if image_url is not None else ''
            user_id = current_user.id  # Ensure user_id is set correctly
            create_recipe(data, user_id, ingredients, instructions, send_url)  # Pass user_id correctly
            flash("Recipe created successfully!", 'success')
            return redirect(url_for('recipe_routes.list_recipes'))

        except Exception as e:
            # Rollback db session in case of an error
            db.session.rollback()
            flash(
                f"An error occurred while creating the recipe: {str(e)}", "error")
            return redirect(url_for('recipe_routes.add_recipe'))


    categories = CategoryService.get_all_categories()
    return render_template('recipes/createPages/create.html', categories=categories, title='Create Recipe | SpiceShare Inc.')


@bp.route('/recipes', methods=['GET'], strict_slashes=False)
def list_recipes():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 9))
    paginated_recipes = get_all_recipes(page, per_page)

    # Fetch user details for each recipe
    for recipe in paginated_recipes['items']:
        recipe.user = db.session.query(User).filter_by(id=recipe.user_id).first()
    return render_template('recipes/readPages/allRecipes.html',
                           recipes=paginated_recipes['items'],
                           total_items=paginated_recipes['total_items'],
                           total_pages=paginated_recipes['total_pages'],
                           current_page=paginated_recipes['current_page'],
                           per_page=per_page,
                           title='Recipes | SpiceShare Inc.')


@bp.route('/recipes/<uuid:recipe_id>', methods=['GET'], strict_slashes=False)
def view_recipe(recipe_id):
    recipe = get_recipe_by_id(recipe_id)
    recipe.view_count += 1
    db.session.commit()

    return render_template('recipes/readPages/recipe_detail.html', recipe=recipe, title=f'{recipe.title} - SpiceShare Inc.')


@bp.route('/recipes/<uuid:recipe_id>/edit', methods=['PUT'], strict_slashes=False)
@login_required
def edit_recipe(recipe_id):
    pass


@bp.route('/recipes/<uuid:recipe_id>/delete', methods=['DELETE'], strict_slashes=False)
@login_required
def remove_recipe(recipe_id):
    pass

@bp.route('/most_viewed', methods=['GET'])
def most_viewed():
    recipes = get_most_viewed_recipes(limit=5) # adjust with preferred limit default 5
    return recipes
