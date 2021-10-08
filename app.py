from flask import Flask, jsonify, g
from flask_login import LoginManager
from resources.users import users
from resources.recipes import recipes
from flask_cors import CORS
import os
import models
from dotenv import load_dotenv

load_dotenv()
SESSION_SECRET = os.getenv('SESSION_SECRET')
DEBUG=True
PORT=8000

app = Flask(__name__)
app.secret_key = SESSION_SECRET

app.config.update(
  SESSION_COOKIE_SECURE=True,
  SESSION_COOKIE_SAMESITE='None'
)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	try:
		return models.User.get_by_id(user_id)
	except models.DoesNotExist:
		return None

# Return JSON if user is unauthorized
@login_manager.unauthorized_handler
def handle_unauthorized():
	return jsonify(
		data={},
		message='You are not authorized to do that',
		status=401), 401

# Return JSON for 404 errors
@app.errorhandler(404)
def handle_404(err):
	return jsonify(
		data={},
		message='404: Resource not found',
		status=404), 404

@app.errorhandler(405)
def handle_405(err):
	return jsonify(
		data={},
		message='405: Method not allowed',
		status=405), 405

CORS(users, origins=["http://localhost:3000", "https://chef-hopper.herokuapp.com", "http://chef-hopper.herokuapp.com"], supports_credentials=True)
CORS(recipes, origins=["http://localhost:3000", "https://chef-hopper.herokuapp.com", "http://chef-hopper.herokuapp.com"], supports_credentials=True)

app.register_blueprint(users, url_prefix="/api/v1/users")
app.register_blueprint(recipes, url_prefix="/api/v1/recipes")

@app.before_request
def before_request():
	g.db = models.DATABASE
	g.db.connect()

@app.after_request
def after_request(response):
	g.db.close()
	return response

if "ON_HEROKU" in os.environ:
	print("\non heroku!")
	models.initialize()

if __name__ == "__main__":
	models.initialize()
	app.run(debug=DEBUG, port=PORT)