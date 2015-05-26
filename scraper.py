from bs4 import BeautifulSoup
import urllib

def scrape_minfind(keywords):
	url = "http://www.minfind.com/search.php?" + urllib.urlencode({"qs":keywords})
	html = urllib.urlopen(url).read()
	soup = BeautifulSoup(html, "lxml")
	minfind_listings = []

	listings = soup.find_all("div", {"class":"minbox"})
	for listing in listings:
			listing_dict = {
				"listing_id": int(filter(str.isdigit, listing.a['href'])),
				"listing_origin": "minfind",
				"url": "http://www.minfind.com/" + listing.a['href'],
				"title": listing.find("div", {"class":"minboxmin"}).string.encode(encoding='UTF-8',errors='strict'),
				"price": float(listing.find("div", {"class":"minboxprice"}).string[1:]),
			}

			details_html = urllib.urlopen(listing_dict["url"]).read()
			details_soup = BeautifulSoup(details_html, "lxml")
			main_content = details_soup.find("div", {"id":"maincontent"})

			unicode_description = main_content.find("div", {"class":"fptext"}).contents[2]
			listing_dict["description"] = unicode_description.encode(encoding='UTF-8',errors='strict').strip()

			minfind_listings.append(listing_dict)

	print minfind_listings

scrape_minfind("pink tourmaline")