from flask import Blueprint, jsonify, request
from app import db

bp = Blueprint('recipe_route', __name__)
