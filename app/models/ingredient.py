from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Ingredient(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'recipe.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Ingredient {self.name}>'
