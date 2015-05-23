from flask import Flask, render_template, redirect, request, flash, session
from model import User, connect_to_db, db
import requests
from search_apis import search_etsy, search_ebay


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


@app.route("/logout")
def logout():
	"""Log user out from session."""

	del session["user_id"]
	flash("You are now logged out.")

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
		

@app.route("/user/<int:user_id>")
def user_page(user_id):
	"""Show details about user"""

	user = User.query.get(user_id)

	return render_template("user.html", user=user)


@app.route("/search")
def search():
	"""User inputs search specifications here"""
	
	return render_template("search.html")


@app.route("/search_results", methods=['POST'])
def get_results():

	keywords = request.form["keywords"]
	min_price = request.form["min_price"]
	max_price = request.form["max_price"]

	etsy_num_results, etsy_listings = search_etsy(keywords, min_price, max_price)
	ebay_num_results, all_listings = search_ebay(keywords, min_price, max_price, etsy_listings)

	total_count = etsy_num_results + int(ebay_num_results)

	return render_template("search_results.html", total_count=total_count, all_listings=all_listings)


# @app.route("/listing/<int:listing_id>")
# def listing_details(listing_id):
# 	"""Show details about a listing."""

# 	r = requests.get("https://openapi.etsy.com/v2/listings/" + str(listing_id) + "?api_key=" + etsy_api_key).json()
# 	listing = r["results"][0]

# 	return render_template("listing.html", title=listing["title"], description=listing["description"], 
# 		price=listing["price"], image_urls=image_urls)


if __name__ == '__main__':
	app.debug = True

	connect_to_db(app)

	app.run()