from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
	"""This is the homepage of Mineralchemy"""

	return render_template("homepage.html")

if __name__ == '__main__':
	app.run(debug=True)