from flask import Blueprint, request, url_for, render_template, flash, redirect, jsonify
from app import db
from app.services.recipe_service import get_all_recipes, get_recipe_by_id, create_recipe, get_most_viewed_recipes, update_recipe, delete_recipe, get_recipe_with_details, get_quick_and_easy_recipe
from app.services.validation_service import validate_recipe_data
from app.services.category_service import CategoryService
from app.services.image_service import upload_image, delete_image, get_image_url
from app.services.comment_service import CommentService
from app.services.nutrition_service import NutritionService
from flask_login import login_required, current_user
from app.models.user import User
from app.models.category import Category
from app.models.comment import Comment
from app.models.newsletter import Subscriber
from app.services.email_service import send_newsletter_email
import os
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('recipe_routes', __name__)


@bp.route('/recipes/create', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def add_recipe():
    if request.method == 'POST':
        data = request.form.to_dict()  # ensuring form data comes as to dictionary.
        
        # Parse ingredients with quantities and units
        ingredient_names = request.form.getlist('ingredients[]')
        ingredient_quantities = request.form.getlist('ingredient_quantities[]')
        ingredient_units = request.form.getlist('ingredient_units[]')
        
        # Combine ingredient data
        ingredients = []
        for i, name in enumerate(ingredient_names):
            if name.strip():  # Only add non-empty ingredients
                quantity = ingredient_quantities[i] if i < len(ingredient_quantities) else None
                unit = ingredient_units[i] if i < len(ingredient_units) else None
                ingredients.append({
                    'name': name.strip(),
                    'quantity': float(quantity) if quantity and quantity.strip() else None,
                    'unit': unit.strip() if unit and unit.strip() else None
                })
        
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
                image_url = upload_image(image)
                flash("Image was uploaded", "success")
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('recipe_routes.add_recipe'))


        try:
            send_url = image_url if image_url is not None else ''
            user_id = current_user.id
            new_recipe = create_recipe(data, user_id, ingredients, instructions, send_url)

            # Auto-calculate nutrition for new recipe
            try:
                logger.info(f"Calculating nutrition for new recipe: {new_recipe.id}")
                nutrition_info = NutritionService.calculate_and_store_nutrition(new_recipe)
                if nutrition_info:
                    flash("Recipe created with nutrition information!", 'success')
                else:
                    flash("Recipe created successfully! Nutrition calculation will be available shortly.", 'info')
            except Exception as nutrition_error:
                logger.error(f"Nutrition calculation failed for recipe {new_recipe.id}: {nutrition_error}")
                flash("Recipe created successfully! Nutrition calculation failed but can be recalculated later.", 'warning')

            # domain = request.host_url
            # recipe_link = url_for('recipe_routes.view_recipe', recipe_id=new_recipe.id, _external=True)

            # subscribers = Subscriber.query.filter_by(is_active=True).all()
            # for subscriber in subscribers:
            #     unsubscribe_link = f'{domain}/unsubscribe?email={subscriber.email}'
            #     try:
            #         send_newsletter_email(user=subscriber, recipe=new_recipe, recipe_link=recipe_link, unsubscribe_link=unsubscribe_link)
            #     except Exception as e:
            #         flash(f"Something occured on our side: {str(e)}", "error")

            flash("Recipe created successfully!", 'success')
            return redirect(url_for('recipe_routes.view_recipe', recipe_id=new_recipe.id))

        except Exception as e:
            # Rollback db session in case of an error
            db.session.rollback()
            flash(f"An error occurred while creating the recipe: {str(e)}", "error")
            # If recipe creation fails, delete the uploaded image if it was uploaded
            if image_url:
                delete_image(image_url)  # delete the image if it was uploaded
            return redirect(url_for('recipe_routes.add_recipe'))


    categories = CategoryService.get_all_categories()
    return render_template('recipes/createPages/create.html', categories=categories, title='Create Recipe | SpiceShare Inc.')


@bp.route('/recipes', methods=['GET'], strict_slashes=False)
def list_recipes():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 9))
    paginated_recipes = get_all_recipes(page, per_page)
    most_viewed_recipes = get_most_viewed_recipes(limit=3)
    quick_recipes = get_quick_and_easy_recipe(limit=3)

    # Fetch user details for each recipe
    for recipe in paginated_recipes['items']:
        recipe.user = db.session.query(User).filter_by(id=recipe.user_id).first()
    return render_template('recipes/readPages/allRecipes.html',
                           recipes=paginated_recipes['items'],
                           total_items=paginated_recipes['total_items'],
                           total_pages=paginated_recipes['total_pages'],
                           current_page=paginated_recipes['current_page'],
                           per_page=per_page,
                           most_viewed=most_viewed_recipes,
                           quick_recipes=quick_recipes,
                           title='Recipes | SpiceShare Inc.')


