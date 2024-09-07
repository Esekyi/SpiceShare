from flask import Blueprint, request, render_template
from app.services.search_service import search_recipes

search_bp = Blueprint('search', __name__)


@search_bp.route('/search', methods=['GET'], strict_slashes=False)
def search():
	query = request.args.get('q', '').strip()
	page = int(request.args.get('page', 1))
	per_page = int(request.args.get('per_page', 10))

	if not query:
		return render_template('search_results.html', query=query, recipes=[])

	results = search_recipes(query, page, per_page)

	return render_template(
		'search_results.html', 
		query=query,
		recipes=results['items'],
		total_pages=results['total_pages'],
		current_page=results['current_page'],
		per_page=results['per_page'],
		)
