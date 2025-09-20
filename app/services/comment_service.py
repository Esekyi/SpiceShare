from app import db
from app.models.comment import Comment
from typing import List, Optional
import uuid

class CommentService:
	@staticmethod
	def add_comment(recipe_id: uuid.UUID, user_id: uuid.UUID, text: str) -> Comment:
		"""Add a comment to a recipe."""
		new_comment = Comment(recipe_id=recipe_id, user_id=user_id, text=text)
		db.session.add(new_comment)
		db.session.commit()
		return new_comment

	
	@staticmethod
	def get_comment_by_recipe(recipe_id: uuid.UUID) -> List[Comment]:
		"""Retrieve all comments for a given recipe."""
		return Comment.query.filter_by(recipe_id=recipe_id).order_by(Comment.created_at.desc()).all()

	
	@staticmethod
	def update_comment(comment_id: uuid.UUID, user_id: uuid.UUID, text: str) -> Optional[Comment]:
		"""Updates a comments."""
		comment = Comment.query.get_or_404(comment_id)
		if comment and comment.user_id == user_id:
			comment.text = text
			db.session.commit()
			return comment
		return None

	@staticmethod
	def delete_comment(comment_id: uuid.UUID, user_id: uuid.UUID) -> bool:
		comment = Comment.query.get_or_404(comment_id)
		if comment and comment.user_id == user_id:
			db.session.delete(comment)
			db.session.commit()
			return True
		return False
