from math import ceil

def paginate(items, page, per_page):
	"""Paginate a list of items.

    Args:
        items (list): The list of items to paginate.
        page (int): The current page number (1-indexed).
        per_page (int): The number of items per page.

    Returns:
        dict: A dictionary containing paginated items and pagination info.
	"""

	# Ensure page is at least 1
	if page < 1:
		page = 1
	
	total_items = len(items)
	total_pages = ceil(total_items / per_page)

	# Adjust page if it exceeds total pages
	if page > total_pages:
		page = total_pages

	start = (page - 1) * per_page
	end = start + per_page
	paginated_items = items[start:end]

	return {
		'items': paginated_items,
		'total_items': total_items,
		'total_pages': total_pages,
		'current_page': page,
		'per_page': per_page
	}
