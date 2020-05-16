import models
from flask import Blueprint, request, jsonify
from flask_bcrypt import generate_password_hash, check_password_hash
from playhouse.shortcuts import model_to_dict
from flask_login import login_user, current_user, logout_user, login_required

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

@users.route("/login", methods=["POST"])
def login():
	payload = request.get_json()
	try:
		user = models.User.get(models.User.username == payload["username"])
		user_dict = model_to_dict(user)
		password_is_correct = check_password_hash(user_dict["password"], payload["password"])
		if password_is_correct:
			login_user(user)
			user_dict.pop("password")
			return jsonify(
				data = user_dict,
				message = "user logged in",
				status = 200
			), 200
		else:
			print("Bad password")
			return jsonify(
				data={},
				message="Invalid username or password",
				status=401
			), 401
	except models.DoesNotExist:
		print("invalid username")
		return jsonify(
			data={},
			message="Invalid username or password",
			status=401
		), 401

@users.route("/logout", methods=["GET"])
def logout():
	logout_user()
	return jsonify(
		data={},
		message="Logged out.",
		status=200
	), 200

@users.route("/saved_recipes", methods=["GET"])
@login_required
def get_saved_recipes():
	saved_recipes = (models.SavedRecipe
		.select()
		.where(models.SavedRecipe.user_id == current_user.id))
	saved_recipe_dicts = [model_to_dict(recipe)["recipe"] for recipe in saved_recipes]
	return jsonify(
		data=saved_recipe_dicts,
		message=f"Returned {len(saved_recipe_dicts)} saved recipes",
		status=200
	), 200
