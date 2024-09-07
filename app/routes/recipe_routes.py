from flask import Blueprint, request, url_for, render_template, flash, redirect
from app import db
from app.services.recipe_service import get_all_recipes, get_recipe_by_id, create_recipe, get_most_viewed_recipes, update_recipe, delete_recipe, get_recipe_with_details
from app.services.validation_service import validate_recipe_data
from app.services.category_service import CategoryService
from app.services.image_service import upload_image_to_s3, delete_image_from_s3
from app.services.comment_service import CommentService
from flask_login import login_required, current_user
from app.models.user import User
from app.models.category import Category
from app.models.comment import Comment
import os

bp = Blueprint('recipe_routes', __name__)


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
            flash(f"An error occurred while creating the recipe: {str(e)}", "error")
            # If recipe creation fails, delete the uploaded image if it was uploaded
            if image_url:
                delete_image_from_s3(image_url)  # delete the image if it was uploaded
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


@bp.route('/recipes/<uuid:recipe_id>', methods=['GET', 'POST'], strict_slashes=False)
def view_recipe(recipe_id):
    recipe, ingredients, instructions = get_recipe_with_details(recipe_id)
    comments = CommentService.get_comment_by_recipe(recipe_id)  # Fetch comments for the recipe

    # Fetch user details for each comment
    for comment in comments:
        comment.user = db.session.query(User).filter_by(id=comment.user_id).first()  # Get the user who made the comment

    if recipe:
        recipe.view_count += 1
        db.session.commit()
        recipe.user = db.session.query(User).filter_by(id=recipe.user_id).first()
        return render_template('recipes/readPages/recipe_detail.html', recipe=recipe, ingredients=ingredients, instructions=instructions, comments=comments, title=f'{recipe.title} - SpiceShare Inc.')
    else:
        flash("Recipe not found.", "error")
        return redirect(url_for('recipe_routes.list_recipes'))


@bp.route('/recipes/<uuid:recipe_id>/edit', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_recipe(recipe_id):
    recipe, ingredients, instructions = get_recipe_with_details(recipe_id)

    if request.method == 'POST':
        if recipe and recipe.user_id == current_user.id:
            data = request.form.to_dict()  # Ensure this is a dictionary

            form_ingredients = request.form.getlist('ingredients[]')
            form_instructions = request.form.getlist('instructions[]')
            image = request.files.get('image')

            # If they are strings instead of lists
            if isinstance(ingredients, str):
                ingredients = [ingredients]
            if isinstance(instructions, str):
                instructions = [instructions]


            errors = validate_recipe_data(data)
            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('recipe_routes.edit_recipe', recipe_id=recipe_id))

            image_url = recipe.image_url
            if image:
                try:
                    image_url = upload_image_to_s3(image)
                    flash("Image updated successfully", "success")
                except ValueError as e:
                    flash(str(e), 'error')
                    return redirect(url_for('recipe_routes.edit_recipe', recipe_id=recipe_id))

            try:
                update_recipe(recipe, data, form_ingredients, form_instructions, image_url)  # Ensure data is a dict
                flash(f"Recipe {recipe.title} updated successfully!", 'success')
                return redirect(url_for('recipe_routes.view_recipe', recipe_id=recipe_id))

            except Exception as e:
                # Rollback db session in case of an error
                db.session.rollback()
                flash(f"An error occurred while updating the recipe: {str(e)}", "error")
                # delete the image if it was uploaded
                if image_url:
                    delete_image_from_s3(image_url)
                return redirect(url_for('recipe_routes.edit_recipe', recipe_id=recipe_id))

    categories = CategoryService.get_all_categories()
    current_category = db.session.query(
        Category).filter_by(id=recipe.category_id).first()
    return render_template('recipes/createPages/edit.html', recipe=recipe, ingredients=ingredients, current_category=current_category, instructions=instructions, categories=categories, title=f'Edit Recipe {recipe.title} | SpiceShare Inc.')


@bp.route('/recipes/<uuid:recipe_id>/delete', methods=['POST'], strict_slashes=False)
@login_required
def remove_recipe(recipe_id):
    recipe = get_recipe_by_id(recipe_id)

    if recipe and recipe.user_id == current_user.id:
        try:
            if recipe.image_url:
                if delete_image_from_s3(recipe.image_url):
                    flash("Image deleted", 'success')
                else:
                    flash("Failed to delet Image", 'info')

            delete_recipe(recipe)
            flash("Recipe deleted successfully!", 'info')
            return redirect(url_for('recipe_routes.recipe_list'))

        except Exception as e:
            flash(
                f"An error occured while deleting the recipe: {str(e)}", "error")
    else:

        flash("Unauthorized action.", 'error')
        return redirect(url_for('recipe_routes.list_recipes'))


@bp.route('/most_viewed', methods=['GET'], strict_slashes=False)
def most_viewed():
    recipes = get_most_viewed_recipes(limit=5) # adjust with preferred limit default 5
    return recipes


@bp.route('/recipes/<uuid:recipe_id>/comments', methods=['POST'])
@login_required
def add_comment(recipe_id):
    text = request.form.get('text')
    if text:
        comment = CommentService.add_comment(recipe_id, current_user.id, text)
        flash("Comment added successfully!", "success")
    else:
        flash("Comment cannot be empty.", "info")
    return redirect(url_for('recipe_routes.view_recipe', recipe_id=recipe_id))


@bp.route('/comments/<uuid:comment_id>/update', methods=['POST'])
@login_required
def update_comment(comment_id):
    text = request.form.get('text')
    comment = CommentService.update_comment(
        comment_id, current_user.id, text)  # Pass current_user.id
    if comment:
        flash("Comment updated successfully!", "success")
    else:
        flash("Comment not found or you are not authorized to update it.", "error")
    return redirect(url_for('recipe_routes.view_recipe', recipe_id=comment.recipe_id))


@bp.route('/comments/<uuid:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    # Pass current_user.id
    comment = Comment.query.get_or_404(comment_id)
    if CommentService.delete_comment(comment_id, current_user.id):
        flash("Comment deleted successfully!", "info")
    else:
        flash("Comment not found or you are not authorized to delete it.", "error")
    return redirect(url_for('recipe_routes.view_recipe', recipe_id=comment.recipe_id))
