from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
	"""This is the homepage of Mineralchemy"""
	return render_template("homepage.html")


@app.route("/login")
def login():
	"""User login"""
	return render_template("login_form.html")


@app.route("/signup")
def signup():
	"""User sign up"""
	return render_template("signup_form.html")

@app.route("/search")
def search():
	"""User inputs search specifications here"""
	return render_template("search.html")


if __name__ == '__main__':
	app.run(debug=True)