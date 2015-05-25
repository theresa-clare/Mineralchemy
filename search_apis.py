import requests


f = open("secret.txt")
keys = f.read().strip().split()
etsy_api_key = keys[0]
ebay_appID = keys[1]


def search_etsy(keywords, min_price, max_price):
	etsy_parameters = {
		"api_key":etsy_api_key,
		"keywords":keywords,
		"min_price":float(min_price),
		"max_price":float(max_price),
		"category":"art_and_collectibles/Collectibles",
		"limit":100,
	}

	r = requests.get("https://openapi.etsy.com/v2/listings/active", params=etsy_parameters).json()
	
	# Create dictionary with keys as API name
	# Value of key is an array of a dictionary with listing information
	etsy_listings = {}
	etsy_listings["etsy"] = []
	count = r["count"]

	for listing in r["results"]:
		# if listing["taxonomy_path"] == ["Art & Collectibles", "Collectibles"]:
		if keywords in listing["title"]: # Filters
			images = requests.get("https://openapi.etsy.com/v2/listings/" + str(listing["listing_id"]) + "/images?api_key=" + etsy_api_key).json()
			image_urls = [image["url_fullxfull"] for image in images["results"]]
			
			etsy_listings["etsy"].append(
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

	return count, etsy_listings 


def search_ebay(keywords, min_price, max_price, all_listings):

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
	ebay_listings = r["findItemsAdvancedResponse"][0]["searchResult"][0]["item"]

	all_listings["ebay"] = []
	count = r["findItemsAdvancedResponse"][0]["searchResult"][0]["@count"]

	for listing in ebay_listings:
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
		all_listings["ebay"].append(new_listing)

	return count, all_listings # Contains Etsy and Ebay listings
