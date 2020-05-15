from flask import Flask, jsonify
from flask_login import LoginManager
from resources.users import users

import models

DEBUG=True
PORT=8000

app = Flask(__name__)
app.secretkey = "kb2WB$#b4qt43b"

app.register_blueprint(users, url_prefix="/api/v1/users")

@app.route("/")
def test_route():
	return "route works"

if __name__ == "__main__":
	models.initialize()
	app.run(debug=DEBUG, port=PORT)