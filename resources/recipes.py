import models
from flask import Blueprint, request, jsonify
from playhouse.shortcuts import model_to_dict
from scraper import scrape_recipes
from flask_login import current_user, login_required
import numpy

recipes = Blueprint("recipes", "recipes")

@recipes.route("/test", methods=["GET"])
def test_recipe_route():
	return "Route works"

@recipes.get("/<id>")
def get_recipe(id):
	try:
		recipe = models.Recipe.get_by_id(id)
		recipe_dict = model_to_dict(recipe)
		return jsonify(
			message="Recipe retrieved",
			data=recipe_dict,
			status=200
		), 200
	except models.DoesNotExist:
		return jsonify(
			message="Invalid recipe ID",
			data={},
			status=400
		), 400

@recipes.route("/search/<query>", methods=["GET"])
def search_recipes(query):
	query = query.replace("+", " ")
	existing_results = (models.Search
		.select()
		.where(models.Search.search_term == query))
	# if no results exist in the db, scrape some
	if len(existing_results) == 0:
		recipes = []
		new_recipes = scrape_recipes(query, 6)
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
		try:
			already_saved = models.SavedRecipe.get(
				(models.SavedRecipe.user_id == current_user.id)
				&
				(models.SavedRecipe.recipe_id == recipe_id))
			return jsonify(
				message="Recipe already saved",
				data={},
				status=400
			), 400
		except models.DoesNotExist:
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

@recipes.route("/rate/<recipe_id>", methods=["POST"])
@login_required
def rate_recipe(recipe_id):
	try:
		recipe_to_rate = models.Recipe.get_by_id(recipe_id)
		# create a rating if one doesn't exist already
		payload = request.get_json()
		new_rating, created = models.RecipeRating.get_or_create(
			recipe_id=recipe_to_rate.id,
			user_id=current_user.id,
			defaults={"rating": payload["rating"]})
		# update the rating entry if it already existed
		if not created:
			new_rating.rating = payload["rating"]
			new_rating.save()
		# get all ratings for that recipe
		all_ratings = models.RecipeRating.select().where(models.RecipeRating.recipe_id == recipe_to_rate.id)
		all_ratings = [model_to_dict(rating_entry)["rating"] for rating_entry in all_ratings]
		# get the average of the ratings
		new_avg = numpy.mean(all_ratings)
		recipe_to_rate.avg_rating = new_avg
		recipe_to_rate.save()
		return jsonify(
			message="Recipe rated",
			data=model_to_dict(recipe_to_rate),
			status=200
		), 200
	except models.DoesNotExist:
		return jsonify(
			message="Recipe does not exist.",
			data={},
			status=400
		), 400