@bp.route('/recipes/<uuid:recipe_id>', methods=['GET', 'POST'], strict_slashes=False)
def view_recipe(recipe_id):
    recipe, ingredients, instructions = get_recipe_with_details(recipe_id)
    comments = CommentService.get_comment_by_recipe(recipe_id)  # Fetch comments for the recipe

    # Fetch user details for each comment
    for comment in comments:
        comment.user = db.session.query(User).filter_by(id=comment.user_id).first()  # Get the user who made the comment

    if recipe:
        if current_user.is_authenticated:
            if current_user.id != recipe.user_id:
                recipe.increment_view_count()  # Increment view count if the viewer is not the author
        else:
            # If anonymous, increment view count
            recipe.increment_view_count()
        recipe.user = db.session.query(User).filter_by(id=recipe.user_id).first()

        # Get or calculate nutrition information
        nutrition_info = None
        nutrition_summary = None
        try:
            nutrition_info = NutritionService.get_or_calculate_nutrition(recipe_id)
            if nutrition_info:
                nutrition_summary = NutritionService.get_nutrition_summary(recipe_id)
        except Exception as e:
            logger.error(f"Error getting nutrition info for recipe {recipe_id}: {e}")

        return render_template('recipes/readPages/recipe_detail.html', 
                             recipe=recipe, 
                             ingredients=ingredients, 
                             instructions=instructions, 
                             comments=comments,
                             nutrition_info=nutrition_info,
                             nutrition_summary=nutrition_summary,
                             title=f'{recipe.title} - SpiceShare Inc.')
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

            # Parse ingredients with quantities and units for editing
            ingredient_names = request.form.getlist('ingredients[]')
            ingredient_quantities = request.form.getlist('ingredient_quantities[]')
            ingredient_units = request.form.getlist('ingredient_units[]')
            
            # Combine ingredient data
            form_ingredients = []
            for i, name in enumerate(ingredient_names):
                if name.strip():  # Only add non-empty ingredients
                    quantity = ingredient_quantities[i] if i < len(ingredient_quantities) else None
                    unit = ingredient_units[i] if i < len(ingredient_units) else None
                    form_ingredients.append({
                        'name': name.strip(),
                        'quantity': float(quantity) if quantity and quantity.strip() else None,
                        'unit': unit.strip() if unit and unit.strip() else None
                    })
            
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
            old_image_url = recipe.image_url  # Store old image URL for cleanup later
            if image:
                try:
                    # Upload new image first
                    image_url = upload_image(image)
                    flash("Image updated successfully", "success")
                except ValueError as e:
                    flash(str(e), 'error')
                    return redirect(url_for('recipe_routes.edit_recipe', recipe_id=recipe_id))

            try:
                update_recipe(recipe, data, form_ingredients, form_instructions, image_url)  # Ensure data is a dict
                
                # Only delete old image after successful database update
                if image and old_image_url and old_image_url != image_url:
                    delete_image(old_image_url)
                    logger.info(f"Deleted old image: {old_image_url}")
                
                # Recalculate nutrition after recipe update
                try:
                    logger.info(f"Recalculating nutrition for updated recipe: {recipe_id}")
                    nutrition_info = NutritionService.recalculate_nutrition(recipe_id, force=True)
                    if nutrition_info:
                        flash(f"Recipe {recipe.title} updated with nutrition information!", 'success')
                    else:
                        flash(f"Recipe {recipe.title} updated! Nutrition calculation will be available shortly.", 'info')
                except Exception as nutrition_error:
                    logger.error(f"Nutrition recalculation failed for recipe {recipe_id}: {nutrition_error}")
                    flash(f"Recipe {recipe.title} updated! Nutrition calculation failed but can be recalculated later.", 'warning')
                
                return redirect(url_for('recipe_routes.view_recipe', recipe_id=recipe_id))

            except Exception as e:
                # Rollback db session in case of an error
                db.session.rollback()
                flash(f"An error occurred while updating the recipe: {str(e)}", "error")
                # delete the image if it was uploaded
                if image_url and image_url != recipe.image_url:
                    delete_image(image_url)
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
                if delete_image(recipe.image_url):
                    flash("Image deleted", 'success')
                else:
                    flash("Failed to delete Image", 'info')

            delete_recipe(recipe)
            flash("Recipe deleted successfully!", 'info')
            return redirect(url_for('recipe_routes.list_recipes'))

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


# Nutrition-related endpoints
@bp.route('/recipes/<uuid:recipe_id>/recalculate-nutrition', methods=['POST'])
@login_required
def recalculate_nutrition(recipe_id):
    """Force recalculation of nutrition data for a recipe"""
    try:
        recipe = get_recipe_by_id(recipe_id)
        
        if not recipe:
            flash("Recipe not found.", "error")
            return redirect(url_for('recipe_routes.list_recipes'))
        
        # Check if user owns the recipe
        if recipe.user_id != current_user.id:
            flash("You can only recalculate nutrition for your own recipes.", "error")
            return redirect(url_for('recipe_routes.view_recipe', recipe_id=recipe_id))
        
        logger.info(f"Manual nutrition recalculation requested for recipe {recipe_id} by user {current_user.id}")
        
        # Force recalculation
        nutrition_info = NutritionService.recalculate_nutrition(recipe_id, force=True)
        
        if nutrition_info:
            flash("Nutrition information updated successfully!", "success")
        else:
            flash("Failed to calculate nutrition information. Please try again later.", "error")
        
        return redirect(url_for('recipe_routes.view_recipe', recipe_id=recipe_id))
        
    except Exception as e:
        logger.error(f"Error in manual nutrition recalculation for recipe {recipe_id}: {e}")
        flash("An error occurred while recalculating nutrition information.", "error")
        return redirect(url_for('recipe_routes.view_recipe', recipe_id=recipe_id))


@bp.route('/api/recipes/<uuid:recipe_id>/nutrition', methods=['GET'])
def get_recipe_nutrition_api(recipe_id):
    """API endpoint to get nutrition information for a recipe"""
    try:
        nutrition_summary = NutritionService.get_nutrition_summary(recipe_id)
        
        if nutrition_summary:
            return jsonify({
                'success': True,
                'nutrition': nutrition_summary
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nutrition information not available'
            }), 404
            
    except Exception as e:
        logger.error(f"API error getting nutrition for recipe {recipe_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@bp.route('/api/nutrition/status', methods=['GET'])
def get_nutrition_service_status():
    """API endpoint to get nutrition service status"""
    try:
        status = NutritionService.get_service_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting nutrition service status: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get service status'
        }), 500
