import requests


f = open("secret.txt")
keys = f.read().strip().split()
etsy_api_key = keys[0]
ebay_appID = keys[1]


def search_etsy(keywords, min_price, max_price):
	"""Search Etsy shops for listings within a price range.

	Each listing is represented by a dictionary. The keys in the dictionary correspond with 
	the listing id, listing origin, title, price, description, URL, and image URLs of the listing.

	Returns number of listings and a list of dictionaries.
	"""

	etsy_shop_ids = [7877556, 10879226, 7777338, 10537127, 8543678, 10879226, 7023347, 6951911]
	etsy_listings = []
	count = 0

	for shop_id in etsy_shop_ids:
		etsy_parameters = {
			"api_key": etsy_api_key,
			"shop_id_or_name": shop_id,
			"keywords": keywords,
			"min_price": float(min_price),
			"max_price": float(max_price),
			"limit": 100,
		}

		r = requests.get("https://openapi.etsy.com/v2/shops/%s/listings/active" % shop_id, params=etsy_parameters).json()

		for listing in r["results"]:
			images = requests.get("https://openapi.etsy.com/v2/listings/" + str(listing["listing_id"]) + "/images?api_key=" + etsy_api_key).json()
			image_urls = [image["url_fullxfull"] for image in images["results"]]
			
			etsy_listings.append(
				{
				"listing_id": listing["listing_id"],
				"listing_origin": "etsy",
				"title": listing["title"],
				"price": listing["price"], 
				"description": listing["description"],
				"url": listing["url"],
				"image_urls": image_urls
				}
			)

			count += 1

	return count, etsy_listings


def search_ebay(keywords, min_price, max_price):
	"""Search eBay for listings within a price range.

	Each listing is represented by a dictionary. The keys in the dictionary correspond with 
	the listing id, listing origin, title, price, description, URL, and image URLs of the listing.

	Returns number of listings and a list of dictionaries.
	"""

	ebay_parameters = {
		"OPERATION-NAME":"findItemsAdvanced",
		"SERVICE-VERSION":"1.13.0",
		"SECURITY-APPNAME":ebay_appID,
		"RESPONSE-DATA-FORMAT":"JSON",
		"keywords":keywords,
		"categoryId":"3225",
		"itemFilter(0).name":"MinPrice",
		"itemFilter(0).value":min_price,
		"itemFilter(0).paramName":"Currency",
		"itemFilter(0).paramValue":"USD",
		"itemFilter(0).name":"MaxPrice",
		"itemFilter(0).value":max_price,
		"itemFilter(0).paramName":"Currency",
		"itemFilter(0).paramValue":"USD"
	}

	r = requests.get("http://svcs.ebay.com/services/search/FindingService/v1", params=ebay_parameters).json()

	ebay_listings = []
	count = int(r["findItemsAdvancedResponse"][0]["searchResult"][0]["@count"])

	if count == 0:
		return count, ebay_listings
	else:
		listings = r["findItemsAdvancedResponse"][0]["searchResult"][0]["item"]

		for listing in listings:
			new_listing = {
				"listing_id": listing["itemId"][0],
				"listing_origin": "ebay",
				"title": listing["title"][0],
				"price": listing["sellingStatus"][0]["currentPrice"][0]["__value__"],
				"description": None, # Double check if need to make a new API call
				"url": listing["viewItemURL"][0]
				}
			try:
				new_listing["image_urls"] = listing["galleryPlusPictureURL"]
			except:
				new_listing["image_urls"] = []
			ebay_listings.append(new_listing)

		return count, ebay_listings
