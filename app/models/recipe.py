from app import db
from datetime import datetime, timezone
import uuid
import logging
from sqlalchemy.dialects.postgresql import UUID

logger = logging.getLogger(__name__)


class Recipe(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # default value in Fahrenheit  # in °F
    oven_temp = db.Column(db.Integer, default=60)
    prep_time = db.Column(db.Integer)  # in minutes
    cook_time = db.Column(db.Integer)  # in minutes
    servings = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    view_count = db.Column(db.Integer, default=0)
    
    # Nutrition tracking fields
    nutrition_calculated = db.Column(db.Boolean, default=False)
    nutrition_last_updated = db.Column(db.DateTime)
    
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'category.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc))
    category = db.relationship('Category', backref='recipes', lazy=True)
    comments = db.relationship('Comment', backref='recipe', cascade='all, delete-orphan', lazy=True)
    ingredients = db.relationship(
        'Ingredient', backref='recipe', cascade='all, delete-orphan', lazy='dynamic')
    instructions = db.relationship(
        'Instruction', backref='recipes', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Recipe {self.title}>'

    def increment_view_count(self):
        """Increment the view count without updating the updated_at timestamp."""
        if self.view_count is None:  # Check if view_count is None
            self.view_count = 0      # Initialize to 0 if None
        self.view_count += 1
        db.session.commit()
        # No commit or onupdate manipulation here
    
    def needs_nutrition_calculation(self):
        """Check if recipe needs nutrition calculation"""
        if not self.nutrition_calculated:
            return True
        
        # Check if nutrition data is stale (older than 7 days)
        try:
            if self.nutrition_info and self.nutrition_info.is_stale():
                return True
        except Exception as e:
            # If there's any error with staleness check, assume we need recalculation
            logger.warning(f"Error checking nutrition staleness for recipe {self.id}: {e}")
            return True
            
        return False
    
    def get_ingredients_for_ai(self):
        """Format ingredients for AI nutrition calculation"""
        ingredients_list = []
        for ingredient in self.ingredients:
            ingredients_list.append({
                'name': ingredient.name,
                'quantity': ingredient.quantity or 1.0,
                'unit': ingredient.unit or 'piece'
            })
        return ingredients_list
    
    def mark_nutrition_calculated(self):
        """Mark recipe as having calculated nutrition"""
        self.nutrition_calculated = True
        self.nutrition_last_updated = datetime.now(timezone.utc)
    
    def reset_nutrition_calculation(self):
        """Reset nutrition calculation status"""
        self.nutrition_calculated = False
        self.nutrition_last_updated = None
