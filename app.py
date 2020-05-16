from flask import Flask, jsonify
from flask_login import LoginManager
from resources.users import users

import models

DEBUG=True
PORT=8000

app = Flask(__name__)
app.secret_key = "kb2WB$#b4qt43b"

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	try:
		return models.User.get(user_id)
	except models.DoesNotExist:
		return None

app.register_blueprint(users, url_prefix="/api/v1/users")

@app.route("/")
def test_route():
	return "route works"

if __name__ == "__main__":
	models.initialize()
	app.run(debug=DEBUG, port=PORT)