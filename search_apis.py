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
	etsy_listings = []
	count = 0

	for listing in r["results"]:
		# if listing["taxonomy_path"] == ["Art & Collectibles", "Collectibles"]:
		if keywords in listing["title"]:
			etsy_listings.append(listing)
			count += 1

	return count, etsy_listings # Array of Etsy listings (listing = dictionary)


def search_ebay(keywords, min_price, max_price):
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
	count = r["findItemsAdvancedResponse"][0]["searchResult"][0]["@count"]
	ebay_listings = r["findItemsAdvancedResponse"][0]["searchResult"][0]["item"]

	return count, ebay_listings #Array of Ebay listings (listing = dictionary)
