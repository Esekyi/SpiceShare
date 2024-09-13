from app import db
import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID


class Subscriber(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_on = db.Column(
        db.DateTime, default=datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Subscriber {self.email}>'
