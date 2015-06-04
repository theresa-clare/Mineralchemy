from bs4 import BeautifulSoup
import urllib
import requests


f = open("secret.txt")
keys = f.read().strip().split()
etsy_api_key = keys[0]
ebay_appID = keys[1]


def get_favorites(results):
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
	return etsy_listings, ebay_listings, minfind_listings