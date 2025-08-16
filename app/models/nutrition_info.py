from app import db
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID


class NutritionInfo(db.Model):
    """Model to store AI-calculated nutrition information for recipes"""
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey('recipe.id'), nullable=False)
    
    # Calorie information
    total_calories = db.Column(db.Float)  # Total calories for entire recipe
    calories_per_serving = db.Column(db.Float)  # Calories per serving
    
    # Macronutrients (per serving)
    protein_g = db.Column(db.Float)  # Protein in grams
    carbs_g = db.Column(db.Float)  # Carbohydrates in grams
    fat_g = db.Column(db.Float)  # Fat in grams
    fiber_g = db.Column(db.Float)  # Fiber in grams
    
    # Micronutrients (per serving)
    sodium_mg = db.Column(db.Float)  # Sodium in milligrams
    sugar_g = db.Column(db.Float)  # Sugar in grams
    cholesterol_mg = db.Column(db.Float)  # Cholesterol in milligrams
    vitamin_c_mg = db.Column(db.Float)  # Vitamin C in milligrams
    calcium_mg = db.Column(db.Float)  # Calcium in milligrams
    iron_mg = db.Column(db.Float)  # Iron in milligrams
    
    # AI metadata
    ai_confidence_score = db.Column(db.Float)  # Gemini's confidence level (0.0-1.0)
    ai_model_version = db.Column(db.String(50))  # Track which AI model was used
    
    # Timestamps
    calculated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )
    
    # Relationship
    recipe = db.relationship('Recipe', backref=db.backref('nutrition_info', uselist=False))
    
    def __repr__(self):
        return f'<NutritionInfo for Recipe {self.recipe_id}: {self.calories_per_serving} cal/serving>'
    
    def to_dict(self):
        """Convert nutrition info to dictionary for API responses"""
        return {
            'id': str(self.id),
            'recipe_id': str(self.recipe_id),
            'total_calories': self.total_calories,
            'calories_per_serving': self.calories_per_serving,
            'protein_g': self.protein_g,
            'carbs_g': self.carbs_g,
            'fat_g': self.fat_g,
            'fiber_g': self.fiber_g,
            'sodium_mg': self.sodium_mg,
            'sugar_g': self.sugar_g,
            'cholesterol_mg': self.cholesterol_mg,
            'vitamin_c_mg': self.vitamin_c_mg,
            'calcium_mg': self.calcium_mg,
            'iron_mg': self.iron_mg,
            'ai_confidence_score': self.ai_confidence_score,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }
    
    def get_nutrition_facts(self):
        """Get formatted nutrition facts for display"""
        return {
            'calories': round(self.calories_per_serving) if self.calories_per_serving else 0,
            'protein': round(self.protein_g, 1) if self.protein_g else 0,
            'carbs': round(self.carbs_g, 1) if self.carbs_g else 0,
            'fat': round(self.fat_g, 1) if self.fat_g else 0,
            'fiber': round(self.fiber_g, 1) if self.fiber_g else 0,
            'sodium': round(self.sodium_mg) if self.sodium_mg else 0,
            'sugar': round(self.sugar_g, 1) if self.sugar_g else 0
        }
    
    def is_stale(self, max_age_days=7):
        """Check if nutrition data is stale and needs recalculation"""
        if not self.calculated_at:
            return True
        
        # Ensure both datetimes are timezone-aware
        now = datetime.now(timezone.utc)
        calculated_at = self.calculated_at
        
        # If calculated_at is naive, assume it's UTC
        if calculated_at.tzinfo is None:
            calculated_at = calculated_at.replace(tzinfo=timezone.utc)
        
        age = now - calculated_at
        return age.days > max_age_days
    
    def confidence_level(self):
        """Return human-readable confidence level"""
        if not self.ai_confidence_score:
            return "Unknown"
        
        if self.ai_confidence_score >= 0.8:
            return "High"
        elif self.ai_confidence_score >= 0.6:
            return "Medium"
        else:
            return "Low"
