from peewee import *
from flask_login import UserMixin
from playhouse.postgres_ext import PostgresqlExtDatabase, ArrayField
import datetime

# define database

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
		User, 
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

	class Meta:
		database = DATABASE

class ScrapeException(Model):
	url = CharField()
	time = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = DATABASE



def initialize():
	DATABASE.connect()
	DATABASE.create_tables([], safe=True)
	print("Connecting to DB and created tables")
	DATABASE.close()