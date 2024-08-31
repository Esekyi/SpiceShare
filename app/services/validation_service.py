def validate_recipe_data(data):
	"""validate_recipe_data(data)
	validate recipe data as they come in
	and display errors if not available
	"""
	errors = []
	if not data.get('title'):
		errors.append('Title is required.')
	if not data.get('description'):
		errors.append('Description is required.')
	if not data.get('instructions[]'):
		errors.append('Instructions are required.')
	if not data.get('category_id'):
		errors.append('Category is required.')

	return errors

