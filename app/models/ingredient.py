from app import db
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Ingredient(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4)
    name = db.Column(db.String(120), nullable=False)
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'recipe.id'), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Ingredient {self.name}>'
