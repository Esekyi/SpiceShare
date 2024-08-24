from app import db
from datetime import datetime
import uuid


class Recipe(db.Model):
    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    prep_time = db.Column(db.Integer)  # in minutes
    cook_time = db.Column(db.Integer)  # in minutes
    servings = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.String(36), db.ForeignKey(
        'category.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey(
        'user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = db.relationship('Category', backref='recipes', lazy=True)
    comments = db.relationship('Comment', backref='recipe', lazy=True)
    ingredients = db.relationship(
        'Ingredient', backref='recipe', lazy='dynamic')

    def __repr__(self):
        return f'<Recipe {self.title}>'
