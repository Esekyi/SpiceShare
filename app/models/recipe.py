from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


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
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'category.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
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
        self.view_count += 1
        db.session.commit()
        # No commit or onupdate manipulation here
