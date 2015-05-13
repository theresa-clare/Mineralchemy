from flask import Flask, render_template, redirect, request, flash, session
from model import User, connect_to_db, db


app = Flask(__name__)
app.secret_key = "mineral"


@app.route("/")
def index():
	"""This is the homepage of Mineralchemy"""

	return render_template("homepage.html")


@app.route("/login", methods=['GET'])
def show_login_form():
	"""User login"""

	return render_template("login_form.html")


@app.route("/login", methods=['POST'])
def login():
	"""Log in user by checking to see if user is in user database and putting user in session."""

	email = request.form["email"]
	password = request.form["password"]

	user = User.query.filter_by(email=email).first()

	if not user:
		flash("User not in database")
		return redirect("/login")

	if user.password != password:
		flash("Password is incorrect")
		return redirect("/login")

	session["user_id"] = user.user_id

	flash("Welcome back! You are now logged in.")
	return redirect("/")


@app.route("/signup", methods=['GET'])
def show_signup_form():
	"""Render form for the user to sign up."""

	return render_template("signup_form.html")


@app.route("/signup", methods=['POST'])
def signup():
	"""Register user by adding user to User table and to session."""

	email = request.form["email"]
	password = request.form["password"]
	firstname = request.form["firstname"]
	lastname = request.form["lastname"]

	new_user = User(email=email, password=password, firstname=firstname, lastname=lastname)

	db.session.add(new_user)
	db.session.commit()

	flash("%s is now registered" % email)
	return redirect("/")
		

@app.route("/search")
def search():
	"""User inputs search specifications here"""
	return render_template("search.html")


if __name__ == '__main__':
	app.debug = True

	connect_to_db(app)

	app.run()