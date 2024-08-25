from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Comment(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'recipe.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.text}>'
