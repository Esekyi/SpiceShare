from flask import Blueprint, request, render_template
from app.services.search_service import search_recipes

search_bp = Blueprint('search', __name__)