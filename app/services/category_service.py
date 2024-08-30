from app import db
from app.models.category import Category
from sqlalchemy import func

class CategoryService:
	@staticmethod
	def create_category(name: str, description: str = None) -> Category:
		"""
			Create a new category.

			Args:
				name (str): The name of the category.
				description (str, optional): The description of the category.

			Returns:
				Category: The newly created category.

			Raises:
				ValueError: If a category with the given name already exists (case-insensitive)..
			"""
		existing_category = Category.query.filter(func.lower(Category.name) == func.lower(name)).first()

		if existing_category:
			raise ValueError(f"A category with the name '{name}' already exists.")
		
		new_category = Category(name=name, description=description)
		db.session.add(new_category)
		db.session.commit()

		return new_category

	@staticmethod
	def get_all_categories():
		categories = Category.query.order_by(Category.name.asc()).all()
		return categories
