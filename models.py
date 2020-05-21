from peewee import *
from flask_login import UserMixin
from playhouse.postgres_ext import PostgresqlExtDatabase, ArrayField
import datetime
import os
from playhouse.db_url import connect

# define database

if "ON_HEROKU" in os.environ:
	DATABASE = connect(os.environ.get("DATABASE_URL"))
else:
	DATABASE = PostgresqlExtDatabase(
		"chef_hopper",
		host="127.0.0.1",
		port=5432
	)

# define models

class User(UserMixin, Model):
	username = CharField(unique=True)
	email = CharField(unique=True)
	password = CharField()

	class Meta:
		database = DATABASE

class Recipe(Model):
	url = CharField()
	title = CharField()
	ingredients = ArrayField(CharField)
	instructions = ArrayField(TextField)
	avg_rating = FloatField(default=0)

	class Meta:
		database = DATABASE

class Search(Model):
	search_term = CharField()
	recipe = ForeignKeyField(
		Recipe, 
		backref="searchs",
		on_delete="CASCADE"
	)

	class Meta:
		database = DATABASE

class SavedRecipe(Model):
	user = ForeignKeyField(
		User,
		backref="savedrecipes",
		on_delete="CASCADE")
	recipe = ForeignKeyField(
		Recipe,
		backref="savedrecipes",
		on_delete="CASCADE")

	class Meta:
		database = DATABASE

class ScrapeException(Model):
	url = CharField()
	exception_type = CharField()
	time = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = DATABASE

class RecipeRating(Model):
	recipe = ForeignKeyField(
		Recipe,
		backref="reciperatings",
		on_delete="CASCADE")
	user = ForeignKeyField(
		User,
		backref="reciperatings",
		on_delete="CASCADE")
	rating = SmallIntegerField()

	class Meta:
		database = DATABASE

# initialize database

def initialize():
	DATABASE.connect()
	DATABASE.create_tables([User, Recipe, Search, SavedRecipe, ScrapeException, RecipeRating], safe=True)
	print("Connecting to DB and created tables")
	DATABASE.close()