from flask import Flask, render_template, redirect, request, flash, session, jsonify
from model import User, connect_to_db, db
from search_apis import search_etsy, search_ebay
from scraper import scrape_minfind
from bs4 import BeautifulSoup
import urllib
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

	return render_template( "search_results.html", 
							keywords=keywords, min_price=min_price, 
							max_price=max_price, user_id=user_id )


@app.route("/scrape_minfind", methods=['GET'])
def get_minfind_results():

	keywords = request.args.get('keywords').encode(encoding='UTF-8',errors='strict')
	min_price = float(request.args.get('min_price'))
	max_price = float(request.args.get('max_price'))

	minfind_num_results, minfind_listings = scrape_minfind(keywords, min_price, max_price)

	success = { "minfindNumResults": minfind_num_results, 
				"minfindListings": minfind_listings }
	return jsonify(success)


@app.route("/search_etsy", methods=['GET'])
def get_etsy_results():

	keywords = request.args.get('keywords').encode(encoding='UTF-8',errors='strict')
	min_price = float(request.args.get('min_price'))
	max_price = float(request.args.get('max_price'))

	etsy_num_results, etsy_listings = search_etsy(keywords, min_price, max_price)

	success = { "etsyNumResults": etsy_num_results,
				"etsyListings": etsy_listings }
	return jsonify(success)


@app.route("/search_ebay", methods=['GET'])
def get_ebay_results():
	keywords = request.args.get('keywords').encode(encoding='UTF-8',errors='strict')
	min_price = float(request.args.get('min_price'))
	max_price = float(request.args.get('max_price'))

	ebay_num_results, ebay_listings = search_ebay(keywords, min_price, max_price)

	success = { "ebayNumResults": int(ebay_num_results), 
				"ebayListings": ebay_listings }
	return jsonify(success)


@app.route("/add_to_favorites", methods=['GET'])
def add_to_favorites():
	"""Add listing to favorites table in database."""
	
	user_id = request.args.get('user_id').encode(encoding='UTF-8',errors='strict')
	listing_origin = request.args.get('listing_origin').encode(encoding='UTF-8',errors='strict')
	listing_id = request.args.get('listing_id').encode(encoding='UTF-8',errors='strict')

	# Check to see if listing is already in favorites table for that user
	old_favorite_query = "SELECT * FROM favorites WHERE user_id = ? AND listing_id = ?"
	cursor.execute(old_favorite_query, (user_id, listing_id))
	old_favorite_result = cursor.fetchall()

	if old_favorite_result != []:
		return "You have already added this to your favorites!"
	else:
		new_favorite_query = "INSERT INTO favorites (user_id, listing_origin, listing_id) VALUES (?, ?, ?)"
		cursor.execute(new_favorite_query, (user_id, listing_origin, listing_id))
		connection.commit()
		return "Successfully added to your favorites!"


@app.route("/user/<int:user_id>", methods=['GET'])
def user_page(user_id):
	"""Show details and favorite listings of user."""

	user = User.query.get(user_id)

	sql_query = "SELECT listing_origin, listing_id FROM favorites WHERE user_id = ?"
	cursor.execute(sql_query,(user.user_id,))
	results = cursor.fetchall()

	etsy_listings = []
	ebay_listings = []
	minfind_listings = []

	# Make API call or scrape from website using listing origin and id
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
		elif result[0] == "ebay":
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
		else:
			minfind_url = "http://www.minfind.com/mineral-%s.html" % str(result[1])
			html = urllib.urlopen(minfind_url).read()
			soup = BeautifulSoup(html, "lxml")

			main_content = soup.find("div", {"id":"maincontent"})

			minfind_listings.append(
				{
				"title": main_content.h1.string.encode(encoding='UTF-8',errors='strict'),
				"price": main_content.find("div",{"class":"price"}).string[1:],
				"url": minfind_url
				}
			)

	return render_template("user.html", user=user, etsy_listings=etsy_listings, 
							ebay_listings=ebay_listings, minfind_listings=minfind_listings)


if __name__ == '__main__':
	app.debug = True
	connect_to_db(app)
	app.run()