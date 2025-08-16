"""
Google Gemini API service for nutrition calculation.
Provides DRY and reusable methods for AI-powered nutrition analysis.
"""
import json
import logging
from typing import Dict, List, Optional
from flask import current_app

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


class GeminiNutritionService:
    """Service for calculating nutrition information using Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini service with API configuration"""
        if not genai:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in configuration")
        
        genai.configure(api_key=api_key)
        self.model_name = current_app.config.get('GEMINI_MODEL', 'gemini-pro')
        self.model = genai.GenerativeModel(self.model_name)
    
    def calculate_recipe_nutrition(self, ingredients_list: List[Dict], servings: int = 1) -> Optional[Dict]:
        """
        Calculate nutrition information for a recipe using Gemini AI
        
        Args:
            ingredients_list: List of ingredient dictionaries with name, quantity, unit
            servings: Number of servings the recipe makes
            
        Returns:
            Dictionary with nutrition information or None if calculation fails
        """
        if not ingredients_list:
            logger.warning("Empty ingredients list provided")
            return None
        
        if servings < 1:
            servings = 1
        
        try:
            prompt = self._build_nutrition_prompt(ingredients_list, servings)
            logger.debug(f"Sending nutrition prompt to Gemini: {prompt[:200]}...")
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                logger.error("Empty response from Gemini API")
                return None
            
            nutrition_data = self._parse_nutrition_response(response.text)
            
            if nutrition_data:
                nutrition_data['ai_model_version'] = self.model_name
                logger.info(f"Successfully calculated nutrition for {len(ingredients_list)} ingredients")
            
            return nutrition_data
            
        except Exception as e:
            logger.error(f"Gemini API nutrition calculation error: {e}")
            return None
    
    def _build_nutrition_prompt(self, ingredients: List[Dict], servings: int) -> str:
        """
        Build a detailed prompt for Gemini to analyze nutrition
        
        Args:
            ingredients: List of ingredient dictionaries
            servings: Number of servings
            
        Returns:
            Formatted prompt string
        """
        ingredients_text = "\n".join([
            f"- {ing.get('quantity', 1)} {ing.get('unit', 'piece')} {ing.get('name', 'unknown ingredient')}"
            for ing in ingredients
        ])
        
        prompt = f"""
You are a professional nutritionist. Analyze the nutritional content of this recipe that makes {servings} serving(s):

INGREDIENTS:
{ingredients_text}

Please calculate the nutrition information and respond ONLY with a valid JSON object in this exact format:
{{
    "total_calories": <total calories for entire recipe>,
    "calories_per_serving": <calories per serving>,
    "protein_g": <protein in grams per serving>,
    "carbs_g": <carbohydrates in grams per serving>,
    "fat_g": <fat in grams per serving>,
    "fiber_g": <fiber in grams per serving>,
    "sodium_mg": <sodium in milligrams per serving>,
    "sugar_g": <sugar in grams per serving>,
    "cholesterol_mg": <cholesterol in milligrams per serving>,
    "vitamin_c_mg": <vitamin C in milligrams per serving>,
    "calcium_mg": <calcium in milligrams per serving>,
    "iron_mg": <iron in milligrams per serving>,
    "confidence_score": <your confidence level from 0.0 to 1.0>
}}

Important guidelines:
- Use standard USDA nutrition database values
- Account for cooking methods (if obvious from ingredients)
- Be conservative with estimates
- Set confidence_score based on ingredient clarity and common knowledge
- Respond with ONLY the JSON object, no additional text
"""
        return prompt.strip()
    
    def _parse_nutrition_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse Gemini's response and extract nutrition data
        
        Args:
            response_text: Raw response from Gemini API
            
        Returns:
            Parsed nutrition dictionary or None if parsing fails
        """
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove any markdown code block markers
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remove ```json
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]   # Remove ```
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remove trailing ```
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            nutrition_data = json.loads(cleaned_text)
            
            # Validate required fields
            required_fields = [
                'total_calories', 'calories_per_serving', 'protein_g', 
                'carbs_g', 'fat_g', 'confidence_score'
            ]
            
            for field in required_fields:
                if field not in nutrition_data:
                    logger.error(f"Missing required field in nutrition data: {field}")
                    return None
            
            # Validate data types and ranges
            if not self._validate_nutrition_data(nutrition_data):
                return None
            
            logger.debug("Successfully parsed nutrition data from Gemini response")
            return nutrition_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Raw response: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Error parsing nutrition response: {e}")
            return None
    
    def _validate_nutrition_data(self, data: Dict) -> bool:
        """
        Validate nutrition data for reasonable values
        
        Args:
            data: Nutrition data dictionary
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check for reasonable calorie ranges (0-10000 per serving)
            calories = float(data.get('calories_per_serving', 0))
            if calories < 0 or calories > 10000:
                logger.warning(f"Unreasonable calories per serving: {calories}")
                return False
            
            # Check confidence score (0.0-1.0)
            confidence = float(data.get('confidence_score', 0))
            if confidence < 0.0 or confidence > 1.0:
                logger.warning(f"Invalid confidence score: {confidence}")
                return False
            
            # Check for negative values in nutrition fields
            nutrition_fields = ['protein_g', 'carbs_g', 'fat_g', 'fiber_g', 
                              'sodium_mg', 'sugar_g', 'total_calories']
            
            for field in nutrition_fields:
                value = data.get(field)
                if value is not None and float(value) < 0:
                    logger.warning(f"Negative value for {field}: {value}")
                    return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f"Data validation error: {e}")
            return False
    
    @staticmethod
    def is_service_available() -> bool:
        """
        Check if Gemini service is properly configured and available
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            if not genai:
                return False
            
            api_key = current_app.config.get('GEMINI_API_KEY')
            return bool(api_key)
            
        except Exception:
            return False
    
    def test_connection(self) -> bool:
        """
        Test connection to Gemini API with a simple request
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_ingredients = [
                {'name': 'apple', 'quantity': 1, 'unit': 'medium'}
            ]
            
            result = self.calculate_recipe_nutrition(test_ingredients, 1)
            return result is not None
            
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False
