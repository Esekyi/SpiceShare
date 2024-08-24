from flask import Blueprint, jsonify, request
from app import db
from app.services.user_services import get_all_users
from app.services.user_services import create_user

bp = Blueprint('user_routes', __name__)

@bp.route('/users', methods=['GET'])
def list_users():
	users = get_all_users()
	return jsonify([user.username for user in users])


@bp.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    user = create_user(data['username'], data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201
