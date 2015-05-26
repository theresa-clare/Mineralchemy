from flask import Flask, render_template, redirect, request, flash, session
from model import User, connect_to_db, db
from search_apis import search_etsy, search_ebay
from scraper import scrape_minfind
import requests
import sqlite3


app = Flask(__name__)
app.secret_key = "mineral"

connection = sqlite3.connect('mineralchemy.db', check_same_thread=False)
cursor = connection.cursor()

f = open("secret.txt")
keys = f.read().strip().split()
etsy_api_key = keys[0]
ebay_appID = keys[1]


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
		

@app.route("/user/<int:user_id>", methods=['GET'])
def user_page(user_id):
	"""Show details about user"""

	user = User.query.get(user_id)

	sql_query = "SELECT listing_origin, listing_id FROM favorites WHERE user_id = ?"
	cursor.execute(sql_query,(user.user_id,))
	results = cursor.fetchall()

	etsy_listings = []
	ebay_listings = []

	for result in results:
		if result[0] == "etsy":
			etsy_api_url = "https://openapi.etsy.com/v2/listings/%s?api_key=%s" % (result[1], etsy_api_key)
			r = requests.get(etsy_api_url).json()
			etsy_listings.append(
				{
				"title": r["results"][0]["title"],
				"price": r["results"][0]["price"],
				"url": r["results"][0]["url"]
				}
			)
		else:
			ebay_parameters = {
				"callname":"GetSingleItem",
				"responseencoding":"JSON",
				"appid":ebay_appID,
				"siteid":0,
				"version":515,
				"ItemID":result[1],
				"IncludeSelector":"Description,ItemSpecifics"
			}
			r = requests.get("http://open.api.ebay.com/shopping", params=ebay_parameters).json()
			ebay_listings.append(
				{
				"title": r["Item"]["Title"],
				"price": r["Item"]["ConvertedCurrentPrice"]["Value"],
				"url": r["Item"]["GalleryURL"]
				}
			)

	return render_template("user.html", user=user, etsy_listings=etsy_listings, ebay_listings=ebay_listings)


@app.route("/search")
def search():
	"""User inputs search specifications here"""
	
	return render_template("search.html")


@app.route("/search_results", methods=['POST'])
def get_results():

	keywords = request.form["keywords"]
	min_price = float(request.form["min_price"])
	max_price = float(request.form["max_price"])

	etsy_num_results, etsy_listings = search_etsy(keywords, min_price, max_price)
	ebay_num_results, ebay_listings = search_ebay(keywords, min_price, max_price)
	# minfind_num_results, minfind_listings = scrape_minfind(keywords, min_price, max_price)

	total_count = etsy_num_results + int(ebay_num_results)
	# total_count = etsy_num_results + int(ebay_num_results) + minfind_num_results

	all_listings = {
		"etsy": etsy_listings,
		"ebay": ebay_listings,
		# "minfind": minfind_listings
	}

	user_id = session.get("user_id", 0)

	return render_template("search_results.html", total_count=total_count, all_listings=all_listings, user_id=user_id)


@app.route("/add_to_favorites", methods=['GET'])
def add_to_favorites():
	
	user_id = request.args.get('user_id').encode(encoding='UTF-8',errors='strict')
	listing_origin = request.args.get('listing_origin').encode(encoding='UTF-8',errors='strict')
	listing_id = request.args.get('listing_id').encode(encoding='UTF-8',errors='strict')

	sql_query = "INSERT INTO favorites (user_id, listing_origin, listing_id) VALUES (?, ?, ?)"
	cursor.execute(sql_query, (user_id, listing_origin, listing_id))
	connection.commit()

	success_string = "Successfully added to your favorites!"

	return success_string

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