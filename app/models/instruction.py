from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Instruction(db.Model):
	id = db.Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4)
	step_number = db.Column(db.Integer, nullable=False)
	name = db.Column(db.Text, nullable=False)
	recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
            'recipe.id'), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(
		db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
	
	def __repr__(self) -> str:
		return f'<Instruction {self.step_number}: {self.name[:20]}>'