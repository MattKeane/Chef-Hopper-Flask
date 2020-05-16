import models
from flask import Blueprint, request, jsonify
from flask_bcrypt import generate_password_hash, check_password_hash
from playhouse.shortcuts import model_to_dict
from flask_login import login_user, current_user

users = Blueprint("users", "users")

@users.route("/test", methods=["GET"])
def test_user_route():
	return "route works"

@users.route("/register", methods=["POST"])
def register():
	payload = request.get_json()
	try:
		models.User.get(models.User.username == payload["username"])
		return jsonify(
			message="Username already taken",
			status=401
			), 401
	except models.DoesNotExist:
		created_user = models.User.create(
			username=payload["username"],
			email=payload["email"],
			password=generate_password_hash(payload["password"])
		)
		created_user_dict = model_to_dict(created_user)
		login_user(created_user)
		created_user_dict.pop("password")
		return jsonify(
			message="User created",
			data=created_user_dict,
			status=201
		), 201