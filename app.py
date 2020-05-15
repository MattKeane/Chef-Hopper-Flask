from flask import Flask, jsonify

DEBUG=True
PORT=8000

app = Flask(__name__)
app.secretkey = "kb2WB$#b4qt43b"

@app.route("/")
def test_route():
	return "route works"

if __name__ == "__main__":
	app.run(debug=DEBUG, port=PORT)