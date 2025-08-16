from app import db
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Ingredient(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Float)  # Amount (e.g., 2.5)
    unit = db.Column(db.String(50))  # Unit (cups, tbsp, oz, etc.)
    estimated_calories = db.Column(db.Float)  # AI-calculated calories for this ingredient
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'recipe.id'), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Ingredient {self.name}>'
    
    def formatted_quantity(self):
        """Return formatted quantity with unit for display"""
        if self.quantity and self.unit:
            return f"{self.quantity} {self.unit}"
        elif self.quantity:
            return str(self.quantity)
        return ""
    
    def to_dict(self):
        """Convert ingredient to dictionary for API responses"""
        return {
            'id': str(self.id),
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'estimated_calories': self.estimated_calories,
            'formatted_quantity': self.formatted_quantity()
        }
