from app import db
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Category(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Category {self.name}>'
