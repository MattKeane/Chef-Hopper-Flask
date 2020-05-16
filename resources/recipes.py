import models
from flask import Blueprint, request, jsonify
from playhouse.shortcuts import model_to_dict
from scraper import scrape_recipes
from flask_login import current_user, login_required

recipes = Blueprint("recipes", "recipes")

@recipes.route("/test", methods=["GET"])
def test_recipe_route():
	return "Route works"

@recipes.route("/search/<query>", methods=["GET"])
def search_recipes(query):
	query = query.replace("+", " ")
	existing_results = (models.Search
		.select()
		.where(models.Search.search_term == query))
	if len(existing_results) == 0:
		recipes = []
		new_recipes = scrape_recipes(query, 5)
		for recipe in new_recipes:
			recipe_entry, created = models.Recipe.get_or_create(
				url=recipe["url"],
				defaults={
					"title": recipe["title"],
					"ingredients": recipe["ingredients"],
					"instructions": recipe["instructions"]
				})
			recipe_dict = model_to_dict(recipe_entry)
			models.Search.create(
				search_term=query,
				recipe=recipe_dict["id"]
			)
			recipes.append(recipe_dict)
		if recipes:
			return jsonify(
				message="Recipes added to database",
				data=recipes,
				status=201
			), 201
		else:
			return jsonify(
				message="Search returned no results.",
				data=[],
				status=200
			), 200
	else:
		recipes = [model_to_dict(result.recipe) for result in existing_results]
		return jsonify(
			message="Recipes returned from database",
			data=recipes,
			status=200
		), 200

@recipes.route("/save/<recipe_id>", methods=["POST"])
@login_required
def save_recipe(recipe_id):
	try:
		recipe_to_save = models.Recipe.get_by_id(recipe_id)
		recipe_dict = model_to_dict(recipe_to_save)
		models.SavedRecipe.create(
			recipe=recipe_dict["id"],
			user=current_user.id)
		return jsonify(
			message="Recipe saved.",
			data=recipe_dict,
			status=201
		), 201
	except models.DoesNotExist:
		return jsonify(
			message="Recipe does not exist.",
			data={},
			status=400
		), 400
