from flask import Flask, render_template, redirect, request, flash, session, jsonify
from model import User, connect_to_db, db
from search_apis import search_etsy, search_ebay
from user_page import get_favorites
from scraper import scrape_minfind
import sqlite3


app = Flask(__name__)
app.secret_key = "mineral"

connection = sqlite3.connect('mineralchemy.db', check_same_thread=False)
cursor = connection.cursor()


@app.route("/")
def index():
	"""Homepage of Mineralchemy."""

	return render_template("homepage.html")


@app.route("/login", methods=['GET'])
def show_login_form():
	"""User login."""

	return render_template("login_form.html")


@app.route("/login", methods=['POST'])
def login():
	"""Log in user and puts user in session."""

	email = request.form["email"]
	password = request.form["password"]

	user = User.query.filter_by(email=email).first()

	# Check to see if user is registered in database
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

	# Check to see if user is already in database
	user = User.query.filter_by(email=email).first()

	if user:
		flash("You already registered! Please sign in!")
		return redirect("/login")
	else:
		new_user = User(email=email, password=password, firstname=firstname, lastname=lastname)

		db.session.add(new_user)
		db.session.commit()

		flash("%s is now registered" % email)
		return redirect("/")


@app.route("/search")
def search():
	"""User inputs search specifications here."""
	
	return render_template("search.html")


@app.route("/search_results", methods=['POST'])
def get_results():
	"""Aggregates listings from Etsy, eBay, and Minfind. Passes results to search result page."""

	keywords = request.form["keywords"]
	min_price = float(request.form["min_price"])
	max_price = float(request.form["max_price"])
	user_id = session.get("user_id", 0)

	if min_price > max_price:
		flash("Minimum price must be smaller than maximum price!")
		return redirect("/search")
	else:
		return render_template("search_results.html", keywords=keywords, min_price=min_price, max_price=max_price, user_id=user_id )	


@app.route("/scrape_minfind", methods=['GET'])
def get_minfind_results():
	keywords = request.args.get('keywords').encode(encoding='UTF-8',errors='strict')
	min_price = float(request.args.get('min_price'))
	max_price = float(request.args.get('max_price'))

	minfind_num_results, minfind_listings = scrape_minfind(keywords, min_price, max_price)

	success = { "numResults": minfind_num_results, 
				"listingsFound": minfind_listings }

	return jsonify(success)


@app.route("/search_etsy", methods=['GET'])
def get_etsy_results():
	keywords = request.args.get('keywords').encode(encoding='UTF-8',errors='strict')
	min_price = float(request.args.get('min_price'))
	max_price = float(request.args.get('max_price'))

	etsy_num_results, etsy_listings = search_etsy(keywords, min_price, max_price)

	success = { "numResults": etsy_num_results,
				"listingsFound": etsy_listings }

	return jsonify(success)


@app.route("/search_ebay", methods=['GET'])
def get_ebay_results():
	keywords = request.args.get('keywords').encode(encoding='UTF-8',errors='strict')
	min_price = float(request.args.get('min_price'))
	max_price = float(request.args.get('max_price'))

	ebay_num_results, ebay_listings = search_ebay(keywords, min_price, max_price)

	success = { "numResults": int(ebay_num_results), 
				"listingsFound": ebay_listings }

	return jsonify(success)


@app.route("/add_to_favorites", methods=['GET'])
def add_to_favorites():
	"""Add listing to favorites table in database."""

	user_id = int(request.args.get('user_id'))
	listing_origin = request.args.get('listing_origin')
	listing_id = int(request.args.get('listing_id'))
	title = request.args.get('title')
	price = float(request.args.get('price'))
	description = request.args.get('description')
	url = request.args.get('url')
	primary_image = request.args.get('primary_image')

	# Check to see if listing is already in favorites table for that user
	old_favorite_query = "SELECT * FROM favorites WHERE user_id = ? AND listing_id = ?"
	cursor.execute(old_favorite_query, (user_id, listing_id))
	old_favorite_result = cursor.fetchall()

	success_response = { "listing_id": listing_id}

	if old_favorite_result != []:
		success_response["success_text"] = "You have already added this to your favorites!"
		return jsonify(success_response)
	else:
		new_favorite_query = "INSERT INTO favorites (user_id, listing_origin, listing_id, title, price, description, url, primary_image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
		cursor.execute(new_favorite_query, (user_id, listing_origin, listing_id, title, price, description, url, primary_image))
		connection.commit()

		success_response["success_text"] = "Successfully added to your favorites!"
		return jsonify(success_response)


@app.route("/user/<int:user_id>", methods=['GET'])
def user_page(user_id):
	"""Show details and favorite listings of user."""

	user = User.query.get(user_id)

	sql_query = "SELECT * FROM favorites WHERE user_id = ?"
	cursor.execute(sql_query,(user.user_id,))
	results = cursor.fetchall()

	etsy_listings, ebay_listings, minfind_listings = get_favorites(results)

	return render_template("user.html", user=user, etsy_listings=etsy_listings, ebay_listings=ebay_listings, minfind_listings=minfind_listings)


@app.route("/data/<string:filename>", methods=['GET'])
def get_file(filename):
	f = open("static/" + filename)
	text = f.read()
	return text


@app.route("/discover", methods=['GET'])
def show_classification():

	return render_template("d3_radial_tree.html")


if __name__ == '__main__':
	app.debug = True
	connect_to_db(app)
	app.run()