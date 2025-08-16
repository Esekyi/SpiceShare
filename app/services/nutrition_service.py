"""
Nutrition service for managing recipe nutrition calculations.
Implements DRY principles and provides reusable methods for nutrition management.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List
from flask import current_app

from app import db
from app.models.recipe import Recipe
from app.models.nutrition_info import NutritionInfo
from app.services.gemini_service import GeminiNutritionService

logger = logging.getLogger(__name__)


class NutritionService:
    """Service for managing recipe nutrition calculations and caching"""
    
    @staticmethod
    def get_or_calculate_nutrition(recipe_id: str) -> Optional[NutritionInfo]:
        """
        Get existing nutrition info or calculate new one if needed
        
        Args:
            recipe_id: UUID of the recipe
            
        Returns:
            NutritionInfo object or None if calculation fails
        """
        try:
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                logger.error(f"Recipe not found: {recipe_id}")
                return None
            
            # Check if we have valid cached nutrition data
            try:
                if recipe.nutrition_info and not recipe.needs_nutrition_calculation():
                    logger.debug(f"Using cached nutrition data for recipe {recipe_id}")
                    return recipe.nutrition_info
            except Exception as datetime_error:
                logger.warning(f"Datetime comparison error for recipe {recipe_id}: {datetime_error}")
                # Force recalculation if there's a datetime issue
                logger.info(f"Forcing nutrition recalculation due to datetime error for recipe {recipe_id}")
            
            # Calculate new nutrition data
            logger.info(f"Calculating new nutrition data for recipe {recipe_id}")
            return NutritionService.calculate_and_store_nutrition(recipe)
            
        except Exception as e:
            logger.error(f"Error getting nutrition for recipe {recipe_id}: {e}")
            return None
    
    @staticmethod
    def calculate_and_store_nutrition(recipe: Recipe) -> Optional[NutritionInfo]:
        """
        Calculate nutrition using AI and store in database
        
        Args:
            recipe: Recipe object to calculate nutrition for
            
        Returns:
            NutritionInfo object or None if calculation fails
        """
        try:
            # Validate recipe has ingredients
            ingredients_list = list(recipe.ingredients)
            if not ingredients_list:
                logger.warning(f"Recipe {recipe.id} has no ingredients")
                return None
            
            # Prepare ingredients data for AI
            ingredients_data = recipe.get_ingredients_for_ai()
            servings = recipe.servings or 1
            
            logger.debug(f"Calculating nutrition for {len(ingredients_data)} ingredients, {servings} servings")
            
            # Call Gemini API
            gemini_service = GeminiNutritionService()
            nutrition_data = gemini_service.calculate_recipe_nutrition(
                ingredients_data, servings
            )
            
            if not nutrition_data:
                logger.error(f"Failed to get nutrition data from Gemini for recipe {recipe.id}")
                return None
            
            # Store nutrition data in database
            nutrition_info = NutritionService._create_nutrition_record(recipe, nutrition_data)
            
            if nutrition_info:
                # Mark recipe as having calculated nutrition
                recipe.mark_nutrition_calculated()
                db.session.commit()
                
                logger.info(f"Successfully calculated and stored nutrition for recipe {recipe.id}")
                return nutrition_info
            
        except Exception as e:
            logger.error(f"Error calculating nutrition for recipe {recipe.id}: {e}")
            db.session.rollback()
        
        return None
    
    @staticmethod
    def _create_nutrition_record(recipe: Recipe, nutrition_data: Dict) -> Optional[NutritionInfo]:
        """
        Create and save nutrition record to database
        
        Args:
            recipe: Recipe object
            nutrition_data: Nutrition data from AI
            
        Returns:
            NutritionInfo object or None if creation fails
        """
        try:
            # Delete existing nutrition info if it exists
            if recipe.nutrition_info:
                db.session.delete(recipe.nutrition_info)
                db.session.flush()
            
            # Create new nutrition record
            nutrition_info = NutritionInfo(
                recipe_id=recipe.id,
                total_calories=nutrition_data.get('total_calories'),
                calories_per_serving=nutrition_data.get('calories_per_serving'),
                protein_g=nutrition_data.get('protein_g'),
                carbs_g=nutrition_data.get('carbs_g'),
                fat_g=nutrition_data.get('fat_g'),
                fiber_g=nutrition_data.get('fiber_g'),
                sodium_mg=nutrition_data.get('sodium_mg'),
                sugar_g=nutrition_data.get('sugar_g'),
                cholesterol_mg=nutrition_data.get('cholesterol_mg'),
                vitamin_c_mg=nutrition_data.get('vitamin_c_mg'),
                calcium_mg=nutrition_data.get('calcium_mg'),
                iron_mg=nutrition_data.get('iron_mg'),
                ai_confidence_score=nutrition_data.get('confidence_score'),
                ai_model_version=nutrition_data.get('ai_model_version')
            )
            
            db.session.add(nutrition_info)
            db.session.flush()  # Get the ID
            
            logger.debug(f"Created nutrition record {nutrition_info.id} for recipe {recipe.id}")
            return nutrition_info
            
        except Exception as e:
            logger.error(f"Error creating nutrition record: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def recalculate_nutrition(recipe_id: str, force: bool = True) -> Optional[NutritionInfo]:
        """
        Force recalculation of nutrition data
        
        Args:
            recipe_id: UUID of the recipe
            force: Whether to force recalculation even if data is fresh
            
        Returns:
            NutritionInfo object or None if calculation fails
        """
        try:
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                logger.error(f"Recipe not found: {recipe_id}")
                return None
            
            if force:
                # Reset nutrition calculation status
                recipe.reset_nutrition_calculation()
                
                # Delete existing nutrition data
                if recipe.nutrition_info:
                    db.session.delete(recipe.nutrition_info)
                    db.session.flush()
            
            # Calculate new nutrition data
            return NutritionService.calculate_and_store_nutrition(recipe)
            
        except Exception as e:
            logger.error(f"Error recalculating nutrition for recipe {recipe_id}: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_nutrition_summary(recipe_id: str) -> Optional[Dict]:
        """
        Get formatted nutrition summary for display
        
        Args:
            recipe_id: UUID of the recipe
            
        Returns:
            Dictionary with formatted nutrition data or None
        """
        try:
            nutrition_info = NutritionService.get_or_calculate_nutrition(recipe_id)
            
            if not nutrition_info:
                return None
            
            return {
                'facts': nutrition_info.get_nutrition_facts(),
                'confidence': nutrition_info.confidence_level(),
                'calculated_at': nutrition_info.calculated_at,
                'is_stale': nutrition_info.is_stale(),
                'total_calories': nutrition_info.total_calories
            }
            
        except Exception as e:
            logger.error(f"Error getting nutrition summary for recipe {recipe_id}: {e}")
            return None
    
    @staticmethod
    def bulk_calculate_nutrition(recipe_ids: List[str]) -> Dict[str, bool]:
        """
        Calculate nutrition for multiple recipes in bulk
        
        Args:
            recipe_ids: List of recipe UUIDs
            
        Returns:
            Dictionary mapping recipe_id to success status
        """
        results = {}
        
        for recipe_id in recipe_ids:
            try:
                nutrition_info = NutritionService.get_or_calculate_nutrition(recipe_id)
                results[recipe_id] = nutrition_info is not None
                
                logger.debug(f"Bulk calculation for {recipe_id}: {'success' if results[recipe_id] else 'failed'}")
                
            except Exception as e:
                logger.error(f"Bulk calculation failed for recipe {recipe_id}: {e}")
                results[recipe_id] = False
        
        logger.info(f"Bulk nutrition calculation completed. Success: {sum(results.values())}/{len(recipe_ids)}")
        return results
    
    @staticmethod
    def delete_nutrition_data(recipe_id: str) -> bool:
        """
        Delete nutrition data for a recipe
        
        Args:
            recipe_id: UUID of the recipe
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                logger.error(f"Recipe not found: {recipe_id}")
                return False
            
            if recipe.nutrition_info:
                db.session.delete(recipe.nutrition_info)
                recipe.reset_nutrition_calculation()
                db.session.commit()
                
                logger.info(f"Deleted nutrition data for recipe {recipe_id}")
                return True
            
            return True  # No data to delete, consider it successful
            
        except Exception as e:
            logger.error(f"Error deleting nutrition data for recipe {recipe_id}: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_recipes_needing_nutrition_calculation(limit: int = 50) -> List[Recipe]:
        """
        Get recipes that need nutrition calculation
        
        Args:
            limit: Maximum number of recipes to return
            
        Returns:
            List of Recipe objects needing nutrition calculation
        """
        try:
            # Get recipes without nutrition calculation or with stale data
            recipes = Recipe.query.filter(
                (Recipe.nutrition_calculated == False) |
                (Recipe.nutrition_calculated == None)
            ).limit(limit).all()
            
            # Also check for recipes with stale nutrition data
            stale_recipes = []
            for recipe in Recipe.query.filter(Recipe.nutrition_calculated == True).limit(limit * 2).all():
                if recipe.needs_nutrition_calculation():
                    stale_recipes.append(recipe)
                    if len(stale_recipes) >= limit - len(recipes):
                        break
            
            all_recipes = recipes + stale_recipes
            return all_recipes[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recipes needing nutrition calculation: {e}")
            return []
    
    @staticmethod
    def is_service_available() -> bool:
        """
        Check if nutrition calculation service is available
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            return GeminiNutritionService.is_service_available()
        except Exception:
            return False
    
    @staticmethod
    def get_service_status() -> Dict:
        """
        Get detailed service status information
        
        Returns:
            Dictionary with service status details
        """
        try:
            gemini_available = GeminiNutritionService.is_service_available()
            
            # Count recipes with/without nutrition data
            total_recipes = Recipe.query.count()
            calculated_recipes = Recipe.query.filter(Recipe.nutrition_calculated == True).count()
            pending_recipes = total_recipes - calculated_recipes
            
            return {
                'gemini_available': gemini_available,
                'total_recipes': total_recipes,
                'calculated_recipes': calculated_recipes,
                'pending_recipes': pending_recipes,
                'calculation_coverage': (calculated_recipes / total_recipes * 100) if total_recipes > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'gemini_available': False,
                'total_recipes': 0,
                'calculated_recipes': 0,
                'pending_recipes': 0,
                'calculation_coverage': 0,
                'error': str(e)
            }
